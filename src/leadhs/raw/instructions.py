"""Sourcing instruction files — schema v1 (v0.3.0).

One JSON file per bulk source (``raw_sources/<source_id>.instruction.json``):
the reviewable contract that drives ``raw run``. The schema authority is
``.3SM/plan/DESIGN/v0.3.0/interfaces.md``; one build-time addition is
recorded there at docs sync: the optional ``table_name`` field (the
pinned 0012 tables carry their slugs; a new source without it derives
``raw_<source_id snake>``).

Validation is fail-closed BEFORE any network call: unknown schema
version, unknown fields (typo protection, forward-only evolution like
migrations), empty/misdirected natural key, ``_``-prefixed columns
(reserved bookkeeping namespace), non-positive budgets, delay < 2 s,
bad URLs — every refusal names its JSON path. Reserved export kinds
(``web_query``, ``html_pages``) are *valid* instructions: ``raw
explain`` renders them; the interpreting commands refuse them.

``manifest_hash`` is the sha256 of the canonical RE-serialization
(sorted keys, 2-space indent, UTF-8, trailing newline) — never of the
raw file bytes, so hand-edited key order or whitespace does not change
the contract version.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from typing import Optional
from urllib.parse import urlparse

SCHEMA_VERSION = 1

EXPORT_KINDS = ("csv_snapshot", "api_endpoint", "web_query", "html_pages")
RESERVED_EXPORT_KINDS = ("web_query", "html_pages")
PAGINATION_KINDS = ("single", "page_param", "offset")
RESERVED_PAGINATION_KINDS = ("cursor",)
COLUMN_TYPES = ("text", "int", "float", "date_iso")
SOURCE_CLASSES = ("CS", "PE", "LG", "ST", "LI", "AS")
MIN_DELAY_SECONDS = 2.0
DEFAULT_PAYLOAD_BUDGET_BYTES = 1024

_SOURCE_ID_RE = re.compile(r"^[A-Z]{2}-[0-9]+$")
_COLUMN_RE = re.compile(r"^[a-z][a-z0-9_]*$")

_TOP_FIELDS = {
    "schema_version", "source_id", "source_name", "source_class",
    "export_kind", "delimiter", "endpoints", "pagination", "records",
    "columns", "natural_key", "payload_budget_bytes", "politeness",
    "notes", "table_name",
}
_TOP_REQUIRED = _TOP_FIELDS - {"payload_budget_bytes", "notes", "table_name"}
_ENDPOINT_FIELDS = {"list", "detail"}
_PAGINATION_FIELDS = {"kind", "page_param", "page_size", "max_pages"}
_PAGINATION_PAGE_PARAM_FIELDS = {"page_param", "page_size", "max_pages"}
_RECORDS_FIELDS = {"expected_count", "count_derivation"}
_COLUMN_FIELDS = {"source_header", "column", "type", "truncation_priority", "description"}
_COLUMN_REQUIRED = _COLUMN_FIELDS - {"description"}
_POLITENESS_FIELDS = {
    "delay_seconds", "crawl_delay_seconds", "request_budget_per_run",
    "records_per_request", "derivation",
}
_POLITENESS_REQUIRED = _POLITENESS_FIELDS - {"crawl_delay_seconds", "records_per_request"}


class InstructionError(Exception):
    """A named-field refusal; the message always carries the JSON path."""


@dataclasses.dataclass(frozen=True)
class Column:
    source_header: str
    column: str
    type: str = "text"
    truncation_priority: int = 1
    description: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Pagination:
    kind: str
    page_param: Optional[str] = None
    page_size: Optional[int] = None
    max_pages: Optional[int] = None


@dataclasses.dataclass(frozen=True)
class Politeness:
    delay_seconds: float
    request_budget_per_run: int
    derivation: str
    crawl_delay_seconds: Optional[float] = None
    records_per_request: Optional[int] = None


@dataclasses.dataclass(frozen=True)
class Instruction:
    source_id: str
    source_name: str
    source_class: str
    export_kind: str
    delimiter: str
    endpoints: dict
    pagination: Pagination
    records: dict
    columns: tuple
    natural_key: tuple
    politeness: Politeness
    payload_budget_bytes: int = DEFAULT_PAYLOAD_BUDGET_BYTES
    notes: Optional[str] = None
    table_name: Optional[str] = None

    @property
    def list_url(self) -> str:
        return self.endpoints["list"]

    @property
    def column_names(self) -> tuple:
        return tuple(c.column for c in self.columns)

    def to_dict(self) -> dict:
        """The exact schema-v1 dict (canonical input to the hash)."""
        doc: dict = {
            "schema_version": SCHEMA_VERSION,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_class": self.source_class,
            "export_kind": self.export_kind,
            "delimiter": self.delimiter,
            "endpoints": dict(self.endpoints),
            "pagination": dataclasses.asdict(self.pagination),
            "records": dict(self.records),
            "columns": [dataclasses.asdict(c) for c in self.columns],
            "natural_key": list(self.natural_key),
            "politeness": dataclasses.asdict(self.politeness),
            "payload_budget_bytes": self.payload_budget_bytes,
        }
        if self.notes is not None:
            doc["notes"] = self.notes
        if self.table_name is not None:
            doc["table_name"] = self.table_name
        return doc

    def to_canonical_json(self) -> bytes:
        return canonical_json(self.to_dict())

    def manifest_hash(self) -> str:
        return hashlib.sha256(self.to_canonical_json()).hexdigest()


def canonical_json(doc: dict) -> bytes:
    """Canonical serialization: sorted keys, 2-space indent, UTF-8,
    trailing newline (interfaces.md rs2)."""
    return (json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _is_http_url(value) -> bool:
    if not isinstance(value, str) or not value:
        return False
    parts = urlparse(value)
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def _require_number(where: str, value, minimum: float):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InstructionError(f"{where}: must be a number, got {value!r}")
    if value < minimum:
        raise InstructionError(f"{where}: must be >= {minimum}, got {value}")
    return value


def _require_int(where: str, value, minimum: int):
    if isinstance(value, bool) or not isinstance(value, int):
        raise InstructionError(f"{where}: must be an integer, got {value!r}")
    if value < minimum:
        raise InstructionError(f"{where}: must be >= {minimum}, got {value}")
    return value


def from_dict(raw) -> Instruction:
    """Parse + validate in one fail-closed pass; refuses with a named
    JSON path on every rule of the interfaces.md matrix."""
    if not isinstance(raw, dict):
        raise InstructionError("root: instruction must be a JSON object")

    version = raw.get("schema_version")
    if version != SCHEMA_VERSION:
        raise InstructionError(
            f"schema_version: unknown {version!r} — this build speaks schema v{SCHEMA_VERSION} only"
        )
    unknown = set(raw) - _TOP_FIELDS
    if unknown:
        raise InstructionError(f"root: unknown field(s) {sorted(unknown)} — refused (typo protection)")
    missing = _TOP_REQUIRED - set(raw)
    if missing:
        raise InstructionError(f"root: missing required field(s) {sorted(missing)}")

    source_id = raw["source_id"]
    if not isinstance(source_id, str) or not _SOURCE_ID_RE.match(source_id):
        raise InstructionError(f"source_id: bad source id {source_id!r} (need CS-1 style)")
    source_name = raw["source_name"]
    if not isinstance(source_name, str) or not source_name.strip():
        raise InstructionError("source_name: must be a non-empty string")
    source_class = raw["source_class"]
    if source_class not in SOURCE_CLASSES:
        raise InstructionError(f"source_class: unknown {source_class!r} (one of {list(SOURCE_CLASSES)})")

    export_kind = raw["export_kind"]
    if export_kind not in EXPORT_KINDS:
        raise InstructionError(f"export_kind: unknown {export_kind!r} (one of {list(EXPORT_KINDS)})")

    delimiter = raw["delimiter"]
    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise InstructionError(f"delimiter: must be exactly one character, got {delimiter!r}")

    endpoints = raw["endpoints"]
    if not isinstance(endpoints, dict):
        raise InstructionError("endpoints: must be an object")
    unknown = set(endpoints) - _ENDPOINT_FIELDS
    if unknown:
        raise InstructionError(f"endpoints: unknown field(s) {sorted(unknown)}")
    if "list" not in endpoints or not _is_http_url(endpoints["list"]):
        raise InstructionError(f"endpoints.list: not an http(s) URL: {endpoints.get('list')!r}")
    detail = endpoints.get("detail")
    if detail is not None and not _is_http_url(detail):
        raise InstructionError(f"endpoints.detail: not an http(s) URL or null: {detail!r}")

    pagination_raw = raw["pagination"]
    if not isinstance(pagination_raw, dict):
        raise InstructionError("pagination: must be an object")
    unknown = set(pagination_raw) - _PAGINATION_FIELDS
    if unknown:
        raise InstructionError(f"pagination: unknown field(s) {sorted(unknown)}")
    kind = pagination_raw.get("kind")
    if kind in RESERVED_PAGINATION_KINDS or kind not in PAGINATION_KINDS:
        raise InstructionError(
            f"pagination.kind: {kind!r} not supported (one of {list(PAGINATION_KINDS)}; cursor reserved)"
        )
    if kind == "page_param":
        missing = _PAGINATION_PAGE_PARAM_FIELDS - set(pagination_raw)
        if missing:
            raise InstructionError(f"pagination: page_param kind requires {sorted(missing)}")
    else:
        stray = _PAGINATION_PAGE_PARAM_FIELDS & set(pagination_raw)
        if stray:
            raise InstructionError(
                f"pagination: field(s) {sorted(stray)} only valid for kind=page_param"
            )
    page_param = pagination_raw.get("page_param")
    if page_param is not None and (not isinstance(page_param, str) or not page_param.strip()):
        raise InstructionError("pagination.page_param: must be a non-empty string")
    page_size = pagination_raw.get("page_size")
    if page_size is not None:
        _require_int("pagination.page_size", page_size, 1)
    max_pages = pagination_raw.get("max_pages")
    if max_pages is not None:
        _require_int("pagination.max_pages", max_pages, 1)
    pagination = Pagination(
        kind=kind, page_param=page_param, page_size=page_size, max_pages=max_pages,
    )

    records_raw = raw["records"]
    if not isinstance(records_raw, dict):
        raise InstructionError("records: must be an object")
    unknown = set(records_raw) - _RECORDS_FIELDS
    if unknown:
        raise InstructionError(f"records: unknown field(s) {sorted(unknown)}")
    missing = _RECORDS_FIELDS - set(records_raw)
    if missing:
        raise InstructionError(f"records: missing required field(s) {sorted(missing)}")
    expected_count = records_raw["expected_count"]
    if expected_count is not None:
        _require_int("records.expected_count", expected_count, 0)
    count_derivation = records_raw["count_derivation"]
    if not isinstance(count_derivation, str) or not count_derivation.strip():
        raise InstructionError("records.count_derivation: must be a non-empty string")

    columns_raw = raw["columns"]
    if not isinstance(columns_raw, list) or not columns_raw:
        raise InstructionError("columns: must be a non-empty array")
    columns = []
    seen_columns: set = set()
    seen_headers: set = set()
    for i, col in enumerate(columns_raw):
        where = f"columns[{i}]"
        if not isinstance(col, dict):
            raise InstructionError(f"{where}: must be an object")
        unknown = set(col) - _COLUMN_FIELDS
        if unknown:
            raise InstructionError(f"{where}: unknown field(s) {sorted(unknown)}")
        missing = _COLUMN_REQUIRED - set(col)
        if missing:
            raise InstructionError(f"{where}: missing required field(s) {sorted(missing)}")
        header = col["source_header"]
        if not isinstance(header, str) or not header.strip():
            raise InstructionError(f"{where}.source_header: must be a non-empty string")
        if header in seen_headers:
            raise InstructionError(f"{where}.source_header: duplicate {header!r}")
        seen_headers.add(header)
        name = col["column"]
        if not isinstance(name, str) or not _COLUMN_RE.match(name):
            raise InstructionError(
                f"{where}.column: bad column name {name!r} (snake_case, must not start with '_')"
            )
        if name.startswith("_"):
            raise InstructionError(f"{where}.column: '_'-prefixed names are reserved bookkeeping")
        if name in seen_columns:
            raise InstructionError(f"{where}.column: duplicate column {name!r}")
        seen_columns.add(name)
        ctype = col["type"]
        if ctype not in COLUMN_TYPES:
            raise InstructionError(f"{where}.type: unknown {ctype!r} (one of {list(COLUMN_TYPES)})")
        priority = _require_int(f"{where}.truncation_priority", col["truncation_priority"], 1)
        description = col.get("description")
        if description is not None and not isinstance(description, str):
            raise InstructionError(f"{where}.description: must be a string")
        columns.append(Column(
            source_header=header, column=name, type=ctype,
            truncation_priority=priority, description=description,
        ))

    natural_key = raw["natural_key"]
    if not isinstance(natural_key, list) or not natural_key:
        raise InstructionError("natural_key: must be a non-empty array of column names")
    known = seen_columns
    for i, key in enumerate(natural_key):
        if key not in known:
            raise InstructionError(f"natural_key[{i}]: {key!r} is not a declared column")
    if len(set(natural_key)) != len(natural_key):
        raise InstructionError("natural_key: duplicate column in key")

    budget = raw.get("payload_budget_bytes", DEFAULT_PAYLOAD_BUDGET_BYTES)
    _require_int("payload_budget_bytes", budget, 1)

    politeness_raw = raw["politeness"]
    if not isinstance(politeness_raw, dict):
        raise InstructionError("politeness: must be an object")
    unknown = set(politeness_raw) - _POLITENESS_FIELDS
    if unknown:
        raise InstructionError(f"politeness: unknown field(s) {sorted(unknown)}")
    missing = _POLITENESS_REQUIRED - set(politeness_raw)
    if missing:
        raise InstructionError(f"politeness: missing required field(s) {sorted(missing)}")
    delay = _require_number("politeness.delay_seconds", politeness_raw["delay_seconds"], MIN_DELAY_SECONDS)
    if delay < MIN_DELAY_SECONDS:
        raise InstructionError(
            f"politeness.delay_seconds: {delay} is below the {MIN_DELAY_SECONDS} s floor"
        )
    crawl_delay = politeness_raw.get("crawl_delay_seconds")
    if crawl_delay is not None:
        _require_number("politeness.crawl_delay_seconds", crawl_delay, 0)
    request_budget = _require_int(
        "politeness.request_budget_per_run", politeness_raw["request_budget_per_run"], 1,
    )
    records_per_request = politeness_raw.get("records_per_request")
    if records_per_request is not None:
        _require_int("politeness.records_per_request", records_per_request, 1)
    derivation = politeness_raw["derivation"]
    if not isinstance(derivation, str) or not derivation.strip():
        raise InstructionError("politeness.derivation: must be a non-empty string")
    politeness = Politeness(
        delay_seconds=delay, request_budget_per_run=request_budget,
        derivation=derivation, crawl_delay_seconds=crawl_delay,
        records_per_request=records_per_request,
    )

    table_name = raw.get("table_name")
    if table_name is not None:
        if not isinstance(table_name, str) or not _COLUMN_RE.match(table_name) or table_name.startswith("_"):
            raise InstructionError(f"table_name: bad table name {table_name!r} (snake_case)")

    notes = raw.get("notes")
    if notes is not None and not isinstance(notes, str):
        raise InstructionError("notes: must be a string")

    return Instruction(
        source_id=source_id, source_name=source_name.strip(), source_class=source_class,
        export_kind=export_kind, delimiter=delimiter,
        endpoints={"list": endpoints["list"], "detail": detail},
        pagination=pagination,
        records={"expected_count": expected_count, "count_derivation": count_derivation},
        columns=tuple(columns), natural_key=tuple(natural_key), politeness=politeness,
        payload_budget_bytes=budget, notes=notes, table_name=table_name,
    )


def loads(text: str) -> Instruction:
    """Parse a JSON string; unparsable JSON is a named refusal."""
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InstructionError(f"root: unparsable JSON — {exc}") from exc
    return from_dict(raw)


def load(path: str) -> tuple:
    """Read an instruction file → (Instruction, manifest_hash)."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise InstructionError(f"{path}: cannot read — {exc}") from exc
    inst = loads(text)
    return inst, inst.manifest_hash()

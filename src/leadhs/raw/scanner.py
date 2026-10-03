"""raw scan — profile a live delivery into a draft sourcing instruction
(v0.3.0, r02).

The scanner is the *derivation* half of the instruction contract: it
fetches the delivery once (politeness floor + robots via the single
fetch seam), counts records exactly, maps headers to snake_case
columns, samples per-column emptiness/types, searches natural-key
candidates (unique singles, then bounded pairs), reads the robots
crawl-delay, and derives the politeness guards (rs4 flood guard: few
records per request → longer delay). Emission (canonical draft file,
drift line vs the newest pinned ``catalog_count`` finding) lives in
``draft_instruction``/``drift_line``.

It NEVER writes DB rows — the draft lands in the instructions
directory for human review (the reviewable-contract gate).
Interpreter depth at v0.3.0: ``csv_snapshot`` and ``api_endpoint``
(``single``); reserved kinds are a named refusal here.
"""

from __future__ import annotations

import csv
import io
import itertools
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .. import db as dbmod
from . import delivery_text
from .instructions import canonical_json

PROBE_URL_CAP = 65536
_FLOOD_RECORDS_PER_REQUEST = 10
_FLOOD_DELAY_SECONDS = 5.0
_REQUEST_HEADROOM = 3  # single fetch + headroom for retries/reruns
_TYPE_SAMPLE = 1000

_INT_RE = re.compile(r"^-?\d+$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ScanError(Exception):
    """Named scan refusal/failure; the CLI maps it to exit 2."""


@dataclass
class ScanProfile:
    source_id: str
    url: str
    export_kind: str = ""
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    robots_policy: str = "unknown"
    crawl_delay: Optional[float] = None
    record_count: int = 0
    records_per_request: int = 0
    delimiter: str = ","
    columns: list = field(default_factory=list)  # {header,column,type,empty_pct}
    natural_key: list = field(default_factory=list)
    key_note: Optional[str] = None
    api_total: Optional[int] = None
    api_single_shape: str = ""
    notes: list = field(default_factory=list)


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def snake_case(header: str, taken: set) -> str:
    """Verbatim source header → SQL-safe snake_case column (D44: the
    mapping is recorded, values stay untouched)."""
    name = re.sub(r"[^0-9a-zA-Z]+", "_", header.strip()).strip("_").lower()
    if not name:
        name = "col"
    if name[0].isdigit():
        name = "c" + name
    base, n = name, 2
    while name in taken:
        name = f"{base}_{n}"
        n += 1
    taken.add(name)
    return name


def _guess_type(values: list) -> str:
    if not values:
        return "text"
    if all(_INT_RE.match(v) for v in values):
        return "int"
    try:
        for v in values:
            float(v)
        return "float"
    except ValueError:
        pass
    if all(_DATE_RE.match(v) for v in values):
        return "date_iso"
    return "text"


def _sniff_delimiter(text: str) -> str:
    line = text.splitlines()[0] if text.splitlines() else ""
    counts = {d: line.count(d) for d in (";", ",", "\t", "|")}
    best = max(counts, key=lambda d: counts[d])
    return best if counts[best] > 0 else ","


def _parse_api_total(payload) -> Optional[int]:
    if isinstance(payload, dict):
        for key in ("total", "count", "totalElements", "recordsTotal"):
            v = payload.get(key)
            if isinstance(v, int) and not isinstance(v, bool):
                return v
    return None


def scan_delivery(fetcher, source, url: str) -> ScanProfile:
    """One polite fetch + full profile of the delivery."""
    profile = ScanProfile(source_id=source.id, url=url)
    profile.robots_policy = fetcher.robots_policy(url)
    if profile.robots_policy == "disallowed":
        raise ScanError(f"{source.id}: robots.txt disallows our path — scan refused")
    profile.crawl_delay = fetcher.crawl_delay(url)

    resp = fetcher.get(url)
    if resp.status_code >= 400:
        raise ScanError(
            f"{source.id}: HTTP {resp.status_code} — no delivery at this URL "
            f"(route dead or moved; content-type {(resp.headers.get('Content-Type') or '?').split(';')[0]})"
        )
    profile.content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    length = resp.headers.get("Content-Length")
    profile.size_bytes = int(length) if length and length.isdigit() else len(resp.content)

    text = delivery_text(resp)
    if "json" in profile.content_type or text.lstrip().startswith(("[", "{")):
        return _scan_json(profile, text)
    return _scan_csv(profile, text)


def _scan_json(profile: ScanProfile, text: str) -> ScanProfile:
    profile.export_kind = "api_endpoint"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ScanError(f"{profile.source_id}: unparsable JSON delivery — {exc}") from exc
    if isinstance(payload, list):
        records = payload
        profile.api_single_shape = "top-level array"
    elif isinstance(payload, dict):
        records = None
        for key in ("items", "value", "results", "data", "records"):
            if isinstance(payload.get(key), list):
                records = payload[key]
                profile.api_single_shape = f"object with {key!r} array"
                break
        if records is None:
            raise ScanError(
                f"{profile.source_id}: JSON object carries no recognizable record array "
                f"(tried items/value/results/data/records) — shape needs a human"
            )
    else:
        raise ScanError(f"{profile.source_id}: JSON delivery is neither object nor array")
    profile.api_total = _parse_api_total(payload)
    profile.record_count = len(records)
    profile.records_per_request = len(records)
    taken: set = set()
    headers: list = []
    for rec in records[:_TYPE_SAMPLE]:
        if isinstance(rec, dict):
            for key in rec:
                if key not in headers:
                    headers.append(str(key))
    if not headers:
        raise ScanError(f"{profile.source_id}: JSON records carry no object keys — shape needs a human")
    empties = [0] * len(headers)
    samples: list = [[] for _ in headers]
    for rec in records[:_TYPE_SAMPLE]:
        for i, h in enumerate(headers):
            v = rec.get(h) if isinstance(rec, dict) else None
            if v is None or v == "":
                empties[i] += 1
            elif len(samples[i]) < _TYPE_SAMPLE:
                samples[i].append(str(v))
    profile.columns = [
        {
            "source_header": headers[i],
            "column": snake_case(headers[i], taken),
            "type": _guess_type(samples[i]),
            "empty_pct": round(100.0 * empties[i] / max(len(records[:_TYPE_SAMPLE]), 1), 1),
        }
        for i in range(len(headers))
    ]
    profile.natural_key = []
    profile.key_note = (
        "JSON sample: declare the business key after reviewing the columns "
        "(the run refuses an empty natural_key)"
    )
    profile.notes.append(
        "single-request draft: fill pagination (kind=page_param + page_param/page_size/max_pages) "
        "if the API paginates — the run refuses until the shape is confirmed"
    )
    return profile


def _scan_csv(profile: ScanProfile, text: str) -> ScanProfile:
    profile.export_kind = "csv_snapshot"
    if not text.strip():
        raise ScanError(f"{profile.source_id}: empty delivery — nothing to profile")
    profile.delimiter = _sniff_delimiter(text)
    reader = csv.reader(io.StringIO(text), delimiter=profile.delimiter)
    try:
        headers = next(reader)
    except StopIteration:
        raise ScanError(f"{profile.source_id}: delivery has no header row")
    headers = [h.strip() for h in headers]
    taken: set = set()
    colnames = [snake_case(h, taken) for h in headers]
    empties = [0] * len(headers)
    samples: list = [[] for _ in range(len(headers))]
    rows: list = []
    for row in reader:
        if not row or (len(row) == 1 and not row[0].strip()):
            continue  # trailing blank line
        rows.append(row)
        for i in range(len(headers)):
            value = row[i].strip() if i < len(row) else ""
            if not value:
                empties[i] += 1
            elif len(samples[i]) < _TYPE_SAMPLE:
                samples[i].append(value)
    profile.record_count = len(rows)
    profile.records_per_request = len(rows)  # one snapshot fetch carries all
    profile.columns = [
        {
            "source_header": headers[i],
            "column": colnames[i],
            "type": _guess_type(samples[i]),
            "empty_pct": round(100.0 * empties[i] / len(rows), 1) if rows else 100.0,
        }
        for i in range(len(headers))
    ]
    _find_csv_key(profile, rows)
    return profile


def _find_csv_key(profile: ScanProfile, rows: list) -> None:
    """Lattice search for the smallest unique column combination:
    singles, then pairs, triples, quads over ALL columns (bounded to
    ≤ 14 columns; wider deliveries fall back to the fully-populated
    bound). Stops at the first unique combo — smaller keys win. An
    unresolvable key emits no key + a loud note (the run refuses an
    empty natural_key — a human declares one)."""
    n = len(profile.columns)
    if not rows:
        profile.key_note = "no data rows — nothing to derive a key from"
        return
    if n <= 14:
        candidates = [list(itertools.combinations(range(n), k)) for k in (1, 2, 3, 4)]
    else:
        full = [i for i in range(n) if profile.columns[i]["empty_pct"] == 0.0]
        candidates = [
            [(i,) for i in full]
            + list(itertools.combinations(full[:12], 2))
            + list(itertools.combinations(full[:8], 3))
            + list(itertools.combinations(full[:10], 4)),
        ]
    depths = {1: "single", 2: "pair", 3: "triple", 4: "quad"}
    for level in candidates:
        for combo in level:
            seen = {tuple(row[i] for i in combo) for row in rows}
            if len(seen) == len(rows):
                profile.natural_key = [profile.columns[i]["column"] for i in combo]
                names = " + ".join(repr(profile.columns[i]["source_header"]) for i in combo)
                profile.key_note = f"unique {depths[len(combo)]}: {names}"
                return
    profile.key_note = (
        "no unique key among singles/pairs/triples/quads of all columns — the export "
        "carries intra-export duplicates; keep natural_key [] for the degraded "
        "row-hash identity mode (byte-identical rows collapse, changed content "
        "inserts), or declare a business key"
    )


# --- guard derivation (rs4) ------------------------------------------


def derive_guards(profile: ScanProfile) -> dict:
    """Politeness block from the scan: delay floor 2 s, crawl-delay
    honored (larger wins), flood guard (few records per request →
    longer delay), small request budget with headroom."""
    delay = 2.0
    if profile.crawl_delay and profile.crawl_delay > delay:
        delay = float(profile.crawl_delay)
    flood = profile.records_per_request < _FLOOD_RECORDS_PER_REQUEST
    if flood:
        delay = max(delay, _FLOOD_DELAY_SECONDS)
    budget = _REQUEST_HEADROOM
    crawl = profile.crawl_delay if profile.crawl_delay and profile.crawl_delay > 2.0 else None
    if flood:
        derivation = (
            f"flood guard: {profile.records_per_request} records/request < "
            f"{_FLOOD_RECORDS_PER_REQUEST} → delay raised to {delay}s; "
            f"budget {budget} requests/run (single-shape draft)"
        )
    else:
        derivation = (
            f"{profile.records_per_request:,} records/request at scan; "
            f"delay {delay}s"
            + (f" (robots crawl-delay)" if crawl else " (floor)")
            + f"; budget {budget} requests/run"
        )
    return {
        "delay_seconds": delay,
        "crawl_delay_seconds": crawl,
        "request_budget_per_run": budget,
        "records_per_request": profile.records_per_request or None,
        "derivation": derivation,
    }


def draft_instruction(profile: ScanProfile, source, table_name: Optional[str] = None) -> dict:
    """Schema-v1 draft dict from the profile (canonical input for the
    committed instruction file)."""
    expected = profile.api_total if profile.export_kind == "api_endpoint" else profile.record_count
    derivation = (
        f"raw scan {today()}: API total field" if profile.export_kind == "api_endpoint" and profile.api_total is not None
        else f"raw scan {today()}: full download, counted"
    )
    if profile.export_kind == "api_endpoint" and profile.api_total is None:
        expected = None
        derivation = f"raw scan {today()}: single-request sample, no total field — count unknown"
    columns = [
        {
            "source_header": c["source_header"],
            "column": c["column"],
            "type": c["type"],
            "truncation_priority": 1,
            "description": f"empty: {c['empty_pct']}%",
        }
        for c in profile.columns
    ]
    key = list(profile.natural_key)
    notes = []
    if profile.key_note:
        notes.append(profile.key_note)
    notes.extend(profile.notes)
    return {
        "schema_version": 1,
        "source_id": source.id,
        "source_name": source.name,
        "source_class": source.class_code,
        "export_kind": profile.export_kind,
        "delimiter": profile.delimiter if profile.export_kind == "csv_snapshot" else ",",
        "endpoints": {"list": profile.url, "detail": None},
        "pagination": {"kind": "single"},
        "records": {"expected_count": expected, "count_derivation": derivation},
        "columns": columns,
        "natural_key": key,
        "payload_budget_bytes": 1024,
        "politeness": derive_guards(profile),
        "notes": "; ".join(notes) if notes else None,
        "table_name": table_name,
    }


def draft_bytes(draft: dict) -> bytes:
    """Validated canonical form (refuses an invalid draft loudly)."""
    from . import instructions as instructionsmod

    instructionsmod.from_dict(draft)  # validation gate — same refusals as the run
    return canonical_json(draft)


def resolve_table_name(conn, source_id: str) -> str:
    """The pinned table when migration 0012 (or a later one) already
    created one for this source; else ``raw_<source_id no-dash>``. The
    lookup tries both snake spellings — the register id ``AS-2``
    sanitizes to ``as2`` (the pinned ``raw_as2_ecat``), a future
    ``AS-33`` to ``as33`` (``raw_as33_basta``)."""
    nodash = source_id.lower().replace("-", "")
    tables = [
        r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
            (f"raw_{nodash}%",),
        )
    ]
    if len(tables) == 1:
        return tables[0]
    if len(tables) > 1:
        return min(tables, key=len)  # ambiguous — shortest wins, noted at scan
    return f"raw_{nodash}"


def pinned_catalog_count(conn, source_id: str) -> Optional[int]:
    """The newest pinned ``catalog_count`` finding for the source (the
    drift anchor)."""
    row = conn.execute(
        """
        SELECT pf.value_numeric FROM probe_finding pf
        JOIN run r ON r.id = pf.run_id
        WHERE pf.metric_code = 'catalog_count' AND r.source_id = ?
          AND pf.value_numeric IS NOT NULL
        ORDER BY r.id DESC LIMIT 1
        """,
        (source_id,),
    ).fetchone()
    return int(row[0]) if row else None


def drift_line(conn, source_id: str, expected: Optional[int]) -> Optional[str]:
    """Drift vs the pinned keyfigure — printed, never silent."""
    pinned = pinned_catalog_count(conn, source_id)
    if pinned is None or expected is None:
        return None
    if pinned == expected:
        return f"drift: none (matches pinned catalog_count {pinned:,})"
    return f"drift: scan count {expected:,} vs pinned catalog_count {pinned:,} (diff {expected - pinned:+,})"

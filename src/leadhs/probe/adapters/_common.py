"""Shared adapter helpers and the error taxonomy (v0.2.3 PHASE02 split).

Error taxonomy (interfaces.md): ``UnexpectedFormat`` (export layout
not as expected), ``BinaryMissing`` / ``ExtractionError`` (mdbtools
absent / SPIN extraction fails), ``ParseError`` (unparseable/empty
HTML). The engine maps them to findings. Adapters may carry a
partial ``ProbeResult`` on the error so findings collected before a
block are preserved (outcome rule: reachable with findings -> done).
"""

from __future__ import annotations

import csv
import io
from typing import Optional, Protocol

from bs4 import BeautifulSoup

from ...fetch import FetchResponse
from ...logutil import log_event
from ...models import DocumentDraft, ProbeResult, SourceRef

__all__ = [
    "AdapterError",
    "UnexpectedFormat",
    "BinaryMissing",
    "ExtractionError",
    "ParseError",
    "ProbeAdapter",
    "registry",
    "get_adapter",
    "register",
    "_log",
    "sniff_kind",
    "read_csv_rows",
    "depth_tier",
    "_delimiter_of",
    "_doc",
    "_match_link",
    "_soup",
    "_JSON_LIST_COUNTS",
]

# Shared list-payload keys (CS _rows_of and AS _json_register).
_JSON_LIST_COUNTS = ("value", "obs", "records", "observations", "data")

class AdapterError(Exception):
    def __init__(
        self,
        detail: str,
        partial: Optional[ProbeResult] = None,
        url: Optional[str] = None,
    ):
        self.detail = detail
        self.partial = partial
        self.url = url
        super().__init__(detail)


class UnexpectedFormat(AdapterError):
    pass


class BinaryMissing(AdapterError):
    pass


class ExtractionError(AdapterError):
    pass


class ParseError(AdapterError):
    pass


class ProbeAdapter(Protocol):
    key: str  # source class: 'CS' | 'PE' | 'ST'

    def supports(self, source: SourceRef) -> bool: ...

    def probe(self, source: SourceRef, ctx: object) -> ProbeResult: ...


registry: list = []


def get_adapter(source: SourceRef):
    for adapter in registry:
        if adapter.supports(source):
            return adapter
    return None


def register(adapter):
    registry.append(adapter)
    return adapter


# --- shared helpers -----------------------------------------------------


def _log(ctx, event, **fields):
    if ctx.logger is not None:
        log_event(ctx.logger, "adapter", event, **fields)


def sniff_kind(content_type: str | None, head: bytes) -> str:
    """Content-type + first-bytes gate, run BEFORE any export parse
    (v0.2.2 e3 — the AS-7 HTML-as-CSV regression class). Returns
    ``csv | tsv | json | jsonstat | xlsx | html | other``."""
    ct = (content_type or "").split(";")[0].strip().lower()
    head_l = head.lstrip()
    if head_l[:1] == b"<":
        return "html"
    if head_l[:1] in (b"{", b"["):
        return "jsonstat" if b'"class"' in head_l and b'"dataset"' in head_l else "json"
    if head_l[:4] == b"PK\x03\x04":
        return "xlsx"
    if ct in ("text/csv", "application/csv"):
        return "csv"
    if ct in ("text/tab-separated-values",):
        return "tsv"
    if "json" in ct:
        return "json"
    if "html" in ct or "xml" in ct:
        return "html" if "html" in ct else "xml"
    if "spreadsheet" in ct or ct.endswith("sheet"):
        return "xlsx"
    return "other"


def read_csv_rows(text, *, separator=",", expected=None):
    """The one CSV-consumer path (e3/Q1): BOM/encoding-tolerant decode,
    shape validation with column-drift detection. Returns
    ``(header, data_rows)``; raises UnexpectedFormat on empty payload or
    header drift (``expected`` names missing from the header)."""
    try:
        text = text.decode("utf-8-sig")
    except AttributeError:
        pass
    except UnicodeDecodeError:
        text = text.decode("latin-1", errors="replace")
    reader = csv.reader(io.StringIO(text), delimiter=separator)
    rows = [r for r in reader if any(c.strip() for c in r)]
    if not rows:
        raise UnexpectedFormat("empty register export")
    header = [c.strip().lower() for c in rows[0]]
    if len(header) < 2:
        raise UnexpectedFormat(f"register layout missing columns (got {header})")
    if expected:
        missing = sorted(set(expected) - set(header))
        if missing:
            raise UnexpectedFormat(f"column drift: missing expected columns {missing} (header: {header})")
    return header, rows[1:]


def depth_tier(has_manu, has_ident):
    """cap_depth_tier, refined wording (fu8): 1 name-only · 2 registry
    metadata (name + ident/licence + category — NO technical data) ·
    3 adds technical performance data / downloadable tech docs ·
    4 standardized full documents. The automated register inspect can
    only certify name + ident + (nomenclature), so the floor is 2."""
    if has_manu and has_ident:
        return 2
    return 1


def _delimiter_of(header_line: bytes) -> str:
    """Delimiter heuristic for the shared CSV path: the header line's
    counts decide (`,` vs `;` vs tab). Real layouts are pinned per
    source at W1; this only unblocks mixed dialects."""
    try:
        line = header_line.decode("utf-8-sig", errors="replace")
    except Exception:
        return ","
    if line.count("\t") > line.count(",") and line.count("\t") > line.count(";"):
        return "\t"
    if line.count(";") > line.count(","):
        return ";"
    return ","
def _doc(url: str, resp: FetchResponse, **kw) -> DocumentDraft:
    return DocumentDraft(
        url=url,
        content=resp.content,
        content_type=resp.headers.get("Content-Type"),
        **kw,
    )


def _match_link(soup: BeautifulSoup, patterns, text_patterns=None) -> Optional[str]:
    text_patterns = text_patterns or []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(" ", strip=True).lower()
        if any(p in href for p in patterns) or any(p in text for p in text_patterns):
            return a["href"]
    return None


def _soup(resp: FetchResponse) -> BeautifulSoup:
    return BeautifulSoup(resp.text, "html.parser")

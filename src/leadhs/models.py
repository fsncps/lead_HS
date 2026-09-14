"""Data models: dataclasses at the DB/adapter boundary.

The adapter contract (interfaces.md) uses these types. Adapters
return ``ProbeResult`` with *drafts*; the engine owns all writes
(i3) and maps drafts to rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourceRef:
    id: str
    class_code: str
    name: str
    url: str
    access_method_code: str
    license_note: Optional[str] = None
    verification_status_code: str = "open"
    active: int = 1
    notes: Optional[str] = None
    export_url: Optional[str] = None
    export_format: Optional[str] = None


@dataclass
class Run:
    id: Optional[int] = None
    run_key: str = ""
    kind_code: str = "probe"
    source_id: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    status_code: str = "planned"
    parameters_json: Optional[str] = None
    seed: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class DocumentDraft:
    """A raw document an adapter wants archived (bytes kept out of the DB)."""

    url: str
    content: bytes
    content_type: Optional[str] = None
    language_code: Optional[str] = None
    title: Optional[str] = None
    retrieval_method_code: str = "scrape"
    notes: Optional[str] = None


@dataclass
class Document:
    id: Optional[int] = None
    source_id: Optional[str] = None
    run_id: Optional[int] = None
    url: str = ""
    retrieved_at: Optional[str] = None
    raw_hash: Optional[str] = None
    content_type: Optional[str] = None
    language_code: Optional[str] = None
    title: Optional[str] = None
    size_bytes: Optional[int] = None
    retrieval_method_code: str = "scrape"
    status_code: str = "archived"
    notes: Optional[str] = None


@dataclass
class FindingDraft:
    metric_code: str
    method_code: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit_code: Optional[str] = None
    document: Optional[DocumentDraft] = None
    notes: Optional[str] = None


@dataclass
class ProbeFinding:
    id: Optional[int] = None
    run_id: Optional[int] = None
    metric_code: str = ""
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit_code: Optional[str] = None
    method_code: str = ""
    document_id: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class StagedRow:
    """A parsed product row destined for the staging DB (fu2/e1).

    The adapter supplies *raw* values plus the ident column hint;
    normalization happens once at ingest (engine, via
    ``leadhs.normalize``). ``document`` carries the archived fetch the
    row was parsed from — provenance is mandatory (loud failure
    without it, c3).
    """

    manufacturer_raw: Optional[str] = None
    ident_raw: Optional[str] = None
    ident_hint: Optional[str] = None
    name: Optional[str] = None
    category_raw: Optional[str] = None
    raw: object = None
    document: Optional[DocumentDraft] = None


@dataclass
class StagedTradeRow:
    """A parsed trade row destined for ``stg_trade_cn8`` (W1 batches)."""

    cn8: Optional[str] = None
    flow: Optional[str] = None
    declarant: Optional[str] = None
    partner: Optional[str] = None
    year: Optional[str] = None
    kg: Optional[float] = None
    eur: Optional[float] = None
    document: Optional[DocumentDraft] = None


@dataclass
class ProbeContext:
    fetcher: object
    store: object
    conn: object
    mode: str = "census"
    sample_n: int = 5
    dry_run: bool = False
    logger: object = None
    staging: object = None  # staging DB conn (v0.2.2 i19); None = no staging


@dataclass
class ProbeResult:
    documents: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    parameters: dict = field(default_factory=dict)  # merged into run.parameters_json (od9)
    staged_products: list = field(default_factory=list)  # StagedRow drafts (fu2/e1)
    staged_trade: list = field(default_factory=list)  # StagedTradeRow drafts
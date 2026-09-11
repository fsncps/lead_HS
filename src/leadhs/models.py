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
class ProbeContext:
    fetcher: object
    store: object
    conn: object
    mode: str = "census"
    sample_n: int = 5
    dry_run: bool = False
    logger: object = None


@dataclass
class ProbeResult:
    documents: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    notes: list = field(default_factory=list)
"""Probe engine — per-source run loop, run lifecycle, single write path.

Engine owns ALL DB writes (i3); adapters return drafts. Maps the
exception taxonomy to findings/run status per interfaces.md.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from .. import db as dbmod
from .. import ids
from .. import metrics as metricmod
from ..fetch import Blocked, ProbeNetworkError, RateLimited, RobotsDisallowed
from ..logutil import log_event
from ..models import FindingDraft, ProbeContext, ProbeResult, SourceRef
from . import adapters as adaptersmod
from .adapters import BinaryMissing, ExtractionError, ParseError, UnexpectedFormat

_EXT_BY_CONTENT_TYPE = {
    "text/html": "html",
    "application/xhtml+xml": "html",
    "text/csv": "csv",
    "application/csv": "csv",
    "application/pdf": "pdf",
    "application/json": "json",
    "application/x-msaccess": "mdb",
    "application/vnd.ms-access": "mdb",
    "application/zip": "zip",
    "application/x-zip-compressed": "zip",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "text/plain": "txt",
}
_EXT_RE = re.compile(r"^[a-z0-9]{1,5}$")


def _ext_for(content_type: str | None, fallback: str = "bin") -> str:
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if ct in _EXT_BY_CONTENT_TYPE:
            return _EXT_BY_CONTENT_TYPE[ct]
    return fallback if _EXT_RE.match(fallback) else "bin"


class EngineError(Exception):
    pass


def _now() -> str:
    return dbmod.utcnow()


def _today() -> "datetime.date":
    return datetime.now(timezone.utc).date()


def _insert_run(conn, kind, source_id, slug, parameters, note_log=None):
    date_ = _today()
    existing = [r[0] for r in conn.execute("SELECT run_key FROM run")]
    attempt = ids.next_attempt(existing, kind, date_, slug)
    key = ids.run_key(kind, date_, slug, attempt)
    now = _now()
    cur = conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code, parameters_json) "
        "VALUES (?, ?, ?, ?, 'running', ?) RETURNING id",
        (key, kind, source_id, now, json.dumps(parameters)),
    ).fetchone()[0]
    return cur, key, now


def _insert_probe_run(conn, run_id, mode_code):
    conn.execute("INSERT INTO probe_run (run_id, mode_code) VALUES (?, ?)", (run_id, mode_code))


def _finish_run(conn, run_id, status, finished_at, notes=None):
    if notes:
        conn.execute(
            "UPDATE run SET status_code=?, finished_at=?, notes=? WHERE id=?",
            (status, finished_at, "; ".join(notes) if isinstance(notes, list) else notes, run_id),
        )
    else:
        conn.execute("UPDATE run SET status_code=?, finished_at=? WHERE id=?", (status, finished_at, run_id))


def _validate_finding(draft: FindingDraft) -> None:
    if not metricmod.is_valid(draft.metric_code):
        raise EngineError(f"unknown metric {draft.metric_code!r}")
    vt = metricmod.value_type_of(draft.metric_code)
    if vt == "numeric" and draft.value_numeric is None:
        raise EngineError(f"metric {draft.metric_code} needs a numeric value")
    if vt == "text" and draft.value_text is None:
        raise EngineError(f"metric {draft.metric_code} needs a text value")
    if draft.method_code not in ("api", "scrape", "download", "manual"):
        raise EngineError(f"bad method {draft.method_code!r} on finding {draft.metric_code}")


def persist(conn, store, source_id, run_id, result: ProbeResult, retrieval_method: str = "scrape"):
    """Insert documents (raw-archived) and findings — the single write path.

    Returns (document_count, finding_count).
    """
    doc_ids = {}
    retrieved_at = _now()
    for draft in result.documents:
        digest, _ = store.put(source_id, draft.content, _ext_for(draft.content_type))
        existing = conn.execute("SELECT id FROM document WHERE raw_hash = ?", (digest,)).fetchone()
        if existing is not None:
            # same content already archived — reuse the row (dedup by
            # fingerprint; append-only evidence, nothing mutated)
            doc_ids[id(draft)] = existing[0]
            continue
        cur = conn.execute(
            "INSERT INTO document (source_id, run_id, url, retrieved_at, raw_hash, content_type, "
            "language_code, title, size_bytes, retrieval_method_code, status_code, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'archived', ?) RETURNING id",
            (
                source_id,
                run_id,
                draft.url,
                retrieved_at,
                digest,
                draft.content_type,
                draft.language_code,
                draft.title,
                len(draft.content),
                draft.retrieval_method_code or retrieval_method,
                draft.notes,
            ),
        ).fetchone()[0]
        doc_ids[id(draft)] = cur
    for draft in result.findings:
        _validate_finding(draft)
        doc_id = doc_ids.get(id(draft.document)) if draft.document is not None else None
        conn.execute(
            "INSERT INTO probe_finding (run_id, metric_code, value_numeric, value_text, unit_code, "
            "method_code, document_id, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                draft.metric_code,
                draft.value_numeric,
                draft.value_text,
                draft.unit_code,
                draft.method_code,
                doc_id,
                draft.notes,
            ),
        )
    conn.commit()
    return len(result.documents), len(result.findings)


def run_one(conn, store, fetcher, source: SourceRef, mode: str = "census", sample_n: int = 5, dry_run: bool = False, logger=None):
    """One per-source probe run. Returns a dict summary; never raises
    for expected failures (they become run statuses)."""
    dbmod.stale_run_reclaim(conn)
    slug = ids.slug_for_source(source.id)
    parameters = {
        "sample_n": sample_n,
        "dry_run": dry_run,
        "contact_set": bool(getattr(fetcher.config, "contact", None)),
    }
    run_id, run_key, started = _insert_run(conn, "probe", source.id, slug, parameters)
    _insert_probe_run(conn, run_id, mode)
    conn.commit()

    if logger:
        log_event(logger, "engine", "run_start", run_key=run_key, source=source.id, mode=mode, dry_run=dry_run)

    adapter = adaptersmod.get_adapter(source)
    if adapter is None:
        _finish_run(conn, run_id, "failed", _now(), notes=[f"no adapter for class {source.class_code}"])
        conn.commit()
        return {"source": source.id, "run_key": run_key, "status": "failed", "documents": 0, "findings": 0, "notes": ["no adapter"]}

    ctx = ProbeContext(fetcher=fetcher, store=store, conn=conn, mode=mode, sample_n=sample_n, dry_run=dry_run, logger=logger)

    outcome = None
    notes = []
    result = ProbeResult()
    try:
        result = adapter.probe(source, ctx)
        outcome = "done"
    except (RobotsDisallowed, Blocked, RateLimited) as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        collected = bool(result.findings or result.documents)
        metric = "robots_denied" if isinstance(exc, RobotsDisallowed) else "access_blocked"
        result.findings.append(
            FindingDraft(metric_code=metric, method_code="manual", value_text=exc.detail, notes="manual fallback rule D4")
        )
        notes.append(str(exc))
        outcome = "blocked" if not collected else "done"
    except ProbeNetworkError as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        notes.append(str(exc))
        outcome = "failed"
    except UnexpectedFormat as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        result.findings.append(FindingDraft(metric_code="format", method_code="manual", value_text=exc.detail, notes="UnexpectedFormat — WARNING, manual review"))
        notes.append(f"UnexpectedFormat: {exc.detail}")
        outcome = "done"
    except (BinaryMissing, ExtractionError) as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        result.findings.append(FindingDraft(metric_code="extraction_path", method_code="manual", value_text=exc.detail))
        notes.append(str(exc))
        outcome = "done"
    except ParseError as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        result.findings.append(FindingDraft(metric_code="page_sample_ok", method_code="manual", value_numeric=0))
        notes.append(str(exc))
        outcome = "done"
    except KeyboardInterrupt:
        _finish_run(conn, run_id, "aborted", _now(), notes=["interrupted; findings persisted"])
        conn.commit()
        if logger:
            log_event(logger, "engine", "run_aborted", run_key=run_key, source=source.id)
        raise

    doc_count, finding_count = persist(conn, store, source.id, run_id, result)
    if result.parameters:
        # od9: adapter-surfaced parameters (e.g. the CS-2 query constants)
        # land in run.parameters_json — engine writes, adapter only drafts
        merged = dict(parameters)
        merged.update(result.parameters)
        conn.execute("UPDATE run SET parameters_json=? WHERE id=?", (json.dumps(merged), run_id))
    _finish_run(conn, run_id, outcome, _now(), notes=notes)
    conn.commit()
    if logger:
        log_event(
            logger, "engine", "run_done", run_key=run_key, source=source.id, status=outcome,
            documents=doc_count, findings=finding_count,
        )
    return {
        "source": source.id,
        "run_key": run_key,
        "status": outcome,
        "documents": doc_count,
        "findings": finding_count,
        "notes": notes,
    }


def run_all(conn, store, fetcher, mode: str = "census", sample_n: int = 5, dry_run: bool = False, logger=None):
    """One run per active, adapter-backed source; a failing source never
    aborts the loop. Returns (summaries, aggregate_exit_code)."""
    from .. import source as sourcemod

    dbmod.stale_run_reclaim(conn)
    summaries = []
    sources = [s for s in sourcemod.all_sources(conn, active_only=True) if adaptersmod.get_adapter(s)]
    if mode == "capability":
        # v0.2.1 cap2/cap5: the capability sweep targets the official
        # register (AS) sources only — PE/CS/ST adapters no-op for
        # non-recon/census modes and are never swept in capability mode.
        sources = [s for s in sources if s.class_code == "AS"]
    if not sources:
        return [], 0
    exit_code = 0
    for source in sources:
        summary = run_one(conn, store, fetcher, source, mode=mode, sample_n=sample_n, dry_run=dry_run, logger=logger)
        summaries.append(summary)
        if summary["status"] in ("blocked", "failed"):
            exit_code = 2
    return summaries, exit_code


def record_manual(conn, store, source_id, metric, value=None, value_text=None, unit=None, url=None, document_file=None, note=None, logger=None, contact=None, mode: str = "census"):
    """`probe record`: manual run (kind=probe, method=manual) + one finding.

    ``mode`` (e8) labels the run honestly (census default; recon for the
    v0.2.0 manual-web records) — must exist in the probe_mode lookup."""
    from .. import source as sourcemod

    source = sourcemod.get_source(conn, source_id)
    if source is None:
        raise EngineError(f"unknown source {source_id!r}")
    if not metricmod.is_valid(metric):
        raise EngineError(f"unknown metric {metric!r}")
    vt = metricmod.value_type_of(metric)
    if vt == "numeric":
        if value is None:
            raise EngineError(f"metric {metric} needs --value")
        try:
            value_numeric = float(value)
        except (TypeError, ValueError):
            raise EngineError(f"metric {metric} --value must be numeric, got {value!r}")
        value_text_out = None
    else:
        if value_text is None:
            raise EngineError(f"metric {metric} needs --value-text")
        if value is not None:
            raise EngineError(f"metric {metric} is text; drop --value")
        value_numeric = None
        value_text_out = value_text

    slug = ids.slug_for_source(source_id) + "manual"
    parameters = {"sample_n": None, "dry_run": False, "contact_set": bool(contact)}
    run_id, run_key, _ = _insert_run(conn, "probe", source_id, slug, parameters)
    _insert_probe_run(conn, run_id, mode)
    conn.commit()

    doc_id = None
    document = None
    if document_file:
        with open(document_file, "rb") as fh:
            content = fh.read()
        digest, _ = store.put(source_id, content, _ext_for(None, document_file.rsplit(".", 1)[-1]))
        document = {"url": url or f"manual:{document_file}", "retrieval_method_code": "manual"}
        doc_id = conn.execute(
            "INSERT INTO document (source_id, run_id, url, retrieved_at, raw_hash, content_type, "
            "status_code, retrieval_method_code, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, 'archived', 'manual', ?) RETURNING id",
            (source_id, run_id, url or f"manual:{document_file}", _now(), digest, "application/octet-stream", note),
        ).fetchone()[0]
    elif url:
        doc_id = conn.execute(
            "INSERT INTO document (source_id, run_id, url, retrieved_at, status_code, retrieval_method_code, notes) "
            "VALUES (?, ?, ?, ?, 'manual', 'manual', ?) RETURNING id",
            (source_id, run_id, url, _now(), note),
        ).fetchone()[0]

    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, value_text, unit_code, method_code, document_id, notes) "
        "VALUES (?, ?, ?, ?, ?, 'manual', ?, ?)",
        (run_id, metric, value_numeric, value_text_out, unit, doc_id, note),
    )
    _finish_run(conn, run_id, "done", _now())
    conn.commit()
    if logger:
        log_event(logger, "engine", "record_done", run_key=run_key, source=source_id, metric=metric)
    return {"source": source_id, "run_key": run_key, "status": "done", "metric": metric}
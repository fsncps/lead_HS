"""Probe engine — per-source run loop, run lifecycle, single write path.

Engine owns ALL DB writes (i3); adapters return drafts. Maps the
exception taxonomy to findings/run status per interfaces.md.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone

from .. import db as dbmod
from .. import ids
from .. import metrics as metricmod
from .. import normalize as normmod
from .. import staging as stagingmod
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


def _stage_and_derive(staging, store, source, run_key, result: ProbeResult, notes: list) -> dict:
    """Staging-first ingest (e1/fu2): archive the referenced documents
    (content-addressed, idempotent), write staged rows to the staging DB
    (one replace per document), then derive the run-close metrics from
    the staging rows — metrics == staging by construction (fu1).

    Returns the staged counts for the run summary. Raises EngineError on
    any missing provenance (loud failure, c3).
    """
    stagingmod.init(staging)
    staged_products = result.staged_products
    staged_trade = result.staged_trade
    counted_zero = result.parameters.get("staged_zero")

    def _doc_groups(rows):
        """Group staged rows by their source document (identity); returns
        [(document_draft, rows)]."""
        groups: dict = {}
        for row in rows:
            if row.document is None:
                raise EngineError("staged row without its source document (loud failure, c3)")
            entry = groups.setdefault(id(row.document), (row.document, []))
            entry[1].append(row)
        return [(draft, rws) for draft, rws in groups.values()]

    def _stage_doc(doc) -> dict:
        digest, _ = store.put(source.id, doc.content, _ext_for(doc.content_type))
        return {
            "url": doc.url,
            "doc_hash": digest,
            "retrieval_date": _today().isoformat(),
            "bytes": len(doc.content),
        }

    n_products, n_trade = 0, 0
    if staged_products or counted_zero is not None:
        if counted_zero is not None and not staged_products:
            # c2 counted-0: the export parsed fine but legitimately holds
            # zero in-scope rows — stage the (empty) export, count 0.
            if not result.documents:
                raise EngineError("staged_zero run without an archived export document")
            doc = result.documents[0]
            sdoc = _stage_doc(doc)
            stagingmod.replace_products(staging, source.id, run_key, sdoc, [])
            notes.append(f"counted-0: {counted_zero}")
        for doc, rows in _doc_groups(staged_products):
            sdoc = _stage_doc(doc)
            normalized = []
            for row in rows:
                ident = normmod.identity(row.manufacturer_raw, row.ident_raw, row.ident_hint, row.name)
                ident["name"] = normmod.norm_name(row.name) if row.name is not None else None
                ident["category_raw"] = row.category_raw
                ident["raw"] = json.dumps(row.raw, sort_keys=True, default=str) if row.raw is not None else None
                normalized.append(ident)
            n_products += stagingmod.replace_products(staging, source.id, run_key, sdoc, normalized)
    for doc, rows in _doc_groups(staged_trade):
        sdoc = _stage_doc(doc)
        trade_rows = [
            {"cn8": r.cn8, "flow": r.flow, "declarant": r.declarant, "partner": r.partner,
             "year": r.year, "kg": r.kg, "eur": r.eur}
            for r in rows
        ]
        n_trade += stagingmod.replace_trade(staging, source.id, run_key, sdoc, trade_rows)

    derived = {"staged_products": n_products, "staged_trade": n_trade}
    if staged_products or counted_zero is not None:
        # run-close derivation (fu1/fu4): the metric IS the staging count
        count = stagingmod.count_products(staging, source.id, run_key)
        agg = stagingmod.product_aggregates(staging, source.id, run_key)
        cats = ", ".join(f"{c}={n}" for c, n in agg["categories"][:5])
        result.findings.append(
            FindingDraft(
                metric_code=metricmod.METRIC_PRODUCTS_IDENTIFIABLE,
                method_code="download",
                value_numeric=float(count),
                unit_code="count",
                notes=(
                    f"run-close derivation from staging ({run_key}): "
                    f"distinct_manufacturers={agg['distinct_manufacturers']} "
                    f"distinct_pairs={agg['distinct_pairs']} "
                    f"identity_completeness_pct={agg['identity_completeness_pct']} "
                    f"categories: {cats or '(none)'}"
                ),
            )
        )
    return derived


def run_one(conn, store, fetcher, source: SourceRef, mode: str = "census", sample_n: int = 5, dry_run: bool = False, logger=None, staging=None):
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

    ctx = ProbeContext(fetcher=fetcher, store=store, conn=conn, mode=mode, sample_n=sample_n, dry_run=dry_run, logger=logger, staging=staging)

    # automated findings carry the observation method (download/scrape/api);
    # "manual" stays reserved for operator records (probe record)
    method = source.access_method_code or "scrape"

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
            FindingDraft(metric_code=metric, method_code=method, value_text=exc.detail, notes="manual fallback rule D4")
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
        result.findings.append(FindingDraft(metric_code="format", method_code=method, value_text=exc.detail, notes="UnexpectedFormat — WARNING, manual review"))
        notes.append(f"UnexpectedFormat: {exc.detail}")
        outcome = "done"
    except (BinaryMissing, ExtractionError) as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        result.findings.append(FindingDraft(metric_code="extraction_path", method_code=method, value_text=exc.detail))
        notes.append(str(exc))
        outcome = "done"
    except ParseError as exc:
        partial = getattr(exc, "partial", None)
        if partial is not None:
            result = partial
        result.findings.append(FindingDraft(metric_code="page_sample_ok", method_code=method, value_numeric=0))
        notes.append(str(exc))
        outcome = "done"
    except KeyboardInterrupt:
        _finish_run(conn, run_id, "aborted", _now(), notes=["interrupted; findings persisted"])
        conn.commit()
        if logger:
            log_event(logger, "engine", "run_aborted", run_key=run_key, source=source.id)
        raise

    staged_counts = None
    if not dry_run and (result.staged_products or result.staged_trade or result.parameters.get("staged_zero") is not None):
        if staging is None:
            raise EngineError("adapter returned staged rows but no staging DB is configured (pass --staging-db)")
        staged_counts = _stage_and_derive(staging, store, source, run_key, result, notes)
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
        "staged": (staged_counts or {}).get("staged_products", 0) if staged_counts else 0,
        "staged_trade": (staged_counts or {}).get("staged_trade", 0) if staged_counts else 0,
    }


def run_all(conn, store, fetcher, mode: str = "census", sample_n: int = 5, dry_run: bool = False, logger=None, classes=None, source_ids=None):
    """One run per active, adapter-backed source; a failing source never
    aborts the loop. Returns (summaries, aggregate_exit_code).

    Source selection (e2): ``classes`` (optional list of class codes) and
    ``source_ids`` (optional explicit ids) — callers compose filters at
    their layer; no ``mode ==`` chain growth here. ``classes=None`` keeps
    the every-class default; the capability sweep passes ``classes=["AS"]``
    from the CLI layer (the v0.2.1 preset, now explicit).
    """
    from .. import source as sourcemod

    dbmod.stale_run_reclaim(conn)
    summaries = []
    sources = [s for s in sourcemod.all_sources(conn, active_only=True) if adaptersmod.get_adapter(s)]
    if classes is not None:
        sources = [s for s in sources if s.class_code in set(classes)]
    if source_ids is not None:
        wanted = set(source_ids)
        sources = [s for s in sources if s.id in wanted]
    if not sources:
        return [], 0
    exit_code = 0
    for source in sources:
        summary = run_one(conn, store, fetcher, source, mode=mode, sample_n=sample_n, dry_run=dry_run, logger=logger)
        summaries.append(summary)
        if summary["status"] in ("blocked", "failed"):
            exit_code = 2
    return summaries, exit_code


# --- dispositions (v0.2.2 c1): the register-row state machine -------------

_FORMAT_MARKERS = ("UnexpectedFormat", "HTML landing page", "register layout missing")
_COUNT_METRICS = frozenset(
    {
        "products_identifiable", "catalog_count", "products_listed",
        "sitemap_products", "category_count", "export_rows",
        "records_hs3208", "records_hs3209", "records_hs3213",
    }
)


def disposition_of(conn, source_id, staging=None) -> dict:
    """Terminal disposition of one register row (c1):

    ``pending`` — no runs (or only failed/retryable runs);
    ``blocked`` — latest run blocked (reason recorded by the engine);
    ``format-finding`` — latest run ended done with an export-shape
    format finding and no count — non-terminal until the manual
    fallback lands a record;
    ``manual-recorded`` — latest run is a manual record;
    ``counted`` — latest run counted (automated findings, a run-close
    staging derivation, or staged trade rows — W1 batches).

    The wave harness asserts the after-run invariant over these.
    """
    rows = conn.execute(
        "SELECT r.id, r.run_key, r.status_code, r.kind_code FROM run r WHERE r.source_id=? ORDER BY r.started_at DESC, r.id DESC LIMIT 1",
        (source_id,),
    ).fetchall()
    if not rows:
        return {"source": source_id, "disposition": "pending", "detail": "no runs"}
    run_id, run_key, status_code, kind_code = rows[0]
    if status_code == "blocked":
        return {"source": source_id, "disposition": "blocked", "detail": f"run {run_id} blocked"}
    if status_code in ("failed", "running"):
        return {"source": source_id, "disposition": "pending", "detail": f"run {run_id} {status_code} (retryable)"}
    findings = conn.execute(
        "SELECT pf.metric_code, pf.method_code, pf.notes, pf.value_text FROM probe_finding pf WHERE pf.run_id=?",
        (run_id,),
    ).fetchall()
    has_count = any(f[0] in _COUNT_METRICS and f[1] != "manual" for f in findings)
    if staging is not None:
        try:
            n_trade = staging.execute(
                "SELECT COUNT(*) FROM stg_trade_cn8 WHERE source_id=? AND run_key=?",
                (source_id, run_key),
            ).fetchone()[0]
        except sqlite3.Error:
            n_trade = 0
        if n_trade > 0:
            return {"source": source_id, "disposition": "counted", "detail": f"run {run_id}: {n_trade} staged trade rows"}
    has_format = any(f[0] == "format" and any(m in (f[2] or "") + (f[3] or "") for m in _FORMAT_MARKERS) for f in findings)
    if findings and all(f[1] == "manual" for f in findings):
        # an operator record is terminal even when its text quotes an
        # automated marker (e.g. a deferral note citing UnexpectedFormat)
        return {"source": source_id, "disposition": "manual-recorded", "detail": f"run {run_id}: manual record"}
    if has_format and not has_count:
        return {"source": source_id, "disposition": "format-finding", "detail": f"run {run_id}: export shape finding, manual fallback required (c1)"}
    if has_count:
        return {"source": source_id, "disposition": "counted", "detail": f"run {run_id}"}
    return {"source": source_id, "disposition": "pending", "detail": f"run {run_id}: no count findings"}


def dispositions(conn, source_ids=None, staging=None) -> dict:
    ids_list = [r[0] for r in conn.execute("SELECT id FROM source ORDER BY id")]
    if source_ids is not None:
        ids_list = [i for i in ids_list if i in set(source_ids)]
    return {i: disposition_of(conn, i, staging=staging) for i in ids_list}


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
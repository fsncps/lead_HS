"""Management CSV sample (v0.2.4, D36) — per-registry reproducible
product-row samples + the generated manifest.

`leadhs probe download-csv-sample` answers, per registry: what data
fields are returned per product item, which identifier columns exist,
and whether cross-identification as individual products is possible —
plus an honest, cited reason for the registries that publish no
product rows at all (only ECAT does; D36 research finding).

Per-source state machine (review 1A — the manifest is ALWAYS written
and tells the truth):

    pending ──▶ delivered    (csv_sample_rows; exit contribution 0)
         ────▶ unavailable  (csv_sample_unavailable, expected → exit 0)
         ────▶ failed       (should-deliver only → exit 2)

The engine owns all DB writes (i3): runs go through engine
``_insert_run``/``_insert_probe_run``/``_finish_run``/``persist``
(kind=probe, mode=csv_sample); the draw seed lands in the existing
``run.seed`` column. Samples are review artifacts, not measurement
rows — no staging writes (de2). Recon-only (D31): official exports
via the polite fetcher, nothing else.
"""

from __future__ import annotations

import csv
import io
import os
import random
from datetime import datetime, timezone

from .. import ids
from ..fetch import FetchError, ProbeNetworkError
from ..store import StoreError
from ..logutil import log_event
from ..models import DocumentDraft, FindingDraft, ProbeResult
from . import engine as probeengine
from .adapters._common import UnexpectedFormat, _delimiter_of, read_csv_rows, sniff_kind
from .adapters.as_adapter import _EXPORT_EXPECTED, _in_scope_group

# The default target set (strategy S2): the five benchmark registries
# of the v0.2.3 summary + Nordic Swan (AS-3), the second-register
# candidate.
DEFAULT_SOURCES = ("AS-2", "AS-3", "ST-1", "ST-3", "ST-6", "ST-7")

# Provenance columns appended to every sample CSV (D2/D20/R1): the rows
# stay reproducible — same seed, same doc hash → same sample.
PROVENANCE_COLUMNS = ("source_id", "run_key", "retrieval_date", "doc_hash", "sample_seed", "sample_index")

# Pinned no-fetch reasons (i4 — constants in the module + the design
# method sheet): the four registries of the benchmark set that publish
# no product-level rows publicly. Each cites the verified finding with
# URL + access date (D36 research pass, 2026-09-14).
_NO_FETCH_REASONS = {
    "ST-1": (
        "no product rows — the ECHA PCN database is restricted to member-state "
        "appointed bodies (login/eDelivery); companies see only their own submissions. "
        "https://poisoncentres.echa.europa.eu/tools-for-authorities (accessed 2026-09-14)"
    ),
    "ST-3": (
        "no product items — Eurostat SBS is enterprise statistics "
        "(NACE 20.30), not a product registry. "
        "https://ec.europa.eu/eurostat (accessed 2026-09-14)"
    ),
    "ST-6": (
        "no product rows — the Danish AT register publishes aggregates only, "
        "via an embedded Power BI report; CKAN resources have no download URL "
        "(v0.2.3 PHASE02 shape gate). "
        "https://datavejviser-indtastning.digst.govcloud.dk/dataset/kemiske-produkter-og-stoffer-i-tal (accessed 2026-09-14)"
    ),
    "ST-7": (
        "no product rows — the KemI Products Register is secrecy-protected at "
        "product level; public access is aggregates only (KemI-stat). "
        "https://www.kemi.se/en/the-swedish-products-register/secrecy-and-handling-of-data-in-the-products-register (accessed 2026-09-14)"
    ),
}

# The manifest's cross-identification line for delivered samples (the
# D36 answer, generic wording — the columns make the candidates real).
_CROSS_ID_DELIVERED = (
    "identifier columns in this sample: {idcols}; cross-identification "
    "candidates: EAN13/GTIN ↔ retail/manufacturer catalogues (the v0.3 "
    "seeding path); name + licence holder ↔ other certified-product registers"
)

# AS-3 (D38): the Nordic Swan export carries no EAN column — its
# identity carriers are the licence number and the name+licensee pair.
_CROSS_ID_DELIVERED_NS = (
    "identifier columns in this sample: {idcols}; cross-identification "
    "candidates: licence number (100% — one licence, many products); "
    "name + licence holder ↔ other certified-product registers; the "
    "export mixes EU Ecolabel and Nordic Swan licences (data model, "
    "joinable by licence number)"
)

# AS-3 bounded discovery (PHASE03): candidate export endpoints tried in
# order, ≤5 polite GETs total; the pinned surface first. Trial code —
# reconciled when the pilot unit pins the real mechanics (TODOS.md,
# v0.2.4 ENG review).
_NS_MAX_GETS = 5
_NS_CANDIDATE_SUFFIXES = ("", "?format=csv", "/export.csv", "?export=csv", "/csv")
_NS_UNAVAILABLE = (
    "export mechanics unpinned after <=5 bounded GETs on the search "
    "surface — browser pass required (v0.2.4 PHASE03 trial; TODOS "
    "reconciliation when the pilot unit pins the real mechanics). "
    "https://www.svanen.se/en/search-for-ecolabelled-products-and-services/ (accessed 2026-09-14)"
)


class SampleError(Exception):
    """Command-level error → usage exit 1 at the CLI layer."""


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


# --- run bookkeeping (engine write path, i3) ------------------------------


def _begin_run(conn, source_id: str, parameters: dict) -> tuple:
    """One probe run (mode csv_sample) per source; the draw seed lands
    in the existing run.seed column (0002)."""
    slug = ids.slug_for_source(source_id) + "csvsample"
    run_id, run_key, _started = probeengine._insert_run(conn, "probe", source_id, slug, parameters)
    probeengine._insert_probe_run(conn, run_id, "csv_sample")
    conn.execute("UPDATE run SET seed=? WHERE id=?", (parameters.get("seed"), run_id))
    conn.commit()
    return run_id, run_key


def _finish(conn, run_id: int, status: str, notes: list) -> None:
    engine_status = "done" if status in ("delivered", "unavailable") else "failed"
    probeengine._finish_run(conn, run_id, engine_status, probeengine._now(), notes=notes)
    conn.commit()


def _unavailable_result(reason: str, method: str = "download") -> ProbeResult:
    return ProbeResult(
        findings=[FindingDraft(metric_code="csv_sample_unavailable", method_code=method, value_text=reason)]
    )


# --- per-source handlers ---------------------------------------------------
#
# Each handler records its run + findings (engine write path) and
# returns a summary dict:
#   {source, status: delivered|unavailable|failed, run_key, rows,
#    fields, idcols, file, reason}


def _summary(source_id, status, run_key, rows=None, fields=None, idcols=None, file=None, reason=None):
    return {"source": source_id, "status": status, "run_key": run_key, "rows": rows,
            "fields": fields, "idcols": idcols, "file": file, "reason": reason}


def _record_failure(conn, source_id, run_id, run_key, detail, logger=None):
    """A should-deliver source failed — text finding + run failed;
    never silent (review 1A)."""
    probeengine.persist(conn, None, source_id, run_id, _unavailable_result(f"FAILED: {detail}"))
    _finish(conn, run_id, "failed", [detail])
    if logger:
        log_event(logger, "csv_sample", "failed", source=source_id, run_key=run_key, detail=detail)
    return _summary(source_id, "failed", run_key, reason=detail)


def _no_fetch(conn, source_id, reason, parameters, logger=None):
    """The ST-* path: zero network, one text finding, run done. Method
    `manual` — a desk record, like `probe record`."""
    run_id, run_key = _begin_run(conn, source_id, parameters)
    probeengine.persist(conn, None, source_id, run_id, _unavailable_result(reason, method="manual"))
    _finish(conn, run_id, "unavailable", [f"no-product-rows record: {source_id}"])
    if logger:
        log_event(logger, "csv_sample", "unavailable", source=source_id, run_key=run_key)
    return _summary(source_id, "unavailable", run_key, reason=reason)


def _parse_export(content: bytes, content_type: str | None, expected) -> tuple:
    """Shared export parse: sniff gate (e3 — HTML-as-CSV class) →
    delimiter heuristic → read_csv_rows. Returns (header, records)."""
    kind = sniff_kind(content_type, content[:512])
    if kind not in ("csv", "tsv"):
        raise UnexpectedFormat(f"export is {kind}, expected CSV/TSV — layout to re-pin")
    sep = "\t" if kind == "tsv" else _delimiter_of(content.split(b"\n", 1)[0])
    header, data_rows = read_csv_rows(content, separator=sep, expected=expected)
    return header, [dict(zip(header, r)) for r in data_rows]


def _sample_delivered(conn, store, source, run_id, run_key, header, records, content, content_type, content_url,
                      n, seed, out_dir, ts, logger=None, key_fields=None):
    """The delivered path: dedupe → seeded draw → CSV + finding +
    archive. Shared by AS-2 (group-044 pool) and AS-3 (paint-group
    pool) — the pool is already filtered by the caller (de3)."""
    # Dedupe to DISTINCT product items (review amendment 2; D38: the
    # identity columns are source-parameterized — the ECAT fallback
    # chain collapsed the Nordic Swan pool to its distinct Category
    # values, the "14 distinct" defect).
    fields = key_fields or _KEY_FIELDS_DEFAULT
    pool: dict = {}
    for rec in records:
        pool.setdefault(_identity_key(rec, fields), rec)
    pool_size = len(pool)

    # Canonical pool order (sorted unique triples) → the seeded draw is
    # reproducible across runs and machines, not just within one.
    ordered = [pool[k] for k in sorted(pool)]
    k = min(n, pool_size)
    sampled = random.Random(seed).sample(ordered, k)
    shortfall = k < n

    digest, doc = None, None
    if content:
        digest, _rel = store.put(source.id, content, "csv")
        doc = DocumentDraft(url=content_url, content=content, content_type=content_type,
                            retrieval_method_code="download")

    findings = [FindingDraft(
        metric_code="csv_sample_rows", method_code="download",
        value_numeric=float(k), unit_code="count", document=doc,
        notes=(f"seeded draw n={n} seed={seed}; pool distinct={pool_size} "
               f"(from {len(records)} in-scope rows); shortfall={shortfall}; "
               f"file=csv-sample.{ts}.{source.id}.csv; header: {', '.join(header)}"),
    )]
    probeengine.persist(conn, store, source.id, run_id, ProbeResult(documents=[doc] if doc else [], findings=findings))

    file_name = f"csv-sample.{ts}.{source.id}.csv"
    _write_sample_csv(os.path.join(out_dir, file_name), header, sampled, source.id, run_key, _today(), digest, seed)
    _finish(conn, run_id, "delivered", [f"sample draw: {k}/{pool_size} distinct items (n={n}, seed={seed})"])
    if logger:
        log_event(logger, "csv_sample", "drawn", source=source.id, run_key=run_key, rows=k, pool=pool_size)

    idcols = [c for c in header if c in ("code_value", "licence_no", "license number", "ean", "gtin", "product_ident")]
    return _summary(
        source.id, "delivered", run_key, rows=k, fields=list(header), idcols=idcols, file=file_name,
        reason=(f"pool smaller than n: {k} of {n} requested (distinct items: {pool_size})" if shortfall else None),
    )


def _sample_ecat(conn, store, fetcher, source, n, seed, out_dir, ts, parameters, logger=None):
    """AS-2: one bulk GET of the pinned export_url (should-deliver)."""
    run_id, run_key = _begin_run(conn, source.id, parameters)
    if not source.export_url:
        return _record_failure(conn, source.id, run_id, run_key, "AS-2 register row has no pinned export_url", logger)
    try:
        resp = fetcher.get(source.export_url)
        header, records = _parse_export(resp.content, resp.headers.get("Content-Type"), _EXPORT_EXPECTED.get(source.id))
    except FetchError as exc:
        return _record_failure(conn, source.id, run_id, run_key, f"fetch failed: {exc}", logger)
    except UnexpectedFormat as exc:
        return _record_failure(conn, source.id, run_id, run_key, f"format: {exc.detail}", logger)
    in_scope = [
        rec for rec in records
        if _in_scope_group((rec.get("group_name") or rec.get("group") or "").strip())
    ]
    if not in_scope:
        return _record_failure(conn, source.id, run_id, run_key,
                               f"0 in-scope rows after the group filter ({len(records)} rows) — data-drift signal", logger)
    return _sample_delivered(conn, store, source, run_id, run_key, header, in_scope,
                             resp.content, resp.headers.get("Content-Type"), source.export_url,
                             n, seed, out_dir, ts, logger)


# The Nordic Swan paint scope: exact match on the `product group`
# column value (the category mechanism, de3 — the register carries no
# CN8 codes). D38: whole-record substrings ("lack" inside "Black")
# let toner/cleaning rows through; the structured column does not.
_NS_PAINT_GROUPS = (
    "EU44 Decorative paints, varnishes, and related products",
    "096 Paints and varnishes",
)


def _in_scope_ns_group(rec) -> bool:
    return (rec.get("product group") or "").strip() in _NS_PAINT_GROUPS


def _identity_key(rec, key_fields) -> tuple:
    """Dedupe key from per-source column chains (D38): the AS-2 default
    is the ECAT fallback chain; AS-3 passes its own column names
    (product, licensee, product group)."""
    def first(names):
        for nm in names:
            v = rec.get(nm)
            if v:
                return str(v).strip().casefold()
        return ""
    return tuple(first(names) for names in key_fields)


_KEY_FIELDS_DEFAULT = (
    ("product_or_service_name", "product_name", "name"),
    ("company_name", "manufacturer"),
    ("group_name", "group", "category"),
)
_KEY_FIELDS_NS = (
    ("product", "product_name", "name"),
    ("licensee", "company_name", "manufacturer"),
    ("product group", "group_name", "group"),
)


def _sample_nordic_swan(conn, store, fetcher, source, n, seed, out_dir, ts, parameters, logger=None):
    """AS-3: bounded discovery (PHASE03 trial). A CSV response feeds the
    ECAT path with the paint-group filter (EU44/096); anything else is an honest
    unavailable record after ≤5 GETs."""
    run_id, run_key = _begin_run(conn, source.id, parameters)
    base = source.export_url or source.url
    detail, delivered, network_failed = None, None, False
    for gets, suffix in enumerate(_NS_CANDIDATE_SUFFIXES, 1):
        if gets > _NS_MAX_GETS:
            break
        url = base + suffix
        try:
            resp = fetcher.get(url)
        except FetchError as exc:
            detail, network_failed = f"network failure on the pinned URL: {exc}", True
            break
        kind = sniff_kind(resp.headers.get("Content-Type"), resp.content[:512])
        if kind in ("csv", "tsv"):
            try:
                header, records = _parse_export(resp.content, resp.headers.get("Content-Type"), None)
            except UnexpectedFormat as exc:
                detail = f"format: {exc.detail}"
                break
            in_scope = [rec for rec in records if _in_scope_ns_group(rec)]
            if not in_scope:
                reason = f"export reached but 0 paint-group rows (EU44/096) among {len(records)} rows"
                probeengine.persist(conn, store, source.id, run_id, _unavailable_result(reason))
                _finish(conn, run_id, "unavailable", [f"AS-3: 0 in-scope rows ({gets} GETs)"])
                return _summary(source.id, "unavailable", run_key, fields=list(header), reason=reason)
            delivered = _sample_delivered(conn, store, source, run_id, run_key, header, in_scope,
                                          resp.content, resp.headers.get("Content-Type"), url,
                                          n, seed, out_dir, ts, logger, key_fields=_KEY_FIELDS_NS)
            break
        detail = f"{gets} GET(s): {kind} at {url}"
    if delivered is not None:
        return delivered
    # Discovery budget spent or network failure — honest record, never
    # silent; expected-unavailable, so exit 0 (de4).
    if network_failed:
        reason = detail
    elif detail:
        reason = f"{_NS_UNAVAILABLE} Last probe: {detail}."
    else:
        reason = _NS_UNAVAILABLE
    probeengine.persist(conn, store, source.id, run_id, _unavailable_result(reason))
    _finish(conn, run_id, "unavailable", [f"AS-3 discovery: {reason}"])
    if logger:
        log_event(logger, "csv_sample", "unavailable", source=source.id, run_key=run_key)
    return _summary(source.id, "unavailable", run_key, reason=reason)


# --- outputs ---------------------------------------------------------------


def _write_sample_csv(path, header, rows, source_id, run_key, retrieval_date, doc_hash, seed) -> None:
    """One sample CSV: verbatim export columns + the provenance block."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(list(header) + list(PROVENANCE_COLUMNS))
        for i, rec in enumerate(rows, 1):
            writer.writerow(
                [rec.get(c, "") for c in header]
                + [source_id, run_key, retrieval_date, doc_hash or "", seed, i]
            )


def _render_manifest_md(ts, n, seed, entries) -> str:
    lines = [
        "# Management CSV sample — manifest",
        "",
        f"Run: `{ts}` · n={n} per registry · seed={seed} (seeded reproducible draw, D2)",
        "",
        "Per registry: what data fields are returned per product item, which",
        "identifier columns exist, whether cross-identification is possible —",
        "and the honest reason where no product rows are published (D36).",
        "",
    ]
    for e in entries:
        lines.append(f"## {e['source']} — {e['status']}")
        lines.append("")
        if e["status"] == "delivered":
            idcols = ", ".join(e["idcols"]) if e["idcols"] else "(none in the header)"
            xline = (_CROSS_ID_DELIVERED_NS if e["source"] == "AS-3" else _CROSS_ID_DELIVERED)
            lines.append(f"- rows drawn: **{e['rows']}** (of the in-scope pool) → `{e['file']}`")
            lines.append(f"- fields returned: {', '.join(e['fields'])}")
            lines.append(f"- {xline.format(idcols=idcols)}")
            if e.get("reason"):
                lines.append(f"- note: {e['reason']}")
        else:
            lines.append(f"- rows: 0 — {e['reason']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Generated by `leadhs probe download-csv-sample` — constants live in")
    lines.append("`src/leadhs/probe/csv_sample.py` + the design method sheet (i4).")
    lines.append("")
    return "\n".join(lines)


def _render_manifest_csv(entries) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["source_id", "status", "rows", "fields", "identifier_columns", "cross_id_candidates", "reason", "file"])
    for e in entries:
        fields = ";".join(e["fields"]) if e["fields"] else ""
        idcols = ";".join(e["idcols"]) if e["idcols"] else ""
        cross = _CROSS_ID_DELIVERED.format(idcols=idcols) if e["status"] == "delivered" else ""
        writer.writerow([e["source"], e["status"], e["rows"] or 0, fields, idcols, cross, e["reason"] or "", e["file"] or ""])
    return buf.getvalue()


# --- orchestration ----------------------------------------------------------


# --- offline re-render transport (D38) ---------------------------------------


class _StoreResponse:
    def __init__(self, content: bytes, content_type: str):
        self.content = content
        self.headers = {"Content-Type": content_type}


class StoreFetcher:
    """Serves a source's newest archived CSV export from the raw store
    instead of the network (D38 re-render; zero GETs). A request is
    served when it targets one of the source's register URLs (url /
    export_url, prefix match) — the discovery handlers may construct
    candidate URLs that differ from the original document URL, and the
    bytes are what the re-render needs (the original URL stays on the
    original document row)."""

    def __init__(self, docs: dict, bases: dict):
        self.docs = docs    # source_id → (bytes, content_type)
        self.bases = bases  # source_id → [url, ...]

    def get(self, url: str):
        for sid, content in self.docs.items():
            for base in self.bases.get(sid, ()):
                if base and (url == base or url.startswith(base.rstrip("/") + "/")
                             or url.startswith(base + "?")):
                    return _StoreResponse(content[0], content[1])
        raise ProbeNetworkError(url, "no archived document serves this URL in re-render mode")


def fetcher_from_store(conn, store) -> StoreFetcher:
    """Newest archived CSV export per source (raw store, content-addressed),
    mapped to the source's register URLs."""
    docs: dict = {}
    bases: dict = {}
    rows = conn.execute(
        "SELECT d.source_id, d.raw_hash, d.content_type FROM document d "
        "WHERE d.raw_hash IS NOT NULL AND d.content_type LIKE '%csv%' "
        "AND d.id = (SELECT MAX(d2.id) FROM document d2 WHERE d2.source_id = d.source_id "
        "AND d2.raw_hash IS NOT NULL AND d2.content_type LIKE '%csv%')"
    ).fetchall()
    for sid, digest, ctype in rows:
        try:
            docs[sid] = (store.get(digest), ctype)
        except (OSError, StoreError):
            continue  # archived file missing — source falls back to honest failure
        src = conn.execute("SELECT url, export_url FROM source WHERE id = ?", (sid,)).fetchone()
        if src:
            bases[sid] = [u for u in (src[0], src[1]) if u]
    return StoreFetcher(docs, bases)


def sample(conn, store, fetcher, source_rows: dict, n: int, seed: int, out_dir: str,
           dry_run: bool = False, ts: str | None = None, logger=None,
           from_store: bool = False) -> tuple:
    """Run the per-registry sample. ``source_rows`` maps id → SourceRef
    (validated by the CLI). Returns (exit_code, entries).

    The manifest is ALWAYS written (review 1A) — unless --dry-run,
    which plans requests and writes nothing.
    """
    ts = ts or _utc_ts()
    if dry_run:
        for sid, src in source_rows.items():
            fetcher.plan(src.export_url or src.url)
            if sid == "AS-3":
                for suffix in _NS_CANDIDATE_SUFFIXES[1:]:
                    fetcher.plan((src.export_url or src.url) + suffix)
        return 0, []

    parameters = {"n": n, "seed": seed, "dry_run": False, "from_store": from_store}
    handlers = {"AS-2": _sample_ecat, "AS-3": _sample_nordic_swan}
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    for sid, source in source_rows.items():
        handler = handlers.get(sid)
        if handler is None:
            reason = _NO_FETCH_REASONS.get(sid, "no product rows published by this register (no handler)")
            entries.append(_no_fetch(conn, sid, reason, parameters, logger))
        else:
            entries.append(handler(conn, store, fetcher, source, n, seed, out_dir, ts, parameters, logger))

    md = _render_manifest_md(ts, n, seed, entries)
    csv_text = _render_manifest_csv(entries)
    for name, text in (
        (f"csv-sample.manifest.{ts}.md", md),
        (f"csv-sample.manifest.{ts}.csv", csv_text),
        ("csv-sample.manifest.md", md),
        ("csv-sample.manifest.csv", csv_text),
    ):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    exit_code = 2 if any(e["status"] == "failed" for e in entries) else 0
    return exit_code, entries

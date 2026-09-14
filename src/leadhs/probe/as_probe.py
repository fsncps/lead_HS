"""AS-class source probe (v0.2.4 addendum, D37) — one finding per AS
source: a product-row CSV where obtainable, otherwise why not and what
is available instead, plus exact-or-estimated record counts.

`leadhs probe as-source-probe` walks all 30 AS rows ("Associations &
registers"). The class is NOT all product registries — two kinds:

    registries (AS-2..AS-10, 9)
        bounded export discovery (<=5 polite GETs, landing page
        included) → CSV/TSV saved whole + exact row count, or XLSX
        parsed and rendered as CSV; else the landing-page text gives
        an estimate (method + access date) or an honest unknown, plus
        what is available instead (per-product downloads, PDF lists,
        auth-gated API, web database).
    associations (AS-1, AS-11..AS-30, 21)
        1 liveness GET — no product register by design; the finding
        points at the member list (member count when trivially
        visible).

AS-2/AS-3 reuse the same-day csv-sample run (copy-if-exists, 2A) —
never refetched here; a missing artifact is an honest unavailable
record, never silent (review 1A spirit).

Per-source state machine:

    pending ──▶ delivered  (as_probe_rows, exact; exit contribution 0)
         ────▶ records     (as_probe_records, exact-or-estimated)
         ────▶ unavailable (as_probe_unavailable, expected → exit 0)
         ────▶ assoc       (as_probe_assoc, expected → exit 0)
         ────▶ failed      (should-deliver network only → exit 2)

The engine owns all DB writes (i3): runs are kind=probe, mode
as_source_probe. The summary (`as-source-probe.summary.{md,csv}`) is
ALWAYS written and tells the truth per source. Recon-only (D31).
"""

from __future__ import annotations

import csv
import glob
import io
import os
import re
import shutil

from .. import ids
from ..fetch import FetchError
from ..logutil import log_event
from ..models import DocumentDraft, FindingDraft, ProbeResult
from .. import xlsx as xlsxmod
from . import engine as probeengine
from .adapters._common import UnexpectedFormat, sniff_kind
from .csv_sample import (
    PROVENANCE_COLUMNS,
    _finish,
    _parse_export,
    _today,
    _utc_ts,
    _write_sample_csv,
)

# The registry subset (explicit sets — access_method does not split the
# class: AS-4 is `manual` with an XLSX export, AS-6..10 are `download`).
# The split guard test asserts 9 + 21 = 30 against the register.
REGISTRY_IDS = ("AS-2", "AS-3", "AS-4", "AS-5", "AS-6", "AS-7", "AS-8", "AS-9", "AS-10")

# Bounded discovery candidates per registry (PHASE05): the pinned
# surface first, then the usual export suffixes — <=5 polite GETs, the
# landing-page response reused for the estimate pass.
_CANDIDATE_SUFFIXES = ("", "?format=csv", "/export.csv", "/export.xlsx", "/export")

# The reuse path (2A): the AS-2/AS-3 findings come from the same-day
# csv-sample run; its artifacts live in the parent report dir.
_REUSE_IDS = ("AS-2", "AS-3")

# Expected-unavailable notes: what the register offers instead of a
# product-row CSV (desk knowledge from the v0.2.1/v0.2.2 capability
# passes + the source register notes).
_INSTEAD = {
    "AS-5": "per-product FDES declarations behind registration (auth-gated API; TODOS.md user action)",
    "AS-8": "certified-product PDF lists (NF 130 peintures/vernis section)",
    "AS-9": "a web product database (natureplus.org) without a bulk export",
    "AS-6": "per-product EPD downloads via the library search",
    "AS-7": "per-product EPD downloads via the library search",
    "AS-10": "per-product EPD downloads via the digi portal",
}

# Landing-page estimate patterns (best effort): a number directly
# followed by a count noun. `unknown` is a valid recorded outcome.
_COUNT_RE = re.compile(
    r"(\d[\d\s,'.\u00a0\u202f]{0,11})\s*\+?\s*(?:published\s+|certified\s+|verified\s+)?"
    r"(products?|epds?|declarations?|entries|listings|systems?)\b",
    re.IGNORECASE,
)

# Association member-count pattern (best effort, same discipline).
_MEMBERS_RE = re.compile(
    r"(\d[\d\s,'.\u00a0\u202f]{0,11})\s*(member companies|members|mitglieder|entreprises membres|entreprise|companies)",
    re.IGNORECASE,
)


def provenance_columns() -> tuple:
    """Re-exported for tests: the provenance block of every written CSV."""
    return PROVENANCE_COLUMNS


def _norm_num(text: str) -> str:
    return re.sub(r"[',.\s\u00a0\u202f]", "", text)


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


# --- run bookkeeping (engine write path, i3) --------------------------------


def _begin_run(conn, source_id: str, parameters: dict) -> tuple:
    slug = ids.slug_for_source(source_id) + "asprobe"
    run_id, run_key, _started = probeengine._insert_run(conn, "probe", source_id, slug, parameters)
    probeengine._insert_probe_run(conn, run_id, "as_source_probe")
    conn.commit()
    return run_id, run_key


def _entry(source_id, name, status, run_key, records=None, basis=None, instead=None, file=None, gets=None, reason=None):
    return {"source": source_id, "name": name, "status": status, "run_key": run_key,
            "records": records, "basis": basis, "instead": instead, "file": file,
            "gets": gets, "reason": reason}


def _persist(conn, store, source_id, run_id, doc, finding):
    probeengine.persist(
        conn, store, source_id, run_id,
        ProbeResult(documents=[doc] if doc else [], findings=[finding]),
    )


# --- handlers ----------------------------------------------------------------


def _reuse(conn, store, source, out_dir, ts, parameters, logger=None):
    """AS-2/AS-3 (2A): copy the newest same-day csv-sample artifact —
    no refetch; missing artifact → honest unavailable."""
    run_id, run_key = _begin_run(conn, source.id, parameters)
    reuse_dir = parameters.get("reuse_dir") or os.path.dirname(out_dir.rstrip("/"))
    candidates = sorted(glob.glob(os.path.join(reuse_dir, f"csv-sample.*.{source.id}.csv")))
    if not candidates:
        reason = (
            f"no same-day csv-sample artifact to reuse for {source.id} — run "
            f"`leadhs probe download-csv-sample` first (the AS probe reuses, never refetches)"
        )
        _persist(conn, store, source.id, run_id, None, FindingDraft(
            metric_code="as_probe_unavailable", method_code="manual", value_text=reason))
        _finish(conn, run_id, "unavailable", [f"AS-2/3 reuse: missing artifact"])
        return _entry(source.id, source.name, "unavailable", run_key, reason=reason)
    src_path = candidates[-1]
    file_name = os.path.basename(src_path)
    os.makedirs(out_dir, exist_ok=True)
    shutil.copy2(src_path, os.path.join(out_dir, file_name))
    with open(src_path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    n_rows = max(len(rows) - 1, 0)
    _persist(conn, store, source.id, run_id, None, FindingDraft(
        metric_code="as_probe_rows", method_code="manual", value_numeric=float(n_rows),
        unit_code="count",
        notes=f"reused same-day csv-sample artifact {file_name} (no refetch; 2A)"))
    _finish(conn, run_id, "delivered", [f"reuse copy: {file_name} ({n_rows} rows)"])
    if logger:
        log_event(logger, "as_probe", "reused", source=source.id, run_key=run_key, rows=n_rows)
    return _entry(source.id, source.name, "delivered", run_key, records=f"{n_rows} (exact)",
                  basis=f"reused {file_name}", file=file_name, gets=0)


def _save_csv(out_dir, ts, source_id, header, rows) -> tuple:
    """Full obtained export → `as-probe.<ts>.<id>.csv` (verbatim
    columns + the provenance block on every row)."""
    file_name = f"as-probe.{ts}.{source_id}.csv"
    _write_sample_csv(os.path.join(out_dir, file_name), header, rows, source_id,
                      "as-source-probe", _today(), "", None)
    return file_name, len(rows)


def _registry(conn, store, fetcher, source, out_dir, ts, parameters, logger=None):
    """AS-4..AS-10: bounded export discovery (<=5 GETs, landing page
    included); CSV/TSV saved whole, XLSX rendered; else estimate from
    the landing-page text; else honest unavailable + what's-instead."""
    run_id, run_key = _begin_run(conn, source.id, parameters)
    base = (source.export_url or source.url).rstrip("/")
    landing_text, detail = None, None
    for gets, suffix in enumerate(_CANDIDATE_SUFFIXES, 1):
        url = base + suffix
        try:
            resp = fetcher.get(url)
        except FetchError as exc:
            if gets == 1:
                # the pinned surface itself is should-deliver
                reason = f"network failure on the pinned URL: {exc}"
                _persist(conn, store, source.id, run_id, None, FindingDraft(
                    metric_code="as_probe_unavailable", method_code="download",
                    value_text=f"FAILED: {reason}"))
                _finish(conn, run_id, "failed", [f"{source.id}: {reason}"])
                return _entry(source.id, source.name, "failed", run_key, reason=reason)
            # a guessed candidate failing is discovery, not delivery
            detail = f"{gets} GET(s): unreachable candidate {url} ({exc})"
            continue
        if resp.status_code != 200:
            detail = f"{gets} GET(s): HTTP {resp.status_code} at {url}"
            continue
        kind = sniff_kind(resp.headers.get("Content-Type"), resp.content[:512])
        if kind in ("csv", "tsv"):
            try:
                header, records = _parse_export(resp.content, resp.headers.get("Content-Type"), None)
            except UnexpectedFormat as exc:
                detail = f"format: {exc.detail}"
                break
            digest, _rel = store.put(source.id, resp.content, "csv")
            doc = DocumentDraft(url=url, content=resp.content,
                                content_type=resp.headers.get("Content-Type"),
                                retrieval_method_code="download")
            file_name, n_rows = _save_csv(out_dir, ts, source.id, header, records)
            _persist(conn, store, source.id, run_id, doc, FindingDraft(
                metric_code="as_probe_rows", method_code="download", value_numeric=float(n_rows),
                unit_code="count", document=doc,
                notes=(f"full export obtained via {url}; file=as-probe.{ts}.{source.id}.csv; "
                       f"header: {', '.join(header)}; doc_hash={digest}")))
            _finish(conn, run_id, "delivered", [f"export: {n_rows} rows ({gets} GETs)"])
            if logger:
                log_event(logger, "as_probe", "delivered", source=source.id, run_key=run_key, rows=n_rows)
            return _entry(source.id, source.name, "delivered", run_key,
                          records=f"{n_rows} (exact)", basis=f"full export, {gets} GETs",
                          file=file_name, gets=gets)
        if kind == "xlsx":
            try:
                sheets = xlsxmod.sheet_rows(resp.content)
            except xlsxmod.XlsxError as exc:
                detail = f"xlsx: {exc}"
                break
            digest, _rel = store.put(source.id, resp.content, "xlsx")
            doc = DocumentDraft(url=url, content=resp.content,
                                content_type=resp.headers.get("Content-Type"),
                                retrieval_method_code="download")
            sheet_name = next(iter(sheets))
            rows = sheets[sheet_name]
            header = rows[0] if rows else []
            data = [dict(zip(header, r)) for r in rows[1:]]
            file_name, n_rows = _save_csv(out_dir, ts, source.id, header, data)
            _persist(conn, store, source.id, run_id, doc, FindingDraft(
                metric_code="as_probe_rows", method_code="download", value_numeric=float(n_rows),
                unit_code="count", document=doc,
                notes=(f"XLSX export obtained via {url} (sheet {sheet_name!r}), rendered as CSV; "
                       f"file=as-probe.{ts}.{source.id}.csv; doc_hash={digest}")))
            _finish(conn, run_id, "delivered", [f"xlsx export: {n_rows} rows ({gets} GETs)"])
            if logger:
                log_event(logger, "as_probe", "delivered", source=source.id, run_key=run_key, rows=n_rows)
            return _entry(source.id, source.name, "delivered", run_key,
                          records=f"{n_rows} (exact)", basis=f"XLSX export ({sheet_name}), {gets} GETs",
                          file=file_name, gets=gets)
        if kind == "html":
            landing_text = resp.content.decode("utf-8", "replace")
        detail = f"{gets} GET(s): {kind} at {url}"
    # Budget spent — estimate from the landing text or record the gap.
    instead = _INSTEAD.get(source.id, "the register's web interface")
    if landing_text:
        m = _COUNT_RE.search(_clean_html(landing_text))
        if m:
            count = _norm_num(m.group(1))
            noun = m.group(2)
            basis = (f"estimate from visible page text ({noun}) on {base}, "
                     f"accessed {_today()}")
            _persist(conn, store, source.id, run_id, None, FindingDraft(
                metric_code="as_probe_records", method_code="download",
                value_text=f"estimated {count} — {basis}; available instead: {instead}"))
            _finish(conn, run_id, "unavailable", [f"estimate: {count} {noun}"])
            return _entry(source.id, source.name, "records", run_key,
                          records=f"≈{count} (estimated)", basis=basis, instead=instead,
                          gets=len(_CANDIDATE_SUFFIXES))
        basis = f"no export endpoint found after <=5 bounded GETs (last: {detail}); count not visible on the landing page"
        _persist(conn, store, source.id, run_id, None, FindingDraft(
            metric_code="as_probe_unavailable", method_code="download",
            value_text=f"no product-row CSV obtainable — {basis}; accessed {_today()}; available instead: {instead}"))
        _finish(conn, run_id, "unavailable", [f"no export ({len(_CANDIDATE_SUFFIXES)} GETs)"])
        return _entry(source.id, source.name, "unavailable", run_key,
                      records="unknown", basis=basis, instead=instead,
                      gets=len(_CANDIDATE_SUFFIXES))
    _persist(conn, store, source.id, run_id, None, FindingDraft(
        metric_code="as_probe_unavailable", method_code="download",
        value_text=f"no product-row CSV obtainable — {detail or 'export mechanics unpinned'}; accessed {_today()}; available instead: {instead}"))
    _finish(conn, run_id, "unavailable", [f"no export after bounded GETs"])
    return _entry(source.id, source.name, "unavailable", run_key,
                  records="unknown", basis=detail, instead=instead, gets=len(_CANDIDATE_SUFFIXES))


def _association(conn, store, fetcher, source, parameters, logger=None):
    """The 21 associations: 1 liveness GET — no product register by
    design; member list is the offer (count when trivially visible)."""
    run_id, run_key = _begin_run(conn, source.id, parameters)
    try:
        resp = fetcher.get(source.url)
    except FetchError as exc:
        text = (f"trade association — no product register by design; site unreachable "
                f"at probe time ({exc}); member list (unverified): {source.url}")
        _persist(conn, store, source.id, run_id, None, FindingDraft(
            metric_code="as_probe_assoc", method_code="manual", value_text=text))
        _finish(conn, run_id, "unavailable", [f"{source.id}: unreachable"])
        return _entry(source.id, source.name, "assoc", run_key,
                      basis="site unreachable at probe time", instead=source.url, gets=1)
    if resp.status_code != 200:
        text = (f"trade association — no product register by design; site not serving "
                f"(HTTP {resp.status_code}) at probe time; member list (unverified): {source.url}")
        _persist(conn, store, source.id, run_id, None, FindingDraft(
            metric_code="as_probe_assoc", method_code="manual", value_text=text))
        _finish(conn, run_id, "unavailable", [f"{source.id}: HTTP {resp.status_code}"])
        return _entry(source.id, source.name, "assoc", run_key,
                      basis=f"site not serving (HTTP {resp.status_code})", instead=source.url, gets=1)
    doc = DocumentDraft(url=source.url, content=resp.content,
                        content_type=resp.headers.get("Content-Type"),
                        retrieval_method_code="download")
    text_plain = _clean_html(resp.content.decode("utf-8", "replace"))
    m = _MEMBERS_RE.search(text_plain)
    count_note = f"; ≈{_norm_num(m.group(1))} {m.group(2).lower()} visible (landing-page text, accessed {_today()})" if m else ""
    _persist(conn, store, source.id, run_id, doc, FindingDraft(
        metric_code="as_probe_assoc", method_code="download", document=doc,
        value_text=(f"trade association — no product register; available instead: member list "
                    f"at {source.url}{count_note}")))
    _finish(conn, run_id, "unavailable", [f"{source.id}: association (live)"])
    if logger:
        log_event(logger, "as_probe", "assoc", source=source.id, run_key=run_key)
    return _entry(source.id, source.name, "assoc", run_key,
                  records="0 product records (not a register)",
                  basis="association landing page live" + (f"; members visible" if m else ""),
                  instead=f"member list {source.url}", gets=1)


# --- summary outputs ---------------------------------------------------------


def _render_summary_md(ts, entries) -> str:
    lines = [
        "# AS-class source probe — summary",
        "",
        f"Run: `{ts}` · all 30 AS rows · one finding per source (D37).",
        "",
        "Registries (AS-2..AS-10): product-row CSV where obtainable,",
        "else exact-or-estimated record count with provenance, else why",
        "not + what is available instead. Associations: no product",
        "register by design — member-list pointer, liveness recorded.",
        "",
    ]
    for e in entries:
        lines.append(f"## {e['source']} — {e['name']} — {e['status']}")
        lines.append("")
        if e["records"]:
            lines.append(f"- records: **{e['records']}**")
        if e["basis"]:
            lines.append(f"- basis: {e['basis']}")
        if e["instead"]:
            lines.append(f"- available instead: {e['instead']}")
        if e["file"]:
            lines.append(f"- artifact: `{e['file']}`")
        if e["gets"] is not None:
            lines.append(f"- GETs spent: {e['gets']}")
        if e["reason"]:
            lines.append(f"- note: {e['reason']}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Generated by `leadhs probe as-source-probe` — constants in")
    lines.append("`src/leadhs/probe/as_probe.py` + the design method sheet (D37).")
    lines.append("")
    return "\n".join(lines)


def _render_summary_csv(entries) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["source_id", "name", "status", "records", "basis", "available_instead", "artifact", "gets", "reason"])
    for e in entries:
        writer.writerow([e["source"], e["name"], e["status"], e["records"] or "", e["basis"] or "",
                         e["instead"] or "", e["file"] or "", e["gets"] if e["gets"] is not None else "", e["reason"] or ""])
    return buf.getvalue()


# --- orchestration -----------------------------------------------------------


def sample(conn, store, fetcher, source_rows: dict, out_dir: str,
           dry_run: bool = False, ts: str | None = None, logger=None,
           reuse_dir: str | None = None) -> tuple:
    """Run the AS-class probe. ``source_rows`` maps id → SourceRef.
    Returns (exit_code, entries). The summary is ALWAYS written (1A) —
    unless --dry-run, which plans requests and writes nothing."""
    ts = ts or _utc_ts()
    if dry_run:
        for sid, src in source_rows.items():
            if sid in _REUSE_IDS:
                continue
            if sid in REGISTRY_IDS:
                base = (src.export_url or src.url).rstrip("/")
                for suffix in _CANDIDATE_SUFFIXES:
                    fetcher.plan(base + suffix)
            else:
                fetcher.plan(src.url)
        return 0, []

    parameters = {"dry_run": False, "reuse_dir": reuse_dir}
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    for sid, source in source_rows.items():
        if sid in _REUSE_IDS:
            entries.append(_reuse(conn, store, source, out_dir, ts, parameters, logger))
        elif sid in REGISTRY_IDS:
            entries.append(_registry(conn, store, fetcher, source, out_dir, ts, parameters, logger))
        else:
            entries.append(_association(conn, store, fetcher, source, parameters, logger))

    md = _render_summary_md(ts, entries)
    csv_text = _render_summary_csv(entries)
    for name, text in (
        (f"as-source-probe.summary.{ts}.md", md),
        (f"as-source-probe.summary.{ts}.csv", csv_text),
        ("as-source-probe.summary.md", md),
        ("as-source-probe.summary.csv", csv_text),
    ):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    exit_code = 2 if any(e["status"] == "failed" for e in entries) else 0
    return exit_code, entries

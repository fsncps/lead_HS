"""Source feasibility census report — od8 content layer as amended by
D28 (product-first; U11–U13).

One DB-only assembly, three renderers (D25/i12): md — the two study
numbers lead (Q1 products available as an observed floor, Q2 reachable
SDS-type documentation), one product-first summary matrix, the
execution log (latest census run per source incl. blocked/failed with
notes), compact per-source blocks, legend; csv — the summary matrix
only; json — the full structure (incl. anchor candidates and source
activity). Dry-run runs are excluded from census sections (malformed
parameters_json fails open toward inclusion). Trade rows are volume
context — tariff-line flows, never products (D28 grain rule). Legend:
"—" = metric absent (not queried); 0 = queried, empty. Product data
only (Strategy MASTER D27): inactive register rows appear in the
matrix, never as findings. P7: every user-facing count comes from the
DB only. Anchor candidates are provisional — promotion is a manual M1
method decision, never automatic (D20).
"""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

from jinja2 import Environment, PackageLoader

_TEMPLATE = "probe_report.md.j2"

TITLE = "Source feasibility census report"
FRAMING = (
    "This report answers two study questions: (Q1) how many paint/varnish "
    "products each registered source exposes — observed listings, a floor, "
    "never a market total — and (Q2) for how many of them SDS-type "
    "documentation is reachable. Trade-statistics rows are volume context: "
    "tariff-line flows, never products. These remain source-feasibility "
    "metrics only: product and lead prevalence are M2+ deliverables and are "
    "never implied here. The tool, the database and the reports carry "
    "product data only (Strategy MASTER D27): inactive register rows appear "
    "in the matrix without findings."
)
LEGEND = [
    "\u201c\u2014\u201d = metric absent (source not queried for it); 0 = queried, empty result.",
    "Metric values cite the run_key of the done run they come from.",
    "Status reflects the latest census run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.",
    "products_listed / doc_links_seen are walk floors (BFS depth \u2264 3, page budget \u2264 12 incl. homepage); walk budget: exhausted marks a budget-limited walk — the floor is then a weaker lower bound.",
    "records_hs* columns are volume context: tariff-line flows, not products (D28 grain rule).",
]
NO_RUNS_LINE = "No census runs yet — run `make probe-dry` to plan or `GO=1 make probe` to execute."

MATRIX_METRICS = (
    "products_listed", "doc_links_seen", "walk_budget_exhausted",
    "catalog_count", "category_count", "page_sample_ok", "sds_sample_ok",
    "records_hs3208", "records_hs3209", "records_hs3213", "export_rows",
)

SECTIONS = {
    "access": ("robots", "terms", "rate_limit", "access_blocked", "robots_denied"),
    "content": ("format", "granularity", "coverage_years", "languages", "category_list", "extraction_path", "census_status"),
    "counts": ("catalog_count", "category_count", "export_rows", "records_hs3208", "records_hs3209", "records_hs3213"),
    "availability": ("free_access", "page_sample_ok", "sds_sample_ok"),
}

_MATRIX_HEADER = ["source_id", "class_code", "active", "status"] + list(MATRIX_METRICS) + ["last_run_key"]


def _is_dry_run(parameters_json: Optional[str]) -> bool:
    if not parameters_json:
        return False
    try:
        return bool(json.loads(parameters_json).get("dry_run"))
    except (ValueError, AttributeError):
        return False  # fail open toward inclusion (the engine writes parseable JSON)


def _fmt_value(row) -> str:
    if row["value_numeric"] is not None:
        v = row["value_numeric"]
        s = str(int(v)) if float(v).is_integer() else str(v)
        return s + (f" {row['unit_code']}" if row["unit_code"] else "")
    return row["value_text"] if row["value_text"] is not None else "\u2014"


def _int_or_dash(value) -> str:
    if value is None:
        return "\u2014"
    v = float(value)
    return str(int(v)) if v.is_integer() else str(v)


def _compact_lines(by_metric: dict) -> tuple:
    """The one-line-per-source compact blocks (U11): access / content /
    counts. Values are display strings ("—" when absent)."""

    def val(code):
        rows = by_metric.get(code)
        return rows[0]["value"] if rows else "\u2014"

    access = [
        f"robots {val('robots')}",
        f"terms {val('terms')}",
        f"rate limit {val('rate_limit')}",
        f"free access {val('free_access')}",
    ]
    for code in ("access_blocked", "robots_denied"):
        for r in by_metric.get(code, []):
            access.append(f"{code}: {r['value']}")
    content = [
        f"format {val('format')}",
        f"granularity {val('granularity')}",
        f"coverage {val('coverage_years')}",
        f"languages {val('languages')}",
    ]
    for r in by_metric.get("extraction_path", []):
        content.append(f"extraction path: {r['value']}")
    for r in by_metric.get("census_status", []):
        content.append(f"census status: {r['value']}")
    counts = []
    if by_metric.get("catalog_count"):
        counts.append(f"catalog {val('catalog_count')}")
    cats = by_metric.get("category_count", [])
    if cats:
        parts = []
        for r in cats:
            path = (r.get("notes") or "").removeprefix("category path: ") or "\u2014"
            parts.append(f"{path}={_int_or_dash(r.get('value_numeric'))}")
        counts.append("categories: " + ", ".join(parts))
    if by_metric.get("export_rows"):
        counts.append(f"export rows {val('export_rows')}")
    if by_metric.get("walk_budget_exhausted"):
        exhausted = int(by_metric["walk_budget_exhausted"][0]["value_numeric"] or 0)
        counts.append("walk budget: exhausted" if exhausted else "walk budget: within budget")
    return " · ".join(access), " · ".join(content), " · ".join(counts)


def _fetch_sources(conn, source_id: Optional[str] = None) -> list:
    sql = (
        "SELECT id, class_code, name, url, access_method_code, "
        "verification_status_code, active, notes FROM source"
    )
    params = ()
    if source_id:
        sql += " WHERE id = ?"
        params = (source_id,)
    return [dict(r) for r in conn.execute(sql + " ORDER BY id", params).fetchall()]


def _fetch_census(conn, source_id: Optional[str] = None) -> list:
    sql = (
        "SELECT v.source_id, v.metric_code, v.value_numeric, v.value_text, v.unit_code, "
        "v.method_code, v.run_key, v.started_at, pf.notes "
        "FROM v_probe_latest v LEFT JOIN probe_finding pf ON pf.id = v.finding_id"
    )
    params = ()
    if source_id:
        sql += " WHERE v.source_id = ?"
        params = (source_id,)
    return [dict(r) for r in conn.execute(sql + " ORDER BY v.source_id, v.metric_code", params).fetchall()]


def _fetch_latest_runs(conn) -> dict:
    """Latest census probe run per source (any status; dry-run runs
    skipped — the first non-dry-run wins). Returns {source_id: run}."""
    rows = conn.execute(
        "SELECT r.id AS run_id, r.source_id, r.run_key, r.started_at, r.finished_at, "
        "r.status_code, r.notes, r.parameters_json "
        "FROM run r JOIN probe_run pr ON pr.run_id = r.id "
        "WHERE r.kind_code = 'probe' AND pr.mode_code = 'census' AND r.source_id IS NOT NULL "
        "ORDER BY r.source_id, r.started_at DESC, r.id DESC"
    ).fetchall()
    doc_counts = dict(conn.execute("SELECT run_id, COUNT(*) FROM document GROUP BY run_id").fetchall())
    finding_counts = dict(conn.execute("SELECT run_id, COUNT(*) FROM probe_finding GROUP BY run_id").fetchall())
    latest: dict = {}
    for row in rows:
        sid = row["source_id"]
        if sid in latest or _is_dry_run(row["parameters_json"]):
            continue
        latest[sid] = {
            "run_key": row["run_key"],
            "status": row["status_code"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
            "notes": row["notes"],
            "documents": doc_counts.get(row["run_id"], 0),
            "findings": finding_counts.get(row["run_id"], 0),
        }
    return latest


def _fetch_anchors(conn, source_id: Optional[str] = None) -> list:
    sql = "SELECT source_id, metric_code, value_numeric, unit_code, run_key FROM v_anchor_candidates"
    params = ()
    if source_id:
        sql += " WHERE source_id = ?"
        params = (source_id,)
    return [dict(r) for r in conn.execute(sql + " ORDER BY source_id, metric_code", params).fetchall()]


def _fetch_activity(conn) -> list:
    rows = conn.execute(
        "SELECT source_id, first_retrieved_at, last_retrieved_at, run_count, finding_count "
        "FROM v_source_activity ORDER BY source_id"
    ).fetchall()
    return [dict(r) for r in rows]


def build(conn, source_id: Optional[str] = None) -> dict:
    """The single od8 assembly — all three renderers read this."""
    sources = _fetch_sources(conn, source_id)
    census = _fetch_census(conn, source_id)
    latest_runs = _fetch_latest_runs(conn)
    anchors = _fetch_anchors(conn, source_id)
    activity = _fetch_activity(conn) if not source_id else [
        dict(r) for r in conn.execute(
            "SELECT source_id, first_retrieved_at, last_retrieved_at, run_count, finding_count "
            "FROM v_source_activity WHERE source_id = ?", (source_id,)
        ).fetchall()
    ]

    metrics_by_source: dict = {}
    for row in census:
        row = dict(row)
        row["value"] = _fmt_value(row)
        metrics_by_source.setdefault(row["source_id"], []).append(row)

    entries = []
    for src in sources:
        sid = src["id"]
        rows = metrics_by_source.get(sid, [])
        by_metric: dict = {}
        for row in rows:
            by_metric.setdefault(row["metric_code"], []).append(row)
        run = latest_runs.get(sid)
        entry = dict(src)
        entry["active"] = bool(src["active"])
        entry["run"] = run
        entry["status"] = run["status"] if run else None
        entry["matrix"] = {code: (by_metric[code][0]["value"] if by_metric.get(code) else "\u2014") for code in MATRIX_METRICS}
        entry["matrix"]["last_run_key"] = run["run_key"] if run else "\u2014"
        entry["access_line"], entry["content_line"], entry["counts_line"] = _compact_lines(by_metric)
        entry["sections"] = {
            name: [dict(r) for code in codes for r in by_metric.get(code, [])]
            for name, codes in SECTIONS.items()
        }
        entries.append(entry)

    return {
        "report": {"title": TITLE, "framing": FRAMING, "legend": LEGEND, "no_runs_line": NO_RUNS_LINE, "source_filter": source_id},
        "sources": entries,
        "anchor_candidates": anchors,
        "source_activity": activity,
    }


def _matrix_rows(data: dict) -> list:
    header = _MATRIX_HEADER
    rows = [header]
    for entry in data["sources"]:
        rows.append([
            entry["id"], entry["class_code"], "1" if entry["active"] else "0",
            entry["status"] or "\u2014",
            *[entry["matrix"][code] for code in MATRIX_METRICS],
            entry["matrix"]["last_run_key"],
        ])
    return rows


def render(conn, format: str = "md", source_id: Optional[str] = None) -> str:
    data = build(conn, source_id=source_id)
    if format == "md":
        env = Environment(loader=PackageLoader("leadhs", "templates"))
        return env.get_template(_TEMPLATE).render(
            report=data["report"],
            sources=data["sources"],
            anchors=data["anchor_candidates"],
            activity=data["source_activity"],
        )
    if format == "csv":
        out = io.StringIO()
        writer = csv.writer(out)
        for row in _matrix_rows(data):
            writer.writerow(row)
        return out.getvalue()
    if format == "json":
        return json.dumps(data, indent=2)
    raise ValueError(f"unknown format {format!r}")

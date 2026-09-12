"""Source feasibility census report — od8 content layer, numbers-first
layout per v0.2.0 nu4/nu5 (i16).

One DB-only assembly, three renderers (D25/i12): md — the N1 headline
(anchors + method sheet, the range arithmetic stays md-only), the N2/N3
headline with access-tier composition (a)–(d), the per-source summary
matrix, trade-context and priors lines, the access-decision bridge,
the execution log, compact per-source blocks, legend; csv — the summary
matrix only; json — the full structure (incl. tier dicts, excluded-
source lists, anchor values — never a computed N1 range, nu5). Values
come from v_probe_latest (latest done probe run per source × metric);
dry-run runs are excluded automatically (malformed parameters_json
fails open toward inclusion). Trade rows are volume context —
tariff-line flows, never products (D28 grain rule). Legend: "—" =
metric absent (not queried); 0 = queried, empty. Product data only
(Strategy MASTER D27): inactive register rows appear in the matrix,
never in sums. P7: every user-facing count comes from the DB only.
Anchor candidates are provisional — promotion is a manual M1 method
decision, never automatic (D20).
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
    "documentation is reachable. The N1 block adds market-size anchors "
    "(trade sums, register counts); the N1 range itself is an estimate "
    "stated in the method sheet, never a DB count. Trade-statistics rows "
    "are volume context: tariff-line flows, never products. These remain "
    "source-feasibility metrics only: product and lead prevalence are M2+ "
    "deliverables and are never implied here. The tool, the database and "
    "the reports carry product data only (Strategy MASTER D27): inactive "
    "register rows appear in the matrix without findings."
)
LEGEND = [
    "\u201c\u2014\u201d = metric absent (source not queried for it); 0 = queried, empty result.",
    "Metric values cite the run_key of the done run they come from.",
    "Status reflects the latest census/recon run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.",
    "Access tiers (active sources): (a) dataset/register access counted \u00b7 (b) sitemap-visible counted \u00b7 (c) visible but uncounted without scraping \u00b7 (d) blocked/unknown. N2 sums tiers (a)+(b) only.",
    "N3 pairs doc-bearing counts with the site count of sds_library_visible = 1 \u2014 a site count, not a product count (labeled as such).",
    "sitemap_products is a recon floor (robots-compliant, counts only; index/size caps render it partial \u2014 \u201cfloor partial\u201d in the notes).",
    "records_hs*/trade_* columns are volume context: tariff-line flows, not products (D28 grain rule); trade quantities carry the API's supplementary unit (see finding notes).",
    "Inactive register rows never enter N2/N3 sums; counted-but-excluded sources are listed explicitly.",
]
NO_RUNS_LINE = "No census runs yet — run `make probe-dry` to plan or `GO=1 make probe` to execute."

MATRIX_METRICS = (
    # numbers-first (v0.2.0 nu4)
    "sitemap_products", "sds_library_visible", "products_registered",
    "producers_registered", "trade_kg_hs3208", "trade_eur_hs3208",
    "trade_kg_hs3209", "trade_eur_hs3209",
    # census metrics (v0.1.2, walk idle since D31 — machinery kept)
    "products_listed", "doc_links_seen", "walk_budget_exhausted",
    "catalog_count", "category_count", "page_sample_ok", "sds_sample_ok",
    "records_hs3208", "records_hs3209", "records_hs3213", "export_rows",
)

# nu4: the plain census_status rides the matrix as a column of its own.
_CENSUS_STATUS_COLUMN = "census_status"

SECTIONS = {
    "access": ("robots", "terms", "rate_limit", "access_blocked", "robots_denied"),
    "content": ("format", "granularity", "coverage_years", "languages", "category_list", "extraction_path", "census_status"),
    "counts": (
        "catalog_count", "category_count", "export_rows",
        "records_hs3208", "records_hs3209", "records_hs3213",
        "trade_kg_hs3208", "trade_eur_hs3208", "trade_kg_hs3209", "trade_eur_hs3209",
    ),
    "availability": ("free_access", "page_sample_ok", "sds_sample_ok", "sds_library_visible"),
    "priors": ("products_registered", "producers_registered", "sitemap_products", "doc_links_seen"),
}

# nu5: N1 anchors render from the DB; the range arithmetic stays in the
# hand-maintained method sheet (md only).
ANCHOR_CODES = (
    "trade_kg_hs3208", "trade_eur_hs3208", "trade_kg_hs3209", "trade_eur_hs3209",
    "producers_registered", "products_registered",
)
_ANCHOR_LABELS = {
    "trade_kg_hs3208": "EU imports HS 3208 (kg)",
    "trade_eur_hs3208": "EU imports HS 3208 (EUR)",
    "trade_kg_hs3209": "EU imports HS 3209 (kg)",
    "trade_eur_hs3209": "EU imports HS 3209 (EUR)",
    "producers_registered": "Producers registered (priors)",
    "products_registered": "Products registered (priors)",
}

# nu5: hand-maintained method sheet (md framing block, like the bridge —
# analytic choices live in prose, D27 documentation-layer precedent).
N1_METHOD_SHEET = [
    "### N1 method sheet (estimate — V2)",
    "",
    "The N1 range is an estimate assembled from the anchors below; every",
    "anchor is a DB-cited count. Formula sketch: N1 \u2248 (producers in scope)",
    "\u00d7 (products per producer), bounded by the trade-flow context; the",
    "anchors carry different coverage (EU vs national registers) and are",
    "never summed naively.",
    "",
    "- **EU trade (CS-2, Eurostat Comext DS-045409):** extra-EU imports",
    "  (flow IMP), full-year sums across partners, HS 3208 + 3209.",
    "  Coverage: CN8-aggregated chapter imports; caveat: trade volume is",
    "  context, never a product count (D28 grain rule); quantities carry",
    "  the API's supplementary unit (see finding notes). Provenance:",
    "  https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409 (accessed 2026-09-12).",
    "- **Producers (AS-1, CEPE; ST-3, Eurostat SBS):** association member",
    "  counts and NACE 20.30 enterprise counts. Coverage: EU paint",
    "  industry; caveat: membership \u2260 full population; assumption bound:",
    "  products-per-producer range stated at M1 with the promoted anchors.",
    "  Provenance: https://www.cepe.org (accessed 2026-09-12);",
    "  https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2 (accessed 2026-09-12).",
    "- **Products registered (priors; ST-2 SPIN, ST-1 PCN, national",
    "  registers):** product-unit register counts as scaling priors.",
    "  Caveat: register populations \u2260 market assortments; each prior is",
    "  a floor over its own frame, not over the EU market.",
    "",
    "The estimate stays labeled as an estimate; json carries the anchor",
    "values, never a computed range (nu5/P7).",
]

# nu4: access-decision bridge (md only, qualitative, evidence-cited).
BRIDGE_INTRO = (
    "### Access-decision bridge\n\n"
    "What a scraping go would buy versus its cost — qualitative, cited to "
    "the run evidence in this report (i14 bridge semantics, stripped of "
    "walk-floor inputs). No decision is taken here; this bridges the "
    "recon numbers to the follow-up options."
)

_MATRIX_HEADER = ["source_id", "class_code", "active", "tier", "status"] + list(MATRIX_METRICS) + [_CENSUS_STATUS_COLUMN, "last_run_key"]


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


def _tier_of(entry: dict, by_metric: dict, run: Optional[dict]) -> Optional[str]:
    """Access tier per active source (nu4): (a) dataset/register access
    counted, (b) sitemap-visible counted, (c) visible but uncounted
    without scraping, (d) blocked/unknown. Inactive sources get None
    (never summed, shown as tier \u2014)."""
    if not entry["active"]:
        return None
    if by_metric.get("products_registered"):
        return "a"
    sitemap = by_metric.get("sitemap_products")
    if sitemap and "no sitemap" not in (sitemap[0].get("notes") or ""):
        return "b"
    if run and run["status"] == "done":
        return "c"
    return "d"


def _counted_value(by_metric: dict, tier: Optional[str]) -> Optional[float]:
    """The N2-relevant count for a tier-(a)/(b) source."""
    if tier == "a" and by_metric.get("products_registered"):
        v = by_metric["products_registered"][0].get("value_numeric")
        return float(v) if v is not None else None
    if tier == "b" and by_metric.get("sitemap_products"):
        v = by_metric["sitemap_products"][0].get("value_numeric")
        return float(v) if v is not None else None
    return None


def _trade_context_lines(by_metric: dict) -> list:
    """One compact line per CS source (nu4): import sums, latest year,
    partner tops from finding notes."""
    lines = []
    parts = []
    for code in ("trade_kg_hs3208", "trade_eur_hs3208", "trade_kg_hs3209", "trade_eur_hs3209"):
        rows = by_metric.get(code)
        if not rows:
            continue
        r = rows[0]
        notes = r.get("notes") or ""
        year = "year ?"
        for token in notes.split(", "):
            if token.startswith("year="):
                year = token
        tops = ""
        if "top partners: " in notes:
            tops = "; top: " + notes.split("top partners: ", 1)[1]
        parts.append(f"{code}: {_int_or_dash(r.get('value_numeric'))} {r.get('unit_code') or ''} ({year}{tops})")
    if parts:
        lines.append("trade context: " + " · ".join(parts))
    return lines


def _priors_lines(entry: dict, by_metric: dict) -> list:
    """One line per ST/AS source (nu4): registered counts + census_status."""
    parts = []
    for code in ("products_registered", "producers_registered", "sitemap_products"):
        rows = by_metric.get(code)
        if rows:
            r = rows[0]
            parts.append(f"{code}={_int_or_dash(r.get('value_numeric'))} [{r.get('run_key')}]")
    for r in by_metric.get("census_status", []):
        parts.append(f"census_status: {r['value']}")
    if parts:
        return [f"priors: " + " · ".join(parts)]
    return []


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
    """Latest census/recon probe run per source (any status; dry-run runs
    skipped — the first non-dry-run wins). Returns {source_id: run}."""
    rows = conn.execute(
        "SELECT r.id AS run_id, r.source_id, r.run_key, r.started_at, r.finished_at, "
        "r.status_code, r.notes, r.parameters_json "
        "FROM run r JOIN probe_run pr ON pr.run_id = r.id "
        "WHERE r.kind_code = 'probe' AND pr.mode_code IN ('census', 'recon') AND r.source_id IS NOT NULL "
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
        entry["tier"] = _tier_of(entry, by_metric, run)
        entry["counted"] = _counted_value(by_metric, entry["tier"])
        entry["matrix"] = {code: (by_metric[code][0]["value"] if by_metric.get(code) else "\u2014") for code in MATRIX_METRICS}
        entry["matrix"]["census_status"] = by_metric["census_status"][0]["value"] if by_metric.get("census_status") else "\u2014"
        entry["matrix"]["last_run_key"] = run["run_key"] if run else "\u2014"
        entry["access_line"], entry["content_line"], entry["counts_line"] = _compact_lines(by_metric)
        entry["trade_lines"] = _trade_context_lines(by_metric)
        entry["priors_lines"] = _priors_lines(entry, by_metric)
        entry["sections"] = {
            name: [dict(r) for code in codes for r in by_metric.get(code, [])]
            for name, codes in SECTIONS.items()
        }
        entries.append(entry)

    numbers = _assemble_numbers(entries)
    anchors = _anchors_from_entries(entries)

    return {
        "report": {"title": TITLE, "framing": FRAMING, "legend": LEGEND, "no_runs_line": NO_RUNS_LINE, "source_filter": source_id},
        "numbers": numbers,
        "anchors": anchors,
        "sources": entries,
        "anchor_candidates": anchors_raw(conn, source_id),
        "source_activity": activity,
    }


def anchors_raw(conn, source_id: Optional[str] = None) -> list:
    sql = "SELECT source_id, metric_code, value_numeric, unit_code, run_key FROM v_anchor_candidates"
    params = ()
    if source_id:
        sql += " WHERE source_id = ?"
        params = (source_id,)
    return [dict(r) for r in conn.execute(sql + " ORDER BY source_id, metric_code", params).fetchall()]


def _anchors_from_entries(entries: list) -> list:
    """N1 anchor values (nu5): latest done value per anchor code per
    source — DB-cited, no computed range."""
    out = []
    for entry in entries:
        for code in ANCHOR_CODES:
            rows = entry.get("sections", {}).get("priors", []) + entry.get("sections", {}).get("counts", [])
            for r in rows:
                if r["metric_code"] == code:
                    out.append({
                        "source_id": entry["id"],
                        "metric_code": code,
                        "label": _ANCHOR_LABELS[code],
                        "value_numeric": r.get("value_numeric"),
                        "unit_code": r.get("unit_code"),
                        "run_key": r.get("run_key"),
                    })
                    break
    return out


def _assemble_numbers(entries: list) -> dict:
    """N2/N3 headline assembly (nu4): tier composition, totals,
    excluded-and-counted, zero-states. All counts DB-cited; no N1 range
    here (nu5 — the estimate stays in the md method sheet)."""
    tiers = {"a": [], "b": [], "c": [], "d": []}
    n2 = 0.0
    n2_components = []
    sds_sites = []
    doc_counts = []
    excluded_counted = []
    for entry in entries:
        sid = entry["id"]
        tier = entry["tier"]
        if tier:
            tiers[tier].append(sid)
        if tier in ("a", "b") and entry["counted"] is not None:
            n2 += entry["counted"]
            n2_components.append({"source_id": sid, "tier": tier, "counted": entry["counted"]})
        elif not entry["active"] and (entry["matrix"]["products_registered"] != "\u2014" or entry["matrix"]["sitemap_products"] != "\u2014"):
            excluded_counted.append(sid)
        rows = entry.get("sections", {}).get("availability", [])
        for r in rows:
            if r["metric_code"] == "sds_library_visible" and (r.get("value_numeric") or 0) == 1:
                sds_sites.append(sid)
        # N3 doc-bearing counts: the walk floor doc_links_seen (idle since
        # D31 — renders as an explicit zero-state while no walk ran)
        for r in entry.get("sections", {}).get("priors", []):
            if r["metric_code"] == "doc_links_seen":
                doc_counts.append({"source_id": sid, "value": r.get("value_numeric") or 0})
    n3_doc_total = sum(d["value"] for d in doc_counts)
    return {
        "tier_sources": tiers,
        "tier_sizes": {k: len(v) for k, v in tiers.items()},
        "n2_total": n2 if n2 > 0 or n2_components else None,
        "n2_components": n2_components,
        "n3_doc_total": n3_doc_total if doc_counts else None,
        "n3_doc_sources": doc_counts,
        "n3_sds_site_count": len(sds_sites) if sds_sites else 0,
        "n3_sds_sites": sds_sites,
        "excluded_counted": excluded_counted,
        "zero_states": {
            "no_counted_sources": not n2_components,
            "no_sds_sites": not sds_sites,
            "no_doc_counts": not doc_counts,
        },
    }


def _matrix_rows(data: dict) -> list:
    header = _MATRIX_HEADER
    rows = [header]
    for entry in data["sources"]:
        rows.append([
            entry["id"], entry["class_code"], "1" if entry["active"] else "0",
            entry["tier"] or "\u2014",
            entry["status"] or "\u2014",
            *[entry["matrix"][code] for code in MATRIX_METRICS],
            entry["matrix"]["census_status"],
            entry["matrix"]["last_run_key"],
        ])
    return rows


def render(conn, format: str = "md", source_id: Optional[str] = None) -> str:
    data = build(conn, source_id=source_id)
    if format == "md":
        env = Environment(loader=PackageLoader("leadhs", "templates"))
        return env.get_template(_TEMPLATE).render(
            report=data["report"],
            numbers=data["numbers"],
            anchors=data["anchors"],
            sources=data["sources"],
            anchor_candidates=data["anchor_candidates"],
            activity=data["source_activity"],
            method_sheet=N1_METHOD_SHEET,
            bridge_intro=BRIDGE_INTRO,
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

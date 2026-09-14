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
    "content": ("format", "granularity", "coverage_years", "languages", "category_list", "extraction_path", "census_status", "sds_doc_urls"),
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

# v0.2.1 capability profile (cap1/C2): one tuple drives the capability-
# matrix columns AND the real-product-source predicate derivation — no
# duplicated literals (i18).
CAPABILITY_METRICS = (
    "products_identifiable", "cap_manufacturer", "cap_product_ident",
    "cap_cn8_linkage", "cap_depth_tier", "cn8_reachable",
)
_CAPABILITY_METRIC_LABELS = {
    "products_identifiable": "identifiable",
    "cap_manufacturer": "mfr",
    "cap_product_ident": "product-ident",
    "cap_cn8_linkage": "cn8-linkage",
    "cap_depth_tier": "depth",
    "cn8_reachable": "cn8-reachable",
}

# A2: the preliminary N2 numerator is a separate derived line with the
# certified-subset caveat — never folded into the existing N2 tiers.
N2_NUMERATOR_CAVEAT = (
    "Preliminary N2 numerator (official registers, floor): sum of "
    "products_identifiable over the real-product sources below. Official "
    "registers are certified/declared subsets of the market, never a "
    "market total — a floor, cited to the run it comes from."
)

# v0.2.2 PHASE06: the three-question funnel landscape (od8 extension).
# Staging sections render conditionally (e5); reconciliation failures
# render as visible flags, never silence (c4).
STAGING_ABSENT_NOTE = (
    "Staging DB not provided or empty — the funnel floor, CN8 trade "
    "table, identity table and per-CN8 pool split render as explicit "
    "absence notes (e5). Re-run the W1 waves with the staging DB to "
    "populate them."
)

FU8_TIER_LABELS = {
    1: "name only",
    2: "name + ident/licence + category (registry metadata, no technical data)",
    3: "adds technical performance data / downloadable tech docs (SDS/TDS links)",
    4: "standardized full documents (EPD declarations; IATA/CMR MSDS)",
}

# Pool model v0 constants (design: producer count bounds; the share s
# comes from the staged Comext kg per CN8). "Modeled estimate" labels
# throughout; pure arithmetic at report time.
POOL_M_LOW = 800
POOL_M_LOW_SOURCE = "CEPE member count (AS-11 manual record)"
POOL_M_HIGH = 3200
POOL_M_HIGH_SOURCE = "Eurostat SBS NACE 20.30 enterprise count (ST-3 prior)"
POOL_FORMULA = "P(cn8) = M × ppp × s(cn8)"

# The overlap pilot pair (calibration-only label per design c5).
OVERLAP_PAIR = ("AS-2", "AS-3")
OVERLAP_LABEL = "ECAT ∩ Nordic Swan (calibration-only)"

# Register sources whose staged categories are criteria classes, not
# CN8 codes — the per-CN8 observed-products proxy is not pinnable.
_CN8_PROXY_NOTE = (
    "per-CN8 observed-products floor not computable from staging: the "
    "staged register categories are criteria classes, not CN8 codes — "
    "the category→CN8 proxy mapping is not pinnable in v0.2.2 (caveat "
    "recorded in PHASE05)."
)


def _q2_union(stg) -> dict:
    """Q2 floor: distinct (manufacturer_norm, ident_norm) pairs over all
    staged registers (union; replace semantics keep only latest runs)."""
    row = stg.execute(
        "SELECT COUNT(DISTINCT manufacturer_norm || '||' || ident_norm), "
        "COUNT(DISTINCT manufacturer_norm) FROM stg_register_product"
    ).fetchone()
    per_source = [
        dict(source_id=r[0], pairs=r[1], entries=r[2])
        for r in stg.execute(
            "SELECT source_id, COUNT(DISTINCT manufacturer_norm || '||' || ident_norm), "
            "COUNT(*) FROM stg_register_product GROUP BY 1 ORDER BY 1"
        ).fetchall()
    ]
    return {"distinct_pairs": row[0] or 0, "distinct_manufacturers": row[1] or 0, "per_source": per_source}


def _overlap_pilot(stg, ids=OVERLAP_PAIR) -> dict:
    """ECAT ∩ Nordic containment + Jaccard on normalized pairs — only
    when both registers are staged; else an explicit zero-state."""
    sets = {}
    for sid in ids:
        rows = stg.execute(
            "SELECT DISTINCT manufacturer_norm || '||' || ident_norm "
            "FROM stg_register_product WHERE source_id=?", (sid,)
        ).fetchall()
        sets[sid] = {r[0] for r in rows}
    missing = [sid for sid, s in sets.items() if not s]
    if missing:
        return {"computed": False, "note": f"overlap pilot not computable — no staged pairs for {', '.join(missing)}"}
    a, b = sets[ids[0]], sets[ids[1]]
    inter = len(a & b)
    smaller = min(len(a), len(b)) or 1
    return {
        "computed": True,
        "a_id": ids[0], "a_pairs": len(a), "b_id": ids[1], "b_pairs": len(b),
        "intersection": inter,
        "containment": round(inter / smaller, 4),
        "jaccard": round(inter / len(a | b), 4) if a | b else 0.0,
        "label": OVERLAP_LABEL,
    }


def _cn8_trade(stg) -> dict:
    """G3/G4: per-CN8 extra-EU import/export sums (kg, EUR) from the
    staged trade rows; flow-code caveat + proxy note carried."""
    flows = {r[0] for r in stg.execute("SELECT DISTINCT flow FROM stg_trade_cn8").fetchall()}
    rows = []
    for r in stg.execute(
        "SELECT cn8, flow, SUM(kg), SUM(eur), COUNT(*) FROM stg_trade_cn8 "
        "GROUP BY 1, 2 ORDER BY 1, 2"
    ).fetchall():
        rows.append({"cn8": r[0], "flow": r[1], "kg": r[2], "eur": r[3], "rows": r[4]})
    verified = stg.execute("SELECT COUNT(*) FROM dict_cn8 WHERE verified=1").fetchone()[0]
    dict_total = stg.execute("SELECT COUNT(*) FROM dict_cn8").fetchone()[0]
    return {
        "rows": rows,
        "flows_seen": sorted(flows),
        "dict_verified": verified,
        "dict_total": dict_total,
        "flow_caveat": (
            None if verified == dict_total and dict_total
            else "intra-EU flow codes not verified — flow labels are provisional"
        ),
        "cn8_proxy_note": _CN8_PROXY_NOTE,
    }


def _identity(stg, entries: list) -> dict:
    """G2/G5: per staged register — entries, distinct manufacturers,
    distinct pairs, identity completeness, category distribution."""
    from .staging import count_products, product_aggregates
    registers = []
    runs = {
        r[0]: r[1]
        for r in stg.execute("SELECT source_id, MAX(run_key) FROM stg_register_product GROUP BY 1").fetchall()
    }
    for sid, run_key in sorted(runs.items()):
        agg = product_aggregates(stg, sid, run_key)
        registers.append({"source_id": sid, "run_key": run_key, "entries": count_products(stg, sid, run_key), **agg})
    q2 = _q2_union(stg)
    return {"registers": registers, "union": q2, "overlap": _overlap_pilot(stg)}


def _depth(entries: list) -> dict:
    """G1 (fu8 refined tiers) + G6 per-PE SDS-URL counts. Tiers derived
    from what the evidence actually carries; nothing asserted."""
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    members = {1: [], 2: [], 3: [], 4: []}
    sds_counts = []
    for e in entries:
        tier = None
        cap = e.get("capability", {})
        if cap.get("cap_depth_tier") not in (None, "\u2014"):
            try:
                tier = int(cap["cap_depth_tier"])
            except (TypeError, ValueError):
                tier = None
        if tier is None and e.get("sections", {}).get("priors"):
            for r in e["sections"]["priors"]:
                if r["metric_code"] == "sitemap_products" and (r.get("value_numeric") or 0) > 0:
                    tier = 1
        if tier in counts:
            counts[tier] += 1
            members[tier].append(e["id"])
        for r in e.get("sections", {}).get("content", []):
            if r["metric_code"] == "sds_doc_urls" and (r.get("value_numeric") or 0) > 0:
                sds_counts.append({"source_id": e["id"], "sds_doc_urls": r["value_numeric"], "run_key": r.get("run_key")})
    return {
        "tier_labels": {str(k): v for k, v in FU8_TIER_LABELS.items()},
        "tier_counts": {str(k): v for k, v in counts.items()},
        "tier_members": {str(k): v for k, v in members.items()},
        "sds_counts": sorted(sds_counts, key=lambda d: -d["sds_doc_urls"]),
        "note": "tier 4 is assigned only from recorded capability metrics (standardized-doc sources are manual records — capability not probed); absence of a tier is not a zero claim",
    }


def _census_sections(conn, entries: list) -> dict:
    """G7: class × channel; enumerated vs probed vs counted."""
    classes = [
        dict(class_code=r[0], channel=r[1], n=r[2])
        for r in conn.execute(
            "SELECT class_code, access_method_code, COUNT(*) FROM source "
            "GROUP BY 1, 2 ORDER BY 1, 2"
        ).fetchall()
    ]
    probed = {e["id"] for e in entries if e.get("run")}
    counted_ids = {e["id"] for e in entries if e.get("counted") is not None}
    return {
        "class_channel": classes,
        "enumerated": conn.execute("SELECT COUNT(*) FROM source").fetchone()[0],
        "probed": len(probed),
        "counted": len(counted_ids),
    }


def _reconcile(stg, entries: list) -> list:
    """c4: metric vs staging count per staged register; every mismatch
    renders as a visible flag."""
    flags = []
    runs = {
        r[0]: r[1]
        for r in stg.execute("SELECT source_id, MAX(run_key) FROM stg_register_product GROUP BY 1").fetchall()
    }
    for e in entries:
        sid = e["id"]
        metric = None
        for r in e.get("sections", {}).get("priors", []):
            if r["metric_code"] == "products_registered":
                metric = r.get("value_numeric")
        if sid in runs:
            n = stg.execute(
                "SELECT COUNT(*) FROM stg_register_product WHERE source_id=? AND run_key=?",
                (sid, runs[sid]),
            ).fetchone()[0]
            if metric is not None and metric != n:
                flags.append({
                    "source_id": sid, "kind": "mismatch",
                    "detail": f"products_registered metric {metric} ≠ staged rows {n} (run {runs[sid]})",
                })
            elif metric is None:
                flags.append({"source_id": sid, "kind": "ok",
                              "detail": f"staged rows {n} (no products_registered metric — reconciled against the staged count, run {runs[sid]})"})
            else:
                flags.append({"source_id": sid, "kind": "ok", "detail": f"staged rows {n} == metric {metric} (run {runs[sid]})"})
        elif metric is not None:
            flags.append({"source_id": sid, "kind": "staging-absent", "detail": "metric present but no staged rows"})
    trade_sources = [r[0] for r in stg.execute("SELECT DISTINCT source_id FROM stg_trade_cn8").fetchall()]
    for sid in trade_sources:
        n = stg.execute("SELECT COUNT(*) FROM stg_trade_cn8 WHERE source_id=?", (sid,)).fetchone()[0]
        flags.append({"source_id": sid, "kind": "ok", "detail": f"{n} staged trade rows"})
    return flags


def _ppp(stg) -> Optional[float]:
    """Products-per-producer estimate (v0): distinct pairs ÷ distinct
    licence holders over the largest staged register — DB-cited."""
    row = stg.execute(
        "SELECT source_id, COUNT(DISTINCT manufacturer_norm || '||' || ident_norm), "
        "COUNT(DISTINCT manufacturer_norm) FROM stg_register_product "
        "GROUP BY 1 ORDER BY 2 DESC LIMIT 1"
    ).fetchone()
    if not row or not row[2]:
        return None
    return {"source_id": row[0], "pairs": row[1], "manufacturers": row[2],
            "ppp": round(row[1] / row[2], 1)}


def _funnel(stg, entries: list) -> dict:
    """The three-question funnel (top section). Q1 range per the pool
    model form with per-CN8 shares from staged trade; Q2 the staged
    pair-union floor; Q3 modeled SDS reach (components DB-cited)."""
    q2 = _q2_union(stg)["distinct_pairs"] if stg else None
    ppp = _ppp(stg) if stg else None
    shares = []
    total_kg = stg.execute("SELECT SUM(kg) FROM stg_trade_cn8").fetchone()[0] if stg else None
    if stg and total_kg:
        for r in stg.execute(
            "SELECT cn8, SUM(kg) FROM stg_trade_cn8 GROUP BY 1 ORDER BY 2 DESC"
        ).fetchall():
            share = r[1] / total_kg
            shares.append({
                "cn8": r[0], "kg": r[1], "share": round(share, 4),
                "p_low": int(POOL_M_LOW * (ppp["ppp"] if ppp else 1) * share),
                "p_high": int(POOL_M_HIGH * (ppp["ppp"] if ppp else 1) * share),
            })
    sds_reach = 0
    for e in entries:
        avail = {r["metric_code"]: r.get("value_numeric") for r in e.get("sections", {}).get("availability", [])}
        if avail.get("sds_library_visible") != 1:
            continue
        for r in e.get("sections", {}).get("priors", []):
            if r["metric_code"] == "sitemap_products":
                sds_reach += r.get("value_numeric") or 0
    if ppp:
        q1_range = [int(POOL_M_LOW * ppp["ppp"]), int(POOL_M_HIGH * ppp["ppp"])]
    else:
        q1_range = None
    funnel = {
        "q1": {
            "formula": POOL_FORMULA,
            "m_bounds": [POOL_M_LOW, POOL_M_HIGH],
            "m_low_source": POOL_M_LOW_SOURCE,
            "m_high_source": POOL_M_HIGH_SOURCE,
            "ppp": ppp,
            "range": q1_range,
            "shares": shares,
            "label": "modeled estimate — never a DB count",
            "absent": q1_range is None or not shares,
        },
        "q2": {
            "value": q2,
            "label": "definitively identifiable: N (floor) — distinct (manufacturer, ident) pairs over staged registers",
            "absent": q2 is None,
        },
        "q3": {
            "value": int(sds_reach) if sds_reach else None,
            "label": "modeled SDS reach — Σ sitemap products over sites with a visible SDS library; match-rate assumption pending (upper bound shown)",
            "absent": not sds_reach,
        },
        "ratio": {
            "formula": "v0.5 ratio = Q2 ÷ Q1",
            "low": round(q2 / q1_range[1], 4) if q2 and q1_range else None,
            "high": round(q2 / q1_range[0], 4) if q2 and q1_range else None,
            "label": "share of the modeled pool that is definitively identifiable (epistemic label: floor ÷ range)",
            "absent": not q2 or not q1_range,
        },
    }
    return funnel


def _landscape(conn, staging_conn, entries: list) -> dict:
    """PHASE06 extension assembly: funnel + CN8 trade + identity +
    depth + census + reconciliation flags. Staging-optional (e5)."""
    stg = staging_conn
    has_products = bool(
        stg and stg.execute("SELECT COUNT(*) FROM stg_register_product").fetchone()[0]
    )
    has_trade = bool(
        stg and stg.execute("SELECT COUNT(*) FROM stg_trade_cn8").fetchone()[0]
    )
    return {
        "staging_present": stg is not None,
        "staging_absent_note": None if (has_products or has_trade) else STAGING_ABSENT_NOTE,
        "funnel": _funnel(stg if (has_products or has_trade) else None, entries),
        "cn8_trade": _cn8_trade(stg) if has_trade else {"rows": [], "absent": True},
        "identity": _identity(stg, entries) if has_products else {"registers": [], "absent": True},
        "depth": _depth(entries),
        "census": _census_sections(conn, entries),
        "reconciliation": _reconcile(stg, entries) if (has_products or has_trade) else [],
    }


def _is_real_product_source(by_metric: dict) -> bool:
    """C3: the single real-product-source predicate
    (cap_manufacturer=1 ∧ cap_product_ident=1 ∧ cap_cn8_linkage!='none'
    ∧ cap_depth_tier>=2), derived at report time, never stored (i17)."""
    def num(code):
        rows = by_metric.get(code)
        return rows[0].get("value_numeric") if rows else None

    mfr = num("cap_manufacturer")
    ident = num("cap_product_ident")
    linkage_rows = by_metric.get("cap_cn8_linkage")
    linkage = linkage_rows[0].get("value_text") if linkage_rows else None
    depth = num("cap_depth_tier")
    return bool(mfr == 1 and ident == 1 and linkage is not None and linkage != "none"
                and depth is not None and depth >= 2)


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


def _fetch_latest_capability_runs(conn) -> dict:
    """A1: the capability matrix fetches its OWN latest-`capability` run
    per source (any status; dry-run skipped), leaving `_fetch_latest_runs`
    (census/recon) untouched so the existing tier logic is unaffected."""
    rows = conn.execute(
        "SELECT r.id AS run_id, r.source_id, r.run_key, r.started_at, r.finished_at, "
        "r.status_code, r.notes, r.parameters_json "
        "FROM run r JOIN probe_run pr ON pr.run_id = r.id "
        "WHERE r.kind_code = 'probe' AND pr.mode_code = 'capability' AND r.source_id IS NOT NULL "
        "ORDER BY r.source_id, r.started_at DESC, r.id DESC"
    ).fetchall()
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


def build(conn, source_id: Optional[str] = None, staging_conn=None) -> dict:
    """The single od8 assembly — all three renderers read this."""
    sources = _fetch_sources(conn, source_id)
    census = _fetch_census(conn, source_id)
    latest_runs = _fetch_latest_runs(conn)
    capability_runs = _fetch_latest_capability_runs(conn)
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
        entry["capability"] = {code: (by_metric[code][0]["value"] if by_metric.get(code) else "\u2014") for code in CAPABILITY_METRICS}
        entry["products_identifiable_num"] = (by_metric["products_identifiable"][0].get("value_numeric")
                                              if by_metric.get("products_identifiable") else None)
        entry["real_product_source"] = _is_real_product_source(by_metric)
        entry["cap_run"] = capability_runs.get(sid)
        entries.append(entry)

    numbers = _assemble_numbers(entries)
    anchors = _anchors_from_entries(entries)
    capability = _assemble_capability(entries)

    return {
        "report": {"title": TITLE, "framing": FRAMING, "legend": LEGEND, "no_runs_line": NO_RUNS_LINE, "source_filter": source_id},
        "numbers": numbers,
        "anchors": anchors,
        "capability": capability,
        "landscape": _landscape(conn, staging_conn, entries),
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


def _assemble_capability(entries: list) -> dict:
    """The capability profile (i18): per-source matrix of the six
    capability metrics + the derived real-product-source flag, and the
    preliminary N2 numerator (A2 — a separate line, never folded into
    the existing N2 tiers)."""
    matrix = []
    numerator_components = []
    numerator_total = 0.0
    for e in entries:
        has_profile = any(v != "\u2014" for v in e["capability"].values())
        if not has_profile and not e["cap_run"]:
            matrix.append({
                "source_id": e["id"], "class_code": e["class_code"], "active": e["active"],
                "run_key": "\u2014", "status": "\u2014",
                "metrics": e["capability"], "real_product_source": False,
            })
            continue
        matrix.append({
            "source_id": e["id"], "class_code": e["class_code"], "active": e["active"],
            "run_key": (e["cap_run"] or {}).get("run_key", "\u2014"),
            "status": (e["cap_run"] or {}).get("status", "\u2014"),
            "metrics": e["capability"],
            "real_product_source": e["real_product_source"],
        })
        if e["real_product_source"] and e["products_identifiable_num"] is not None:
            numerator_components.append({
                "source_id": e["id"],
                "products_identifiable": e["products_identifiable_num"],
                "run_key": (e["cap_run"] or {}).get("run_key", "\u2014"),
            })
            numerator_total += e["products_identifiable_num"]
    return {
        "matrix": matrix,
        "numerator": {
            "total": numerator_total if numerator_components else None,
            "components": numerator_components,
            "caveat": N2_NUMERATOR_CAVEAT,
        },
    }


def _matrix_rows(data: dict) -> list:
    header = _MATRIX_HEADER + list(CAPABILITY_METRICS) + ["real_product_source"]
    rows = [header]
    for entry in data["sources"]:
        rows.append([
            entry["id"], entry["class_code"], "1" if entry["active"] else "0",
            entry["tier"] or "\u2014",
            entry["status"] or "\u2014",
            *[entry["matrix"][code] for code in MATRIX_METRICS],
            entry["matrix"]["census_status"],
            entry["matrix"]["last_run_key"],
            *[entry["capability"][code] for code in CAPABILITY_METRICS],
            "1" if entry["real_product_source"] else "0",
        ])
    return rows


def render(conn, format: str = "md", source_id: Optional[str] = None, staging_conn=None) -> str:
    data = build(conn, source_id=source_id, staging_conn=staging_conn)
    if format == "md":
        env = Environment(loader=PackageLoader("leadhs", "templates"))
        return env.get_template(_TEMPLATE).render(
            report=data["report"],
            numbers=data["numbers"],
            anchors=data["anchors"],
            capability=data["capability"],
            landscape=data["landscape"],
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
        _landscape_rows(writer, data["landscape"])
        return out.getvalue()
    if format == "json":
        return json.dumps(data, indent=2)
    raise ValueError(f"unknown format {format!r}")


def _landscape_rows(writer, landscape: dict) -> None:
    """PHASE06: the landscape sections append to the csv after the
    matrix (full structure per the v0.2.2 design; the matrix block is
    unchanged and first)."""
    writer.writerow([])
    writer.writerow(["section", "key", "subkey", "value"])
    f = landscape.get("funnel", {})
    for q in ("q1", "q2", "q3", "ratio"):
        block = f.get(q, {})
        writer.writerow(["funnel", q, "label", block.get("label", "")])
        if "range" in block:
            writer.writerow(["funnel", q, "range", block["range"]])
        if "value" in block:
            writer.writerow(["funnel", q, "value", block.get("value")])
        for lo_hi in ("low", "high"):
            if block.get(lo_hi) is not None:
                writer.writerow(["funnel", q, lo_hi, block[lo_hi]])
    trade = landscape.get("cn8_trade", {})
    for r in trade.get("rows", []):
        writer.writerow(["cn8_trade", r["cn8"], f"flow {r['flow']}", f"kg={r['kg']} eur={r['eur']} rows={r['rows']}"])
    if trade.get("flow_caveat"):
        writer.writerow(["cn8_trade", "caveat", "flow", trade["flow_caveat"]])
    ident = landscape.get("identity", {})
    for reg in ident.get("registers", []):
        writer.writerow([
            "identity", reg["source_id"], "run " + str(reg["run_key"]),
            f"entries={reg['distinct_pairs'] and reg.get('entries', 0)} pairs={reg['distinct_pairs']} "
            f"mfr={reg['distinct_manufacturers']} completeness={reg['identity_completeness_pct']}%",
        ])
    depth = landscape.get("depth", {})
    for tier, n in depth.get("tier_counts", {}).items():
        writer.writerow(["depth", f"tier {tier}", depth.get("tier_labels", {}).get(int(tier), ""), n])
    for s in depth.get("sds_counts", []):
        writer.writerow(["sds_counts", s["source_id"], "sds_doc_urls", s["sds_doc_urls"]])
    census = landscape.get("census", {})
    writer.writerow(["census", "enumerated", "", census.get("enumerated")])
    writer.writerow(["census", "probed", "", census.get("probed")])
    writer.writerow(["census", "counted", "", census.get("counted")])
    for flag in landscape.get("reconciliation", []):
        writer.writerow(["reconciliation", flag["source_id"], flag["kind"], flag["detail"]])
    if landscape.get("staging_absent_note"):
        writer.writerow(["staging", "absent", "", landscape["staging_absent_note"]])

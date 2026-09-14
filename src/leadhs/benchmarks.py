"""Pool-estimate meta-benchmarking — the magnitude-class verdict engine
(v0.2.3, tr1–tr10; ENG 1A: pure module, zero I/O in the compute layer).

Six independent benchmarks B1–B6 triangulate the total number of
individual paint products/formulas on the EU market and vote over the
contiguous magnitude classes (tr1):

    a) 20k–50k   b) 50k–100k   c) 100k–200k   d) 200k–300k   e) >300k

Deliverable: a dual-level class verdict (SKU/registration and
formulation) under the pinned confidence rule (tr4) — ≥3 *available*
benchmarks implicate the same class at base AND no benchmark is
exclusively compatible with a non-adjacent class; a tie renders the
span plus flip assumptions without a confidence claim (c3); fewer
than three available ⇒ the verdict reads "insufficient basis" (c1).
Indeterminate benchmarks stay visible rows — never dropped silently
(c1); never scaled from zero (c5); every input carries its vintage
(c4); the compression factor is a range per key tier (c2/tr6).

Layering (ENG 1A/2A):
- named query functions (bottom of this module) read the staging and
  evidence DBs and return plain dicts — the only I/O here;
- ``compute_b1()``…``compute_b6()``, ``vote_table()``, ``verdict()``
  and the md renderers are pure — inputs passed in, deterministic;
- report.py (PHASE04) wires real inputs and renders the section.

No legal referencing (Strategy MASTER D27); product data only.
"""

from __future__ import annotations

import json
from typing import Optional

# ------------------------------------------------------------------
# Class taxonomy (tr1: contiguous — every total maps to exactly one
# class above the 20k floor; totals below it are visible out-of-
# taxonomy votes, flagged, never silently dropped).
# ------------------------------------------------------------------

CLASS_KEYS = ("a", "b", "c", "d", "e")
CLASS_BOUNDS = {
    "a": (20_000, 50_000),
    "b": (50_000, 100_000),
    "c": (100_000, 200_000),
    "d": (200_000, 300_000),
    "e": (300_000, None),
}
CLASS_LABELS = {
    "a": "20k\u201350k",
    "b": "50k\u2013100k",
    "c": "100k\u2013200k",
    "d": "200k\u2013300k",
    "e": ">300k",
}
BELOW_TAXONOMY = "<a"
TAXONOMY_FLOOR = CLASS_BOUNDS["a"][0]
CONFIDENCE_OK = "reasonable-high"
SCENARIOS = ("low", "base", "high")


def class_for_value(value: float) -> str:
    """Map one total to its class key (BELOW_TAXONOMY under the floor)."""
    if value < TAXONOMY_FLOOR:
        return BELOW_TAXONOMY
    for key in CLASS_KEYS:
        low, high = CLASS_BOUNDS[key]
        if value >= low and (high is None or value < high):
            return key
    return CLASS_KEYS[-1]


def _adjacent(a: str, b: str) -> bool:
    try:
        return abs(CLASS_KEYS.index(a) - CLASS_KEYS.index(b)) <= 1
    except ValueError:  # BELOW_TAXONOMY is non-adjacent to everything
        return False


def classes_for_band(band: dict) -> dict:
    """Implicated class keys per scenario; None edges are skipped."""
    out = {}
    for scenario in SCENARIOS:
        value = band.get(scenario)
        out[scenario] = [class_for_value(value)] if value is not None else []
    return out


# ------------------------------------------------------------------
# Benchmark-result structure (c7): name, quantity, vintage, band,
# class implication — plain dicts, json-serializable for i12/i16.
# ------------------------------------------------------------------

def result(
    benchmark: str,
    title: str,
    quantity: str,
    vintage: str,
    level: str,
    band: Optional[dict],
    assumptions: Optional[list] = None,
    notes: Optional[list] = None,
    inputs: Optional[dict] = None,
) -> dict:
    """One available benchmark result with its scenario band."""
    band = band or {}
    return {
        "benchmark": benchmark,
        "title": title,
        "quantity": quantity,
        "vintage": vintage,
        "level": level,
        "band": {s: band.get(s) for s in SCENARIOS},
        "classes": classes_for_band(band),
        "indeterminate": None,
        "assumptions": list(assumptions or []),
        "notes": list(notes or []),
        "inputs": dict(inputs or {}),
    }


def indeterminate_result(
    benchmark: str,
    title: str,
    quantity: str,
    vintage: str,
    level: str,
    reason: str,
    notes: Optional[list] = None,
    inputs: Optional[dict] = None,
) -> dict:
    """One indeterminate benchmark — a visible row with its reason (c1)."""
    row = result(benchmark, title, quantity, vintage, level, band=None, notes=notes, inputs=inputs)
    row["indeterminate"] = reason
    return row


def _band(low: float, base: float, high: float) -> dict:
    return {"low": low, "base": base, "high": high}


# ------------------------------------------------------------------
# Named query functions (ENG 2A) — the only I/O in this module.
# Each returns plain dicts; absent inputs are explicit, never zeros.
# ------------------------------------------------------------------

def metric_value(conn, source_id: str, metric_code: str) -> Optional[float]:
    """One probe-metric value from v_probe_latest (latest done run per
    source × metric); None when the metric was never recorded."""
    row = conn.execute(
        "SELECT value_numeric FROM v_probe_latest WHERE source_id=? AND metric_code=?",
        (source_id, metric_code),
    ).fetchone()
    return row[0] if row and row[0] is not None else None


def _staged_run(stg, source_id: str) -> Optional[str]:
    row = stg.execute(
        "SELECT MAX(run_key) FROM stg_register_product WHERE source_id=?", (source_id,)
    ).fetchone()
    return row[0] if row and row[0] else None


def ecat_refinement(stg, source_id: str = "AS-2") -> dict:
    """X1 — ECAT category breakdown + key-tier variant structure.

    Returns per-category row counts and the per-tier collapse factors
    (c2/tr6): rows ÷ distinct (manufacturer, key) for the EAN key
    (within the gtin-bearing subset), the name key, and the licence
    key (licence_number parsed from the staged raw JSON). The
    compression factor is the range across the measurable tiers —
    never a point. ``computed=False`` when the source is not staged
    or no staging DB is given.
    """
    if stg is None:
        return {"computed": False, "note": "no staging DB connected"}
    run_key = _staged_run(stg, source_id)
    if not run_key:
        return {"computed": False, "note": f"{source_id} not staged"}
    base = (
        "SELECT COUNT(*), COUNT(DISTINCT manufacturer_norm || '||' || ident_norm), "
        "COUNT(DISTINCT manufacturer_norm || '||' || name) "
        "FROM stg_register_product WHERE source_id=? AND run_key=?"
    )
    rows, ean_distinct, name_distinct = stg.execute(base, (source_id, run_key)).fetchone()
    ean_rows = stg.execute(
        "SELECT COUNT(*) FROM stg_register_product WHERE source_id=? AND run_key=? AND ident_type='gtin'",
        (source_id, run_key),
    ).fetchone()[0]
    ean_rows_distinct = stg.execute(
        "SELECT COUNT(DISTINCT manufacturer_norm || '||' || ident_norm) "
        "FROM stg_register_product WHERE source_id=? AND run_key=? AND ident_type='gtin'",
        (source_id, run_key),
    ).fetchone()[0]
    ean_names_distinct = stg.execute(
        "SELECT COUNT(DISTINCT manufacturer_norm || '||' || name) "
        "FROM stg_register_product WHERE source_id=? AND run_key=? AND ident_type='gtin'",
        (source_id, run_key),
    ).fetchone()[0]
    licences = set()
    for (raw,) in stg.execute(
        "SELECT raw FROM stg_register_product WHERE source_id=? AND run_key=? AND raw IS NOT NULL",
        (source_id, run_key),
    ):
        try:
            lic = json.loads(raw).get("licence_number")
        except (ValueError, AttributeError):
            lic = None
        if lic:
            licences.add(str(lic))
    categories = [
        dict(category=r[0], rows=r[1])
        for r in stg.execute(
            "SELECT COALESCE(category_raw, '(none)'), COUNT(*) FROM stg_register_product "
            "WHERE source_id=? AND run_key=? GROUP BY 1 ORDER BY 2 DESC",
            (source_id, run_key),
        )
    ]
    factors = {}
    if ean_rows and ean_rows_distinct:
        factors["ean"] = round(ean_rows / ean_rows_distinct, 3)
    if rows and name_distinct:
        factors["name"] = round(rows / name_distinct, 3)
    if rows and licences:
        factors["licence"] = round(rows / len(licences), 3)
    measurable = [v for v in factors.values() if v]
    compression = {
        "low": min(measurable),
        "high": max(measurable),
        "per_tier": factors,
        "measurable_tiers": sorted(factors),
    }
    if len(measurable) < 2:
        compression["note"] = "thin tier evidence — single-tier range, widen only with stated assumptions (c2)"
    return {
        "computed": True,
        "source_id": source_id,
        "run_key": run_key,
        "rows": rows,
        "ean_rows": ean_rows,
        "ean_distinct": ean_rows_distinct,
        "ean_names_distinct": ean_names_distinct,
        "name_distinct": name_distinct,
        "licence_distinct": len(licences),
        "categories": categories,
        "compression": compression,
    }


def pe_distribution(conn) -> dict:
    """X2 — PE products_listed distribution by channel (from the source
    register notes); sitemap_products rides along as the recon-floor
    context. All-zero/absent counts ⇒ ``products_listed_available``
    False — B4's PE calibration is explicitly absent, never a zero."""
    rows = []
    for r in conn.execute(
        "SELECT id, notes FROM source WHERE class_code='PE' AND active=1 ORDER BY id"
    ):
        channel = None
        for part in (r["notes"] or "").split(";"):
            part = part.strip()
            if part.startswith("channel="):
                channel = part.split("=", 1)[1]
        rows.append(
            {
                "source_id": r["id"],
                "channel": channel or "unmapped",
                "products_listed": metric_value(conn, r["id"], "products_listed"),
                "sitemap_products": metric_value(conn, r["id"], "sitemap_products"),
            }
        )
    by_channel = {}
    for row in rows:
        slot = by_channel.setdefault(row["channel"], {"sources": 0, "products_listed": 0})
        slot["sources"] += 1
        if row["products_listed"]:
            slot["products_listed"] += row["products_listed"]
    any_listed = any(row["products_listed"] for row in rows)
    return {
        "computed": True,
        "per_source": rows,
        "by_channel": by_channel,
        "products_listed_available": any_listed,
        "note": None if any_listed else "no staged products_listed values (walk idle since D31) — B4 falls back to extraction anchors",
    }


def dk_paint_counts(stg, source_id: str) -> dict:
    """X3 — staged Danish paint counts by category. Staging is detected
    from the document registry, so a staged-but-empty register stays
    distinguishable: it is a **counted-0** (c5: B2 must not scale from
    an empty base). A source never staged is an explicit absence."""
    run_key = stg.execute(
        "SELECT MAX(run_key) FROM stg_source_document WHERE source_id=?", (source_id,)
    ).fetchone()[0]
    if not run_key:
        return {"computed": False, "note": f"{source_id} not staged"}
    rows = stg.execute(
        "SELECT COUNT(*) FROM stg_register_product WHERE source_id=? AND run_key=?",
        (source_id, run_key),
    ).fetchone()[0]
    by_category = [
        dict(category=r[0], rows=r[1])
        for r in stg.execute(
            "SELECT COALESCE(category_raw, '(none)'), COUNT(*) FROM stg_register_product "
            "WHERE source_id=? AND run_key=? GROUP BY 1 ORDER BY 2 DESC",
            (source_id, run_key),
        )
    ]
    out = {"computed": True, "source_id": source_id, "run_key": run_key, "rows": rows, "by_category": by_category}
    if rows == 0:
        out["counted_zero"] = True
        out["note"] = "counted-0 semantics (c5) — an empty base is never scaled"
    total = sum(c["rows"] for c in by_category if c["category"] != "(none)")
    if by_category and total and total < rows // 2:
        out["note"] = (out.get("note") or "") + "sparse function-category column — B2 range widens with a missingness note (c6)".strip()
    return out


def comext_totals(stg) -> dict:
    """Staged Comext extra-EU sums (kg, EUR) + per-CN8 kg shares — B1
    context and B4's per-CN8 weighting (s(cn8), v0.2.2)."""
    row = stg.execute("SELECT SUM(kg), SUM(eur), COUNT(*) FROM stg_trade_cn8").fetchone()
    total_kg = row[0]
    per_cn8 = []
    if total_kg:
        per_cn8 = [
            dict(cn8=r[0], kg=r[1], share=round(r[1] / total_kg, 4))
            for r in stg.execute(
                "SELECT cn8, SUM(kg) FROM stg_trade_cn8 GROUP BY 1 ORDER BY 2 DESC"
            )
        ]
    return {"computed": bool(total_kg), "kg": total_kg, "eur": row[1], "trade_rows": row[2], "per_cn8": per_cn8}


# ------------------------------------------------------------------
# Benchmark computations (pure; X5). Uniform contract: a missing core
# input yields the visible indeterminate result (c1) — never a guess.
# Bands are products-counts; scenario order low/base/high.
# ------------------------------------------------------------------

def _span(low: float, high: float) -> dict:
    return _band(low, round((low + high) / 2), high)


# ------------------------------------------------------------------
# PHASE04 assembly (X5 wiring). DB inputs ride through the named
# query functions; everything else is a **method-sheet constant**
# (nu5 pattern): a dated extraction carried as a named module
# constant with its source — never a DB field (no legal referencing,
# D27), cited again in the report method sheet.
# ------------------------------------------------------------------

# EU paints & coatings tonnage — JRC AHWG 2024 discussion (accessed 2026-09-14).
TONNAGE_KG = (3.7e9, 4.2e9)
# Per-SKU throughput — flip assumption; the X4 abstracts did not pin it.
THROUGHPUT_KG_PER_SKU = (20_000, 40_000, 80_000)
# Population scales — Eurostat population 2024 (EU-27 449.2M).
SCALE_SE = 449.2 / 10.6
SCALE_DK = 449.2 / 5.89
# B2 scope corrections: SE PC base is voluntary + submission-level
# (upper envelope); DK register is hazardous-only, ≥100 kg/yr, with
# measured coverage 75–82% (NO analogue) and a paint-share band.
B2_SE_SCOPE = (0.6, 1.0)
B2_DK_SCOPE = (0.15 / 0.82, 0.25 / 0.75)
# B3 — tr10 assumption bands; SWD(2022) 435 Annex 16 provides neither
# a paint share nor a non-hazardous constant.
PCN_PAINT_SHARE = (0.10, 0.15, 0.20)
PCN_UPLIFT = (1.0, 2.0, 3.0)
# B4 assortment — long-tail replacement of the uniform ppp ≈107
# (strategy A4); mid-size mfr floor Tikkurila ≈190 SKUs (catalogue).
PPP_BAND = (25, 60, 150)
# B5 certified counts — JRC final report (DOI 10.2760/4572222):
# 36,960 products 03/2025; Commission facts 03/2026: 38,233.
CERTIFIED_COUNT = 36_960
AWARDED_COUNT = 38_233
# B5 penetration scenarios — JRC 2012 UK trade ≈30% upper bound;
# no official market share exists (SWD(2017) 253, JRC 2026 final).
PENETRATION = (0.05, 0.15, 0.30)
# Formulation-level compression (c2) — the shade-collapse band is an
# assumption: X1 measurable tiers (name 1.049×, EAN 1.266× on AS-2)
# do NOT capture shade-collapse; the 10× upper edge is the JRC AHWG
# variant claim. Pinned, flagged, never presented as measured.
COMPRESSION_ASSUMED = (1.0, 10.0)
# B6 out-of-pool sanity anchors (non-official aggregators;
# sanity-only, sanity anchors are floors, never central estimates).
# Only landscape-scale anchors carry a band; per-actor counts ride as
# labels — mixing scales into one span would fabricate a range.
B6_ANCHORS = [
    {
        "label": "US named-colour catalogs: 26,597 colours / 13 brands, ≈14,700 distinct after ΔE-dedup (Paint Color HQ 07/2026)",
        "band": (14_700, 26_597),
    },
    {
        "label": "one major manufacturer's DIY references, one country: >3,000 (AkzoNobel FR, daiteo case study)",
        "band": None,
    },
    {
        "label": "one major manufacturer's colour range: 3,500+ colours (Benjamin Moore, CoatingsTech 02/2021)",
        "band": None,
    },
]


def assemble(conn, stg) -> dict:
    """Wire the real inputs (DB + method-sheet constants) into the
    B1–B6 results, the vote tables and the dual-level verdict. DB
    reads via the named query functions; absent DB records flow
    through as visible indeterminates (c1), never zeros."""
    se = metric_value(conn, "ST-7", "products_registered")
    dk = metric_value(conn, "ST-6", "products_registered")
    pcn = metric_value(conn, "ST-1", "products_registered")
    producers = [
        v
        for v in (
            metric_value(conn, "AS-1", "producers_registered"),
            metric_value(conn, "ST-3", "producers_registered"),
        )
        if v is not None
    ]

    results = [
        compute_b1(TONNAGE_KG, THROUGHPUT_KG_PER_SKU, "2024 (JRC AHWG; accessed 2026-09-14)"),
        compute_b2(
            se, round(SCALE_SE, 1), tuple(round(s, 3) for s in B2_SE_SCOPE),
            "2022-09-15 (SE PC Echo, BfR-Akademie deck)",
            source_note="SE PC poison-centre submissions — voluntary-inclusive, upper envelope",
        ),
        compute_b2(
            dk, round(SCALE_DK, 1), tuple(round(s, 3) for s in B2_DK_SCOPE),
            "undated web figure (at.dk, accessed 2026-09-14)",
            source_note="DK total notified ≈40,000 — hazardous-only; paint split Power-BI-only (not extractable, D31)",
        ),
        compute_b3(pcn, PCN_PAINT_SHARE, PCN_UPLIFT, "2021 (SWD(2022) 435 Annex 16)"),
        compute_b4(producers or None, PPP_BAND, "2020 (SBS C2030) / 2026 (CEPE web)"),
        compute_b5(
            CERTIFIED_COUNT, PENETRATION, "03/2025 (JRC final report)", awarded_count=AWARDED_COUNT,
        ),
        compute_b6(B6_ANCHORS, "07/2026 (Paint Color HQ; CoatingsTech 02/2021)"),
    ]
    results[1]["benchmark"] = "B2-SE"
    results[2]["benchmark"] = "B2-DK"

    compression = {
        "low": COMPRESSION_ASSUMED[0],
        "high": COMPRESSION_ASSUMED[1],
        "measured": ecat_refinement(stg),
        "note": (
            "formulation-level conversion rides the pinned 1\u201310 shade-collapse band "
            "(assumption \u2014 not measurable from registry metadata)"
        ),
    }

    vote_sku = vote_table(results)
    verdict_sku = verdict(results, "sku")
    verdict_form = verdict(results, "formulation", compression)
    vote_formulation = {
        key: verdict_form[key]
        for key in ("rows", "tally", "available", "indeterminate_rows")
    }

    return {
        "constants": {
            "tonnage_kg": TONNAGE_KG,
            "throughput_kg_per_sku": THROUGHPUT_KG_PER_SKU,
            "scale_se": round(SCALE_SE, 1),
            "scale_dk": round(SCALE_DK, 1),
            "pcn_paint_share": PCN_PAINT_SHARE,
            "pcn_uplift": PCN_UPLIFT,
            "ppp_band": PPP_BAND,
            "certified_count": CERTIFIED_COUNT,
            "awarded_count": AWARDED_COUNT,
            "penetration": PENETRATION,
            "compression_assumed": COMPRESSION_ASSUMED,
        },
        "results": results,
        "compression": compression,
        "vote_sku": vote_sku,
        "verdict_sku": verdict_sku,
        "vote_formulation": vote_formulation,
        "verdict_formulation": verdict_form,
    }



def compute_b1(tonnage_kg, throughput_kg_per_sku, vintage: str) -> dict:
    """B1 tonnage-Fermi: EU paint tonnage ÷ per-SKU throughput
    scenarios. ``tonnage_kg`` = (low, high); ``throughput_kg_per_sku``
    = (low, base, high) — higher throughput ⇒ fewer SKUs."""
    if not tonnage_kg or not throughput_kg_per_sku:
        return indeterminate_result(
            "B1", "Tonnage-Fermi", "EU tonnage ÷ per-SKU throughput", vintage or "", "sku",
            "missing tonnage or per-SKU throughput input",
        )
    t_low, t_high = min(tonnage_kg), max(tonnage_kg)
    p_low, p_base, p_high = throughput_kg_per_sku
    return result(
        "B1", "Tonnage-Fermi", "EU tonnage ÷ per-SKU throughput", vintage, "sku",
        band=_band(t_low / p_high, round((t_low + t_high) / 2 / p_base), t_high / p_low),
        assumptions=[
            f"per-SKU throughput scenarios {p_low:g}–{p_high:g} kg/yr (base {p_base:g})",
            "throughput per SKU is the flip assumption — abstracts pin it (X4)",
        ],
        inputs={"tonnage_kg": [t_low, t_high], "throughput_kg_per_sku": [p_low, p_base, p_high]},
    )


def compute_b2(counts, scale: float, scope, vintage: str, source_note: str = "") -> dict:
    """B2 national-register scaling: staged paint count × population
    scale × scope-correction band. ``counts`` None ⇒ indeterminate
    (not staged); 0 ⇒ indeterminate (c5, never scale from zero)."""
    if counts is None:
        return indeterminate_result(
            "B2", "Register scaling", "national paint count × EU scale × scope", vintage or "", "sku",
            "no staged national register counts" + (f" ({source_note})" if source_note else ""),
        )
    if counts == 0:
        return indeterminate_result(
            "B2", "Register scaling", "national paint count × EU scale × scope", vintage or "", "sku",
            "counted-0 — an empty base is never scaled (c5)",
        )
    s_low, s_high = min(scope), max(scope)
    return result(
        "B2", "Register scaling", "national paint count × EU scale × scope", vintage, "sku",
        band=_span(counts * scale * s_low, counts * scale * s_high),
        assumptions=[f"population scale ×{scale:g}; scope correction ×{s_low:g}–{s_high:g}"],
        notes=[source_note] if source_note else [],
        inputs={"count": counts, "scale": scale, "scope": [s_low, s_high]},
    )


def compute_b3(pcn_mixtures, paint_share, uplift, vintage: str) -> dict:
    """B3 PCN mixture share: notified mixtures × paint share ×
    non-hazardous uplift band (tr10 — uplift stays an explicit
    assumption band unless an extraction yields a constant)."""
    if not pcn_mixtures:
        return indeterminate_result(
            "B3", "PCN mixture share", "notified mixtures × paint share × uplift", vintage or "", "sku",
            "missing PCN mixture count",
        )
    sh_low, sh_base, sh_high = paint_share
    u_low, u_base, u_high = uplift
    return result(
        "B3", "PCN mixture share", "notified mixtures × paint share × uplift", vintage, "sku",
        band=_band(
            pcn_mixtures * sh_low * u_low,
            round(pcn_mixtures * sh_base * u_base),
            pcn_mixtures * sh_high * u_high,
        ),
        assumptions=[
            f"paint share of notified mixtures {sh_low:g}–{sh_high:g} (base {sh_base:g})",
            f"non-hazardous uplift ×{u_low:g}–{u_high:g} (base {u_base:g}) — tr10 assumption band",
        ],
        inputs={"pcn_mixtures": pcn_mixtures, "paint_share": [sh_low, sh_base, sh_high], "uplift": [u_low, u_base, u_high]},
    )


def compute_b4(producer_count, ppp_band, vintage: str, per_cn8=None) -> dict:
    """B4 bottom-up: producer count × products-per-producer band (the
    long-tail replacement of the uniform ppp, strategy A4; PE
    calibration rides in ``ppp_band`` when staged)."""
    if not producer_count or not ppp_band:
        return indeterminate_result(
            "B4", "Bottom-up build-up", "producers × assortment", vintage or "", "both",
            "missing producer count or assortment band",
        )
    m_low, m_high = min(producer_count), max(producer_count)
    p_low, p_base, p_high = ppp_band
    return result(
        "B4", "Bottom-up build-up", "producers × assortment", vintage, "both",
        band=_band(m_low * p_low, round((m_low + m_high) / 2 * p_base), m_high * p_high),
        assumptions=[f"producer count {m_low:g}–{m_high:g}; products-per-producer {p_low:g}–{p_high:g} (base {p_base:g})"],
        inputs={"producer_count": [m_low, m_high], "ppp": [p_low, p_base, p_high], "per_cn8": per_cn8 or {}},
    )


def compute_b5(certified_count, penetration, vintage: str, awarded_count=None, probe=None) -> dict:
    """B5 ECAT-inverse: certified paint count ÷ label-penetration
    scenarios; the empirical ECAT∩DK probe (calibration-only) refines
    the band when available; ``awarded_count`` rides as the
    consistency column (tr8/T4 — supporting, never a gate)."""
    if not certified_count:
        return indeterminate_result(
            "B5", "ECAT-inverse", "certified count ÷ penetration", vintage or "", "both",
            "missing certified count",
        )
    if not penetration:
        return indeterminate_result(
            "B5", "ECAT-inverse", "certified count ÷ penetration", vintage or "", "both",
            "no penetration denominator (c1)",
        )
    p_low, p_base, p_high = penetration
    notes = []
    if probe:
        notes.append(f"empirical ECAT∩DK penetration probe {probe:.3f} (calibration-only)")
    return result(
        "B5", "ECAT-inverse", "certified count ÷ penetration", vintage, "both",
        band=_band(certified_count / p_high, round(certified_count / p_base), certified_count / p_low),
        assumptions=[f"penetration scenarios {p_low:g}–{p_high:g} (base {p_base:g}) — no official market share exists"],
        notes=notes,
        inputs={"certified_count": certified_count, "awarded_count": awarded_count, "penetration": [p_low, p_base, p_high], "probe": probe},
    )


def compute_b6(anchors, vintage: str) -> dict:
    """B6 literature sweep: out-of-pool sanity anchors. An empty anchor
    list is a **documented gap** — an indeterminate row, an acceptable
    outcome (tr10/design)."""
    if not anchors:
        return indeterminate_result(
            "B6", "Literature sweep", "out-of-pool sanity anchors", vintage or "", "both",
            "documented gap — no out-of-pool anchors found",
        )
    lows = [a["band"][0] for a in anchors if a.get("band")]
    highs = [a["band"][1] for a in anchors if a.get("band")]
    return result(
        "B6", "Literature sweep", "out-of-pool sanity anchors", vintage, "both",
        band=_span(min(lows), max(highs)),
        assumptions=[a["label"] for a in anchors],
        inputs={"anchors": anchors},
    )


# ------------------------------------------------------------------
# Synthesis (pure; X6) — vote table + verdict per the pinned rule.
# ------------------------------------------------------------------

def _base_classes(row: dict) -> set:
    return set(row["classes"]["base"]) if row.get("classes") else set()


def vote_table(results: list) -> dict:
    """Assemble the vote table: one row per benchmark (indeterminate
    rows visible, c1), per-class tally of base votes, vintage carried
    per row (c4)."""
    rows = [dict(r) for r in results]
    tally = {key: 0 for key in CLASS_KEYS}
    for row in rows:
        if row.get("indeterminate"):
            continue
        for key in _base_classes(row):
            if key in tally:
                tally[key] += 1
    available = [r for r in rows if not r.get("indeterminate")]
    return {
        "rows": rows,
        "available": len(available),
        "tally": tally,
        "indeterminate_rows": [r["benchmark"] for r in rows if r.get("indeterminate")],
    }


def _formulation_band(band: dict, compression: dict) -> Optional[dict]:
    """SKU band → formulation band via the compression-factor range
    (c2): ÷f_high for the low edge, ÷f_low for the high edge."""
    f_low, f_high = compression["low"], compression["high"]
    if not f_low or not f_high or band.get("low") is None:
        return None
    base = band.get("base")
    return _band(
        band["low"] / f_high,
        round(base / ((f_low + f_high) / 2)) if base is not None else None,
        band["high"] / f_low,
    )


def verdict(results: list, level: str = "sku", compression: Optional[dict] = None) -> dict:
    """The pinned rule (tr4) at one level. Formulation level converts
    sku-level rows through the compression range (c2); without a
    compression range the formulation verdict refuses visibly (c1)."""
    converted = []
    if level == "formulation" and not compression:
        return {
            "level": level, "verdict": "insufficient-basis", "class": None, "span": None,
            "confidence": None, "available": 0, "tally": {k: 0 for k in CLASS_KEYS},
            "indeterminate_rows": [], "divergences": [], "flip_assumptions": [],
            "reason": "compression factor unavailable \u2014 the formulation level refuses visibly (c1/c2)",
        }
    for row in results:
        row = dict(row)
        if level == "formulation" and row["level"] == "sku":
            fband = _formulation_band(row["band"], compression) if not row.get("indeterminate") else None
            if fband is None:
                if row.get("indeterminate"):
                    converted.append(row)
                    continue
                row["indeterminate"] = "band not convertible to the formulation level"
            else:
                row["band"] = fband
                row["classes"] = classes_for_band(fband)
                row["notes"] = list(row.get("notes", [])) + [
                    f"formulation level via compression factor \u00d7{compression['low']:g}\u2013{compression['high']:g} (c2)"
                ]
        elif row["level"] == "formulation" and level == "sku":
            continue
        converted.append(row)

    vote = vote_table(converted)
    out = {
        "level": level,
        "verdict": None,
        "class": None,
        "span": None,
        "confidence": None,
        "available": vote["available"],
        "tally": vote["tally"],
        "rows": vote["rows"],
        "indeterminate_rows": vote["indeterminate_rows"],
        "divergences": [],
        "flip_assumptions": [],
        "reason": None,
    }
    if vote["available"] < 3:
        out["verdict"] = "insufficient-basis"
        out["reason"] = f"only {vote['available']} of {len(converted)} benchmarks computable at the {level} level (c1)"
        return out

    top = max(vote["tally"].values())
    tied = sorted(key for key, n in vote["tally"].items() if n == top and n > 0)
    if not tied:
        out["verdict"] = "insufficient-basis"
        out["reason"] = "no base votes cast at this level (c1)"
        return out

    for row in converted:
        if row.get("indeterminate"):
            continue
        base = _base_classes(row)
        if len(base) == 1 and tied and list(base)[0] not in tied and not _adjacent(list(base)[0], tied[0]):
            out["divergences"].append({"benchmark": row["benchmark"], "base_classes": sorted(base)})

    if len(tied) == 1:
        out["verdict"] = tied[0]
        out["class"] = tied[0]
        if not out["divergences"]:
            out["confidence"] = CONFIDENCE_OK
        else:
            out["reason"] = (
                "divergent benchmark(s) exclusively compatible with a non-adjacent class — "
                "confidence withheld, open items recorded (tr4)"
            )
    else:
        out["verdict"] = "\u2013".join(tied)
        out["span"] = tied
        out["reason"] = "tie — span reported with flip assumptions, no confidence claim (c3)"
        for row in converted:
            if not row.get("indeterminate") and _base_classes(row) & set(tied):
                out["flip_assumptions"].extend(row.get("assumptions", []))
    return out


# ------------------------------------------------------------------
# Pure md renderers (c7 golden surface — no report-time state).
# ------------------------------------------------------------------

def _fmt(value) -> str:
    if value is None:
        return "\u2014"
    return f"{value:,.0f}"


def render_vote_table_md(vote: dict) -> str:
    """The class-vote table: rows = benchmarks (vintage + notes), the
    base class(es) with low\u2192high arrows, indeterminate rows visible (c1)."""
    lines = [
        "| # | Quantity | Vintage | Band (low\u2013high) | Base class(es) | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in vote["rows"]:
        if row.get("indeterminate"):
            lines.append(
                f"| {row['benchmark']} | {row['quantity']} | {row['vintage'] or '\u2014'} | \u2014 | \u2014 |"
                f" indeterminate: {row['indeterminate']} |"
            )
            continue
        base = ", ".join(sorted(_base_classes(row))) or "\u2014"
        band = row["band"]
        band_txt = f"{_fmt(band['low'])}\u2013{_fmt(band['high'])}"
        arrows = ""
        low_cls = row["classes"]["low"]
        high_cls = row["classes"]["high"]
        if low_cls and high_cls and (low_cls[0] != base or high_cls[0] != base):
            arrows = f" (\u2193{low_cls[0]} \u2191{high_cls[0]})"
        notes = "; ".join(list(row.get("notes", [])) + list(row.get("assumptions", [])))
        lines.append(
            f"| {row['benchmark']} | {row['quantity']} | {row['vintage'] or '\u2014'} | {band_txt} | {base}{arrows} | {notes} |"
        )
    return "\n".join(lines)


def render_verdict_md(vote: dict, verdict_dict: dict) -> str:
    """The verdict block: taxonomy, tally, verdict or its refusal (c1/c3)."""
    tally_txt = " \u00b7 ".join(f"{CLASS_LABELS[k]}: {vote['tally'][k]}" for k in CLASS_KEYS)
    lines = [f"Base-vote tally: {tally_txt}."]
    if verdict_dict["verdict"] == "insufficient-basis":
        lines.append(f"**Verdict: insufficient basis.** {verdict_dict['reason']}")
        if verdict_dict["indeterminate_rows"]:
            lines.append(f"Indeterminate benchmarks: {', '.join(verdict_dict['indeterminate_rows'])}.")
        return "\n\n".join(lines)
    if verdict_dict["span"]:
        label = " \u00b7 ".join(CLASS_LABELS[k] for k in verdict_dict["span"])
        label = f"span {label}"
    else:
        label = f"class {CLASS_LABELS[verdict_dict['class']]}"
    lines.append(f"**Verdict: {label}** at the {verdict_dict['level']} level.")
    if verdict_dict["confidence"]:
        lines.append(f"Confidence: {verdict_dict['confidence']} (\u22653 available benchmarks converge; no exclusive non-adjacent conflict).")
    elif verdict_dict["reason"]:
        lines.append(f"Confidence: not claimed \u2014 {verdict_dict['reason']}")
    if verdict_dict["span"]:
        lines.append("Flip assumptions: " + ("; ".join(verdict_dict["flip_assumptions"]) or "none recorded") + ".")
    if verdict_dict["divergences"]:
        div = ", ".join(f"{d['benchmark']} \u2192 {'/'.join(d['base_classes'])}" for d in verdict_dict["divergences"])
        lines.append(f"Divergent benchmarks (open items): {div}.")
    return "\n\n".join(lines)

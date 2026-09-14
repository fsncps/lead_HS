"""t13 — v0.2.3 benchmark + verdict-path tests (offline, synthetic).

Refinement queries pinned on synthetic distributions (hostile-QA:
distributions chosen to flip the compression factor — the outputs must
flip honestly); benchmark scenario arithmetic; confidence-rule unit
tests — convergence, exclusive-conflict, tie → span, <3 available →
"insufficient basis" (c1/c3); counted-0 → indeterminate B2 (c5); vote
table as a pure function with a rendering golden (c7); vintage
visibility (c4).
"""

import pytest

from leadhs import benchmarks as bm


# ------------------------------------------------------------------
# Class taxonomy (tr1: contiguous; sub-20k totals are visible "<a")
# ------------------------------------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [
        (19_999, "<a"),
        (20_000, "a"),
        (49_999, "a"),
        (50_000, "b"),
        (99_999, "b"),
        (100_000, "c"),
        (199_999, "c"),
        (200_000, "d"),
        (299_999, "d"),
        (300_000, "e"),
        (10_000_000, "e"),
    ],
)
def test_class_for_value_contiguous(value, expected):
    assert bm.class_for_value(value) == expected


# ------------------------------------------------------------------
# X1 refinement queries on synthetic distributions (hostile-QA)
# ------------------------------------------------------------------

def test_ecat_refinement_tier_factors(make_synthetic_staging):
    # 6 rows over 2 EANs, 3 names, 1 licence → factors ean=3, name=2,
    # licence=6; compression range [2, 6].
    stg, _ = make_synthetic_staging(ecat_groups=[(6, 2, 3, 1)])
    ref = bm.ecat_refinement(stg)
    assert ref["computed"] and ref["rows"] == 6
    assert ref["ean_rows"] == 6 and ref["ean_distinct"] == 2
    assert ref["name_distinct"] == 3 and ref["licence_distinct"] == 1
    assert ref["compression"]["per_tier"] == {"ean": 3.0, "name": 2.0, "licence": 6.0}
    assert ref["compression"]["low"] == 2.0 and ref["compression"]["high"] == 6.0


def test_ecat_refinement_hostile_flip(make_synthetic_staging):
    # Hostile distribution: 6 rows, 6 distinct EANs, 2 names — the EAN
    # and name factors flip ranking vs the friendly case; the range
    # must follow the data honestly (min 1 instead of 2).
    stg, _ = make_synthetic_staging(ecat_groups=[(6, 6, 2, 1)])
    ref = bm.ecat_refinement(stg)
    assert ref["compression"]["per_tier"]["ean"] == 1.0
    assert ref["compression"]["per_tier"]["name"] == 3.0
    assert ref["compression"]["low"] == 1.0 and ref["compression"]["high"] == 6.0
    assert ref["compression"]["measurable_tiers"] == ["ean", "licence", "name"]


def test_ecat_refinement_not_staged(make_synthetic_staging):
    stg, _ = make_synthetic_staging()
    ref = bm.ecat_refinement(stg)
    assert ref["computed"] is False


def test_metric_value_and_absence(make_synthetic_staging):
    _, ev = make_synthetic_staging(
        sources=[("AS-2", "AS", "ecat", [("products_identifiable", 17838.0)])]
    )
    assert bm.metric_value(ev, "AS-2", "products_identifiable") == 17838.0
    assert bm.metric_value(ev, "AS-2", "sitemap_products") is None


def test_pe_distribution_channel_sums_and_absence(make_synthetic_staging):
    stg, ev = make_synthetic_staging(
        sources=[
            ("PE-10", "PE", "channel=mfr; x", [("products_listed", 10.0)]),
            ("PE-11", "PE", "channel=mfr; x", [("products_listed", 5.0)]),
            ("PE-20", "PE", "channel=diy; x", []),
        ]
    )
    dist = bm.pe_distribution(ev)
    assert dist["computed"] and dist["products_listed_available"] is True
    assert dist["by_channel"]["mfr"] == {"sources": 2, "products_listed": 15.0}
    assert dist["by_channel"]["diy"] == {"sources": 1, "products_listed": 0}


def test_pe_distribution_all_absent_is_not_zero(make_synthetic_staging):
    _, ev = make_synthetic_staging(sources=[("PE-10", "PE", "channel=mfr; x", [])])
    dist = bm.pe_distribution(ev)
    assert dist["products_listed_available"] is False
    assert "walk idle" in dist["note"]


# ------------------------------------------------------------------
# X3 query guards (c5 counted-0, c6 sparse categories, absence)
# ------------------------------------------------------------------

def test_dk_paint_counts_zero_is_counted_zero(make_synthetic_staging):
    stg, _ = make_synthetic_staging(dk=("DK-1", []))
    dk = bm.dk_paint_counts(stg, "DK-1")
    assert dk["computed"] and dk["rows"] == 0
    assert dk["counted_zero"] is True and "c5" in dk["note"]


def test_dk_paint_counts_sparse_category_note(make_synthetic_staging):
    stg, _ = make_synthetic_staging(dk=("DK-1", [(4, 4, 4, 2)]))
    # 4 rows all in one synthetic category — not sparse. Force sparse:
    from leadhs import staging as stgmod

    stgmod.replace_products(
        stg, "DK-2", "synthetic-dk",
        {"url": "u", "doc_hash": "h-dk2", "retrieval_date": "2026-09-14"},
        [
            {"manufacturer_norm": "m", "ident_norm": f"n{i}", "ident_basis": "name", "name": f"n{i}", "category_raw": None}
            for i in range(3)
        ]
        + [{"manufacturer_norm": "m", "ident_norm": "p", "ident_basis": "name", "name": "p", "category_raw": "Paints"}],
    )
    dk = bm.dk_paint_counts(stg, "DK-2")
    assert dk["rows"] == 4 and "c6" in dk["note"]


def test_dk_paint_counts_not_staged(make_synthetic_staging):
    stg, _ = make_synthetic_staging()
    assert bm.dk_paint_counts(stg, "DK-1")["computed"] is False


def test_comext_totals(make_synthetic_staging):
    stg, _ = make_synthetic_staging(trade_rows=[("32081010", 750.0), ("32091000", 250.0)])
    cx = bm.comext_totals(stg)
    assert cx["computed"] and cx["kg"] == 1000.0
    assert cx["per_cn8"][0] == {"cn8": "32081010", "kg": 750.0, "share": 0.75}


# ------------------------------------------------------------------
# X5 compute functions — scenario arithmetic + c1 guards
# ------------------------------------------------------------------

def test_b1_scenario_arithmetic():
    row = bm.compute_b1((3.7e9, 4.2e9), (20_000.0, 40_000.0, 80_000.0), "2024 (JRC AHWG)")
    assert row["indeterminate"] is None
    assert row["band"]["low"] == pytest.approx(3.7e9 / 80_000)
    assert row["band"]["high"] == pytest.approx(4.2e9 / 20_000)
    assert row["band"]["base"] == pytest.approx(3.95e9 / 40_000)
    assert "b" == bm.class_for_value(row["band"]["base"])


def test_b1_missing_input_indeterminate():
    row = bm.compute_b1(None, (1.0, 2.0, 3.0), "")
    assert row["indeterminate"] and row["band"]["base"] is None


def test_b2_scaling_and_never_scale_from_zero():
    row = bm.compute_b2(10_000, 75.0, (0.8, 1.0), "09/2026")
    assert row["band"]["low"] == pytest.approx(10_000 * 75.0 * 0.8)
    assert row["band"]["high"] == pytest.approx(10_000 * 75.0 * 1.0)
    zero = bm.compute_b2(0, 75.0, (0.8, 1.0), "")
    assert zero["indeterminate"] and "c5" in zero["indeterminate"]
    absent = bm.compute_b2(None, 75.0, (0.8, 1.0), "")
    assert absent["indeterminate"]


def test_b3_share_uplift_band():
    row = bm.compute_b3(1.4e6, (0.10, 0.15, 0.20), (1.0, 2.0, 3.0), "2021 (SWD(2022) 435)")
    assert row["band"]["low"] == pytest.approx(1.4e6 * 0.10 * 1.0)
    assert row["band"]["high"] == pytest.approx(1.4e6 * 0.20 * 3.0)
    assert row["band"]["base"] == pytest.approx(1.4e6 * 0.15 * 2.0)
    assert any("tr10" in a for a in row["assumptions"])


def test_b4_bottom_up_band():
    row = bm.compute_b4((800, 3200), (25.0, 60.0, 150.0), "2026")
    assert row["band"]["low"] == pytest.approx(800 * 25.0)
    assert row["band"]["high"] == pytest.approx(3200 * 150.0)


def test_b5_inverse_penetration_and_probe_note():
    row = bm.compute_b5(38_233, (0.05, 0.15, 0.30), "03/2026", probe=0.08)
    assert row["band"]["low"] == pytest.approx(38_233 / 0.30)
    assert row["band"]["base"] == pytest.approx(round(38_233 / 0.15))
    assert row["band"]["high"] == pytest.approx(38_233 / 0.05)
    assert any("calibration-only" in n for n in row["notes"])
    no_pen = bm.compute_b5(38_233, None, "")
    assert no_pen["indeterminate"] and "c1" in no_pen["indeterminate"]


def test_b6_documented_gap_is_indeterminate():
    row = bm.compute_b6([], "2026")
    assert row["indeterminate"] and "documented gap" in row["indeterminate"]
    row2 = bm.compute_b6([{"label": "US count", "band": (500_000, 900_000)}], "2026")
    assert row2["band"]["high"] == 900_000


# ------------------------------------------------------------------
# X6 synthesis — the pinned confidence rule (tr4) and its refusals
# ------------------------------------------------------------------

def _r(bench, low, base, high, **kw):
    return bm.result(
        bench, kw.get("title", bench), "quantity", kw.get("vintage", "2026"),
        kw.get("level", "sku"), band={"low": low, "base": base, "high": high},
        assumptions=kw.get("assumptions", ["flip: none"]),
    )


def test_vote_convergence_confident():
    rows = [_r("B1", 90_000, 120_000, 150_000), _r("B3", 100_000, 140_000, 190_000),
            _r("B4", 95_000, 130_000, 180_000), _r("B5", 110_000, 160_000, 195_000)]
    v = bm.verdict(rows)
    assert v["verdict"] == "c" and v["confidence"] == bm.CONFIDENCE_OK
    assert v["tally"]["c"] == 4


def test_vote_adjacent_single_vote_keeps_confidence():
    rows = [_r("B1", 10_000, 120_000, 200_000), _r("B3", 100_000, 140_000, 190_000),
            _r("B4", 95_000, 130_000, 180_000)]
    v = bm.verdict(rows)
    assert v["verdict"] == "c" and v["confidence"] == bm.CONFIDENCE_OK


def test_vote_insufficient_basis_with_visible_rows():
    rows = [_r("B1", 90_000, 120_000, 150_000), _r("B3", 100_000, 140_000, 190_000)]
    ind = bm.indeterminate_result("B5", "ECAT-inverse", "q", "2026", "both", "no penetration denominator (c1)")
    v = bm.verdict(rows + [ind, bm.compute_b6([], "2026")])
    assert v["verdict"] == "insufficient-basis"
    assert v["available"] == 2
    assert "B5" in v["indeterminate_rows"] and "B6" in v["indeterminate_rows"]


def test_vote_tie_renders_span_without_confidence():
    rows = [_r("B1", 60_000, 80_000, 90_000), _r("B3", 60_000, 85_000, 90_000),
            _r("B4", 110_000, 120_000, 190_000), _r("B5", 110_000, 130_000, 190_000)]
    v = bm.verdict(rows)
    assert v["span"] == ["b", "c"]
    assert v["verdict"] == "b\u2013c"
    assert v["confidence"] is None and "c3" in v["reason"]
    assert v["flip_assumptions"] == ["flip: none"] * 4


def test_vote_exclusive_conflict_withholds_confidence():
    rows = [_r("B1", 100_000, 120_000, 150_000), _r("B3", 100_000, 140_000, 190_000),
            _r("B4", 95_000, 130_000, 180_000), _r("B2", 20_000, 25_000, 45_000)]
    v = bm.verdict(rows)
    assert v["verdict"] == "c" and v["confidence"] is None
    assert v["divergences"] == [{"benchmark": "B2", "base_classes": ["a"]}]


def test_formulation_level_applies_compression():
    rows = [_r("B1", 90_000, 150_000, 270_000, level="sku"),
            _r("B3", 120_000, 150_000, 200_000, level="sku"),
            _r("B4", 60_000, 100_000, 180_000, level="both")]
    compression = {"low": 3.0, "high": 9.0}
    v = bm.verdict(rows, level="formulation", compression=compression)
    assert v["available"] == 3
    b1 = next(r for r in v["rows"] if r["benchmark"] == "B1")
    assert b1["band"]["low"] == pytest.approx(90_000 / 9.0)
    assert b1["band"]["high"] == pytest.approx(270_000 / 3.0)
    assert any("c2" in n for n in b1["notes"])


def test_formulation_level_without_compression_refuses():
    rows = [_r("B1", 90_000, 150_000, 270_000), _r("B3", 120_000, 150_000, 200_000)]
    v = bm.verdict(rows, level="formulation", compression=None)
    assert v["verdict"] == "insufficient-basis"
    assert "c1" in v["reason"] and "compression" in v["reason"]


# ------------------------------------------------------------------
# Renderers — vintage visibility (c4) + golden (c7)
# ------------------------------------------------------------------

def _fixture_vote():
    rows = [
        _r("B1", 90_000, 120_000, 150_000, vintage="2024 (JRC AHWG)"),
        bm.indeterminate_result("B5", "ECAT-inverse", "certified ÷ penetration", "03/2026", "both", "no penetration denominator (c1)"),
    ]
    vote = bm.vote_table(rows)
    verdict = bm.verdict(rows)
    return vote, verdict


def test_render_vote_table_golden():
    vote, _ = _fixture_vote()
    expected = "\n".join(
        [
            "| # | Quantity | Vintage | Band (low–high) | Base class(es) | Notes |",
            "|---|---|---|---|---|---|",
            "| B1 | quantity | 2024 (JRC AHWG) | 90,000–150,000 | c (↓b ↑c) | flip: none |",
            "| B5 | certified ÷ penetration | 03/2026 | — | — | indeterminate: no penetration denominator (c1) |",
        ]
    )
    assert bm.render_vote_table_md(vote) == expected


def test_render_verdict_insufficient_basis_lists_rows():
    vote, verdict = _fixture_vote()
    md = bm.render_verdict_md(vote, verdict)
    assert "insufficient basis" in md
    assert "B5" in md  # indeterminate rows never silently dropped (c1)


def test_render_verdict_confident():
    rows = [_r("B1", 90_000, 120_000, 150_000), _r("B3", 100_000, 140_000, 190_000),
            _r("B4", 95_000, 130_000, 180_000)]
    vote, verdict = bm.vote_table(rows), bm.verdict(rows)
    md = bm.render_verdict_md(vote, verdict)
    assert "class 100k–200k" in md
    assert bm.CONFIDENCE_OK in md

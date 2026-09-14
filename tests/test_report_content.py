"""od8 report content tests (t8) as amended by D28 (product-first,
U11–U13): the two numbers lead, product-first summary matrix, execution
log incl. blocked/failed + notes, dry-run exclusion, "—" vs 0, compact
per-source blocks with category paths, csv = matrix only, json full
structure."""

import csv
import io
import json
import re

from leadhs import report as reportmod
from leadhs.probe import engine
from leadhs.source import get_source


def _run(loaded_conn, store, fetcher, sid, **kw):
    return engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, sid), **kw)


def _setup(loaded_conn, store, fetcher):
    """done + blocked + failed corpus."""
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    _run(loaded_conn, store, fetcher, "PX-2")   # robots deny -> blocked
    _run(loaded_conn, store, fetcher, "CX-4")   # 500 -> failed


def test_title_framing_legend(loaded_conn, store, fetcher):
    _setup(loaded_conn, store, fetcher)
    md = reportmod.render(loaded_conn, format="md")
    assert reportmod.TITLE in md
    assert "never a market total" in md  # Q1 floor framing (D28)
    assert "volume context" in md  # trade rows demoted (D28 grain rule)
    assert "source-feasibility metrics only" in md
    assert "product data only" in md
    assert "M2+" in md  # product/lead prevalence never implied
    for line in reportmod.LEGEND:
        assert line in md


def _db_ids(loaded_conn):
    return [r[0] for r in loaded_conn.execute("SELECT id FROM source ORDER BY id").fetchall()]


def _matrix_csv(loaded_conn, **kw):
    """v0.2.2 PHASE06: the csv is the matrix block FIRST, then the
    landscape section blocks — the matrix block ends at the blank line."""
    out = reportmod.render(loaded_conn, format="csv", **kw)
    parts = re.split(r"\r?\n\r?\n", out, maxsplit=1)
    return parts[0], out


def test_matrix_covers_all_registered_sources_incl_inactive(loaded_conn, store, fixture_register):
    matrix, _full = _matrix_csv(loaded_conn)
    rows = list(csv.DictReader(io.StringIO(matrix)))
    assert [r["source_id"] for r in rows] == _db_ids(loaded_conn)
    st1 = next(r for r in rows if r["source_id"] == "ST-1")
    assert st1["active"] == "0"
    assert st1["catalog_count"] == "\u2014" and st1["status"] == "\u2014"


def test_n1_n2_n3_numbers_lead(loaded_conn, store, fetcher):
    """nu4/nu5: the numbers blocks lead the md report; N2/N3 tiers;
    explicit zero-states (never a bare 0)."""
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    md = reportmod.render(loaded_conn, format="md")
    assert "## N1 — market-size anchors" in md
    assert "no counted sources yet" in md  # zero-state line
    assert "## N2/N3 — access coverage" in md
    # PX-1 is active with a done run and no counted metric -> tier (c)
    assert "| c | visible, uncounted without scraping | PX-1 | 1 |" in md
    assert "manual-web records pending" in md  # N3 zero-state
    assert "Excluded-and-counted" not in md  # nothing inactive-and-counted here


def test_execution_log_incl_blocked_and_failed_with_notes(loaded_conn, store, fetcher):
    _setup(loaded_conn, store, fetcher)
    md = reportmod.render(loaded_conn, format="md")
    assert "## Execution log" in md
    assert "| source | run_key | status | started | finished | notes |" in md
    assert "| PX-2 |" in md and "blocked" in md
    assert "| CX-4 |" in md and "failed" in md
    # notes visible (engine writes the reason into run.notes)
    assert "robots.txt disallows" in md or "HTTP 500 after retries" in md


def test_dash_vs_zero_distinction(loaded_conn, store, fetcher):
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    rows = {r["source_id"]: r for r in csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv")))}
    # queried and empty -> 0 (grundierung category contributes one 0 row; the
    # matrix shows the first category_count row = wandfarben = 2, unit cited)
    assert rows["PX-1"]["category_count"] == "2 count"
    # D28 walk metrics (numeric, no unit on the budget flag)
    assert rows["PX-1"]["products_listed"] == "6 count"
    assert rows["PX-1"]["doc_links_seen"] == "1 count"
    assert rows["PX-1"]["walk_budget_exhausted"] == "0"
    # never queried -> em-dash
    assert rows["ST-1"]["records_hs3208"] == "\u2014"
    assert rows["ST-1"]["status"] == "\u2014"


def test_compact_blocks_list_category_paths(loaded_conn, store, fetcher):
    """U11: compact per-source blocks; access metadata is one line;
    duplicate category_count rows stay visible with their paths (R4)."""
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    md = reportmod.render(loaded_conn, format="md")
    assert "- identity: class PE · active yes" in md
    assert "- access: robots allowed" in md
    assert "- content: format" in md
    assert "categories: /cat/wandfarben=2, /cat/grundierung=0" in md
    assert "walk budget: within budget" in md


def test_dry_run_only_db_shows_no_runs(loaded_conn, store, fetcher):
    _run(loaded_conn, store, fetcher, "PX-1", dry_run=True)
    md = reportmod.render(loaded_conn, format="md")
    assert reportmod.NO_RUNS_LINE in md
    rows = {r["source_id"]: r for r in csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv")))}
    assert rows["PX-1"]["status"] == "\u2014"
    assert rows["PX-1"]["catalog_count"] == "\u2014"


def test_metric_values_cite_run_key(loaded_conn, store, fetcher):
    summary = _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    md = reportmod.render(loaded_conn, format="md")
    assert summary["run_key"] in md  # cited in compact blocks + matrix last-run column


def test_csv_matrix_first_then_landscape_blocks(loaded_conn, store, fetcher):
    """v0.2.2 PHASE06 (supersedes the D28 matrix-only csv contract):
    matrix block first, landscape sections appended after a blank line."""
    matrix, full = _matrix_csv(loaded_conn)
    lines = matrix.splitlines()
    assert lines[0].split(",") == reportmod._MATRIX_HEADER + list(reportmod.CAPABILITY_METRICS) + ["real_product_source"]
    assert len(lines) == 1 + len(_db_ids(loaded_conn))
    assert "anchor" not in matrix.lower()
    # the landscape block carries the funnel + reconciliation sections
    assert "section,key,subkey,value" in full
    assert "funnel,q1" in full.replace('"', "")


def test_json_full_structure(loaded_conn, store, fetcher):
    _setup(loaded_conn, store, fetcher)
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    assert set(data) == {"report", "numbers", "anchors", "capability", "landscape", "sources", "anchor_candidates", "source_activity"}
    assert data["report"]["title"] == reportmod.TITLE
    # nu5: json carries anchor values, never a computed N1 range
    assert "range" not in json.dumps(data["numbers"])
    # tier dicts + excluded-source lists + zero-states ride "numbers"
    assert set(data["numbers"]["tier_sizes"]) == {"a", "b", "c", "d"}
    assert "excluded_counted" in data["numbers"] and "zero_states" in data["numbers"]
    px1 = next(s for s in data["sources"] if s["id"] == "PX-1")
    assert px1["run"]["status"] == "done"
    assert px1["tier"] == "c"
    assert px1["matrix"]["catalog_count"] != "\u2014"
    assert px1["matrix"]["products_listed"] != "\u2014"
    assert set(px1["sections"]) == set(reportmod.SECTIONS)
    assert "robots" in px1["access_line"] and "categories:" in px1["counts_line"]
    px2 = next(s for s in data["sources"] if s["id"] == "PX-2")
    assert px2["run"]["status"] == "blocked" and px2["run"]["notes"]


# --- v0.2.0 nu4/nu5: numbers-first layout (t10) ----------------------------


def _record(loaded_conn, store, sid, metric, value, **kw):
    from leadhs.probe import engine

    return engine.record_manual(loaded_conn, store, sid, metric, value=value, **kw)


def test_tier_a_and_b_derivation_with_n2_sum(loaded_conn, store, fetcher):
    """(a) products_registered on an active source, (b) sitemap_products,
    (c) done run without counted metrics; N2 = Σ tier (a)+(b); inactive
    rows never summed."""
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)          # tier b (after record)
    _run(loaded_conn, store, fetcher, "CX-1")                      # tier c
    _record(loaded_conn, store, "SX-1", "products_registered", "42")   # tier a
    _record(loaded_conn, store, "PX-1", "sitemap_products", "5")       # tier b
    md = reportmod.render(loaded_conn, format="md")
    assert "| a | dataset/register access counted | SX-1 | 1 |" in md
    assert "| b | sitemap-visible counted | PX-1 | 1 |" in md
    assert "| c | visible, uncounted without scraping | CX-1 | 1 |" in md
    assert "N2 (Σ tier a+b counts): 47" in md
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    assert data["numbers"]["n2_total"] == 47.0
    assert data["numbers"]["tier_sizes"] == {"a": 1, "b": 1, "c": 1, "d": 12}


def test_excluded_and_counted_line(loaded_conn, store, fetcher):
    """i14 semantics carried: inactive sources with counts are listed,
    never summed."""
    _record(loaded_conn, store, "ST-1", "products_registered", "7")  # inactive
    md = reportmod.render(loaded_conn, format="md")
    assert "Excluded-and-counted" in md and "ST-1" in md
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    assert data["numbers"]["excluded_counted"] == ["ST-1"]
    assert data["numbers"]["n2_total"] is None  # the inactive count is not summed


def test_n1_anchor_block_md_and_json(loaded_conn, store, fetcher):
    """nu5: anchors render DB-cited (source/value/unit/run_key); json
    carries anchor values, never a computed range."""
    summary = _record(loaded_conn, store, "CX-3", "trade_kg_hs3208", "123.5", unit="kg",
                      note="flow=IMP, year=2024, indicators=QUANTITY_IN_100KG; sum across partners")
    md = reportmod.render(loaded_conn, format="md")
    assert "| CX-3 | EU imports HS 3208 (kg) | 123.5 | kg |" in md
    assert "N1 method sheet" in md and "estimate" in md
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    anchor = next(a for a in data["anchors"] if a["metric_code"] == "trade_kg_hs3208")
    assert anchor["value_numeric"] == 123.5 and anchor["run_key"] == summary["run_key"]


def test_trade_and_priors_lines(loaded_conn, store, fetcher):
    _record(loaded_conn, store, "CX-3", "trade_kg_hs3208", "123.5", unit="kg",
            note="flow=IMP, year=2024, indicators=QUANTITY_IN_100KG; sum across partners; top partners: DE=90, FR=20")
    _record(loaded_conn, store, "SX-1", "products_registered", "42")
    md = reportmod.render(loaded_conn, format="md")
    assert "trade context: trade_kg_hs3208: 123.5 kg (year=2024; top: DE=90, FR=20)" in md
    assert "priors: products_registered=42 [" in md


def test_csv_json_column_gains(loaded_conn, store, fetcher):
    rows = list(csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv"))))
    expected_new = {"tier", "sitemap_products", "sds_library_visible", "products_registered",
                    "producers_registered", "trade_kg_hs3208", "trade_eur_hs3208",
                    "trade_kg_hs3209", "trade_eur_hs3209", "census_status"}
    assert expected_new <= set(rows[0])
    assert rows[0]["tier"] == "\u2014" or rows[0]["tier"]


def test_census_status_plain_column(loaded_conn, store, fetcher):
    """V4: census_status rides the matrix plain (no walk column)."""
    from leadhs.probe import engine

    engine.record_manual(loaded_conn, store, "PX-2", "census_status",
                         value_text="blocked: 403 wall; manual fallback documented (D4)")
    rows = {r["source_id"]: r for r in csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv")))}
    assert "manual fallback" in rows["PX-2"]["census_status"]


def test_access_decision_bridge(loaded_conn, store, fetcher):
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    _run(loaded_conn, store, fetcher, "PX-2")  # robots deny -> blocked
    md = reportmod.render(loaded_conn, format="md")
    assert "Access-decision bridge" in md
    assert "PX-1" in md.split("## Execution log")[0].split("Access-decision bridge")[1]


# --- v0.2.1: capability profile + N2 numerator (t11, cap3/i18) --------------


def _capability_run(loaded_conn, store, fetcher, sid, mode="capability"):
    """A capability-mode run over a fixture AS source (reg.csv: mfr +
    ident + cn_code) via the AS adapter."""
    return engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, sid),
                          mode=mode, sample_n=3)


def _cap_record(loaded_conn, store, sid, metric, value=None, value_text=None):
    return engine.record_manual(loaded_conn, store, sid, metric, value=value,
                                value_text=value_text, mode="capability")


def test_capability_matrix_section_and_predicate(loaded_conn, store, fetcher):
    """cap3/C3: the capability matrix renders; a full register passes the
    predicate; the N2 numerator sums the real-product sources."""
    _capability_run(loaded_conn, store, fetcher, "AX-1")  # full CSV register
    md = reportmod.render(loaded_conn, format="md")
    assert "## Capability profile" in md
    assert "N2 numerator (official registers, floor)" in md
    assert "| AX-1 | AS | 1 |" in md
    assert "| yes |" in md  # the AX-1 row ends real-product-source = yes
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    ax1 = next(c for c in data["capability"]["matrix"] if c["source_id"] == "AX-1")
    assert ax1["real_product_source"] is True
    assert ax1["metrics"]["products_identifiable"] == "3 count"
    assert data["capability"]["numerator"]["total"] == 3.0
    assert data["capability"]["numerator"]["components"][0]["source_id"] == "AX-1"


def test_predicate_fails_on_each_axis(loaded_conn, store, fetcher):
    """C3: the predicate is false on each failing axis — manufacturer=0,
    product_ident=0, linkage='none', depth<2. Each is a separate manual
    capability record; the source must not sum into the numerator."""
    _cap_record(loaded_conn, store, "ST-1", "products_identifiable", value="5")
    # manufacturer=0
    _cap_record(loaded_conn, store, "ST-1", "cap_manufacturer", value="0")
    _cap_record(loaded_conn, store, "ST-1", "cap_product_ident", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_cn8_linkage", value_text="category")
    _cap_record(loaded_conn, store, "ST-1", "cap_depth_tier", value="2")
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    st1 = next(c for c in data["capability"]["matrix"] if c["source_id"] == "ST-1")
    assert st1["real_product_source"] is False
    assert data["capability"]["numerator"]["total"] is None


def test_predicate_requires_all_four(loaded_conn, store, fetcher):
    """C3: manufacturer=1, product_ident=1, linkage != 'none', depth >= 2
    — all four hold => real product source."""
    _cap_record(loaded_conn, store, "ST-1", "products_identifiable", value="5")
    _cap_record(loaded_conn, store, "ST-1", "cap_manufacturer", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_product_ident", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_cn8_linkage", value_text="prodcom")
    _cap_record(loaded_conn, store, "ST-1", "cap_depth_tier", value="2")
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    st1 = next(c for c in data["capability"]["matrix"] if c["source_id"] == "ST-1")
    assert st1["real_product_source"] is True
    assert data["capability"]["numerator"]["total"] == 5.0
    assert data["capability"]["numerator"]["components"][0]["source_id"] == "ST-1"


def test_linkage_none_fails_predicate(loaded_conn, store, fetcher):
    _cap_record(loaded_conn, store, "ST-1", "products_identifiable", value="5")
    _cap_record(loaded_conn, store, "ST-1", "cap_manufacturer", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_product_ident", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_cn8_linkage", value_text="none")
    _cap_record(loaded_conn, store, "ST-1", "cap_depth_tier", value="2")
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    st1 = next(c for c in data["capability"]["matrix"] if c["source_id"] == "ST-1")
    assert st1["real_product_source"] is False
    assert data["capability"]["numerator"]["total"] is None


def test_depth_tier_below_2_fails_predicate(loaded_conn, store, fetcher):
    _cap_record(loaded_conn, store, "ST-1", "products_identifiable", value="5")
    _cap_record(loaded_conn, store, "ST-1", "cap_manufacturer", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_product_ident", value="1")
    _cap_record(loaded_conn, store, "ST-1", "cap_cn8_linkage", value_text="category")
    _cap_record(loaded_conn, store, "ST-1", "cap_depth_tier", value="1")
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    st1 = next(c for c in data["capability"]["matrix"] if c["source_id"] == "ST-1")
    assert st1["real_product_source"] is False
    assert data["capability"]["numerator"]["total"] is None


def test_capability_run_not_in_existing_execution_log(loaded_conn, store, fetcher):
    """A1: a capability run does NOT surface as the source's latest
    census/recon run (its own fetch is separate), so the existing tier
    logic is untouched."""
    _capability_run(loaded_conn, store, fetcher, "AX-1")
    rows = {r["source_id"]: r for r in csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv")))}
    assert rows["AX-1"]["status"] == "\u2014"  # no census/recon run -> tier dash
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    ax1 = next(c for c in data["capability"]["matrix"] if c["source_id"] == "AX-1")
    assert ax1["status"] == "done"  # but its capability run IS recorded
    assert ax1["run_key"] != "\u2014"


def test_certified_subset_caveat_line(loaded_conn, store, fetcher):
    _capability_run(loaded_conn, store, fetcher, "AX-1")
    md = reportmod.render(loaded_conn, format="md")
    assert "Preliminary N2 numerator (official registers, floor)" in md
    assert "certified/declared subsets" in md
    assert "never a market total" in md


def test_csv_capability_columns_added(loaded_conn, store, fetcher):
    _capability_run(loaded_conn, store, fetcher, "AX-1")
    rows = {r["source_id"]: r for r in csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv")))}
    expected = set(reportmod.CAPABILITY_METRICS) | {"real_product_source"}
    assert expected <= set(next(csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv")))))
    assert rows["AX-1"]["products_identifiable"] == "3 count"
    assert rows["AX-1"]["cap_manufacturer"] == "1"
    assert rows["AX-1"]["cap_cn8_linkage"] == "category"
    assert rows["AX-1"]["real_product_source"] == "1"

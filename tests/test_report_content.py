"""od8 report content tests (t8) as amended by D28 (product-first,
U11–U13): the two numbers lead, product-first summary matrix, execution
log incl. blocked/failed + notes, dry-run exclusion, "—" vs 0, compact
per-source blocks with category paths, csv = matrix only, json full
structure."""

import csv
import io
import json

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


def test_matrix_covers_all_registered_sources_incl_inactive(loaded_conn, store, fixture_register):
    rows = list(csv.DictReader(io.StringIO(reportmod.render(loaded_conn, format="csv"))))
    assert [r["source_id"] for r in rows] == _db_ids(loaded_conn)
    st1 = next(r for r in rows if r["source_id"] == "ST-1")
    assert st1["active"] == "0"
    assert st1["catalog_count"] == "\u2014" and st1["status"] == "\u2014"


def test_two_numbers_lead(loaded_conn, store, fetcher):
    """U11/D28: the two study numbers lead the md report."""
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    md = reportmod.render(loaded_conn, format="md")
    assert "## The two numbers" in md
    assert "products listed (Q1)" in md and "doc links seen (Q2)" in md
    # PX-1: 6 distinct product links (4 landing + 2 wandfarben);
    # 1 distinct SDS link URL seen on the sampled product pages.
    assert "| PX-1 | PE | 1 | done | 6 count | 1 count |" in md


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


def test_csv_is_matrix_only(loaded_conn, store, fetcher):
    _setup(loaded_conn, store, fetcher)
    out = reportmod.render(loaded_conn, format="csv")
    lines = out.splitlines()
    assert lines[0].split(",") == reportmod._MATRIX_HEADER
    assert len(lines) == 1 + len(_db_ids(loaded_conn))
    assert "anchor" not in out.lower()


def test_json_full_structure(loaded_conn, store, fetcher):
    _setup(loaded_conn, store, fetcher)
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    assert set(data) == {"report", "sources", "anchor_candidates", "source_activity"}
    assert data["report"]["title"] == reportmod.TITLE
    px1 = next(s for s in data["sources"] if s["id"] == "PX-1")
    assert px1["run"]["status"] == "done"
    assert px1["matrix"]["catalog_count"] != "\u2014"
    assert px1["matrix"]["products_listed"] != "\u2014"
    assert set(px1["sections"]) == set(reportmod.SECTIONS)
    assert "robots" in px1["access_line"] and "categories:" in px1["counts_line"]
    px2 = next(s for s in data["sources"] if s["id"] == "PX-2")
    assert px2["run"]["status"] == "blocked" and px2["run"]["notes"]

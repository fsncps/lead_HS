"""od8 report content tests (t8): framing/title, summary matrix incl.
inactive sources, run status incl. blocked/failed + notes, dry-run
exclusion, "—" vs 0, duplicate category_count rows, csv = matrix only,
json full structure."""

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


def test_run_status_incl_blocked_and_failed_with_notes(loaded_conn, store, fetcher):
    _setup(loaded_conn, store, fetcher)
    md = reportmod.render(loaded_conn, format="md")
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
    # never queried -> em-dash
    assert rows["ST-1"]["records_hs3208"] == "\u2014"
    assert rows["ST-1"]["status"] == "\u2014"


def test_duplicate_category_count_rows_listed(loaded_conn, store, fetcher):
    _run(loaded_conn, store, fetcher, "PX-1", sample_n=3)
    md = reportmod.render(loaded_conn, format="md")
    # both same-run rows listed in full; path carried in notes (R4 strict)
    section_rows = [ln for ln in md.splitlines() if ln.startswith("| category_count |")]
    assert len(section_rows) == 2
    assert "category path: /cat/wandfarben" in md
    assert "category path: /cat/grundierung" in md


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
    assert summary["run_key"] in md  # cited in sections + matrix last-run column


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
    assert set(px1["sections"]) == set(reportmod.SECTIONS)
    px2 = next(s for s in data["sources"] if s["id"] == "PX-2")
    assert px2["run"]["status"] == "blocked" and px2["run"]["notes"]

"""Views: v_probe_latest (latest done run wins; blocked/aborted never
shadow), v_anchor_candidates, v_source_activity."""

from leadhs import db as dbmod
from leadhs.probe import engine


def _run(loaded_conn, store, fetcher, sid):
    from leadhs.source import get_source

    return engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, sid), sample_n=1)


def test_latest_done_run_wins(loaded_conn, store, fetcher, monkeypatch):
    s1 = _run(loaded_conn, store, fetcher, "PX-1")
    first = dict(loaded_conn.execute(
        "SELECT metric_code, run_key FROM v_probe_latest WHERE metric_code='catalog_count'"
    ).fetchone())
    assert first["run_key"] == s1["run_key"]

    # a second done run shadows the first
    s2 = _run(loaded_conn, store, fetcher, "PX-1")
    now_latest = dict(loaded_conn.execute(
        "SELECT metric_code, run_key FROM v_probe_latest WHERE metric_code='catalog_count'"
    ).fetchone())
    assert now_latest["run_key"] == s2["run_key"] != s1["run_key"]


def test_blocked_run_does_not_shadow(loaded_conn, store, fetcher):
    done = _run(loaded_conn, store, fetcher, "PX-1")
    before = loaded_conn.execute("SELECT COUNT(*) FROM v_probe_latest").fetchone()[0]
    blocked = _run(loaded_conn, store, fetcher, "PX-2")  # blocked, one robots_denied finding
    after = loaded_conn.execute("SELECT COUNT(*) FROM v_probe_latest").fetchone()[0]
    assert after == before  # blocked findings never enter the census
    assert loaded_conn.execute(
        "SELECT COUNT(*) FROM v_probe_latest WHERE metric_code='robots_denied'"
    ).fetchone()[0] == 0


def test_anchor_candidates(loaded_conn, store, fetcher):
    _run(loaded_conn, store, fetcher, "PX-1")
    rows = loaded_conn.execute(
        "SELECT source_id, metric_code, value_numeric FROM v_anchor_candidates WHERE metric_code = 'catalog_count'"
    ).fetchall()
    assert rows[0][0] == "PX-1" and rows[0][2] == 500.0
    metrics = {r[0] for r in loaded_conn.execute("SELECT metric_code FROM v_anchor_candidates").fetchall()}
    # count-metrics from the PE census; products_listed joins via 0004 (U13),
    # doc_links_seen / walk_budget_exhausted are not anchor candidates
    assert metrics == {"catalog_count", "category_count", "products_listed"}


def test_anchor_candidates_includes_records_hs(loaded_conn, store):
    """0003 view redefinition (od10): the records_hs* metrics are anchors."""
    engine.record_manual(loaded_conn, store, "CX-1", "records_hs3208", value="12", unit="count")
    engine.record_manual(loaded_conn, store, "CX-1", "records_hs3213", value="0", unit="count")
    rows = loaded_conn.execute(
        "SELECT metric_code, value_numeric FROM v_anchor_candidates WHERE source_id = 'CX-1'"
    ).fetchall()
    assert {r[0] for r in rows} == {"records_hs3208", "records_hs3213"}
    assert dict(rows)["records_hs3213"] == 0.0


def test_source_activity(loaded_conn, store, fetcher):
    _run(loaded_conn, store, fetcher, "PX-1")
    _run(loaded_conn, store, fetcher, "PX-2")
    rows = {r[0]: dict(r) for r in loaded_conn.execute("SELECT * FROM v_source_activity").fetchall()}
    assert rows["PX-1"]["finding_count"] > 0
    assert rows["PX-1"]["run_count"] == 1
    assert rows["PX-1"]["first_retrieved_at"] is not None
    assert rows["PX-2"]["finding_count"] == 1  # the robots_denied finding

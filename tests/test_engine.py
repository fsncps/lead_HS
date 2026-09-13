"""Engine: per-source runs, loop survival, re-run keys, stale reclaim,
outcomes, record_manual."""

import re

import pytest

from leadhs import db as dbmod
from leadhs.fetch import FetchConfig, Fetcher
from leadhs.probe import engine


@pytest.fixture()
def fetcher(make_fetcher):
    return make_fetcher()


def _get(loaded_conn, sid):
    from leadhs.source import get_source

    return get_source(loaded_conn, sid)


def test_run_one_done(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-1"), sample_n=3)
    assert summary["status"] == "done"
    assert summary["findings"] >= 9
    row = loaded_conn.execute("SELECT status_code, finished_at FROM run WHERE run_key=?", (summary["run_key"],)).fetchone()
    assert row[0] == "done" and row[1]


def test_run_one_robots_blocked(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-2"))
    assert summary["status"] == "blocked"
    finding = loaded_conn.execute(
        "SELECT metric_code FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=?",
        (summary["run_key"],),
    ).fetchone()
    assert finding[0] == "robots_denied"


def test_run_one_403_blocked(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-3"))
    assert summary["status"] == "blocked"
    finding = loaded_conn.execute(
        "SELECT metric_code FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=?",
        (summary["run_key"],),
    ).fetchone()
    assert finding[0] == "access_blocked"


def test_run_one_persistent_429_blocked(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-4"))
    assert summary["status"] == "blocked"


def test_run_one_429_once_recovers(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-5"))
    assert summary["status"] == "done"


def test_run_one_parse_error(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-6"))
    assert summary["status"] == "done"  # ParseError -> finding + done
    finding = loaded_conn.execute(
        "SELECT pf.value_numeric FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=? AND pf.metric_code='page_sample_ok'",
        (summary["run_key"],),
    ).fetchone()
    assert finding[0] == 0


def test_run_one_network_fail(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "CX-4"))
    assert summary["status"] == "failed"
    assert summary["notes"]


def test_run_one_unexpected_format_done_with_finding(loaded_conn, store, fetcher):
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "CX-2"))
    assert summary["status"] == "done"
    finding = loaded_conn.execute(
        "SELECT pf.value_text FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=? AND pf.metric_code='format'",
        (summary["run_key"],),
    ).fetchone()
    assert finding is not None


def test_rerun_new_run_key(loaded_conn, store, fetcher):
    s1 = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-1"), sample_n=1)
    s2 = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-1"), sample_n=1)
    assert re.fullmatch(r"probe-\d{8}-px1", s1["run_key"])
    assert s2["run_key"] == s1["run_key"] + "-2"
    assert s2["status"] == "done"


def test_run_all_continues_past_failures(loaded_conn, store, fetcher):
    summaries, exit_code = engine.run_all(loaded_conn, store, fetcher, sample_n=1)
    statuses = {s["source"]: s["status"] for s in summaries}
    assert statuses["PX-1"] == "done"
    assert statuses["PX-2"] == "blocked"
    assert statuses["PX-3"] == "blocked"
    assert statuses["CX-4"] == "failed"
    assert exit_code == 2


def test_run_all_empty_register(conn, store, fetcher):
    summaries, exit_code = engine.run_all(conn, store, fetcher)
    assert summaries == [] and exit_code == 0


def test_run_all_capability_only_as_sources(loaded_conn, store, fetcher):
    """v0.2.1 cap2/cap5: the capability sweep targets AS sources only —
    PE/CS/ST sources are never swept in capability mode."""
    summaries, exit_code = engine.run_all(loaded_conn, store, fetcher, mode="capability")
    swept = {s["source"] for s in summaries}
    assert swept == {"AX-1"}
    assert exit_code == 0


def test_stale_run_reclaim_via_run(loaded_conn, store, fetcher):
    loaded_conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260101-px1','probe','PX-1','2026-01-01T00:00:00Z','running')"
    )
    loaded_conn.commit()
    engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-1"), sample_n=1)
    row = loaded_conn.execute("SELECT status_code, notes FROM run WHERE run_key='probe-20260101-px1'").fetchone()
    assert row[0] == "failed"
    assert "stale run reclaimed" in row[1]


def test_dry_run_zero_network(loaded_conn, store, make_fetcher, monkeypatch):
    fetcher = make_fetcher()

    def no_network(*a, **kw):
        raise AssertionError("network call in dry-run")

    monkeypatch.setattr(fetcher._session, "get", no_network)
    summary = engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-1"), dry_run=True)
    assert summary["status"] == "done"
    assert summary["documents"] == 0
    params = loaded_conn.execute("SELECT parameters_json FROM run WHERE run_key=?", (summary["run_key"],)).fetchone()[0]
    import json

    assert json.loads(params)["dry_run"] is True


def test_interrupt_aborts_run(loaded_conn, store, fetcher, monkeypatch):
    from leadhs.probe.adapters import get_adapter

    source = _get(loaded_conn, "PX-1")

    def interrupted(*a, **kw):
        raise KeyboardInterrupt()

    adapter = get_adapter(source)
    monkeypatch.setattr(adapter, "probe", interrupted)
    with pytest.raises(KeyboardInterrupt):
        engine.run_one(loaded_conn, store, fetcher, source, sample_n=1)
    runs = loaded_conn.execute("SELECT run_key, status_code FROM run ORDER BY id DESC LIMIT 1").fetchone()
    assert runs[1] == "aborted"


def test_record_manual(loaded_conn, store):
    summary = engine.record_manual(
        loaded_conn, store, "ST-1", "catalog_count", value="42", unit="count",
        url="https://echa.europa.eu/pcn", note="PCN test",
    )
    assert summary["status"] == "done"
    row = loaded_conn.execute(
        "SELECT r.run_key, pf.value_numeric, pf.method_code FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=?",
        (summary["run_key"],),
    ).fetchone()
    assert re.fullmatch(r"probe-\d{8}-st1manual", row[0])
    assert row[1] == 42.0
    assert row[2] == "manual"


def test_record_manual_bad_metric(loaded_conn, store):
    with pytest.raises(engine.EngineError):
        engine.record_manual(loaded_conn, store, "ST-1", "nope", value="1")


def test_record_manual_census_status_on_inactive_source(loaded_conn, store):
    """od9/od10: census_status records work on inactive sources (ST-1)."""
    summary = engine.record_manual(
        loaded_conn, store, "ST-1", "census_status",
        value_text="PCN aggregates located manually; deferral noted",
        url="https://echa.europa.eu/pcn",
    )
    assert summary["status"] == "done"
    row = loaded_conn.execute(
        "SELECT pf.value_text, pf.method_code FROM probe_finding pf "
        "JOIN run r ON r.id = pf.run_id WHERE r.run_key = ?",
        (summary["run_key"],),
    ).fetchone()
    assert row[0] == "PCN aggregates located manually; deferral noted"
    assert row[1] == "manual"


def test_record_manual_census_status_rejects_value(loaded_conn, store):
    with pytest.raises(engine.EngineError):
        engine.record_manual(loaded_conn, store, "ST-1", "census_status", value="1")


def test_record_manual_numeric_metric_needs_value(loaded_conn, store):
    with pytest.raises(engine.EngineError):
        engine.record_manual(loaded_conn, store, "ST-1", "catalog_count", value_text="x")


def test_record_manual_unknown_source(loaded_conn, store):
    with pytest.raises(engine.EngineError):
        engine.record_manual(loaded_conn, store, "ZZ-1", "catalog_count", value="1")


# --- v0.2.0 e8: record_manual mode parameter -------------------------------


def test_record_manual_mode_recon(loaded_conn, store):
    summary = engine.record_manual(
        loaded_conn, store, "ST-1", "sds_library_visible", value="1",
        mode="recon", note="landing page shows SDS library",
    )
    assert summary["status"] == "done"
    row = loaded_conn.execute(
        "SELECT pr.mode_code FROM probe_run pr JOIN run r ON r.id = pr.run_id WHERE r.run_key = ?",
        (summary["run_key"],),
    ).fetchone()
    assert row[0] == "recon"


def test_record_manual_mode_default_census(loaded_conn, store):
    summary = engine.record_manual(loaded_conn, store, "ST-1", "products_registered", value="1234")
    row = loaded_conn.execute(
        "SELECT pr.mode_code FROM probe_run pr JOIN run r ON r.id = pr.run_id WHERE r.run_key = ?",
        (summary["run_key"],),
    ).fetchone()
    assert row[0] == "census"

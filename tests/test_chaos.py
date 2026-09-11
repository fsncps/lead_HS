"""Chaos: simulated interrupt mid-source — run aborted, findings
persist, re-run idempotent, audit clean, v_probe_latest unchanged."""

import pytest

from leadhs import db as dbmod
from leadhs.probe import engine
from leadhs.source import get_source


def test_chaos_interrupt(loaded_conn, store, make_fetcher, monkeypatch):
    fetcher = make_fetcher()

    # 1) a clean done run establishes the census
    done = engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, "PX-1"), sample_n=2)
    census_before = loaded_conn.execute("SELECT COUNT(*) FROM v_probe_latest").fetchone()[0]
    assert census_before > 0

    # 2) interrupt the re-run mid-source
    from leadhs.probe.adapters import get_adapter

    source = get_source(loaded_conn, "PX-1")
    monkeypatch.setattr(get_adapter(source), "probe", lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        engine.run_one(loaded_conn, store, fetcher, source, sample_n=2)

    aborted = loaded_conn.execute(
        "SELECT status_code FROM run WHERE run_key = 'probe-20260911-px1-2'"
    ).fetchone()[0]
    assert aborted == "aborted"

    # 3) the census is unchanged by the aborted run
    assert loaded_conn.execute("SELECT COUNT(*) FROM v_probe_latest").fetchone()[0] == census_before

    # 4) audit still clean
    assert dbmod.audit(loaded_conn, store) == []

    # 5) re-run idempotent: a NEW done run, census stable in shape
    monkeypatch.undo()
    again = engine.run_one(loaded_conn, store, fetcher, source, sample_n=2)
    assert again["status"] == "done"
    assert again["run_key"] == "probe-20260911-px1-3"
    assert dbmod.audit(loaded_conn, store) == []

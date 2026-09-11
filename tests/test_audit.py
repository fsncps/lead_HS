"""db audit rules: R2/R4 violations, R8 orphans, clean corpus."""

import os

import pytest

from leadhs import db as dbmod
from leadhs.probe import engine


def test_clean_corpus(loaded_conn, store, make_fetcher):
    engine.run_one(loaded_conn, store, make_fetcher(), _src(loaded_conn, "PX-1"), sample_n=2)
    engine.run_one(loaded_conn, store, make_fetcher(), _src(loaded_conn, "CX-1"))
    assert dbmod.audit(loaded_conn, store, unreferenced=True) == []


def _src(loaded_conn, sid):
    from leadhs.source import get_source

    return get_source(loaded_conn, sid)


def test_r2_archived_without_file(loaded_conn, store):
    loaded_conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code, finished_at) "
        "VALUES ('probe-20260901-cx1','probe','CX-1','2026-09-01T00:00:00Z','done','2026-09-01T00:00:01Z')"
    )
    loaded_conn.execute(
        "INSERT INTO probe_run (run_id, mode_code) SELECT id, 'census' FROM run WHERE run_key='probe-20260901-cx1'"
    )
    loaded_conn.execute(
        "INSERT INTO document (source_id, run_id, url, retrieved_at, raw_hash, retrieval_method_code) "
        "SELECT 'CX-1', id, 'u', '2026-09-01T00:00:00Z', '" + "a" * 64 + "', 'manual' FROM run WHERE run_key='probe-20260901-cx1'"
    )
    loaded_conn.commit()
    violations = dbmod.audit(loaded_conn, store)
    assert any(v.startswith("R2") for v in violations)


def test_r4_value_type_mismatch(loaded_conn, store):
    loaded_conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code, finished_at) "
        "VALUES ('probe-20260901-cx1','probe','CX-1','2026-09-01T00:00:00Z','done','2026-09-01T00:00:01Z')"
    )
    loaded_conn.execute(
        "INSERT INTO probe_run (run_id, mode_code) SELECT id, 'census' FROM run WHERE run_key='probe-20260901-cx1'"
    )
    # numeric metric with text value only
    loaded_conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_text, method_code) "
        "SELECT id, 'catalog_count', 'oops', 'manual' FROM run WHERE run_key='probe-20260901-cx1'"
    )
    loaded_conn.commit()
    violations = dbmod.audit(loaded_conn, store)
    assert any(v.startswith("R4") for v in violations)


def test_r8_orphans_listed(loaded_conn, store):
    digest, _ = store.put("CX-1", b"orphan bytes", "html")
    violations = dbmod.audit(loaded_conn, store, unreferenced=True)
    assert any(v.startswith("R8") for v in violations)
    # without the flag: no R8 lines
    assert dbmod.audit(loaded_conn, store) == [v for v in dbmod.audit(loaded_conn, store) if not v.startswith("R8")]


def test_r5_finished_without_finished_at(loaded_conn, store):
    loaded_conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260901-cx1','probe','CX-1','2026-09-01T00:00:00Z','done')"
    )
    loaded_conn.commit()
    violations = dbmod.audit(loaded_conn, store)
    assert any(v.startswith("R5") for v in violations)


def test_r5_failed_without_notes(loaded_conn, store):
    loaded_conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code, finished_at) "
        "VALUES ('probe-20260901-cx1','probe','CX-1','2026-09-01T00:00:00Z','failed','2026-09-01T00:00:01Z')"
    )
    loaded_conn.commit()
    violations = dbmod.audit(loaded_conn, store)
    assert any(v.startswith("R5") for v in violations)

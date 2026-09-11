"""Migrations: fresh apply, idempotency, order, CHECKs, backup round-trip."""

import os
import sqlite3

import pytest

from leadhs import db as dbmod


def test_fresh_apply_all_migrations(conn):
    applied = {r[0] for r in conn.execute("SELECT version FROM schema_version")}
    assert applied == {1, 2, 3}
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in ("source", "document", "run", "probe_run", "probe_finding", "probe_metric"):
        assert table in tables
    views = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")}
    assert {"v_probe_latest", "v_anchor_candidates", "v_source_activity"} <= views


def test_0003_metric_seeds_present(conn):
    codes = {r[0] for r in conn.execute("SELECT code FROM probe_metric")}
    assert {"records_hs3208", "records_hs3209", "records_hs3213", "census_status"} <= codes
    types = dict(conn.execute("SELECT code, value_type FROM probe_metric WHERE code LIKE 'records_hs%' OR code = 'census_status'").fetchall())
    assert types == {"records_hs3208": "numeric", "records_hs3209": "numeric",
                     "records_hs3213": "numeric", "census_status": "text"}


def test_0003_view_redefined(conn):
    """v_anchor_candidates includes the records_hs* codes (od10)."""
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-9','CS','n','u','api')")
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260911-cs9','probe','CS-9','2026-09-11T00:00:00Z','done')"
    )
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, method_code) "
        "SELECT id, 'records_hs3208', 7, 'api' FROM run WHERE run_key = 'probe-20260911-cs9'"
    )
    conn.commit()
    rows = conn.execute("SELECT metric_code FROM v_anchor_candidates WHERE source_id = 'CS-9'").fetchall()
    assert [r[0] for r in rows] == ["records_hs3208"]


def test_reinit_idempotent(conn, db_path):
    applied, pending = dbmod.migrate(conn, db_path=db_path)
    assert applied == []
    assert pending == []


def test_migration_order_enforced(tmp_path):
    """A gap in applied versions is detected: 0002/0003 apply in order on a
    DB that claims only 0001 (whose tables really exist)."""
    conn = dbmod.connect(str(tmp_path / "x.sqlite"))
    try:
        conn.executescript(next(sql for num, _, sql in dbmod.migration_files() if num == 1))
        conn.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)")
        conn.execute("INSERT INTO schema_version VALUES (1, '0001__probe_base.sql', '2026-01-01T00:00:00Z')")
        conn.commit()
        applied, pending = dbmod.migrate(conn)
        assert applied == ["0002__probe_core.sql", "0003__probe_metrics.sql"]
    finally:
        conn.close()


def test_check_probe_run_requires_source(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO run (run_key, kind_code, started_at) VALUES ('probe-20260910-x', 'probe', '2026-09-10T00:00:00Z')"
        )


def test_check_document_requires_run(conn):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')"
    )
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at) VALUES ('probe-20260910-cs1','probe','CS-1','2026-09-10T00:00:00Z')"
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO document (source_id, run_id, url, retrieved_at) VALUES ('CS-1', NULL, 'u', '2026-09-10T00:00:00Z')"
        )


def test_run_default_status_planned(conn):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')"
    )
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at) VALUES ('probe-20260910-cs1','probe','CS-1','2026-09-10T00:00:00Z')"
    )
    conn.commit()
    status = conn.execute("SELECT status_code FROM run WHERE run_key='probe-20260910-cs1'").fetchone()[0]
    assert status == "planned"


def test_source_id_glob_check(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('bad','CS','n','u','api')"
        )


def test_backup_round_trip(conn, db_path):
    """Seed a DB, add a pending migration, migrate -> timestamped backup
    restores a working DB with the seeded rows and without the new table."""
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')"
    )
    conn.commit()
    conn.close()

    orig = dbmod.migration_files
    dbmod.migration_files = lambda: orig() + [(4, "0004__fake.sql", "CREATE TABLE fake (x INTEGER);")]
    try:
        conn2 = dbmod.connect(db_path)
        applied, _ = dbmod.migrate(conn2, db_path=db_path)
        assert applied == ["0004__fake.sql"]
        conn2.close()
    finally:
        dbmod.migration_files = orig

    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    backups = os.listdir(backup_dir)
    assert len(backups) == 1
    backup_path = os.path.join(backup_dir, backups[0])
    with open(backup_path, "rb") as fh:
        header = fh.read(32)
    backup_conn = sqlite3.connect(backup_path)
    try:
        tables = [r[0] for r in backup_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert "source" in tables, f"header={header!r} tables={tables}"
        assert backup_conn.execute("SELECT COUNT(*) FROM source").fetchone()[0] == 1
        assert backup_conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='fake'").fetchone()[0] == 0
    finally:
        backup_conn.close()


def test_no_backup_on_fresh_db(conn, db_path):
    backups_dir = os.path.join(os.path.dirname(db_path), "backups")
    assert not os.path.exists(backups_dir) or os.listdir(backups_dir) == []

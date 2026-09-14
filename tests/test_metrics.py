"""Sync test (t6): migration 0001 probe_metric seeds == metrics.py."""

import sqlite3

from leadhs.metrics import PROBE_METRIC_SEEDS


def test_metric_vocabulary_size():
    assert len(PROBE_METRIC_SEEDS) == 41  # 17 (0001) + 4 (0003, od10) + 3 (0004, D28) + 1 (0005) + 7 (0006) + 6 (0007) + 1 (0008, v0.2.2) + 2 (0009, v0.2.4)


def test_migration_seeds_match_metrics(conn):
    rows = conn.execute("SELECT code, label, value_type FROM probe_metric ORDER BY code").fetchall()
    db_seeds = {r[0]: (r[1], r[2]) for r in rows}
    py_seeds = {m.code: (m.label, m.value_type) for m in PROBE_METRIC_SEEDS}
    assert db_seeds == py_seeds


def test_value_types_valid(conn):
    for row in conn.execute("SELECT code, value_type FROM probe_metric"):
        assert row[1] in ("numeric", "text")

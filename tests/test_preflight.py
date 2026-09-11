"""Preflight tests (t7): uninitialized DB → guided error, exit 1, never
`bug:`, on all seven schema-reading commands (i11/B2)."""

import os
import sqlite3
import subprocess
import sys

import pytest

SEVEN = [
    ["db", "status"],
    ["db", "audit"],
    ["source", "load"],
    ["source", "list"],
    ["probe", "run", "--all", "--dry-run"],
    ["probe", "record", "--source", "ST-1", "--metric", "catalog_count", "--value", "1"],
    ["probe", "report"],
]

GUIDED = "error: database not initialized"


def _lead(db_path, *args):
    env = dict(os.environ, LEADHS_CONTACT="test@example.com")
    return subprocess.run(
        [sys.executable, "-m", "leadhs.cli", "--db", db_path, *args],
        capture_output=True, text=True, env=env,
    )


def _assert_guided(result, where):
    assert result.returncode == 1, f"{where}: exit {result.returncode}\n{result.stderr}"
    assert GUIDED in result.stderr, f"{where}: {result.stderr}"
    assert "bug:" not in result.stderr


def _make_noschema(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE unrelated (x INTEGER)")
    conn.commit()
    conn.close()


@pytest.mark.parametrize("state", ["missing", "empty", "noschema"])
def test_seven_commands_guided_error(tmp_path, state):
    db_path = str(tmp_path / "t.sqlite")
    if state == "empty":
        open(db_path, "w").close()
    elif state == "noschema":
        _make_noschema(db_path)
    for cmd in SEVEN:
        _assert_guided(_lead(db_path, *cmd), f"{state}: {cmd}")


@pytest.mark.parametrize("state", ["missing", "empty", "noschema"])
def test_db_init_works_on_all_states(tmp_path, state):
    db_path = str(tmp_path / "t.sqlite")
    if state == "empty":
        open(db_path, "w").close()
    elif state == "noschema":
        _make_noschema(db_path)
    r = _lead(db_path, "db", "init")
    assert r.returncode == 0, r.stderr


def test_after_init_commands_proceed(db_path, fixture_register):
    assert _lead(db_path, "db", "init").returncode == 0
    assert _lead(db_path, "source", "load", "--file", fixture_register).returncode == 0
    for cmd in SEVEN:
        r = _lead(db_path, *cmd)
        assert r.returncode in (0, 1, 2), f"{cmd}: exit {r.returncode}\n{r.stderr}"
        assert GUIDED not in r.stderr


def test_directory_at_db_path(tmp_path):
    db_path = str(tmp_path / "adir")
    os.makedirs(db_path)
    _assert_guided(_lead(db_path, "db", "status"), "directory")

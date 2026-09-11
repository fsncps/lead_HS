"""Makefile wiring tests (t7): dry-run and guarded targets only —
no side effects (flakiness rule: no DB creation, no installs, no network)."""

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    subprocess.run(["which", "make"], capture_output=True).returncode != 0,
    reason="make not available",
)


def _make(*args, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "GO"}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["make", *args], cwd=REPO, capture_output=True, text=True, env=env,
    )


def test_make_help():
    r = _make("help")
    assert r.returncode == 0
    assert "probe-dry" in r.stdout
    assert "census" in r.stdout


def test_guard_probe_blocks_without_go():
    db_file = REPO / "data" / "leadhs.sqlite"
    existed = db_file.exists()
    r = _make("probe")
    assert r.returncode != 0
    assert "set GO=1" in r.stderr
    assert db_file.exists() == existed  # no side effects


def test_guard_census_blocks_before_setup():
    db_file = REPO / "data" / "leadhs.sqlite"
    existed = db_file.exists()
    r = _make("census")
    assert r.returncode != 0
    assert "set GO=1" in r.stderr
    assert "pip" not in r.stdout.lower()
    assert db_file.exists() == existed  # guard fired before setup


def test_milestone_stub_fails():
    r = _make("sample")
    # the recipe exits 1; GNU make surfaces any recipe failure as exit 2
    assert r.returncode != 0
    assert "milestone-gated" in r.stderr


def test_dry_run_probe_line():
    r = _make("-n", "probe", env_extra={"GO": "1"})
    assert r.returncode == 0
    assert "probe run --all --mode" in r.stdout


def test_dry_run_report_three_outs():
    r = _make("-n", "report")
    assert r.returncode == 0
    assert r.stdout.count("--out") == 3


def test_report_publish_requires_which():
    r = _make("report-publish")
    assert r.returncode != 0
    assert "WHICH" in r.stderr

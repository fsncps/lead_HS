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


# --- v0.2.0: recon targets + chain exit-2 tolerance (e1/1A) ----------------


def test_guard_probe_recon_blocks_without_go():
    r = _make("probe-recon")
    assert r.returncode != 0
    assert "set GO=1" in r.stderr


def test_recon_chain_dry_run():
    r = _make("-n", "recon", env_extra={"GO": "1"})
    assert r.returncode == 0
    assert "probe run --all --mode recon" in r.stdout


def test_probe_single_mode_passthrough():
    r = _make("-n", "probe-single", env_extra={"SOURCE": "CS-2", "MODE": "recon"})
    assert r.returncode == 0
    assert "--mode recon" in r.stdout


def test_chain_exit_2_tolerance_idiom():
    """e1/1A: the census/recon chains tolerate exactly the expected
    sweep exit 2 — the idiom is visible in the recipes."""
    import pathlib

    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    tolerance = "|| test $$? -eq 2"
    census_block = makefile.split("census:")[1].split("probe-recon:")[0]
    recon_block = makefile.split("\nrecon:")[1].split("test:")[0]
    assert tolerance in census_block
    assert tolerance in recon_block


# --- v0.2.1: capability targets + MODE pass-through ------------------------


def test_guard_probe_capability_blocks_without_go():
    r = _make("probe-capability")
    assert r.returncode != 0
    assert "set GO=1" in r.stderr


def test_capability_chain_dry_run():
    r = _make("-n", "capability", env_extra={"GO": "1"})
    assert r.returncode == 0
    assert "probe run --all --mode capability" in r.stdout


def test_capability_chain_exit_2_tolerance():
    import pathlib

    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    capability_block = makefile.split("\ncapability:")[1].split("test:")[0]
    assert "|| test $$? -eq 2" in capability_block


def test_probe_single_mode_capability_passthrough():
    r = _make("-n", "probe-single", env_extra={"SOURCE": "AS-1", "MODE": "capability"})
    assert r.returncode == 0
    assert "--mode capability" in r.stdout

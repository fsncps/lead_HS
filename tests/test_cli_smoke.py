"""2am-Friday confidence test: init -> load -> probe run -> report ->
audit, end-to-end via the CLI on a temp DB + fixture site."""

import os
import subprocess
import sys


def _lead(db_path, *args, expect=None):
    env = dict(os.environ, LEADHS_CONTACT="test@example.com")
    result = subprocess.run(
        [sys.executable, "-m", "leadhs.cli", "--db", db_path, *args],
        capture_output=True, text=True, env=env,
    )
    if expect is not None:
        assert result.returncode == expect, f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}"
    return result


def test_cli_smoke(db_path, fixture_register, tmp_path):
    _lead(db_path, "db", "init", expect=0)
    _lead(db_path, "source", "load", "--file", fixture_register, expect=0)
    _lead(db_path, "probe", "run", "--all", "--sample", "2", expect=2)  # blocked/failed present in fixtures
    report = _lead(db_path, "probe", "report", expect=0)
    assert "Source feasibility census report" in report.stdout
    csv_out = _lead(db_path, "probe", "report", "--format", "csv", expect=0)
    assert csv_out.stdout.startswith("source_id")
    _lead(db_path, "db", "audit", "--unreferenced", expect=0)
    _lead(db_path, "db", "status", expect=0)


def test_cli_bare_groups_help():
    env = dict(os.environ, LEADHS_CONTACT="test@example.com")
    for group in ([], ["db"], ["source"], ["probe"]):
        r = subprocess.run(
            [sys.executable, "-m", "leadhs.cli", *group],
            capture_output=True, text=True, env=env,
        )
        assert r.returncode == 0, group
        assert "Usage:" in r.stdout and not r.stderr, group


def test_cli_version_0_2_0():
    env = dict(os.environ, LEADHS_CONTACT="test@example.com")
    r = subprocess.run(
        [sys.executable, "-m", "leadhs.cli", "--version"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0 and "0.2.1" in r.stdout


def test_cli_probe_record_and_report(db_path, fixture_register, tmp_path):
    _lead(db_path, "db", "init", expect=0)
    _lead(db_path, "source", "load", "--file", fixture_register, expect=0)
    _lead(db_path, "probe", "record", "--source", "ST-1", "--metric", "catalog_count",
          "--value", "17", "--unit", "count", "--url", "https://echa.europa.eu/x", expect=0)
    _lead(db_path, "db", "audit", expect=0)
    report = _lead(db_path, "probe", "report", "--source", "ST-1", expect=0)
    assert "ST-1" in report.stdout and "counts:" in report.stdout  # compact block (U11)


def test_cli_bad_usage(db_path):
    _lead(db_path, "probe", "run")  # no --source/--all -> exit 1


def test_cli_source_load_malformed(db_path, tmp_path):
    _lead(db_path, "db", "init", expect=0)
    bad = tmp_path / "bad.csv"
    bad.write_text("id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes\nXX,PE,n,u,scrape,,open,1,\n")
    result = _lead(db_path, "source", "load", "--file", str(bad))
    assert result.returncode == 1

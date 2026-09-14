"""v0.2.4 tests: the management CSV sample command (D36).

Offline (fixture site only). Covers the design's test list: seeded-draw
determinism, column preservation + provenance, dedupe, clamping, the
four no-fetch records with citations, the AS-3 bounded discovery, the
manifest-always-written rule (review 1A), exit codes, dry-run, column
drift, and the CLI usage paths.
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest

from leadhs.probe import csv_sample as csvsample

REPO = Path(__file__).resolve().parents[1]

_ECAT_HEADER = ["product_or_service_name", "company_name", "group_name", "code_value"]


def _reg(rows, tmp_path):
    path = tmp_path / "register.csv"
    path.write_text("\n".join([
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes,export_url,export_format",
        *rows,
    ]) + "\n", encoding="utf-8")
    return str(path)


def _csv_register(tmp_path, site):
    """The six-registry D36 target set: AS-2 → fixture export, AS-3 →
    HTML search surface, ST-1/3/6/7 → no-fetch rows (unique hosts per
    active row, i13)."""
    port = site.rsplit(":", 1)[1]

    def h(i):
        return f"http://127.0.0.{i}:{port}"

    return _reg([
        f"AS-2,AS,ECAT,{h(30)}/,download,,verified,1,fixture,{h(30)}/ecat.csv,csv",
        # the /svanen/ prefix avoids colliding with shared fixture paths
        # (/export.csv is the CS export fixture) — the guessed candidate
        # endpoints 404, so the discovery budget is spent honestly
        f"AS-3,AS,Nordic Swan,{h(31)}/svanen/,download,,verified,1,fixture,,",
        "ST-1,ST,PCN,https://echa.europa.eu,manual,,open,0,aggregates only,,",
        "ST-3,ST,SBS,https://ec.europa.eu/eurostat,api,,verified,0,enterprise stats,,",
        "ST-6,ST,DK AT,https://at.dk,manual,,verified,0,aggregates only,,",
        "ST-7,ST,SE Echo,https://kemi.se,manual,,open,0,secrecy-protected,,",
    ], tmp_path)


def _load(conn, register):
    from leadhs.source import load

    load(conn, register)


def _sources(conn, ids):
    from leadhs.source import get_source

    return {sid: get_source(conn, sid) for sid in ids}


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))


# --- ECAT delivered path ----------------------------------------------------


def test_ecat_sample_delivered(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _csv_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-2"]),
        n=100, seed=42, out_dir=str(out), ts="20260914-000000",
    )
    assert code == 0
    e = entries[0]
    assert e["status"] == "delivered"
    assert e["rows"] == 2  # pool 2 < n 100 → clamped (amendment 1)
    assert e["fields"] == _ECAT_HEADER
    assert e["idcols"] == ["code_value"]

    rows = _read_csv(out / "csv-sample.20260914-000000.AS-2.csv")
    assert rows[0] == _ECAT_HEADER + list(csvsample.PROVENANCE_COLUMNS)
    assert len(rows) == 3  # header + 2 in-scope (furniture row dropped)
    prov = rows[1][-6:]
    assert prov[0] == "AS-2" and prov[1] == e["run_key"] and prov[5] == "1"

    # the finding + seed are in the DB (i3 write path)
    run = conn.execute("SELECT seed, status_code FROM run WHERE run_key=?", (e["run_key"],)).fetchone()
    assert run[0] == 42 and run[1] == "done"
    finding = conn.execute(
        "SELECT pf.value_numeric FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=?",
        (e["run_key"],),
    ).fetchone()
    assert finding[0] == 2.0
    doc = conn.execute(
        "SELECT d.raw_hash FROM document d JOIN run r ON r.id=d.run_id WHERE r.run_key=?",
        (e["run_key"],),
    ).fetchone()
    assert doc is not None and len(doc[0]) == 64
    assert prov[3] == doc[0]  # doc_hash provenance == archived hash


def test_seeded_determinism(conn, store, make_fetcher, tmp_path, site):
    port = site.rsplit(":", 1)[1]
    reg = _reg([f"AS-2,AS,ECAT,http://127.0.0.32:{port}/,download,,verified,1,fixture,http://127.0.0.32:{port}/ecat-pool.csv,csv"], tmp_path)
    _load(conn, reg)
    fetcher = make_fetcher()
    rows = _sources(conn, ["AS-2"])
    out = tmp_path / "out"
    code, entries_a = csvsample.sample(conn, store, fetcher, rows, n=10, seed=7, out_dir=str(out), ts="20260914-000001")
    code_b, entries_b = csvsample.sample(conn, store, fetcher, rows, n=10, seed=7, out_dir=str(out), ts="20260914-000002")
    _, entries_c = csvsample.sample(conn, store, fetcher, rows, n=10, seed=8, out_dir=str(out), ts="20260914-000003")
    assert code == code_b == 0
    names = lambda path: [r[0] for r in _read_csv(path)[1:]]
    a = names(out / "csv-sample.20260914-000001.AS-2.csv")
    b = names(out / "csv-sample.20260914-000002.AS-2.csv")
    c = names(out / "csv-sample.20260914-000003.AS-2.csv")
    assert a == b and len(a) == 10  # same seed → same draw
    assert a != c  # different seed → different draw
    assert len(set(a)) == 10  # distinct items only (amendment 2)


def test_pool_clamp_and_note(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _csv_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-2"]),
        n=100, seed=1, out_dir=str(out), ts="20260914-000004",
    )
    assert code == 0
    assert entries[0]["reason"] and "pool smaller than n" in entries[0]["reason"]


def test_column_drift_failed_exit_2(conn, store, make_fetcher, tmp_path, site):
    port = site.rsplit(":", 1)[1]
    reg = _reg([f"AS-2,AS,ECAT,http://127.0.0.35:{port}/,download,,verified,1,fixture,http://127.0.0.35:{port}/export-bad.csv,csv"], tmp_path)
    _load(conn, reg)
    out = tmp_path / "out"
    code, entries = csvsample.sample(conn, store, make_fetcher(), _sources(conn, ["AS-2"]), n=100, seed=1, out_dir=str(out), ts="20260914-000005")
    assert code == 2
    assert entries[0]["status"] == "failed"
    assert "column drift" in entries[0]["reason"]
    value = conn.execute(
        "SELECT pf.value_text FROM probe_finding pf JOIN run r ON r.id=pf.run_id WHERE r.run_key=?",
        (entries[0]["run_key"],),
    ).fetchone()
    assert value[0].startswith("FAILED:")


# --- manifest + no-fetch records ---------------------------------------------


def test_st_no_fetch_records_and_manifest(conn, store, make_fetcher, tmp_path, site, site_hits):
    _load(conn, _csv_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["ST-1", "ST-3", "ST-6", "ST-7"]),
        n=100, seed=42, out_dir=str(out), ts="20260914-000006",
    )
    assert code == 0  # expected-unavailable is exit 0 (de4)
    assert all(e["status"] == "unavailable" for e in entries)
    for e in entries:
        assert "accessed 2026-09-14" in e["reason"]
    assert site_hits == {}  # zero network (amendment: asserted via fixture hits)

    md = (out / "csv-sample.manifest.20260914-000006.md").read_text(encoding="utf-8")
    for sid in ("ST-1", "ST-3", "ST-6", "ST-7"):
        assert f"## {sid} — unavailable" in md
    latest = (out / "csv-sample.manifest.md").read_text(encoding="utf-8")
    assert latest == md


def test_manifest_always_written_on_failure(conn, store, make_fetcher, tmp_path, site):
    """Review 1A: a should-deliver failure still writes the manifest,
    with failed + good records visible; exit 2."""
    port = site.rsplit(":", 1)[1]
    path = tmp_path / "register.csv"
    path.write_text("\n".join([
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes,export_url,export_format",
        f"AS-2,AS,ECAT,http://127.0.0.34:{port}/,download,,verified,1,fixture,http://127.0.0.34:{port}/error500,csv",
        "ST-1,ST,PCN,https://echa.europa.eu,manual,,open,0,aggregates only,,",
    ]) + "\n", encoding="utf-8")
    _load(conn, path)
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-2", "ST-1"]),
        n=100, seed=42, out_dir=str(out), ts="20260914-000007",
    )
    assert code == 2
    statuses = {e["source"]: e["status"] for e in entries}
    assert statuses == {"AS-2": "failed", "ST-1": "unavailable"}
    md = (out / "csv-sample.manifest.20260914-000007.md").read_text(encoding="utf-8")
    assert "## AS-2 — failed" in md and "## ST-1 — unavailable" in md
    run = conn.execute("SELECT status_code FROM run WHERE run_key=?", (entries[0]["run_key"],)).fetchone()
    assert run[0] == "failed"


def test_dry_run_zero_network_zero_files(conn, store, make_fetcher, tmp_path, site, site_hits):
    _load(conn, _csv_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-2", "AS-3"]),
        n=100, seed=42, out_dir=str(out), dry_run=True,
    )
    assert code == 0 and entries == []
    assert not out.exists() or list(out.iterdir()) == []
    assert not any(k.startswith("/robots") for k in site_hits)


# --- AS-3 bounded discovery (PHASE03) ----------------------------------------


def test_as3_html_surface_unavailable_bounded(conn, store, make_fetcher, tmp_path, site, site_hits):
    _load(conn, _csv_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-3"]),
        n=100, seed=42, out_dir=str(out), ts="20260914-000008",
    )
    assert code == 0
    e = entries[0]
    assert e["status"] == "unavailable"
    assert "browser pass required" in e["reason"]
    gets = sum(v for k, v in site_hits.items() if k != "/robots.txt" and k.startswith(("/", "/export.csv", "/csv")))
    assert gets <= csvsample._NS_MAX_GETS


def test_as3_csv_response_delivered_via_096_filter(conn, store, make_fetcher, tmp_path, site):
    port = site.rsplit(":", 1)[1]
    reg = _reg([f"AS-3,AS,Nordic Swan,http://127.0.0.33:{port}/,download,,verified,1,fixture,http://127.0.0.33:{port}/ecat-pool.csv,csv"], tmp_path)
    _load(conn, reg)
    out = tmp_path / "out"
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-3"]),
        n=10, seed=7, out_dir=str(out), ts="20260914-000009",
    )
    assert code == 0
    e = entries[0]
    assert e["status"] == "delivered" and e["rows"] == 10
    rows = _read_csv(out / "csv-sample.20260914-000009.AS-3.csv")
    assert all("Paint" in r[0] for r in rows[1:])  # criterion-096 filter held


def test_as3_zero_in_scope_unavailable(conn, store, make_fetcher, tmp_path, site):
    port = site.rsplit(":", 1)[1]
    reg = _reg([f"AS-3,AS,Nordic Swan,http://127.0.0.36:{port}/,download,,verified,1,fixture,http://127.0.0.36:{port}/ecat-furniture.csv,csv"], tmp_path)
    _load(conn, reg)
    code, entries = csvsample.sample(
        conn, store, make_fetcher(), _sources(conn, ["AS-3"]),
        n=10, seed=7, out_dir=str(tmp_path / "out"), ts="20260914-000010",
    )
    assert code == 0
    assert entries[0]["status"] == "unavailable"
    assert "0 criterion-096 rows" in entries[0]["reason"]


# --- CLI wiring (subprocess, house smoke pattern) ----------------------------


def _lead(db_path, *args, expect=None):
    env = dict(os.environ, LEADHS_CONTACT="test@example.com")
    result = subprocess.run(
        [sys.executable, "-m", "leadhs.cli", "--db", str(db_path), *args],
        capture_output=True, text=True, env=env, cwd=REPO,
    )
    if expect is not None:
        assert result.returncode == expect, f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}"
    return result


@pytest.fixture()
def cli_state(db_path, tmp_path, site):
    register = _csv_register(tmp_path, site)
    _lead(db_path, "db", "init", expect=0)
    _lead(db_path, "source", "load", "--file", register, expect=0)
    return tmp_path


def test_cli_sample_end_to_end(db_path, cli_state):
    out = cli_state / "cli-out"
    _lead(db_path, "probe", "download-csv-sample", "--out-dir", str(out), expect=0)
    files = sorted(p.name for p in out.iterdir())
    assert any(p.endswith(".AS-2.csv") for p in files)  # csv-sample.<ts>.AS-2.csv
    assert "csv-sample.manifest.md" in files
    _lead(db_path, "db", "audit", expect=0)


def test_cli_unknown_source_exit_1(db_path, cli_state):
    _lead(db_path, "probe", "download-csv-sample", "--source", "ZZ-9", expect=1)


def test_cli_n_zero_exit_1(db_path, cli_state):
    _lead(db_path, "probe", "download-csv-sample", "--n", "0", expect=1)


def test_cli_dry_run_zero_files(db_path, cli_state, site_hits):
    out = cli_state / "dry-out"
    r = _lead(db_path, "probe", "download-csv-sample", "--out-dir", str(out), "--dry-run", expect=0)
    assert "zero network" in r.stdout
    assert not out.exists()


def test_cli_help_line(db_path, cli_state):
    r = _lead(db_path, "probe", "--help", expect=0)
    assert "download-csv-sample" in r.stdout

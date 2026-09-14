"""v0.2.4 addendum tests (D37): the AS-class source probe.

Offline (fixture site only). Covers the PHASE05 test list: registry
CSV/XLSX delivery with exact counts, estimate-with-provenance, unknown
as a valid outcome, the AS-2/AS-3 reuse path (copy + missing artifact),
association liveness (count visible / not visible / down / 404),
summary-always-written, exit codes, dry-run, the register split guard,
migration 0010 seeds, and the CLI surface.
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest

from leadhs.probe import as_probe
from leadhs.probe.as_probe import REGISTRY_IDS

REPO = Path(__file__).resolve().parents[1]


def _reg(rows, tmp_path):
    path = tmp_path / "register.csv"
    path.write_text("\n".join([
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes,export_url,export_format",
        *rows,
    ]) + "\n", encoding="utf-8")
    return str(path)


def _as_register(tmp_path, site):
    """AS rows for the probe paths (unique hosts per active row, i13):
    AS-2 → reuse (artifact planted by the test), AS-3 → reuse, AS-6 →
    pinned CSV export, AS-4 → XLSX export, AS-9 → landing with count,
    AS-8 → landing without count, AS-5 → landing + auth note, plus
    three associations."""
    port = site.rsplit(":", 1)[1]

    def h(i):
        return f"http://127.0.0.{i}:{port}"

    return _reg([
        f"AS-2,AS,ECAT,{h(40)}/,download,,verified,1,fixture,,",
        f"AS-3,AS,Nordic Swan,{h(41)}/svanen/,download,,verified,1,fixture,,",
        f"AS-4,AS,Blue Angel,{h(42)}/,manual,,partially_verified,0,fixture,{h(42)}/as-export.xlsx,xlsx",
        f"AS-5,AS,INIES,{h(43)}/as-count.html,manual,,partially_verified,0,auth-gated,,",
        f"AS-6,AS,IBU,{h(44)}/,download,,partially_verified,1,fixture,{h(44)}/reg.csv,csv",
        f"AS-8,AS,NF Env,{h(45)}/ecat.html,download,,open,0,pdf lists,,",
        f"AS-9,AS,natureplus,{h(46)}/empty.html,download,,open,0,web database,,",
        f"AS-1,AS,CEPE,{h(47)}/assoc.html,manual,,open,0,association,,",
        f"AS-11,AS,FCiO,{h(48)}/,manual,,open,0,association,,",
        f"AS-16,AS,VdL,{h(49)}/missing,manual,,open,0,association down,,",
    ], tmp_path)


def _load(conn, register):
    from leadhs.source import load

    load(conn, register)


def _sources(conn, ids=None):
    from leadhs.source import get_source

    if ids is None:
        ids = [r[0] for r in conn.execute("SELECT id FROM source WHERE class_code='AS' ORDER BY rowid")]
    return {sid: get_source(conn, sid) for sid in ids}


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))


def _finding(conn, run_key, metric):
    return conn.execute(
        "SELECT pf.value_numeric, pf.value_text, pf.notes FROM probe_finding pf "
        "JOIN run r ON r.id=pf.run_id JOIN probe_run pr ON pr.run_id=r.id "
        "WHERE r.run_key=? AND pr.mode_code=? AND pf.metric_code=?",
        (run_key, "as_source_probe", metric),
    ).fetchone()


# --- registry delivery paths -------------------------------------------------


def test_registry_csv_delivered(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-6"]),
                                    out_dir=str(out), ts="20260914-120000")
    assert code == 0
    e = entries[0]
    assert e["status"] == "delivered" and e["gets"] == 1
    assert e["records"] == "3 (exact)" and e["file"] == "as-probe.20260914-120000.AS-6.csv"
    rows = _read_csv(out / e["file"])
    assert rows[0] == ["product_name", "manufacturer", "licence_no", "cn_code"] + list(as_probe.provenance_columns())
    assert len(rows) == 4
    f = _finding(conn, e["run_key"], "as_probe_rows")
    assert f is not None and f[0] == 3.0
    run = conn.execute("SELECT status_code FROM run WHERE run_key=?", (e["run_key"],)).fetchone()
    assert run[0] == "done"


def test_registry_xlsx_rendered(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-4"]),
                                    out_dir=str(out), ts="20260914-120001")
    assert code == 0
    e = entries[0]
    assert e["status"] == "delivered" and "XLSX" in e["basis"]
    assert e["records"] == "2 (exact)"
    rows = _read_csv(out / "as-probe.20260914-120001.AS-4.csv")
    assert rows[0] == ["Manufacturer", "Product"] + list(as_probe.provenance_columns())
    assert rows[1][:2] == ["Acme GmbH", "Paint A"] and rows[2][:2] == ["Beier AG", "Paint B"]


# --- estimate / unknown paths -------------------------------------------------


def test_registry_estimate_with_provenance(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-5"]),
                                    out_dir=str(out), ts="20260914-120002")
    assert code == 0
    e = entries[0]
    assert e["status"] == "records" and e["records"] == "≈12400 (estimated)"
    assert "visible page text" in e["basis"] and "accessed" in e["basis"]
    f = _finding(conn, e["run_key"], "as_probe_records")
    assert f is not None and "estimated 12400" in f[1] and "instead" in f[1]


def test_registry_unknown_when_no_count(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-8"]),
                                    out_dir=str(out), ts="20260914-120003")
    assert code == 0
    e = entries[0]
    assert e["status"] == "unavailable" and e["records"] == "unknown"
    assert e["instead"] == as_probe._INSTEAD["AS-8"]
    f = _finding(conn, e["run_key"], "as_probe_unavailable")
    assert "no product-row CSV obtainable" in f[1] and "PDF lists" in f[1]


def test_registry_failed_pinned_url_exit_2(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    conn.execute("UPDATE source SET url='http://127.0.0.13:1/error500', export_url=NULL WHERE id='AS-6'")
    conn.commit()
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-6"]),
                                    out_dir=str(tmp_path / "out"), ts="20260914-120004")
    assert code == 2
    assert entries[0]["status"] == "failed"


# --- AS-2/AS-3 reuse path (2A) -------------------------------------------------


def _plant_sample(reuse_dir: Path, source_id: str, ts="20260914-111921", data_rows=2):
    path = reuse_dir / f"csv-sample.{ts}.{source_id}.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "company"] + list(as_probe.provenance_columns()))
        for i in range(data_rows):
            w.writerow([f"Paint {i}", "Acme"] + [source_id, "probe-x", "2026-09-14", "", "42", str(i + 1)])
    return path.name


def test_reuse_copies_without_refetch(conn, store, make_fetcher, tmp_path, site, site_hits):
    _load(conn, _as_register(tmp_path, site))
    reuse_dir = tmp_path / "report"
    reuse_dir.mkdir()
    _plant_sample(reuse_dir, "AS-2")
    _plant_sample(reuse_dir, "AS-3", data_rows=3)
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-2", "AS-3"]),
                                    out_dir=str(out), ts="20260914-120005", reuse_dir=str(reuse_dir))
    assert code == 0
    assert all(e["status"] == "delivered" and e["gets"] == 0 for e in entries)
    assert entries[0]["records"] == "2 (exact)" and entries[1]["records"] == "3 (exact)"
    assert (out / "csv-sample.20260914-111921.AS-2.csv").exists()
    assert (out / "csv-sample.20260914-111921.AS-3.csv").exists()
    assert site_hits == {}  # zero network on the reuse path
    f = _finding(conn, entries[0]["run_key"], "as_probe_rows")
    assert f is not None and "reused same-day csv-sample artifact" in (f[2] or "")


def test_reuse_missing_artifact_honest_record(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    reuse_dir = tmp_path / "report"
    reuse_dir.mkdir()
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-2"]),
                                    out_dir=str(tmp_path / "out"), ts="20260914-120006", reuse_dir=str(reuse_dir))
    assert code == 0  # honest unavailable, not a failure
    e = entries[0]
    assert e["status"] == "unavailable"
    assert "run `leadhs probe download-csv-sample` first" in e["reason"]
    f = _finding(conn, e["run_key"], "as_probe_unavailable")
    assert f is not None


# --- association paths ----------------------------------------------------------


def test_association_live_with_member_count(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-1"]),
                                    out_dir=str(tmp_path / "out"), ts="20260914-120007")
    assert code == 0
    e = entries[0]
    assert e["status"] == "assoc" and e["gets"] == 1
    assert "member list" in e["instead"]
    f = _finding(conn, e["run_key"], "as_probe_assoc")
    assert "trade association — no product register" in f[1]
    assert "1200 member companies" in f[1] and "accessed" in f[1]
    doc = conn.execute("SELECT d.raw_hash FROM document d JOIN run r ON r.id=d.run_id WHERE r.run_key=?",
                       (e["run_key"],)).fetchone()
    assert doc is not None and len(doc[0]) == 64


def test_association_no_count_visible(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-11"]),
                                    out_dir=str(tmp_path / "out"), ts="20260914-120008")
    e = entries[0]
    assert code == 0 and e["status"] == "assoc"
    f = _finding(conn, e["run_key"], "as_probe_assoc")
    assert "member companies visible" not in f[1]


def test_association_down_recorded_not_failed(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-16"]),
                                    out_dir=str(tmp_path / "out"), ts="20260914-120009")
    assert code == 0  # association reachability is expected-can-fail
    e = entries[0]
    assert e["status"] == "assoc"
    f = _finding(conn, e["run_key"], "as_probe_assoc")
    assert "not serving (HTTP 404)" in f[1]


# --- summary + exit contract ------------------------------------------------------


def test_summary_always_written_even_all_fail(conn, store, make_fetcher, tmp_path, site):
    _load(conn, _as_register(tmp_path, site))
    conn.execute("UPDATE source SET url='http://127.0.0.13:1/error500', export_url=NULL WHERE id='AS-6'")
    conn.execute("UPDATE source SET url='http://127.0.0.13:1/error500' WHERE id='AS-16'")
    conn.commit()
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn),
                                    out_dir=str(out), ts="20260914-120010")
    assert code == 2  # the failed registry drives the exit; assoc 500 is expected
    statuses = {e["source"]: e["status"] for e in entries}
    assert statuses["AS-6"] == "failed" and statuses["AS-16"] == "assoc"
    summary = _read_csv(out / "as-source-probe.summary.csv")
    assert [r[0] for r in summary[1:]] == sorted(statuses) or [r[0] for r in summary[1:]] == list(statuses)
    assert (out / "as-source-probe.summary.md").exists()
    assert (out / f"as-source-probe.summary.20260914-120010.md").exists()


def test_dry_run_zero_network_zero_files(conn, store, make_fetcher, tmp_path, site, site_hits):
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn),
                                    out_dir=str(out), dry_run=True)
    assert code == 0 and entries == []
    assert not out.exists() and site_hits == {}


# --- register split guard -----------------------------------------------------------


def test_split_guard_against_real_register():
    """Explicit sets vs the register: 30 AS rows, 9 registries, 21
    associations — a register change fails loudly here."""
    import csv as _csv

    reg = REPO / "src" / "leadhs" / "dict" / "sources.csv"
    rows = list(_csv.DictReader(open(reg, newline="", encoding="utf-8")))
    as_ids = {r["id"] for r in rows if r["class_code"] == "AS"}
    assert len(as_ids) == 30
    assert set(REGISTRY_IDS) <= as_ids
    as_rows = [r for r in rows if r["class_code"] == "AS"]
    assert all(r["id"] in REGISTRY_IDS or r["access_method_code"] == "manual" for r in as_rows)


# --- migration 0010 ------------------------------------------------------------------


def test_mode_and_metrics_seeded(conn):
    mode = conn.execute("SELECT label FROM probe_mode WHERE code='as_source_probe'").fetchone()
    assert mode is not None
    metrics = {r[0] for r in conn.execute("SELECT code FROM probe_metric WHERE code LIKE 'as_probe_%'")}
    assert metrics == {"as_probe_rows", "as_probe_records", "as_probe_unavailable", "as_probe_assoc"}


# --- CLI wiring (subprocess, house smoke pattern) ------------------------------------


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
    register = _as_register(tmp_path, site)
    _lead(db_path, "db", "init", expect=0)
    _lead(db_path, "source", "load", "--file", register, expect=0)
    return tmp_path


def test_cli_help_line(db_path, cli_state):
    r = _lead(db_path, "probe", "--help", expect=0)
    assert "as-source-probe" in r.stdout


def test_cli_unknown_source_exit_1(db_path, cli_state):
    _lead(db_path, "probe", "as-source-probe", "--source", "ZZ-9", expect=1)


def test_cli_dry_run_zero_files(db_path, cli_state, site_hits):
    out = cli_state / "dry-out"
    r = _lead(db_path, "probe", "as-source-probe", "--out-dir", str(out), "--dry-run", expect=0)
    assert "zero network" in r.stdout
    assert not out.exists() and site_hits == {}


@pytest.fixture()
def reuse_state(tmp_path):
    d = tmp_path / "reuse"
    d.mkdir()
    _plant_sample(d, "AS-2")
    _plant_sample(d, "AS-3", data_rows=3)
    return d


def test_cli_end_to_end_offline(db_path, cli_state, reuse_state):
    out = cli_state / "cli-out"
    _lead(db_path, "probe", "as-source-probe", "--out-dir", str(out), "--reuse-dir", str(reuse_state), expect=0)
    files = sorted(p.name for p in out.iterdir())
    assert any(p.startswith("as-probe.") and p.endswith(".AS-6.csv") for p in files)
    assert "as-source-probe.summary.md" in files
    _lead(db_path, "db", "audit", expect=0)


# --- D38: evidence archiving, relabel, offline rebuild ------------------------


def test_estimate_archives_landing_evidence(conn, store, make_fetcher, tmp_path, site):
    """The estimate's landing page is archived (D38) and the finding
    cites its doc_hash — no URL-only provenance."""
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-5"]),
                                    out_dir=str(out), ts="20260914-150000")
    assert code == 0
    e = [x for x in entries if x["source"] == "AS-5"][0]
    assert e["status"] == "records"
    doc = conn.execute(
        "SELECT raw_hash, content_type FROM document WHERE source_id='AS-5' "
        "AND content_type LIKE '%html%' ORDER BY id DESC LIMIT 1").fetchone()
    assert doc and doc[1].startswith("text/html")
    f = _finding(conn, e["run_key"], "as_probe_records")
    assert f[1] and f"doc_hash={doc[0]}" in f[1]


def test_reuse_records_relabel_with_pool(conn, store, make_fetcher, tmp_path, site):
    """D38 relabel: the reuse entry reads 'N rows (sample of P distinct
    register products)' — P from the newest csv_sample_rows finding."""
    from leadhs.probe import csv_sample as csvsample
    port = site.rsplit(":", 1)[1]
    reg = _reg([f"AS-2,AS,ECAT,http://127.0.0.40:{port}/,download,,verified,1,fixture,http://127.0.0.40:{port}/ecat-pool.csv,csv"], tmp_path)
    _load(conn, reg)
    out_csv = tmp_path / "csv"
    code, _ = csvsample.sample(conn, store, make_fetcher(), _sources(conn, ["AS-2"]),
                               n=100, seed=42, out_dir=str(out_csv), ts="20260914-150001")
    assert code == 0
    out = tmp_path / "out"
    code2, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn, ["AS-2"]),
                                     out_dir=str(out), ts="20260914-150002", reuse_dir=str(out_csv))
    assert code2 == 0
    e = entries[0]
    assert e["status"] == "delivered" and e["gets"] == 0
    # the fixture pool is 10 distinct items (clamped draw of 10 rows)
    assert e["records"] == "10 rows (sample of 10 distinct register products)"


def test_rebuild_summary_from_findings(conn, store, make_fetcher, tmp_path, site):
    """rebuild_summary re-derives the entries from the latest
    as_source_probe run per source — statuses and key fields match the
    live run; zero network."""
    _load(conn, _as_register(tmp_path, site))
    out = tmp_path / "out"
    code, entries = as_probe.sample(conn, store, make_fetcher(), _sources(conn),
                                    out_dir=str(out), ts="20260914-150003")
    assert code == 0
    entries2 = as_probe.rebuild_summary(conn, out, ts="20260914-150004")
    assert [e["source"] for e in entries2] == [e["source"] for e in entries]
    for a, b in zip(entries, entries2):
        assert b["status"] == a["status"], (a, b)
        if a["status"] in ("records", "unavailable", "assoc"):
            assert b["records"] == a["records"], (a["source"], a, b)
            assert b["instead"] == a["instead"], (a["source"], a, b)
    assert (out / "as-source-probe.summary.20260914-150004.md").exists()
    assert (out / "as-source-probe.summary.md").exists()

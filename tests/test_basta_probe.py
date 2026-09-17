"""v0.2.4 addendum tests (D40): the BASTA special probe.

Offline (fixture site only). Covers the D40 implementation plan test
list: the bundle-chain pin (found / not-found / auth-gated), exact
public counts, the seeded draw over the pinned identity chains, the
pool threshold fallbacks (random-page / head-of-pool prefix), the
paint filter (db5 — monkeypatched; the live constant is None at recon
time), shortfall honesty, method recording, the CSV layout, exit
codes, dry-run, migration 0011 seeds, the Crawl-delay fetcher fix
(decision 4B), and the CLI surface.
"""

import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest

from leadhs.probe import basta_probe as bp

REPO = Path(__file__).resolve().parents[1]


def _reg(tmp_path, url):
    """One active AS row pointing the BASTA probe at the fixture site."""
    path = tmp_path / "register.csv"
    path.write_text("\n".join([
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes,export_url,export_format",
        f"AS-33,AS,BASTA online,{url},download,,open,1,fixture,,",
    ]) + "\n", encoding="utf-8")
    return str(path)


def _fresh_conn(db_path):
    from leadhs import db as dbmod

    c = dbmod.connect(str(db_path))
    dbmod.migrate(c, db_path=str(db_path))
    return c


def _load(conn, register):
    from leadhs.source import load

    load(conn, register)


def _finding(conn, run_key, metric):
    return conn.execute(
        "SELECT pf.value_numeric, pf.value_text, pf.notes FROM probe_finding pf "
        "JOIN run r ON r.id=pf.run_id JOIN probe_run pr ON pr.run_id=r.id "
        "WHERE r.run_key=? AND pr.mode_code=? AND pf.metric_code=?",
        (run_key, "basta_special_probe", metric),
    ).fetchone()


def _rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))


@pytest.fixture()
def module_defaults(monkeypatch):
    """Point the pinned counts paths at the fixture routes."""
    monkeypatch.setattr(bp, "KEYFIGURES_ARTICLES", "/api-keyfigures")
    monkeypatch.setattr(bp, "KEYFIGURES_COMPANIES", "/api-keyfigures")
    yield


def test_pin_routes_and_delivers_full_pool(basta_conn, store, make_fetcher, tmp_path,
                                           module_defaults):
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), _src(basta_conn),
                               out_dir=str(tmp_path / "out"), ts="20260917-120000")
    assert code == 0
    assert entry["status"] == "delivered"
    assert entry["rows"] == 6
    assert "full-pool paginated" in entry["method"]
    rows = _rows(tmp_path / "out" / entry["file"])
    header = rows[0]
    assert "bk04Code" in header and "articleNumber" in header
    assert header[-len(bp.PROVENANCE_COLUMNS):] == list(bp.PROVENANCE_COLUMNS)


@pytest.fixture()
def basta_conn(conn, tmp_path, site):
    """Load the AS-33 register row at the fixture site (happy path)."""
    _load(conn, _reg(tmp_path, site))
    return conn


def _src(conn, url=None):
    """The register row (updated to ``url`` first when given)."""
    from leadhs import source as sourcemod

    if url is not None:
        conn.execute("UPDATE source SET url=? WHERE id='AS-33'", (url,))
        conn.commit()
    return sourcemod.get_source(conn, "AS-33")


def test_seeded_draw_reproducible(basta_conn, store, make_fetcher, tmp_path,
                                  module_defaults):
    fetcher = make_fetcher()
    out = str(tmp_path / "out")
    _c1, e1 = bp.run_probe(basta_conn, store, fetcher, _src(basta_conn), out_dir=out,
                           ts="20260917-120001")
    _c2, e2 = bp.run_probe(basta_conn, store, fetcher, _src(basta_conn), out_dir=out,
                           ts="20260917-120002")
    def data(fn):
        return [r[:-len(bp.PROVENANCE_COLUMNS)]
                for r in _rows(os.path.join(out, fn))][1:]
    assert data(e1["file"]) == data(e2["file"])  # same seed → same draw (D2)


def test_counts_recorded_with_provenance(basta_conn, store, make_fetcher, tmp_path,
                                         module_defaults):
    _code, entry = bp.run_probe(basta_conn, store, make_fetcher(), _src(basta_conn),
                                out_dir=str(tmp_path / "out"))
    f = _finding(basta_conn, entry["run_key"], "catalog_count")
    assert f is not None and f[0] == 195390.0
    assert "api-keyfigures" in f[2] and "accessed" in f[2]


def test_shortfall_recorded_never_padded(basta_conn, store, make_fetcher, tmp_path,
                                         module_defaults):
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), _src(basta_conn),
                               out_dir=str(tmp_path / "out"), n=100)
    assert code == 0 and entry["status"] == "delivered"
    assert "pool smaller than n" in entry["reason"]
    assert entry["rows"] == 6  # exact pool size, never padded
    f = _finding(basta_conn, entry["run_key"], "basta_special_rows")
    assert "shortfall=True" in f[2]


def test_paint_filter_pinned_drops_toner(basta_conn, store, make_fetcher, tmp_path,
                                         module_defaults, monkeypatch):
    monkeypatch.setattr(bp, "_PAINT_FILTER_PARAM", ("category", "paint"))
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), _src(basta_conn),
                               out_dir=str(tmp_path / "out"))
    assert code == 0 and entry["status"] == "delivered"
    rows = _rows(tmp_path / "out" / entry["file"])
    cats = {r[rows[0].index("category")] for r in rows[1:]}
    assert cats == {"paints"}  # the toner row dropped, not name-guessed


def test_random_page_draw_above_threshold(basta_conn, store, make_fetcher, tmp_path, site,
                                          module_defaults, monkeypatch):
    source = _src(basta_conn, f"http://127.0.0.62:{site.rsplit(':', 1)[1]}")
    monkeypatch.setattr(bp, "_PAGE_SIZE", 2)
    monkeypatch.setattr(bp, "_POOL_THRESHOLD", 3)
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), source,
                               out_dir=str(tmp_path / "out"))
    assert code == 0 and entry["status"] == "delivered"
    assert "random-page draws" in entry["method"]
    f = _finding(basta_conn, entry["run_key"], "basta_special_rows")
    assert "method=random-page draws" in f[2]


def test_head_of_pool_when_no_total(basta_conn, store, make_fetcher, tmp_path,
                                    module_defaults, monkeypatch):
    monkeypatch.setattr(bp, "_PAGE_SIZE", 6)
    monkeypatch.setattr(bp, "_POOL_THRESHOLD", 3)  # < one oversized page → cap hit
    source = _src(basta_conn)
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), source,
                               out_dir=str(tmp_path / "out"))
    assert code == 0 and entry["status"] == "delivered"
    assert "head-of-pool" in entry["method"]
    f = _finding(basta_conn, entry["run_key"], "basta_special_rows")
    assert "method=head-of-pool" in f[2]


def test_identity_dedupe():
    from leadhs.probe.basta_probe import _KEY_FIELDS_BASTA, _value_at

    def _key(rec):
        return tuple(
            str(_value_at(rec, names[0]) or _value_at(rec, names[1]) or "").strip().casefold()
            for names in _KEY_FIELDS_BASTA
        )

    dup = {"articleName": "Paint A", "articleNumber": "AR-0001",
           "company": {"name": "Acme AB"}, "id": "B0001", "gtin": "",
           "bk04Code": {"code": "211"}}
    recs = [dup, dict(dup), {"articleName": "Paint B", "articleNumber": "AR-0001",
                             "company": {"name": "Acme AB"}, "id": "B0002"}]
    pool: dict = {}
    for rec in recs:
        pool.setdefault(_key(rec), rec)
    assert len(pool) == 2  # dedupe on (company.name, articleNumber, id)


def test_identity_completeness_reported(basta_conn, store, make_fetcher, tmp_path,
                                        module_defaults):
    _code, entry = bp.run_probe(basta_conn, store, make_fetcher(), _src(basta_conn),
                                out_dir=str(tmp_path / "out"))
    f = _finding(basta_conn, entry["run_key"], "basta_special_rows")
    assert "identity share" in f[2] and "company.name=" in f[2]
    assert "id=100.0%" in f[2] and "gtin=66.7%" in f[2]  # empty gtins all visible


# --- honesty paths ------------------------------------------------------------------


def test_pin_not_found_is_honest_unavailable(basta_conn, store, make_fetcher, tmp_path, site,
                                             module_defaults):
    port = site.rsplit(":", 1)[1]
    source = _src(basta_conn, f"http://127.0.0.61:{port}")
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), source,
                               out_dir=str(tmp_path / "out"))
    assert code == 0  # expected-unavailable, honest record, exit 0
    assert entry["status"] == "unavailable"
    f = _finding(basta_conn, entry["run_key"], "basta_special_unavailable")
    assert "pin-not-found" in f[1] and "agreement" in f[1]


def test_auth_gated_shell_recorded(basta_conn, store, make_fetcher, tmp_path, site,
                                   module_defaults):
    port = site.rsplit(":", 1)[1]
    source = _src(basta_conn, f"http://127.0.0.63:{port}")
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), source,
                               out_dir=str(tmp_path / "out"))
    assert code == 0 and entry["status"] == "unavailable"
    f = _finding(basta_conn, entry["run_key"], "basta_special_unavailable")
    assert "agreement" in f[1] and "api.bastaonline.se" in f[1]


def test_network_failure_exit_2(basta_conn, store, make_fetcher, tmp_path,
                                module_defaults):
    source = _src(basta_conn, f"http://127.0.0.14:1/error500")
    code, entry = bp.run_probe(basta_conn, store, make_fetcher(), source,
                               out_dir=str(tmp_path / "out"))
    assert code == 2 and entry["status"] == "failed"


def test_dry_run_plans_zero_network(db_path, store, make_fetcher, tmp_path,
                                    site_hits, module_defaults):
    from leadhs.models import SourceRef

    src = SourceRef(id="AS-33", class_code="AS", name="BASTA online",
                    url="http://127.0.0.60", access_method_code="download")
    conn = _fresh_conn(db_path)
    try:
        code, entries = bp.sample(conn, store, make_fetcher(),
                                  {"AS-33": src},
                                  out_dir=str(tmp_path / "out"), dry_run=True)
    finally:
        conn.close()
    assert code == 0 and not (tmp_path / "out").exists()
    assert site_hits == {} and entries[0]["status"] == "dry-run"


# --- migration + cli ----------------------------------------------------------------


def test_mode_and_metrics_seeded(conn):
    mode = conn.execute("SELECT label FROM probe_mode WHERE code='basta_special_probe'").fetchone()
    assert mode is not None
    metrics = {r[0] for r in conn.execute(
        "SELECT code FROM probe_metric WHERE code LIKE 'basta_special_%'")}
    assert metrics == {"basta_special_rows", "basta_special_unavailable"}


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
    register = _reg(tmp_path, site)
    _lead(db_path, "db", "init", expect=0)
    _lead(db_path, "source", "load", "--file", register, expect=0)
    return tmp_path


def test_cli_help_line(db_path, cli_state):
    r = _lead(db_path, "probe", "--help", expect=0)
    assert "basta-probe" in r.stdout


def test_cli_unknown_source_exit_1(db_path, cli_state):
    _lead(db_path, "probe", "basta-probe", "--source", "ZZ-9", expect=1)


def test_cli_dry_run_zero_files(db_path, cli_state, site_hits):
    out = cli_state / "dry-out"
    _lead(db_path, "probe", "basta-probe", "--out-dir", str(out), "--dry-run", expect=0)
    assert not out.exists() and site_hits == {}


# --- the crawl-delay fetcher fix (decision 4B) ---------------------------------------


def test_crawl_delay_honored(site, fake_clock, make_fetcher):
    f = make_fetcher(fake_clock, robots_path="/basta-robots.txt")
    f.get(f"{site}/")
    t1 = fake_clock.t
    f.get(f"{site}/terms")
    assert fake_clock.t - t1 >= 10.0  # Crawl-delay: 10 respected, not the 2 s floor


def test_crawl_delay_capped(site, fake_clock, make_fetcher):
    f = make_fetcher(fake_clock, robots_path="/basta-robots.txt",
                     rate_limit_cap=5.0)
    f.get(f"{site}/")
    t1 = fake_clock.t
    f.get(f"{site}/terms")
    assert fake_clock.t - t1 <= 5.5  # the cap applies to the crawl delay too

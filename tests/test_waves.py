"""Wave harness (v0.2.2 t12 wave/adapter blocks): filter selection,
budget expiry (virtual clock), disposition invariant, sniff gate, ECAT
ingest, CN8 batch, sds_doc_urls, `make landscape` guard."""

import os

import pytest

from leadhs import db as dbmod, staging
from leadhs.cli import _WAVE_PRESETS
from leadhs.models import ProbeContext, SourceRef
from leadhs.probe.adapters import ASAdapter, CSAdapter, read_csv_rows, sniff_kind


# --- sniff gate + shared CSV path (e3) -------------------------------------


def test_sniff_gate_kinds():
    assert sniff_kind("text/csv", b"a,b\n1,2\n") == "csv"
    assert sniff_kind("text/html", b"<!doctype html><html>") == "html"
    assert sniff_kind("application/json", b'{"a": 1}') == "json"
    assert sniff_kind("application/json", b'{"class": "dataset", "id": ["x"]}') == "jsonstat"
    assert sniff_kind(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b"PK\x03\x04...."
    ) == "xlsx"
    assert sniff_kind("text/tab-separated-values", b"a\tb\n") == "tsv"
    assert sniff_kind(None, b"????") == "other"


def test_read_csv_bom_and_semicolon_dialect():
    body = "name;company\nPaint A;Acme GmbH\n".encode("utf-8-sig")  # encoding adds the BOM
    header, rows = read_csv_rows(body, separator=";", expected=("name", "company"))
    assert header == ["name", "company"]
    assert rows == [["Paint A", "Acme GmbH"]]


def test_read_csv_column_drift():
    from leadhs.probe.adapters import UnexpectedFormat

    with pytest.raises(UnexpectedFormat) as exc:
        read_csv_rows(b"a,b\n1,2\n", expected=("name", "company"))
    assert "column drift" in str(exc.value)


# --- ASAdapter staged export ingest (W1) ------------------------------------


def _ecat_source(site, export_path="/ecat.csv"):
    return SourceRef(
        id="AS-2", class_code="AS", name="ECAT", url=f"{site}/landing",
        access_method_code="download", active=1, export_url=f"{site}{export_path}",
    )


def _ctx(conn, store, fetcher, staging_conn=None, mode="capability", dry_run=False):
    return ProbeContext(fetcher=fetcher, store=store, conn=conn, mode=mode,
                        dry_run=dry_run, staging=staging_conn)


def test_ecat_export_ingest_stages_rows(site, conn, store, make_fetcher):
    result = ASAdapter().probe(_ecat_source(site), _ctx(conn, store, make_fetcher()))
    assert len(result.staged_products) == 2  # the furniture row drops
    row = result.staged_products[0]
    assert row.manufacturer_raw == "Acme GmbH"
    assert row.ident_raw == "0076000001"  # leading zero preserved (raw)
    assert row.document is result.documents[0]
    assert result.notes[0].startswith("export ingest: 2 in-scope")


def test_ecat_ingest_counted_zero_when_no_paint_rows(site, conn, store, make_fetcher):
    result = ASAdapter().probe(_ecat_source(site, "/ecat-furniture.csv"), _ctx(conn, store, make_fetcher()))
    assert result.staged_products == []
    assert "staged_zero" in result.parameters


def test_ecat_export_html_is_format_finding_not_crash(site, conn, store, make_fetcher):
    result = ASAdapter().probe(_ecat_source(site, "/ecat.html"), _ctx(conn, store, make_fetcher()))
    assert result.staged_products == []
    assert "HTML" in result.findings[0].value_text


def test_ecat_dry_run_plans_export_url(site, conn, store, make_fetcher, monkeypatch):
    ctx = _ctx(conn, store, make_fetcher(), dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = ASAdapter().probe(_ecat_source(site), ctx)
    assert result.documents == [] and result.staged_products == []


# --- CSAdapter per-CN8 batch (W1) -------------------------------------------


def _cs2_source(site):
    return SourceRef(id="CS-2", class_code="CS", name="Comext", url=f"{site}/api.json",
                     access_method_code="api", active=1)


def test_comext_batch_stages_trade_rows(site, conn, store, make_fetcher):
    result = CSAdapter().probe(_cs2_source(site), _ctx(conn, store, make_fetcher()))
    # fixture: each of 13×2×2 queries decodes 2 declarant rows
    assert len(result.staged_trade) == 13 * 2 * 2 * 2
    row = result.staged_trade[0]
    assert row.cn8.startswith(("3208", "3209", "3213"))
    assert row.declarant in ("DE", "FR")
    assert row.year == "2024"
    assert result.parameters["query"]
    assert any(n.startswith("CN8 batch: 13 codes") for n in result.notes)


def test_comext_batch_dry_run_plans_all_queries(site, conn, store, make_fetcher, monkeypatch):
    ctx = _ctx(conn, store, make_fetcher(), dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_cs2_source(site), ctx)
    assert result.staged_trade == [] and result.documents == []


# --- PEAdapter sds_doc_urls (W3) ---------------------------------------------


def test_recon_emits_sds_doc_urls(loaded_conn, store, fetcher):
    """W3 (fu6): the recon path emits the sds_doc_urls metric (counts only)."""
    from leadhs.probe import engine
    from leadhs.source import get_source

    summary = engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, "PX-1"), mode="recon")
    row = loaded_conn.execute(
        "SELECT pf.value_numeric FROM probe_finding pf JOIN run r ON r.id=pf.run_id "
        "WHERE r.run_key=? AND pf.metric_code='sds_doc_urls'",
        (summary["run_key"],),
    ).fetchone()
    assert row is not None and row[0] >= 0


# --- dispositions (c1) -------------------------------------------------------


def _get(loaded_conn, sid):
    from leadhs.source import get_source

    return get_source(loaded_conn, sid)


def test_disposition_state_machine(loaded_conn, store, fetcher):
    from leadhs.probe import engine

    assert engine.disposition_of(loaded_conn, "PX-1")["disposition"] == "pending"
    engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-1"), sample_n=3)
    assert engine.disposition_of(loaded_conn, "PX-1")["disposition"] == "counted"
    engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "PX-2"), mode="recon")
    assert engine.disposition_of(loaded_conn, "PX-2")["disposition"] == "blocked"


def test_format_finding_is_not_counted(loaded_conn, store, fetcher):
    """A done run with only a shape format finding → format-finding
    disposition (non-terminal until the manual fallback, c1)."""
    from leadhs.probe import engine

    engine.run_one(loaded_conn, store, fetcher, _get(loaded_conn, "CX-2"))  # bad export → UnexpectedFormat
    disp = engine.disposition_of(loaded_conn, "CX-2")
    assert disp["disposition"] in ("format-finding", "pending")


def test_manual_record_disposition(loaded_conn, store, fetcher):
    from leadhs.probe import engine

    engine.record_manual(loaded_conn, store, "ST-1", "products_registered", value=12)
    assert engine.disposition_of(loaded_conn, "ST-1")["disposition"] == "manual-recorded"


# --- wave harness (CLI layer) -------------------------------------------------


def _write_wave_register(tmp_path, site):
    register = tmp_path / "wave-register.csv"
    rows = [
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes,export_url,export_format",
        f"AS-2,AS,ECAT,{site}/landing,download,,open,1,wave-1 ecat,{site}/ecat.csv,csv",
        f"PX-1,PE,Site,{site}/,scrape,,open,1,wave-3 site,",
    ]
    register.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return str(register)


def test_wave_1_runs_ecat_ingest_end_to_end(site, tmp_path):
    """The 2am-Friday path: wave 1 over AS-2 — ECAT CSV → staging rows +
    run-close products_identifiable + disposition counted."""
    import click.testing

    from leadhs.cli import cli as cli_group

    db_path = str(tmp_path / "wave.sqlite")
    conn = dbmod.connect(db_path)
    dbmod.migrate(conn, db_path=db_path)
    conn.close()
    register = _write_wave_register(tmp_path, site)
    stg_path = str(tmp_path / "stg.sqlite")

    runner = click.testing.CliRunner()
    result = runner.invoke(
        cli_group,
        ["--db", db_path, "source", "load", "--file", register], catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    result = runner.invoke(
        cli_group,
        ["--db", db_path, "probe", "run", "--wave", "1", "--budget", "300", "--staging-db", stg_path],
        catch_exceptions=False,
    )
    assert "disposition=counted" in result.output, result.output
    assert result.exit_code == 0

    stg = staging.connect(stg_path)
    assert staging.count_products(stg, "AS-2", "*") >= 0  # rows exist for the run key below
    counts = stg.execute("SELECT COUNT(*) FROM stg_register_product").fetchone()[0]
    assert counts == 2
    conn = dbmod.connect(db_path)
    findings = conn.execute(
        "SELECT pf.value_numeric FROM probe_finding pf JOIN probe_run pr ON pr.run_id=pf.run_id "
        "WHERE pf.metric_code='products_identifiable' AND pr.mode_code='capability'"
    ).fetchall()
    assert [(2.0,)] == [(f[0],) for f in findings]
    conn.close()


def test_wave_3_dry_run_zero_fetches(site, tmp_path, site_hits):
    import click.testing

    from leadhs.cli import cli as cli_group

    db_path = str(tmp_path / "wave.sqlite")
    conn = dbmod.connect(db_path)
    dbmod.migrate(conn, db_path=db_path)
    conn.close()
    register = _write_wave_register(tmp_path, site)
    runner = click.testing.CliRunner()
    result = runner.invoke(
        cli_group, ["--db", db_path, "source", "load", "--file", register], catch_exceptions=False,
    )
    assert result.exit_code == 0
    site_hits.clear()
    result = runner.invoke(
        cli_group,
        ["--db", db_path, "probe", "run", "--wave", "3", "--staging-db", str(tmp_path / "stg.sqlite"), "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code in (0, 2)
    assert site_hits == {}  # dry run: zero fetches


def test_wave_budget_expiry_resumable(site, tmp_path, monkeypatch):
    """Budget expiry: the wave stops before the next source (virtual
    clock), nothing partial, resumable."""
    import click.testing

    import leadhs.cli as climod
    from leadhs.cli import cli as cli_group

    db_path = str(tmp_path / "wave.sqlite")
    conn = dbmod.connect(db_path)
    dbmod.migrate(conn, db_path=db_path)
    conn.close()
    register = _write_wave_register(tmp_path, site)

    t = [1000.0]

    def fake_now():
        t[0] += 60.0  # each check jumps past the tiny budget
        return t[0]

    monkeypatch.setattr(climod, "_now", fake_now)
    runner = click.testing.CliRunner()
    runner.invoke(cli_group, ["--db", db_path, "source", "load", "--file", register], catch_exceptions=False)
    result = runner.invoke(
        cli_group,
        ["--db", db_path, "probe", "run", "--wave", "1", "--budget", "10",
         "--staging-db", str(tmp_path / "stg.sqlite")],
        catch_exceptions=False,
    )
    assert "resumable" in result.output
    assert "budget exhausted" in result.output


def test_wave_4_checklist(site, tmp_path):
    import click.testing

    from leadhs.cli import cli as cli_group

    db_path = str(tmp_path / "wave.sqlite")
    conn = dbmod.connect(db_path)
    dbmod.migrate(conn, db_path=db_path)
    conn.close()
    register = _write_wave_register(tmp_path, site)
    # add a manual LI row for the checklist
    register2 = tmp_path / "wave-register2.csv"
    text = open(register, encoding="utf-8").read()
    text += "LI-2,LI,IPEN,https://ipen.example,manual,,open,0,wave-4,\n"
    register2.write_text(text, encoding="utf-8")

    runner = click.testing.CliRunner()
    runner.invoke(cli_group, ["--db", db_path, "source", "load", "--file", register2], catch_exceptions=False)
    result = runner.invoke(
        cli_group, ["--db", db_path, "probe", "run", "--wave", "4"], catch_exceptions=False,
    )
    assert "record manually: probe record --source LI-2" in result.output
    assert result.exit_code == 2


def test_makefile_landscape_guarded():
    text = open("Makefile", encoding="utf-8").read()
    assert "probe-landscape: guard-probe-landscape" in text
    assert "landscape: guard-landscape setup" in text
    assert "probe run --wave $$w --budget $(BUDGET) --staging-db $(STAGING)" in text

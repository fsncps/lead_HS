"""Engine ingest path (e1/fu2): staged rows ride ProbeResult; staging
written before evidence; run-close derivation == staging count;
counted-0 semantics; staging required."""

import json

import pytest

from leadhs import staging
from leadhs.models import DocumentDraft, ProbeContext, ProbeResult, StagedRow, StagedTradeRow, SourceRef
from leadhs.probe import adapters as adaptersmod
from leadhs.probe import engine


class _StubAdapter:
    key = "SX"

    def __init__(self, result):
        self.result = result

    def supports(self, source):
        return source.id == "SX-1"

    def probe(self, source, ctx):
        return self.result


@pytest.fixture()
def sx_source(loaded_conn):
    return SourceRef(id="SX-1", class_code="AS", name="staged export", url="https://sx.example/export.csv",
                     access_method_code="download", active=1)


@pytest.fixture()
def stg_conn(tmp_path):
    conn = staging.connect(str(tmp_path / "stg.sqlite"))
    staging.init(conn)
    return conn


def _run(loaded_conn, store, stg_conn, fetcher, adapter, sx_source):
    adaptersmod.registry.insert(0, adapter)
    try:
        return engine.run_one(loaded_conn, store, fetcher, sx_source, mode="capability", staging=stg_conn)
    finally:
        adaptersmod.registry.pop(0)


def test_staging_first_then_evidence(loaded_conn, store, stg_conn, fetcher, sx_source):
    doc = DocumentDraft(url="https://sx.example/export.csv", content=b"export", content_type="text/csv")
    result = ProbeResult(
        documents=[doc],
        staged_products=[
            StagedRow(manufacturer_raw="Acme GmbH", ident_raw="DE-1234", ident_hint="licence_no",
                      name="Paint A", category_raw="Paints", raw={"col": "x"}, document=doc),
            StagedRow(manufacturer_raw="Beier AG", ident_raw="", ident_hint="licence_no",
                      name="Paint  B", document=doc),
        ],
    )
    summary = _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    assert summary["status"] == "done"
    assert summary["staged"] == 2

    # staging side: rows + provenance document
    assert staging.count_products(stg_conn, "SX-1", summary["run_key"]) == 2
    registry = staging.doc_registry(stg_conn, "SX-1")
    assert len(registry) == 1 and registry[0]["retrieval_date"] and registry[0]["doc_hash"]

    # evidence side: the run-close derived finding IS the staging count
    findings = loaded_conn.execute(
        "SELECT pf.value_numeric, pf.notes FROM probe_finding pf JOIN run r ON r.id=pf.run_id "
        "WHERE r.run_key=? AND pf.metric_code='products_identifiable'",
        (summary["run_key"],),
    ).fetchall()
    assert len(findings) == 1
    assert findings[0][0] == 2.0
    assert "distinct_manufacturers=2" in findings[0][1]
    assert "identity_completeness_pct=50.0" in findings[0][1]


def test_counted_zero_semantics(loaded_conn, store, stg_conn, fetcher, sx_source):
    """c2: a legitimate empty export counts 0 with a note — no format
    finding, no pending row."""
    doc = DocumentDraft(url="https://sx.example/export.csv", content=b"empty export", content_type="text/csv")
    result = ProbeResult(documents=[doc], parameters={"staged_zero": "no in-scope rows (group 044 filter)"})
    summary = _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    assert summary["status"] == "done" and summary["staged"] == 0
    findings = loaded_conn.execute(
        "SELECT pf.value_numeric, pf.notes FROM probe_finding pf JOIN run r ON r.id=pf.run_id "
        "WHERE r.run_key=? AND pf.metric_code='products_identifiable'",
        (summary["run_key"],),
    ).fetchall()
    assert len(findings) == 1 and findings[0][0] == 0.0
    assert any("counted-0" in n for n in summary["notes"])
    assert len(staging.doc_registry(stg_conn, "SX-1")) == 1


def test_staged_rows_without_staging_db_fail_loudly(loaded_conn, store, fetcher, sx_source):
    doc = DocumentDraft(url="u", content=b"export", content_type="text/csv")
    result = ProbeResult(documents=[doc], staged_products=[StagedRow(ident_raw="X", document=doc)])
    adaptersmod.registry.insert(0, _StubAdapter(result))
    try:
        with pytest.raises(engine.EngineError) as exc:
            engine.run_one(loaded_conn, store, fetcher, sx_source, mode="capability", staging=None)
        assert "staging" in str(exc.value)
    finally:
        adaptersmod.registry.pop(0)


def test_staged_row_without_document_fails_loudly(loaded_conn, store, stg_conn, fetcher, sx_source):
    result = ProbeResult(staged_products=[StagedRow(ident_raw="X", document=None)])
    with pytest.raises(engine.EngineError):
        _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    assert staging.count_products(stg_conn, "SX-1", "any") == 0


def test_trade_rows_staged(loaded_conn, store, stg_conn, fetcher, sx_source):
    doc = DocumentDraft(url="https://sx.example/api.json", content=b"{}", content_type="application/json")
    result = ProbeResult(
        documents=[doc],
        staged_trade=[
            StagedTradeRow(cn8="32081010", flow="1", declarant="DE", partner="CN", year="2024", kg=10.0, eur=90.0, document=doc),
            StagedTradeRow(cn8="32091000", flow="1", declarant="FR", partner="CH", year="2024", kg=5.0, eur=40.0, document=doc),
        ],
    )
    summary = _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    assert summary["staged_trade"] == 2
    # trade sources get no products_identifiable derivation
    rows = loaded_conn.execute(
        "SELECT COUNT(*) FROM probe_finding pf JOIN run r ON r.id=pf.run_id "
        "WHERE r.run_key=? AND pf.metric_code='products_identifiable'",
        (summary["run_key"],),
    ).fetchone()
    assert rows[0] == 0
    n = stg_conn.execute("SELECT COUNT(*) FROM stg_trade_cn8 WHERE cn8='32081010'").fetchone()[0]
    assert n == 1


def test_interrupt_mid_ingest_no_orphans(loaded_conn, store, stg_conn, fetcher, sx_source):
    """Chaos: a crash during the staging write leaves no partial rows and
    the run is reclaimable — a re-run heals by replace."""
    doc = DocumentDraft(url="u", content=b"export", content_type="text/csv")

    class Boom(Exception):
        pass

    orig_replace = staging.replace_products

    def flaky(*a, **kw):
        raise Boom("interrupted mid-ingest")

    result = ProbeResult(
        documents=[doc],
        staged_products=[StagedRow(manufacturer_raw="A", ident_raw="X", document=doc)],
    )
    staging.replace_products = flaky
    adaptersmod.registry.insert(0, _StubAdapter(result))
    try:
        with pytest.raises(Boom):
            _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    finally:
        staging.replace_products = orig_replace
        adaptersmod.registry.pop(0)
    assert staging.count_products(stg_conn, "SX-1", "any") == 0


def test_rerun_stages_new_run_rows(loaded_conn, store, stg_conn, fetcher, sx_source):
    """Idempotent re-run: a second run stages its own rows; evidence
    per-run counts equal; nothing accumulates within a run."""
    doc = DocumentDraft(url="u", content=b"export", content_type="text/csv")
    result = ProbeResult(documents=[doc], staged_products=[StagedRow(manufacturer_raw="A", ident_raw="X", document=doc)])
    s1 = _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    s2 = _run(loaded_conn, store, stg_conn, fetcher, _StubAdapter(result), sx_source)
    assert s1["run_key"] != s2["run_key"]
    assert s1["staged"] == s2["staged"] == 1
    assert staging.count_products(stg_conn, "SX-1", s2["run_key"]) == 1

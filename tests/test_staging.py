"""Staging DB (L2, v0.2.2 t12 staging block): idempotent replace, loud
provenance failure, aggregates, dict seed, interruption atomicity."""

import pytest

from leadhs import normalize as normmod
from leadhs import staging


@pytest.fixture()
def stg(tmp_path):
    conn = staging.connect(str(tmp_path / "stg.sqlite"))
    staging.init(conn)
    return conn


def _doc(url="https://ecat.example/export.csv", doc_hash="a" * 64):
    return {"url": url, "doc_hash": doc_hash, "retrieval_date": "2026-09-14", "bytes": 100}


def _row(mfr="Acme GmbH", ident="DE-1234", hint="licence_no", name="Paint A", cat="Paints"):
    return {
        **normmod.identity(mfr, ident, hint, name),
        "category_raw": cat,
        "raw": '{"x": 1}',
    }


def test_idempotent_replace_counts_stable(stg):
    doc = _doc()
    n = staging.replace_products(stg, "AS-1", "probe-20260914-as1a1", doc, [_row(), _row(ident="DE-5678", name="Paint B")])
    assert n == 2
    # re-run with the same (source_id, run_key) — replace, not accumulate
    n = staging.replace_products(stg, "AS-1", "probe-20260914-as1a1", doc, [_row(), _row(ident="DE-5678", name="Paint B")])
    assert n == 2
    assert staging.count_products(stg, "AS-1", "probe-20260914-as1a1") == 2
    assert len(staging.doc_registry(stg, "AS-1")) == 1


def test_loud_failure_without_provenance(stg):
    with pytest.raises(staging.StagingError) as exc:
        staging.replace_products(stg, "AS-1", "run", {"url": "u", "doc_hash": None, "retrieval_date": "d"}, [_row()])
    assert "doc_hash" in str(exc.value)
    with pytest.raises(staging.StagingError):
        staging.replace_products(stg, "AS-1", "run", {"url": "u", "doc_hash": "h"}, [_row()])  # no retrieval_date
    assert staging.count_products(stg, "AS-1", "run") == 0  # nothing written


def test_interrupt_mid_write_leaves_no_partial_rows(stg):
    """Chaos: a failure mid-batch (constraint violation on row 11 of a
    10-row batch) leaves zero rows — the write is one transaction."""
    import sqlite3

    doc = _doc()
    rows = [_row(ident=f"DE-{i}") for i in range(10)]
    bad = _row(ident="DE-6")
    bad["ident_basis"] = "bogus"  # CHECK violation fires mid-batch
    with pytest.raises(sqlite3.IntegrityError):
        staging.replace_products(stg, "AS-1", "run", doc, rows + [bad])
    assert staging.count_products(stg, "AS-1", "run") == 0


def test_leading_zero_ident_round_trip(stg):
    """e4: TEXT affinity with explicit cast — '007' stays '007'."""
    doc = _doc(doc_hash="b" * 64)
    staging.replace_products(stg, "AS-1", "run", doc, [_row(ident="007")])
    row = stg.execute("SELECT ident_norm, typeof(ident_norm) FROM stg_register_product").fetchone()
    assert row["ident_norm"] == "007"
    assert row[1] == "text"


def test_run_close_aggregates(stg):
    doc = _doc()
    rows = [
        _row(mfr="Acme GmbH", ident="DE-1234", name="Paint A", cat="Paints"),
        _row(mfr="Acme GmbH", ident="DE-5678", name="Paint B", cat="Paints"),
        _row(mfr="Beier AG", ident="DE-9999", name="Paint C", cat="Lacquers"),
        _row(mfr="Nameless Oy", ident="", name="No Ident Paint", cat="Lacquers"),
    ]
    staging.replace_products(stg, "AS-1", "run", doc, rows)
    agg = staging.product_aggregates(stg, "AS-1", "run")
    assert agg["distinct_manufacturers"] == 3  # acme + beier + nameless
    assert agg["distinct_pairs"] == 4
    assert agg["identity_completeness_pct"] == 75.0  # 3 of 4 ident-based
    assert agg["categories"][0] == ("Paints", 2)


def test_trade_rows_and_dict(stg):
    doc = _doc(doc_hash="c" * 64)
    n = staging.replace_trade(
        stg, "CS-2", "run", doc,
        [{"cn8": "32081010", "flow": "1", "declarant": "DE", "partner": "CN", "year": "2024", "kg": 100.0, "eur": 500.0}],
    )
    assert n == 1
    assert staging.replace_trade(stg, "CS-2", "run", doc, []) == 0
    count = staging.seed_dict(stg)
    assert count == 13  # 9 × 3208 + 2 × 3209 core, 2 × 3213 annex
    heads = {r["hs_heading"] for r in stg.execute("SELECT hs_heading FROM dict_cn8 WHERE kind='core'")}
    assert heads == {"3208", "3209"}


def test_rebuild_from_archive_entry(stg):
    """c3: the staging layer is replace-based — re-ingesting the same
    archived document (same hash) restores identical counts."""
    doc = _doc(doc_hash="d" * 64)
    staging.replace_products(stg, "AS-1", "run", doc, [_row(), _row(ident="DE-2", name="B")])
    before = staging.doc_registry(stg, "AS-1")
    staging.replace_products(stg, "AS-1", "run", doc, [_row(), _row(ident="DE-2", name="B")])
    assert staging.doc_registry(stg, "AS-1") == before
    assert staging.count_products(stg, "AS-1", "run") == 2

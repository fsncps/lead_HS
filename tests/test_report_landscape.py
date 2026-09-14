"""v0.2.2 PHASE06: landscape report extension (od8) — funnel floor,
CN8 trade table, identity table + union + overlap, depth counts,
census, reconciliation flags; staging-conditional rendering (e5) and
visible flags (c4)."""

import json
import re

import pytest

from leadhs import report as reportmod
from leadhs import staging


@pytest.fixture()
def stg(tmp_path):
    conn = staging.connect(str(tmp_path / "stg.sqlite"))
    staging.init(conn)
    staging.seed_dict(conn)
    return conn


def _register_doc(source_id, run_key="probe-x"):
    return {"source_id": source_id, "run_key": run_key, "url": f"https://{source_id}.example/export.csv",
            "doc_hash": ("0" if source_id == "CS-2" else "2") * 64, "retrieval_date": "2026-09-14"}


def _stage_products(stg, source_id, rows, run_key="probe-x"):
    doc = _register_doc(source_id, run_key)
    staging.replace_products(stg, source_id, run_key, doc, rows)


def _rows(prefix, n, ident=True, cat="2014 criteria"):
    out = []
    for i in range(n):
        out.append({
            "manufacturer_raw": f"{prefix} GmbH",
            "manufacturer_norm": f"{prefix} gmbh",
            "ident_raw": f"LIC-{i:04d}" if ident else None,
            "ident_norm": f"lic{i:04d}" if ident else f"name{i:04d}",
            "ident_type": "licence" if ident else "none",
            "ident_basis": "ident" if ident else "name",
            "name": f"Product {prefix} {i}",
            "category_raw": cat,
        })
    return out


def test_funnel_q2_floor_and_ratio(stg, loaded_conn, store, fetcher):
    """Q2 = distinct pairs over staged registers (union); the pool model
    is M × ppp × s; the v0.5 ratio is floor ÷ modeled range, labeled."""
    _stage_products(stg, "AS-2", _rows("Acme", 10) + _rows("Acme", 5, cat="2025 criteria"))
    _stage_products(stg, "AS-3", _rows("Acme", 3))  # 3 pairs overlap with AS-2
    data = reportmod.build(loaded_conn, staging_conn=stg)
    fun = data["landscape"]["funnel"]
    assert fun["q2"]["value"] == 10  # 10 distinct pairs (Acme LIC-0000..0009)
    assert fun["q1"]["ppp"] == {"source_id": "AS-2", "pairs": 10, "manufacturers": 1, "ppp": 10.0}
    assert fun["q1"]["range"] == [10 * reportmod.POOL_M_LOW, 10 * reportmod.POOL_M_HIGH]
    assert fun["ratio"]["low"] == round(10 / (10 * reportmod.POOL_M_HIGH), 4)
    assert fun["ratio"]["high"] == round(10 / (10 * reportmod.POOL_M_LOW), 4)


def test_identity_table_union_and_overlap(stg, loaded_conn):
    _stage_products(stg, "AS-2", _rows("Acme", 10))
    _stage_products(stg, "AS-3", _rows("Acme", 3))
    data = reportmod.build(loaded_conn, staging_conn=stg)
    idt = data["landscape"]["identity"]
    assert {r["source_id"]: r["entries"] for r in idt["registers"]} == {"AS-2": 10, "AS-3": 3}
    assert idt["union"]["distinct_pairs"] == 10
    assert idt["overlap"]["computed"] is True
    assert idt["overlap"]["intersection"] == 3
    assert idt["overlap"]["containment"] == 1.0  # AS-3 ⊂ AS-2
    assert idt["overlap"]["jaccard"] == round(3 / 10, 4)


def test_overlap_absent_when_one_register_missing(stg, loaded_conn):
    _stage_products(stg, "AS-2", _rows("Acme", 5))
    data = reportmod.build(loaded_conn, staging_conn=stg)
    ov = data["landscape"]["identity"]["overlap"]
    assert ov["computed"] is False and "AS-3" in ov["note"]


def test_cn8_trade_table_and_flow_caveat(stg, loaded_conn):
    doc = {"source_id": "CS-2", "run_key": "probe-cs", "url": "https://example/api.json",
           "doc_hash": "1" * 64, "retrieval_date": "2026-09-14"}
    staging.replace_trade(stg, "CS-2", "probe-cs", doc, [
        {"cn8": "32081010", "flow": "1", "declarant": "DE", "partner": "CN", "year": "2024", "kg": 100.0, "eur": 500.0},
        {"cn8": "32081010", "flow": "2", "declarant": "DE", "partner": "CH", "year": "2024", "kg": 30.0, "eur": 200.0},
    ])
    data = reportmod.build(loaded_conn, staging_conn=stg)
    ct = data["landscape"]["cn8_trade"]
    assert ct["dict_verified"] == 0  # seeded unverified → caveat visible
    assert "flow codes not verified" in ct["flow_caveat"]
    by_flow = {(r["cn8"], r["flow"]): r for r in ct["rows"]}
    assert by_flow[("32081010", "1")]["kg"] == 100.0
    assert by_flow[("32081010", "2")]["kg"] == 30.0


def _insert_finding(conn, run_key, code, value):
    run_id = conn.execute("SELECT id FROM run WHERE run_key=?", (run_key,)).fetchone()[0]
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, method_code) VALUES (?, ?, ?, ?)",
        (run_id, code, value, "scrape"),
    )


def test_reconciliation_mismatch_flag_visible(stg, loaded_conn, store, fetcher):
    """c4: metric ≠ staged rows renders as a visible flag, never silence."""
    from leadhs.source import get_source
    from leadhs.probe import engine
    # a products_registered metric of 42 for a source with staged rows 5
    src = get_source(loaded_conn, "ST-1")
    result = engine.run_one(loaded_conn, store, fetcher, src, mode="capability")
    _insert_finding(loaded_conn, result["run_key"], "products_registered", 42)
    _stage_products(stg, "ST-1", _rows("Spin", 5))
    data = reportmod.build(loaded_conn, staging_conn=stg)
    flags = {f["source_id"]: f for f in data["landscape"]["reconciliation"]}
    assert flags["ST-1"]["kind"] == "mismatch"
    assert "42" in flags["ST-1"]["detail"] and "5" in flags["ST-1"]["detail"]
    md = reportmod.render(loaded_conn, staging_conn=stg)
    assert "⚠ **ST-1** (mismatch)" in md


def test_staging_absent_renders_note(loaded_conn):
    """e5: without staging the sections render as explicit notes."""
    md = reportmod.render(loaded_conn)
    assert "Staging DB not provided or empty" in md
    assert "renders only from the staging DB" in md
    data = json.loads(reportmod.render(loaded_conn, format="json"))
    assert data["landscape"]["staging_present"] is False
    assert data["landscape"]["funnel"]["q2"]["absent"] is True


def test_depth_counts_and_sds_urls(stg, loaded_conn, store, fetcher):
    from leadhs.source import get_source
    from leadhs.probe import engine
    # a capability run with an explicit depth tier + per-site SDS count
    src = get_source(loaded_conn, "ST-1")
    result = engine.run_one(loaded_conn, store, fetcher, src, mode="capability")
    _insert_finding(loaded_conn, result["run_key"], "cap_depth_tier", 2)
    _insert_finding(loaded_conn, result["run_key"], "sds_doc_urls", 7)
    data = reportmod.build(loaded_conn, staging_conn=stg)
    dep = data["landscape"]["depth"]
    assert dep["tier_counts"]["2"] == 1 and "ST-1" in dep["tier_members"]["2"]
    assert {"source_id": "ST-1", "sds_doc_urls": 7, "run_key": result["run_key"]} in dep["sds_counts"]
    assert "not a zero claim" in dep["note"]

"""Raw source layer (v0.3.0): instruction refusals, canonical hashing,
migration 0012, seed interpreter (upsert triple, truncation, checkpoints,
resume), scanner derivation, register sync — the RUNS.md r01–r03
provisional-test inputs."""

import hashlib
import json
import os

import pytest

from leadhs import db as dbmod
from leadhs.fetch import FetchConfig, Fetcher
from leadhs.raw import delivery_text
from leadhs.raw import interpreter as interp
from leadhs.raw import instructions as instmod
from leadhs.raw import scanner as scanmod
from leadhs.raw.interpreter import Pacer, SeedStats, apply_budget, row_hash, seed, upsert_record
from leadhs.raw.instructions import InstructionError, canonical_json, from_dict, load

from conftest import FakeClock


# --- instruction schema v1 -----------------------------------------------

def base_instruction(**over):
    doc = {
        "schema_version": 1,
        "source_id": "ZX-1",
        "source_name": "Fixture bulk source",
        "source_class": "AS",
        "export_kind": "csv_snapshot",
        "delimiter": ";",
        "endpoints": {"list": "https://fixture.invalid/export.csv", "detail": None},
        "pagination": {"kind": "single"},
        "records": {"expected_count": 3, "count_derivation": "scan: counted"},
        "columns": [
            {"source_header": "Licence", "column": "licence_number", "type": "text",
             "truncation_priority": 1, "description": "key"},
            {"source_header": "Product", "column": "product_name", "type": "text",
             "truncation_priority": 2},
        ],
        "natural_key": ["licence_number"],
        "payload_budget_bytes": 1024,
        "politeness": {
            "delay_seconds": 2.0, "request_budget_per_run": 5,
            "records_per_request": 3, "derivation": "1 fetch/run",
        },
        "notes": "test instruction",
    }
    doc.update(over)
    return doc


def test_valid_instruction_roundtrips_and_hashes_stably():
    inst = from_dict(base_instruction())
    shuffled = {k: base_instruction()[k] for k in reversed(list(base_instruction()))}
    assert from_dict(shuffled).manifest_hash() == inst.manifest_hash()
    text = canonical_json(inst.to_dict()).decode()
    assert text == json.dumps(json.loads(text), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _mutate(doc, key):
    if key == "unknown_schema_version":
        doc["schema_version"] = 2
    elif key == "delay_below_floor":
        doc["politeness"]["delay_seconds"] = 1.0
    elif key == "typo_in_politeness_field":
        doc["politeness"]["request_budegt_per_run"] = 5
    elif key == "typo_in_top_field":
        doc["natual_key"] = ["licence_number"]
    elif key == "undeclared_natural_key":
        doc["natural_key"] = ["nope"]
    elif key == "null_natural_key":
        doc["natural_key"] = None
    elif key == "empty_columns":
        doc["columns"] = []
    elif key == "duplicate_column":
        doc["columns"].append({"source_header": "Licence 2", "column": "licence_number",
                               "type": "text", "truncation_priority": 1})
    elif key == "duplicate_source_header":
        doc["columns"].append({"source_header": "Licence", "column": "licence_number_2",
                               "type": "text", "truncation_priority": 1})
    elif key == "reserved_underscore_column":
        doc["columns"].append({"source_header": "Hash", "column": "_row_hash",
                               "type": "text", "truncation_priority": 1})
    elif key == "zero_payload_budget":
        doc["payload_budget_bytes"] = 0
    elif key == "zero_request_budget":
        doc["politeness"]["request_budget_per_run"] = 0
    elif key == "unknown_export_kind":
        doc["export_kind"] = "web_form"
    elif key == "reserved_cursor_pagination":
        doc["pagination"]["kind"] = "cursor"
    elif key == "unknown_pagination_kind":
        doc["pagination"]["kind"] = "nonsense"
    elif key == "non_http_endpoint":
        doc["endpoints"]["list"] = "ftp://x/y"
    elif key == "multi_char_delimiter":
        doc["delimiter"] = ";;"
    elif key == "bad_source_id":
        doc["source_id"] = "bad-id"
    elif key == "negative_expected_count":
        doc["records"]["expected_count"] = -1
    elif key == "empty_count_derivation":
        doc["records"]["count_derivation"] = ""
    elif key == "empty_guard_derivation":
        doc["politeness"]["derivation"] = ""
    elif key == "missing_politeness":
        doc.pop("politeness")
    else:
        raise AssertionError(key)


_MUTATIONS = {
    "unknown_schema_version": "schema_version",
    "delay_below_floor": "delay_seconds",
    "typo_in_politeness_field": "unknown field",
    "typo_in_top_field": "unknown field",
    "undeclared_natural_key": "not a declared column",
    "null_natural_key": "must be an array",
    "empty_columns": "non-empty",
    "duplicate_column": "duplicate column",
    "duplicate_source_header": "duplicate",
    "reserved_underscore_column": "must not start with",
    "zero_payload_budget": "payload_budget_bytes",
    "zero_request_budget": "request_budget_per_run",
    "unknown_export_kind": "export_kind",
    "reserved_cursor_pagination": "cursor",
    "unknown_pagination_kind": "pagination.kind",
    "non_http_endpoint": "http(s) URL",
    "multi_char_delimiter": "delimiter",
    "bad_source_id": "source_id",
    "negative_expected_count": "expected_count",
    "empty_count_derivation": "count_derivation",
    "empty_guard_derivation": "derivation",
    "missing_politeness": "missing required",
}


@pytest.mark.parametrize("case", sorted(_MUTATIONS))
def test_refusal_matrix_names_the_field(case):
    doc = base_instruction()
    _mutate(doc, case)
    with pytest.raises(InstructionError) as exc:
        from_dict(doc)
    assert _MUTATIONS[case] in str(exc.value)


def test_reserved_kinds_validate_but_are_refused_by_interpreter():
    doc = base_instruction(export_kind="html_pages")
    inst = from_dict(doc)  # validator accepts
    assert inst.export_kind == "html_pages"


def test_load_missing_file_is_named(tmp_path):
    with pytest.raises(InstructionError) as exc:
        load(str(tmp_path / "nope.json"))
    assert "nope.json" in str(exc.value)


def test_load_unparsable_json_is_named(tmp_path):
    p = tmp_path / "broken.json"
    p.write_text("{oops", encoding="utf-8")
    with pytest.raises(InstructionError) as exc:
        load(str(p))
    assert "unparsable" in str(exc.value)


# --- migration 0012 -------------------------------------------------------

def test_migration_chain_complete_and_0012_idempotent(conn):
    files = dbmod.migration_files()
    numbers = [f[0] for f in files]
    assert numbers == list(range(1, 14))
    applied, _pending = dbmod.migrate(conn, db_path=":memory:")
    assert applied == []  # fresh conn fixture already migrated; idempotent
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"raw_export_kind", "raw_source_profile", "raw_as2_ecat", "raw_as3_nordic_swan", "raw_change",
            "manufacturer", "product", "identity_state", "linkage_candidate"} <= tables
    kinds = {r[0] for r in conn.execute("SELECT code FROM raw_export_kind")}
    assert kinds == {"csv_snapshot", "api_endpoint", "web_query", "html_pages"}
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


# --- truncation (rs8) -----------------------------------------------------

def _inst_for_budget(budget):
    return from_dict(base_instruction(payload_budget_bytes=budget))


def test_truncation_boundary_exactly_at_budget_and_one_over():
    inst = _inst_for_budget(100)
    # key 10 bytes + 90 bytes = exactly 100 -> untouched
    values = {"licence_number": "L" * 10, "product_name": "P" * 90}
    out, truncated = apply_budget(values, inst)
    assert not truncated and out == values
    out, truncated = apply_budget({"licence_number": "L" * 10, "product_name": "P" * 91}, inst)
    assert truncated
    assert out["licence_number"] == "L" * 10  # identity never truncated
    assert len(out["product_name"].encode()) <= 90


def test_truncation_priority_one_keeps_longest_and_is_deterministic():
    doc = base_instruction(payload_budget_bytes=50)
    doc["columns"] = [
        {"source_header": "Licence", "column": "licence_number", "type": "text", "truncation_priority": 3},
        {"source_header": "Product", "column": "product_name", "type": "text", "truncation_priority": 2},
        {"source_header": "Note", "column": "note", "type": "text", "truncation_priority": 1},
    ]
    doc["natural_key"] = ["product_name"]
    inst = from_dict(doc)
    values = {"licence_number": "A" * 40, "product_name": "B" * 5, "note": "C" * 40}
    out1, flag1 = apply_budget(values, inst)
    out2, flag2 = apply_budget(dict(values), inst)
    assert out1 == out2 and flag1 is flag2 is True
    assert out1["note"] == "C" * 40        # priority 1 keeps longest
    assert out1["product_name"] == "B" * 5
    assert out1["licence_number"] is not None and len(out1["licence_number"]) < 40


def test_row_hash_flips_when_truncation_changes():
    inst = _inst_for_budget(100)
    short = {"licence_number": "L", "product_name": "P" * 50}
    long = {"licence_number": "L", "product_name": "P" * 200}
    s, t1 = apply_budget(short, inst)
    l, t2 = apply_budget(long, inst)
    assert t1 is False and t2 is True
    assert row_hash(s) != row_hash(l)


# --- seed interpreter ------------------------------------------------------

def _load_register_and_run(conn, source_id="ZX-1"):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code, active) "
        "VALUES (?, 'AS', 'Fixture', 'https://fixture.invalid', 'download', 1)",
        (source_id,),
    )
    probe_run = conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code, parameters_json) "
        "VALUES ('acquire-20261003-zx1raw', 'acquire', ?, '2026-10-03T00:00:00Z', 'running', "
        "'{\"instruction_hash\": \"x\", \"table\": \"raw_zx1\", \"cursor\": null, \"complete\": false}') "
        "RETURNING id",
        (source_id,),
    ).fetchone()[0]
    conn.commit()
    return probe_run


def _zx_instruction(columns_over=None, natural_key=None):
    doc = base_instruction()
    if columns_over is not None:
        doc["columns"] = columns_over
    if natural_key is not None:
        doc["natural_key"] = natural_key
    return from_dict(doc)


def test_upsert_triple_insert_update_journal_skip(conn):
    run_id = _load_register_and_run(conn)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, licence_number TEXT, product_name TEXT, "
        "_row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    inst = _zx_instruction()
    stats = SeedStats()
    v1 = {"licence_number": "DE-1", "product_name": "Paint A"}
    upsert_record(conn, inst, "raw_zx1", v1, run_id, stats)
    assert stats.inserted == 1
    # identical -> skip
    upsert_record(conn, inst, "raw_zx1", dict(v1), run_id, stats)
    assert stats.skipped == 1 and stats.updated == 0
    # changed -> update + exactly one journal row
    upsert_record(conn, inst, "raw_zx1", {"licence_number": "DE-1", "product_name": "Paint A2"}, run_id, stats)
    assert stats.updated == 1
    journal = conn.execute("SELECT old_hash, new_hash, run_id FROM raw_change").fetchall()
    assert len(journal) == 1 and journal[0]["run_id"] == run_id
    assert journal[0]["old_hash"] != journal[0]["new_hash"]
    row = conn.execute("SELECT product_name, _row_hash, _truncated FROM raw_zx1").fetchone()
    assert row["product_name"] == "Paint A2"


def test_upsert_truncation_flag_flips_hash_and_journal(conn):
    run_id = _load_register_and_run(conn)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, licence_number TEXT, product_name TEXT, "
        "_row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    doc = base_instruction(payload_budget_bytes=30)
    inst = from_dict(doc)
    stats = SeedStats()
    upsert_record(conn, inst, "raw_zx1", {"licence_number": "L", "product_name": "short"}, run_id, stats)
    first = conn.execute("SELECT _row_hash, _truncated FROM raw_zx1").fetchone()
    assert first["_truncated"] == 0
    upsert_record(conn, inst, "raw_zx1", {"licence_number": "L", "product_name": "P" * 100}, run_id, stats)
    second = conn.execute("SELECT _row_hash, _truncated FROM raw_zx1").fetchone()
    assert second["_truncated"] == 1
    assert second["_row_hash"] != first["_row_hash"]  # truncation change flips the hash
    assert conn.execute("SELECT COUNT(*) FROM raw_change").fetchone()[0] == 1


def test_degraded_row_hash_identity_mode(conn):
    """Empty natural_key = data_model degraded mode: row hash is the
    identity — inserts only, byte-identical duplicates collapse,
    changed content inserts."""
    run_id = _load_register_and_run(conn)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, licence_number TEXT, product_name TEXT, "
        "_row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    inst = from_dict(base_instruction(natural_key=[]))
    stats = SeedStats()
    v = {"licence_number": "DE-1", "product_name": "Paint A"}
    upsert_record(conn, inst, "raw_zx1", dict(v), run_id, stats)
    upsert_record(conn, inst, "raw_zx1", dict(v), run_id, stats)  # byte-identical dup collapses
    assert stats.inserted == 1 and stats.skipped == 1 and stats.updated == 0
    upsert_record(conn, inst, "raw_zx1", {"licence_number": "DE-1", "product_name": "Paint A2"}, run_id, stats)
    assert stats.inserted == 2 and stats.updated == 0  # changed content inserts, never updates
    assert conn.execute("SELECT COUNT(*) FROM raw_change").fetchone()[0] == 0  # no journal in degraded mode


def test_seed_csv_snapshot_end_to_end_verbatim(conn, site, make_fetcher):
    run_id = _load_register_and_run(conn)
    doc = {
        "schema_version": 1,
        "source_id": "ZX-1",
        "source_name": "Fixture Nordic",
        "source_class": "AS",
        "export_kind": "csv_snapshot",
        "delimiter": ";",
        "endpoints": {"list": f"{site}/ns-pool.csv", "detail": None},
        "pagination": {"kind": "single"},
        "records": {"expected_count": 62, "count_derivation": "scan"},
        "columns": [
            {"source_header": h, "column": c, "type": "text", "truncation_priority": 1}
            for h, c in [
                ("Product", "product"), ("License number", "license_number"),
                ("Ecolabel", "ecolabel"), ("Category", "category"),
                ("Product group", "product_group"), ("Criteria generation", "criteria_generation"),
                ("Brand", "brand"), ("Licensee", "licensee"), ("Address", "address"), ("City", "city"),
            ]
        ],
        "natural_key": ["product"],
        "payload_budget_bytes": 1024,
        "politeness": {"delay_seconds": 2.0, "request_budget_per_run": 3,
                       "records_per_request": 62, "derivation": "1 fetch"},
    }
    inst = from_dict(doc)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, product TEXT, license_number TEXT, ecolabel TEXT, "
        "category TEXT, product_group TEXT, criteria_generation TEXT, brand TEXT, licensee TEXT, "
        "address TEXT, city TEXT, _row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    fetcher = make_fetcher()
    clock = FakeClock()
    stats = seed(conn, fetcher, inst, run_id, "raw_zx1",
                 pacer=Pacer(inst.politeness.delay_seconds, clock.now, clock.sleep))
    assert stats.records == 62
    assert stats.inserted == 22 and stats.skipped == 40  # 20 pool paints + 2 out-of-scope rows, 3x each
    # verbatim: the multi-licence string stays one string; "." stays "."
    row = conn.execute("SELECT license_number, category FROM raw_zx1 WHERE product LIKE 'TURBON%'").fetchone()
    assert row["license_number"] == "3008 0046 (308046)"
    # idempotent rerun: everything skips, nothing changes
    stats2 = seed(conn, fetcher, inst, run_id, "raw_zx1",
                  pacer=Pacer(inst.politeness.delay_seconds, clock.now, clock.sleep))
    assert stats2.inserted == 0 and stats2.updated == 0 and stats2.skipped == 62


def test_seed_page_param_with_checkpoint_resume(conn, site, make_fetcher):
    run_id = _load_register_and_run(conn)
    doc = {
        "schema_version": 1,
        "source_id": "ZX-1",
        "source_name": "Fixture API",
        "source_class": "AS",
        "export_kind": "api_endpoint",
        "delimiter": ",",
        "endpoints": {"list": f"{site}/api-articles", "detail": None},
        "pagination": {"kind": "page_param", "page_param": "page", "page_size": 2, "max_pages": None},
        "records": {"expected_count": None, "count_derivation": "scan: no total field"},
        "columns": [
            {"source_header": "articleName", "column": "article_name", "type": "text", "truncation_priority": 1},
            {"source_header": "articleNumber", "column": "article_number", "type": "text", "truncation_priority": 1},
            {"source_header": "company", "column": "company", "type": "text", "truncation_priority": 2},
        ],
        "natural_key": ["article_number"],
        "payload_budget_bytes": 1024,
        "politeness": {"delay_seconds": 2.0, "request_budget_per_run": 10,
                       "records_per_request": 2, "derivation": "paged"},
    }
    inst = from_dict(doc)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, article_name TEXT, article_number TEXT, company TEXT, "
        "_row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    fetcher = make_fetcher()
    clock = FakeClock()
    pacer = Pacer(inst.politeness.delay_seconds, clock.now, clock.sleep)

    # page 1 only, then "interrupt": cap=2 stops after the first page;
    # a checkpoint cursor exists -> an unfinished run is detected
    state_before = json.loads(conn.execute("SELECT parameters_json FROM run WHERE id=?", (run_id,)).fetchone()[0])
    assert state_before["cursor"] is None
    seed(conn, fetcher, inst, run_id, "raw_zx1", cap=2, pacer=pacer)
    state = json.loads(conn.execute("SELECT parameters_json FROM run WHERE id=?", (run_id,)).fetchone()[0])
    assert state["complete"] is True and state["records"] == 2  # cap-reached exits complete

    # real partial state: forge the checkpoint like an interrupt would leave it
    state.update({"complete": False, "cursor": {"next": 2}, "records": 2})
    conn.execute("UPDATE run SET parameters_json=? WHERE id=?", (json.dumps(state), run_id))
    conn.commit()
    unfinished = interp.find_unfinished_run(conn, "ZX-1")
    assert unfinished is not None and unfinished["id"] == run_id

    # resume: continues at page 2, no duplicates, reaches the end
    stats = seed(conn, fetcher, inst, run_id, "raw_zx1", pacer=pacer)
    assert stats.records == 4  # pages 2-4 carry the remaining items (2+2+0-empty stop)
    assert conn.execute("SELECT COUNT(*) FROM raw_zx1").fetchone()[0] == 6
    assert interp.find_unfinished_run(conn, "ZX-1") is None  # complete=True now


def test_json_scalar_projection_is_verbatim_json(conn, site, make_fetcher):
    run_id = _load_register_and_run(conn)
    doc = {
        "schema_version": 1,
        "source_id": "ZX-1",
        "source_name": "Fixture API meta",
        "source_class": "AS",
        "export_kind": "api_endpoint",
        "delimiter": ",",
        "endpoints": {"list": f"{site}/basta.json", "detail": None},
        "pagination": {"kind": "single"},
        "records": {"expected_count": 2, "count_derivation": "scan"},
        "columns": [
            {"source_header": "articleNumber", "column": "article_number", "type": "text", "truncation_priority": 1},
            {"source_header": "gtin", "column": "gtin", "type": "text", "truncation_priority": 1},
            {"source_header": "company", "column": "company", "type": "text", "truncation_priority": 1},
        ],
        "natural_key": ["article_number"],
        "payload_budget_bytes": 1024,
        "politeness": {"delay_seconds": 2.0, "request_budget_per_run": 3, "derivation": "1 fetch"},
    }
    inst = from_dict(doc)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, article_number TEXT, gtin TEXT, company TEXT, "
        "_row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    clock = FakeClock()
    seed(conn, make_fetcher(), inst, run_id, "raw_zx1",
         pacer=Pacer(inst.politeness.delay_seconds, clock.now, clock.sleep))
    row = conn.execute("SELECT gtin, company FROM raw_zx1 WHERE article_number='AR-0002'").fetchone()
    assert row["gtin"] == "" and row["company"] == "Acme AB"


def test_json_dotpath_projection_is_verbatim(conn, site, make_fetcher):
    run_id = _load_register_and_run(conn)
    doc = {
        "schema_version": 1,
        "source_id": "ZX-1",
        "source_name": "Fixture API meta",
        "source_class": "AS",
        "export_kind": "api_endpoint",
        "delimiter": ",",
        "endpoints": {"list": f"{site}/basta-nested.json", "detail": None},
        "pagination": {"kind": "single"},
        "records": {"expected_count": 2, "count_derivation": "scan"},
        "columns": [
            {"source_header": "id", "column": "src_id", "type": "text", "truncation_priority": 1},
            {"source_header": "company.name", "column": "company_name", "type": "text", "truncation_priority": 1},
            {"source_header": "bk04.code", "column": "bk04_code", "type": "text", "truncation_priority": 1},
            {"source_header": "bk04.missing.deep", "column": "bk04_missing", "type": "text", "truncation_priority": 1},
            {"source_header": "company", "column": "company_full", "type": "text", "truncation_priority": 1},
        ],
        "natural_key": ["src_id"],
        "payload_budget_bytes": 1024,
        "politeness": {"delay_seconds": 2.0, "request_budget_per_run": 3, "derivation": "1 fetch"},
    }
    inst = from_dict(doc)
    conn.execute(
        "CREATE TABLE raw_zx1 (id INTEGER PRIMARY KEY, src_id TEXT, company_name TEXT, bk04_code TEXT, "
        "bk04_missing TEXT, company_full TEXT, "
        "_row_hash TEXT NOT NULL, _first_run_id INTEGER, _last_run_id INTEGER, "
        "_last_changed_run_id INTEGER, _truncated INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    clock = FakeClock()
    seed(conn, make_fetcher(), inst, run_id, "raw_zx1",
         pacer=Pacer(inst.politeness.delay_seconds, clock.now, clock.sleep))
    row = conn.execute("SELECT * FROM raw_zx1 WHERE src_id='1'").fetchone()
    assert row["company_name"] == "Acme AB"
    assert row["bk04_code"] == "211"
    assert row["bk04_missing"] is None  # missing link projects None, never an error
    assert json.loads(row["company_full"]) == {"name": "Acme AB", "url": None}  # container stays verbatim JSON


# --- init phase (rs6) --------------------------------------------------------

def test_register_sync_warning_for_new_source(conn):
    inst = _zx_instruction()
    warnings = interp.ensure_source_row(conn, inst)
    assert any("register of record" in w for w in warnings)
    row = conn.execute("SELECT id, access_method_code FROM source WHERE id='ZX-1'").fetchone()
    assert row is not None and row["access_method_code"] == "download"


def test_register_metadata_mismatch_warns_but_never_clobbers(conn):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code, active) "
        "VALUES ('ZX-1', 'AS', 'Register Name', 'https://fixture.invalid', 'download', 1)"
    )
    conn.commit()
    inst = _zx_instruction()  # source_name differs
    warnings = interp.ensure_source_row(conn, inst)
    assert any("register of record wins" in w for w in warnings)
    assert conn.execute("SELECT name FROM source WHERE id='ZX-1'").fetchone()[0] == "Register Name"


def test_ensure_table_from_instruction_columns(conn):
    inst = _zx_instruction()
    created = interp.ensure_table(conn, inst, "raw_zx1")
    assert created
    cols = {r[1] for r in conn.execute("PRAGMA table_info(raw_zx1)")}
    assert {"licence_number", "product_name", "_row_hash", "_truncated"} <= cols
    assert interp.ensure_table(conn, inst, "raw_zx1") is False  # idempotent


def test_profile_row_upsert(conn):
    _load_register_and_run(conn)
    inst = _zx_instruction()
    interp.ensure_profile_row(conn, inst, "raw_zx1")
    row = conn.execute("SELECT * FROM raw_source_profile").fetchone()
    assert row["source_id"] == "ZX-1" and row["table_name"] == "raw_zx1"
    assert row["manifest_hash"] == inst.manifest_hash()
    assert json.loads(row["natural_key_json"]) == ["licence_number"]
    interp.ensure_profile_row(conn, inst, "raw_zx1_other")
    assert conn.execute("SELECT COUNT(*) FROM raw_source_profile").fetchone()[0] == 1


# --- scanner derivation -------------------------------------------------------

def test_snake_case_and_collisions():
    taken = set()
    assert scanmod.snake_case("License number", taken) == "license_number"
    assert scanmod.snake_case("License number", taken) == "license_number_2"
    assert scanmod.snake_case("2024 data", taken) == "c2024_data"
    assert scanmod.snake_case("___", taken) == "col"


def test_guess_type():
    assert scanmod._guess_type(["1", "2", "-3"]) == "int"
    assert scanmod._guess_type(["1.5", "2"]) == "float"
    assert scanmod._guess_type(["2024-01-02", "2023-12-31"]) == "date_iso"
    assert scanmod._guess_type(["Paint A", "x"]) == "text"
    assert scanmod._guess_type([]) == "text"


def test_guard_derivation_flood_boundary():
    prof = scanmod.ScanProfile(source_id="ZX-1", url="https://x/y.csv", export_kind="csv_snapshot")
    prof.records_per_request = 10
    guards = scanmod.derive_guards(prof)
    assert guards["delay_seconds"] == 2.0 and "flood" not in guards["derivation"]
    prof.records_per_request = 9
    guards = scanmod.derive_guards(prof)
    assert guards["delay_seconds"] == 5.0 and "flood guard" in guards["derivation"]
    prof.crawl_delay = 10.0
    guards = scanmod.derive_guards(prof)
    assert guards["delay_seconds"] == 10.0 and guards["crawl_delay_seconds"] == 10.0


def test_drift_line_vs_pinned_keyfigure(conn):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code, active) "
        "VALUES ('ZX-1', 'AS', 'X', 'https://fixture.invalid', 'download', 1)"
    )
    run_row = conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20261003-zx1', 'probe', 'ZX-1', '2026-10-03T00:00:00Z', 'done') RETURNING id"
    ).fetchone()[0]
    conn.execute("INSERT INTO probe_run (run_id, mode_code) VALUES (?, 'census')", (run_row,))
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, method_code) "
        "VALUES (?, 'catalog_count', 100, 'api')", (run_row,)
    )
    conn.commit()
    assert scanmod.drift_line(conn, "ZX-1", 100) == "drift: none (matches pinned catalog_count 100)"
    line = scanmod.drift_line(conn, "ZX-1", 95)
    assert line and "95" in line and "100" in line and "-5" in line
    assert scanmod.drift_line(conn, "ZX-1", None) is None


# --- pacer -----------------------------------------------------------------

def test_pacer_spaces_request_starts():
    clock = FakeClock()
    pacer = Pacer(2.5, clock.now, clock.sleep)
    pacer.wait()  # immediate
    assert clock.t == 1000.0
    pacer.wait()
    assert clock.t == 1002.5
    pacer.wait()
    assert clock.t == 1005.0


def test_scan_refuses_error_page_deliveries(site, make_fetcher):
    """Live-found bug: a 404 HTML page must never be profiled as a CSV
    delivery (the route is dead — named refusal, scan exit 2)."""
    from types import SimpleNamespace

    fetcher = make_fetcher()
    src = SimpleNamespace(id="ZX-1", class_code="AS", name="X", url=site,
                          access_method_code="download", export_url=None, export_format=None)
    with pytest.raises(scanmod.ScanError) as exc:
        scanmod.scan_delivery(fetcher, src, f"{site}/missing")
    assert "HTTP 404" in str(exc.value)


def test_delivery_text_utf8_first_and_bom_stripped():
    """Live-found rule (AS-2 2026-10-03): text/csv without charset +
    UTF-8 content must decode UTF-8 (BOM stripped), never ISO-8859-1."""

    class Resp:
        content = "product_or_service;søborg".encode("utf-8")
        encoding = "ISO-8859-1"
        text = "product_or_service;sÃ¸borg"

    assert delivery_text(Resp()) == "product_or_service;søborg"

    class NonUtf8:
        content = b"\xff\xfe broken"
        encoding = "ISO-8859-1"
        text = "dec-fallback"

    assert delivery_text(NonUtf8()) == "dec-fallback"

    class Utf8Declared:
        content = "søborg".encode("utf-8")
        encoding = "utf-8"
        text = "søborg"

    assert delivery_text(Utf8Declared()) == "søborg"


def test_resolve_table_name_finds_pinned_tables(conn):
    assert scanmod.resolve_table_name(conn, "AS-2") == "raw_as2_ecat"
    assert scanmod.resolve_table_name(conn, "AS-3") == "raw_as3_nordic_swan"
    assert scanmod.resolve_table_name(conn, "AS-99") == "raw_as99"

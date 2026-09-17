"""Migrations: fresh apply, idempotency, order, CHECKs, backup round-trip."""

import os
import sqlite3

import pytest

from leadhs import db as dbmod


def test_fresh_apply_all_migrations(conn):
    applied = {r[0] for r in conn.execute("SELECT version FROM schema_version")}
    assert applied == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in ("source", "document", "run", "probe_run", "probe_finding", "probe_metric"):
        assert table in tables
    views = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view'")}
    assert {"v_probe_latest", "v_anchor_candidates", "v_source_activity"} <= views


def test_0003_metric_seeds_present(conn):
    codes = {r[0] for r in conn.execute("SELECT code FROM probe_metric")}
    assert {"records_hs3208", "records_hs3209", "records_hs3213", "census_status"} <= codes
    types = dict(conn.execute("SELECT code, value_type FROM probe_metric WHERE code LIKE 'records_hs%' OR code = 'census_status'").fetchall())
    assert types == {"records_hs3208": "numeric", "records_hs3209": "numeric",
                     "records_hs3213": "numeric", "census_status": "text"}


def test_0004_walk_metric_seeds_present(conn):
    """0004/D28: the walk metrics are seeded, all numeric."""
    codes = {r[0] for r in conn.execute("SELECT code FROM probe_metric")}
    assert {"products_listed", "doc_links_seen", "walk_budget_exhausted"} <= codes
    types = dict(conn.execute(
        "SELECT code, value_type FROM probe_metric WHERE code IN "
        "('products_listed', 'doc_links_seen', 'walk_budget_exhausted')"
    ).fetchall())
    assert types == {"products_listed": "numeric", "doc_links_seen": "numeric",
                     "walk_budget_exhausted": "numeric"}


def test_0004_view_includes_products_listed(conn):
    """v_anchor_candidates redefined (dm11): products_listed is an anchor
    candidate; doc_links_seen is not (U13)."""
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('PE-9','PE','n','u','scrape')")
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260912-pe9','probe','PE-9','2026-09-12T00:00:00Z','done')"
    )
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, unit_code, method_code) "
        "SELECT id, 'products_listed', 6, 'count', 'scrape' FROM run WHERE run_key = 'probe-20260912-pe9'"
    )
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, unit_code, method_code) "
        "SELECT id, 'doc_links_seen', 1, 'count', 'scrape' FROM run WHERE run_key = 'probe-20260912-pe9'"
    )
    conn.commit()
    codes = {r[0] for r in conn.execute("SELECT metric_code FROM v_anchor_candidates WHERE source_id = 'PE-9'")}
    assert codes == {"products_listed"}


def test_0004_prunes_lg_li_rows_with_evidence(tmp_path):
    """0004/D28 register slim: LG-*/LI-* rows and their runs/findings/
    documents are pruned; product rows survive."""
    conn = dbmod.connect(str(tmp_path / "x.sqlite"))
    orig = dbmod.migration_files
    dbmod.migration_files = lambda: [m for m in orig() if m[0] <= 3]
    try:
        applied, _ = dbmod.migrate(conn)
        assert applied == ["0001__probe_base.sql", "0002__probe_core.sql", "0003__probe_metrics.sql"]
    finally:
        dbmod.migration_files = orig

    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('PE-9','PE','n','u','scrape')")
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('LG-9','LG','n','u','download')")
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('LI-9','LI','n','u','download')")
    for sid in ("PE-9", "LG-9", "LI-9"):
        conn.execute(
            "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code, finished_at) "
            "VALUES (?, 'probe', ?, '2026-09-11T00:00:00Z', 'done', '2026-09-11T00:01:00Z')",
            (f"probe-20260911-{sid.lower().replace('-', '')}", sid),
        )
        conn.execute(
            "INSERT INTO document (source_id, run_id, url, retrieved_at, status_code, retrieval_method_code) "
            f"SELECT '{sid}', id, 'u', '2026-09-11T00:00:00Z', 'manual', 'manual' FROM run WHERE source_id = '{sid}'"
        )
        conn.execute(
            "INSERT INTO probe_finding (run_id, metric_code, value_text, method_code) "
            "SELECT id, 'census_status', 'x', 'manual' FROM run WHERE source_id = ?",
            (sid,),
        )
    conn.commit()

    applied, _ = dbmod.migrate(conn)
    assert applied == ["0004__product_census.sql", "0005__priors_metric.sql", "0006__recon_numbers.sql", "0007__capability.sql", "0008__landscape.sql", "0009__csv_sample.sql", "0010__as_source_probe.sql", "0011__basta_probe.sql"]

    ids = {r[0] for r in conn.execute("SELECT id FROM source")}
    assert "LG-9" not in ids and "LI-9" not in ids and "PE-9" in ids
    assert conn.execute("SELECT COUNT(*) FROM run WHERE source_id LIKE 'LG-%' OR source_id LIKE 'LI-%'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM document WHERE source_id LIKE 'LG-%' OR source_id LIKE 'LI-%'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM probe_finding pf JOIN run r ON r.id = pf.run_id WHERE r.source_id = 'LG-9'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM probe_finding pf JOIN run r ON r.id = pf.run_id WHERE r.source_id = 'PE-9'").fetchone()[0] == 1
    conn.close()


def test_0003_view_redefined(conn):
    """v_anchor_candidates includes the records_hs* codes (od10)."""
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-9','CS','n','u','api')")
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260911-cs9','probe','CS-9','2026-09-11T00:00:00Z','done')"
    )
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, method_code) "
        "SELECT id, 'records_hs3208', 7, 'api' FROM run WHERE run_key = 'probe-20260911-cs9'"
    )
    conn.commit()
    rows = conn.execute("SELECT metric_code FROM v_anchor_candidates WHERE source_id = 'CS-9'").fetchall()
    assert [r[0] for r in rows] == ["records_hs3208"]


def test_reinit_idempotent(conn, db_path):
    applied, pending = dbmod.migrate(conn, db_path=db_path)
    assert applied == []
    assert pending == []


def test_migration_order_enforced(tmp_path):
    """A gap in applied versions is detected: 0002/0003 apply in order on a
    DB that claims only 0001 (whose tables really exist)."""
    conn = dbmod.connect(str(tmp_path / "x.sqlite"))
    try:
        conn.executescript(next(sql for num, _, sql in dbmod.migration_files() if num == 1))
        conn.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)")
        conn.execute("INSERT INTO schema_version VALUES (1, '0001__probe_base.sql', '2026-01-01T00:00:00Z')")
        conn.commit()
        applied, pending = dbmod.migrate(conn)
        assert applied == ["0002__probe_core.sql", "0003__probe_metrics.sql",
                           "0004__product_census.sql", "0005__priors_metric.sql",
                           "0006__recon_numbers.sql", "0007__capability.sql",
                           "0008__landscape.sql", "0009__csv_sample.sql",
                           "0010__as_source_probe.sql", "0011__basta_probe.sql"]
    finally:
        conn.close()


def test_check_probe_run_requires_source(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO run (run_key, kind_code, started_at) VALUES ('probe-20260910-x', 'probe', '2026-09-10T00:00:00Z')"
        )


def test_check_document_requires_run(conn):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')"
    )
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at) VALUES ('probe-20260910-cs1','probe','CS-1','2026-09-10T00:00:00Z')"
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO document (source_id, run_id, url, retrieved_at) VALUES ('CS-1', NULL, 'u', '2026-09-10T00:00:00Z')"
        )


def test_run_default_status_planned(conn):
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')"
    )
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at) VALUES ('probe-20260910-cs1','probe','CS-1','2026-09-10T00:00:00Z')"
    )
    conn.commit()
    status = conn.execute("SELECT status_code FROM run WHERE run_key='probe-20260910-cs1'").fetchone()[0]
    assert status == "planned"


def test_source_id_glob_check(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('bad','CS','n','u','api')"
        )


def test_backup_round_trip(conn, db_path):
    """Seed a DB, add a pending migration, migrate -> timestamped backup
    restores a working DB with the seeded rows and without the new table."""
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')"
    )
    conn.commit()
    conn.close()

    orig = dbmod.migration_files
    dbmod.migration_files = lambda: orig() + [(12, "0012__fake.sql", "CREATE TABLE fake (x INTEGER);")]
    try:
        conn2 = dbmod.connect(db_path)
        applied, _ = dbmod.migrate(conn2, db_path=db_path)
        assert applied == ["0012__fake.sql"]
        conn2.close()
    finally:
        dbmod.migration_files = orig

    backup_dir = os.path.join(os.path.dirname(db_path), "backups")
    backups = os.listdir(backup_dir)
    assert len(backups) == 1
    backup_path = os.path.join(backup_dir, backups[0])
    with open(backup_path, "rb") as fh:
        header = fh.read(32)
    backup_conn = sqlite3.connect(backup_path)
    try:
        tables = [r[0] for r in backup_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert "source" in tables, f"header={header!r} tables={tables}"
        assert backup_conn.execute("SELECT COUNT(*) FROM source").fetchone()[0] == 1
        assert backup_conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='fake'").fetchone()[0] == 0
    finally:
        backup_conn.close()


def test_no_backup_on_fresh_db(conn, db_path):
    backups_dir = os.path.join(os.path.dirname(db_path), "backups")
    assert not os.path.exists(backups_dir) or os.listdir(backups_dir) == []


# --- v0.2.0: 0005 priors metric, 0006 recon/numbers ------------------------


def test_0005_priors_metric_seeded(conn):
    row = conn.execute(
        "SELECT label, value_type FROM probe_metric WHERE code = 'products_registered'"
    ).fetchone()
    assert (row[0], row[1]) == ("Products registered (prior)", "numeric")


def test_0005_view_includes_products_registered(conn):
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('ST-9','ST','n','u','api')")
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260912-st9','probe','ST-9','2026-09-12T00:00:00Z','done')"
    )
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, unit_code, method_code) "
        "SELECT id, 'products_registered', 42, 'count', 'manual' FROM run WHERE run_key = 'probe-20260912-st9'"
    )
    conn.commit()
    codes = {r[0] for r in conn.execute("SELECT metric_code FROM v_anchor_candidates WHERE source_id = 'ST-9'")}
    assert codes == {"products_registered"}


def test_0005_no_population_anchor_reference():
    """nu6 hostile case: 0005 predates the population_anchor table (0008)
    and must not reference it."""
    import pathlib

    import leadhs

    mig = pathlib.Path(leadhs.__file__).parent / "migrations" / "0005__priors_metric.sql"
    assert "population_anchor" not in mig.read_text(encoding="utf-8")


def test_0006_recon_seeds_present(conn):
    classes = {r[0] for r in conn.execute("SELECT code FROM source_class")}
    assert "AS" in classes
    modes = {r[0] for r in conn.execute("SELECT code FROM probe_mode")}
    assert {"census", "format_check", "access_check", "recon"} <= modes
    codes = {r[0] for r in conn.execute("SELECT code FROM probe_metric")}
    assert {"sitemap_products", "sds_library_visible", "producers_registered",
            "trade_kg_hs3208", "trade_eur_hs3208", "trade_kg_hs3209", "trade_eur_hs3209"} <= codes
    types = dict(conn.execute(
        "SELECT code, value_type FROM probe_metric WHERE code IN "
        "('sitemap_products', 'sds_library_visible', 'producers_registered', "
        "'trade_kg_hs3208', 'trade_eur_hs3208', 'trade_kg_hs3209', 'trade_eur_hs3209')"
    ).fetchall())
    assert set(types.values()) == {"numeric"}


def test_0006_view_gains_sitemap_products(conn):
    cols = conn.execute("SELECT metric_code FROM v_anchor_candidates LIMIT 0")
    conn.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('PE-8','PE','n','u','scrape')")
    conn.execute(
        "INSERT INTO run (run_key, kind_code, source_id, started_at, status_code) "
        "VALUES ('probe-20260912-pe8','probe','PE-8','2026-09-12T00:00:00Z','done')"
    )
    conn.execute(
        "INSERT INTO probe_finding (run_id, metric_code, value_numeric, unit_code, method_code) "
        "SELECT id, 'sitemap_products', 7, 'count', 'scrape' FROM run WHERE run_key = 'probe-20260912-pe8'"
    )
    conn.commit()
    codes = {r[0] for r in conn.execute("SELECT metric_code FROM v_anchor_candidates WHERE source_id = 'PE-8'")}
    assert codes == {"sitemap_products"}


def _apply_scripts(conn, upto):
    from leadhs import db as dbmod

    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
    )
    done = {r[0] for r in conn.execute("SELECT version FROM schema_version")}
    conn.isolation_level = None
    for number, name, sql in dbmod.migration_files():
        if number > upto:
            break
        if number in done:
            continue
        conn.executescript("BEGIN;\n" + sql + "\nCOMMIT;\n")
        conn.execute(
            "INSERT INTO schema_version (version, name, applied_at) VALUES (?, ?, '2026-09-12T00:00:00Z')",
            (number, name),
        )


def test_0006_retires_cs1(tmp_path):
    """dm12: CS-1 is retired inactive with the D31 supersession note —
    never deleted; pre-existing notes are preserved."""
    conn = sqlite3.connect(str(tmp_path / "cs1.sqlite"))
    _apply_scripts(conn, 5)
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code, active, notes) "
        "VALUES ('CS-1','CS','swiss-impex','https://swiss-impex.admin.ch','download',1,'pre-existing note')"
    )
    _apply_scripts(conn, 6)
    row = conn.execute("SELECT active, notes FROM source WHERE id = 'CS-1'").fetchone()
    assert row[0] == 0
    assert "pre-existing note" in row[1]
    assert "out of scope D31" in row[1]
    conn.close()


# --- v0.2.1: 0007 capability mode + metrics -------------------------------


def test_0007_capability_mode_seeded(conn):
    modes = {r[0] for r in conn.execute("SELECT code FROM probe_mode")}
    assert "capability" in modes


def test_0007_capability_metrics_seeded(conn):
    """cap1: the six capability metrics are in the vocabulary with the
    right value_types (four numeric, one text for the linkage)."""
    codes = {r[0] for r in conn.execute("SELECT code FROM probe_metric")}
    assert {"products_identifiable", "cap_manufacturer", "cap_product_ident",
            "cap_cn8_linkage", "cap_depth_tier", "cn8_reachable"} <= codes
    types = dict(conn.execute(
        "SELECT code, value_type FROM probe_metric WHERE code IN "
        "('products_identifiable', 'cap_manufacturer', 'cap_product_ident', "
        "'cap_cn8_linkage', 'cap_depth_tier', 'cn8_reachable')"
    ).fetchall())
    assert types == {"products_identifiable": "numeric", "cap_manufacturer": "numeric",
                     "cap_product_ident": "numeric", "cap_cn8_linkage": "text",
                     "cap_depth_tier": "numeric", "cn8_reachable": "numeric"}


def test_0007_no_view_change(conn):
    """cap7: 0007 adds no view — v_anchor_candidates is unchanged."""
    cols = {r[0] for r in conn.execute("SELECT metric_code FROM v_anchor_candidates LIMIT 0")}
    # the anchor-candidate view keeps its v0.2.0 code set (0006 shape)
    assert "products_identifiable" not in cols


# --- v0.2.2: 0008 landscape ------------------------------------------------


def test_0008_source_export_columns(conn):
    """fu3: source gains the structural export anchors (nullable TEXT)."""
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code, export_url, export_format) "
        "VALUES ('AS-1','AS','ecat','https://ecat.example','download','https://ecat.example/export.csv','csv')"
    )
    row = conn.execute("SELECT export_url, export_format FROM source WHERE id = 'AS-1'").fetchone()
    assert tuple(row) == ("https://ecat.example/export.csv", "csv")
    # nullable — legacy rows and plain loads keep working
    conn.execute(
        "INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('AS-2','AS','x','https://x.example','download')"
    )
    row = conn.execute("SELECT export_url, export_format FROM source WHERE id = 'AS-2'").fetchone()
    assert tuple(row) == (None, None)


def test_0008_sds_doc_urls_seeded(conn):
    """fu-metrics: the one new metric is numeric; no new probe_mode."""
    row = conn.execute(
        "SELECT label, value_type FROM probe_metric WHERE code = 'sds_doc_urls'"
    ).fetchone()
    assert row[1] == "numeric"
    modes = {r[0] for r in conn.execute("SELECT code FROM probe_mode")}
    assert {"census", "format_check", "access_check", "recon", "capability", "csv_sample", "as_source_probe"} <= modes


def test_0008_no_view_change(conn):
    """fu3: 0008 adds no view — the anchor view keeps its code set."""
    codes = {r[0] for r in conn.execute("SELECT code FROM probe_metric LIMIT 0")}
    assert "sds_doc_urls" not in codes  # view unchanged; metric lives in probe_metric
    cols = conn.execute("SELECT metric_code FROM v_anchor_candidates LIMIT 0")
    assert cols.fetchall() is not None


# --- v0.2.4: 0009 csv sample ------------------------------------------------


def test_0009_csv_sample_mode_seeded(conn):
    """D36: the csv_sample probe mode is a lookup row only."""
    row = conn.execute(
        "SELECT label FROM probe_mode WHERE code = 'csv_sample'"
    ).fetchone()
    assert row is not None and row[0] == "Management CSV sample"


def test_0009_csv_sample_metrics_seeded(conn):
    """D36: the two sample metrics — rows numeric, reason text."""
    types = dict(
        conn.execute(
            "SELECT code, value_type FROM probe_metric WHERE code IN ('csv_sample_rows', 'csv_sample_unavailable')"
        ).fetchall()
    )
    assert types == {"csv_sample_rows": "numeric", "csv_sample_unavailable": "text"}


def test_0009_no_new_tables(conn):
    """0009 is lookup-seed only — the table set is unchanged from 0008."""
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "probe_mode" in tables and "probe_metric" in tables
    assert not any("csv" in t for t in tables)


# --- v0.2.4 addendum: 0010 as-source probe ----------------------------------


def test_0010_as_probe_mode_seeded(conn):
    """D37: the as_source_probe probe mode is a lookup row only."""
    row = conn.execute(
        "SELECT label FROM probe_mode WHERE code = 'as_source_probe'"
    ).fetchone()
    assert row is not None and row[0] == "AS-class source probe"


def test_0010_as_probe_metrics_seeded(conn):
    """D37: four probe metrics — rows numeric, the rest text."""
    types = dict(
        conn.execute(
            "SELECT code, value_type FROM probe_metric WHERE code LIKE 'as_probe_%'"
        ).fetchall()
    )
    assert types == {
        "as_probe_rows": "numeric",
        "as_probe_records": "text",
        "as_probe_unavailable": "text",
        "as_probe_assoc": "text",
    }


def test_0010_no_new_tables(conn):
    """0010 is lookup-seed only — no as-probe-specific tables."""
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert not any("as_probe" in t for t in tables)

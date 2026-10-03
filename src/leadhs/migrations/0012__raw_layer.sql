-- 0012__raw_layer.sql — v0.3.0: the instruction-driven raw source
-- layer. Per-source verbatim tables (D44: values untouched, parsing
-- happens downstream), one profile row per bulk source binding the
-- committed instruction manifest (manifest_hash), the export-kind
-- vocabulary, and the row-level change journal (R7 upsert semantics
-- live in the interpreter, not here). Bookkeeping columns are
-- `-prefixed so they can never collide with source headers.
-- PostgreSQL-portable DDL (d1/R1 hedge); forward-only, no back-fills.

CREATE TABLE raw_export_kind (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO raw_export_kind (code, description) VALUES
    ('csv_snapshot', 'single-file CSV snapshot (full delivery per request)'),
    ('api_endpoint', 'JSON API endpoint (single call or page_param pagination)'),
    ('web_query', 'reserved: interactive web query (not interpreted at v0.3.0)'),
    ('html_pages', 'reserved: HTML page walk (not interpreted at v0.3.0)');

CREATE TABLE raw_source_profile (
    source_id TEXT PRIMARY KEY REFERENCES source (id) ON DELETE RESTRICT,
    table_name TEXT NOT NULL UNIQUE,
    manifest_hash TEXT NOT NULL,
    export_kind_code TEXT NOT NULL REFERENCES raw_export_kind (code) ON DELETE RESTRICT,
    natural_key_json TEXT NOT NULL,
    payload_budget_bytes INTEGER NOT NULL DEFAULT 1024,
    created_at TEXT NOT NULL
);

CREATE TABLE raw_as2_ecat (
    id INTEGER PRIMARY KEY,
    product_or_service TEXT,
    licence_number TEXT,
    group_name TEXT,
    code_type TEXT,
    code_value TEXT,
    product_or_service_name TEXT,
    decision TEXT,
    expiration_date TEXT,
    company_name TEXT,
    company_country TEXT,
    vat_number TEXT,
    extract_date TEXT,
    _row_hash TEXT NOT NULL,
    _first_run_id INTEGER,
    _last_run_id INTEGER,
    _last_changed_run_id INTEGER,
    _truncated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE raw_as3_nordic_swan (
    id INTEGER PRIMARY KEY,
    product TEXT,
    license_number TEXT,
    ecolabel TEXT,
    category TEXT,
    product_group TEXT,
    criteria_generation TEXT,
    brand TEXT,
    licensee TEXT,
    address TEXT,
    city TEXT,
    _row_hash TEXT NOT NULL,
    _first_run_id INTEGER,
    _last_run_id INTEGER,
    _last_changed_run_id INTEGER,
    _truncated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE raw_change (
    id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES source (id) ON DELETE RESTRICT,
    row_key TEXT NOT NULL,
    old_hash TEXT,
    new_hash TEXT NOT NULL,
    run_id INTEGER NOT NULL REFERENCES run (id) ON DELETE RESTRICT,
    note TEXT
);

CREATE INDEX idx_raw_change_source_row ON raw_change (source_id, row_key);
CREATE INDEX idx_raw_change_run ON raw_change (run_id);

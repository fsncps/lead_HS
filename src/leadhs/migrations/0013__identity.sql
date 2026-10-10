-- 0013__identity.sql — v0.3.4 r01: the canonical identity layer.
-- manufacturer + product are the canonical tables (MA10/MA12: one row
-- per real-world manufacturer / per identity group; name_norm UNIQUE,
-- ident_string UNIQUE). identity_state binds each resolved source to
-- the raw manifest hash it consumed (drift guard, il2). linkage_candidate
-- is the r03 review-queue surface, created now while the migration is
-- fresh (empty until matching runs). The raw->product back-link columns
-- are NOT declared here: SQLite ALTER TABLE ADD COLUMN cannot carry a
-- FOREIGN KEY clause, so identity/spec.ensure_backlink_column() adds
-- them at run time and doctor checks orphans (integrity is application
-- level + R7 for the FK-bound canonical edges). PostgreSQL-portable
-- DDL (d1 hedge); forward-only, no back-fills.

INSERT INTO run_kind (code, label, description) VALUES
    ('identity_resolve', 'Identity resolve',
     'derive canonical manufacturer/product rows from raw source tables');

CREATE TABLE manufacturer (
    uuid TEXT PRIMARY KEY,
    name_norm TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT,
    city TEXT,
    vat_id TEXT,
    created_run_id INTEGER
);

CREATE TABLE product (
    uuid TEXT PRIMARY KEY,
    ident_string TEXT NOT NULL UNIQUE,
    ident_nr TEXT NOT NULL,
    manufacturer_uuid TEXT NOT NULL REFERENCES manufacturer (uuid) ON DELETE RESTRICT,
    hs_code TEXT,
    eu_group TEXT,
    name TEXT,
    brand TEXT,
    url TEXT,
    created_run_id INTEGER
);

CREATE TABLE identity_state (
    source_id TEXT PRIMARY KEY REFERENCES source (id) ON DELETE RESTRICT,
    manifest_hash TEXT NOT NULL,
    resolved_run_id INTEGER NOT NULL
);

CREATE TABLE linkage_candidate (
    id INTEGER PRIMARY KEY,
    row_a TEXT NOT NULL,
    row_b TEXT NOT NULL,
    method TEXT NOT NULL,
    score REAL,
    band TEXT,
    verdict TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'pending',
    decided_run_id INTEGER,
    created_run_id INTEGER,
    UNIQUE (row_a, row_b, method)
);

CREATE INDEX idx_product_manufacturer ON product (manufacturer_uuid);
CREATE INDEX idx_linkage_candidate_verdict ON linkage_candidate (verdict);
CREATE INDEX idx_linkage_candidate_review ON linkage_candidate (review_status);

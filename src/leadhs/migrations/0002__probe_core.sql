-- 0002__probe_core.sql — M0 (v0.1.1): source, document, run, probe_run,
-- probe_finding + the three probe-era views and indexes.
-- Semantics per 20_DESIGN/MASTER/data_model.md §Probe-era schema, incl.
-- the ENG review 2026-09-11 items: run.status_code DEFAULT 'planned'
-- (dm14), document.run_id NOT NULL (dm15), covering index on run.

CREATE TABLE source (
    id TEXT PRIMARY KEY CHECK (id GLOB '[A-Z][A-Z]-[0-9]*'),
    class_code TEXT NOT NULL REFERENCES source_class (code) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    access_method_code TEXT NOT NULL REFERENCES access_method (code) ON DELETE RESTRICT,
    license_note TEXT,
    verification_status_code TEXT NOT NULL DEFAULT 'open' REFERENCES verification_status (code) ON DELETE RESTRICT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    notes TEXT
);

CREATE TABLE run (
    id INTEGER PRIMARY KEY,
    run_key TEXT UNIQUE NOT NULL,
    kind_code TEXT NOT NULL REFERENCES run_kind (code) ON DELETE RESTRICT,
    source_id TEXT REFERENCES source (id) ON DELETE RESTRICT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status_code TEXT NOT NULL DEFAULT 'planned' REFERENCES run_status (code) ON DELETE RESTRICT,
    parameters_json TEXT,
    seed INTEGER,
    notes TEXT,
    CHECK (kind_code != 'probe' OR source_id IS NOT NULL)
);

CREATE INDEX idx_run_source_id ON run (source_id);
CREATE INDEX idx_run_kind_code ON run (kind_code);
CREATE INDEX idx_run_status_code ON run (status_code);
CREATE INDEX idx_run_source_status_started ON run (source_id, status_code, started_at);

CREATE TABLE document (
    id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES source (id) ON DELETE RESTRICT,
    run_id INTEGER NOT NULL REFERENCES run (id) ON DELETE RESTRICT,
    url TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    raw_hash TEXT UNIQUE,
    content_type TEXT,
    language_code TEXT REFERENCES language (code) ON DELETE RESTRICT,
    title TEXT,
    size_bytes INTEGER,
    retrieval_method_code TEXT NOT NULL REFERENCES access_method (code) ON DELETE RESTRICT,
    status_code TEXT NOT NULL DEFAULT 'archived' REFERENCES document_status (code) ON DELETE RESTRICT,
    notes TEXT,
    CHECK (status_code != 'archived' OR raw_hash IS NOT NULL)
);

CREATE INDEX idx_document_source_id ON document (source_id);
CREATE INDEX idx_document_run_id ON document (run_id);

CREATE TABLE probe_run (
    run_id INTEGER PRIMARY KEY REFERENCES run (id) ON DELETE RESTRICT,
    mode_code TEXT NOT NULL REFERENCES probe_mode (code) ON DELETE RESTRICT
);

CREATE TABLE probe_finding (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES run (id) ON DELETE RESTRICT,
    metric_code TEXT NOT NULL REFERENCES probe_metric (code) ON DELETE RESTRICT,
    value_numeric REAL,
    value_text TEXT,
    unit_code TEXT REFERENCES quantity_unit (code) ON DELETE RESTRICT,
    method_code TEXT NOT NULL REFERENCES access_method (code) ON DELETE RESTRICT,
    document_id INTEGER REFERENCES document (id) ON DELETE RESTRICT,
    notes TEXT,
    CHECK (value_numeric IS NOT NULL OR value_text IS NOT NULL)
);

CREATE INDEX idx_finding_run_metric ON probe_finding (run_id, metric_code);
CREATE INDEX idx_finding_document ON probe_finding (document_id);

CREATE VIEW v_probe_latest AS
SELECT
    r.source_id,
    r.id AS run_id,
    r.run_key,
    r.started_at,
    pf.id AS finding_id,
    pf.metric_code,
    pf.value_numeric,
    pf.value_text,
    pf.unit_code,
    pf.method_code,
    pf.document_id
FROM probe_finding pf
JOIN run r ON r.id = pf.run_id
WHERE r.kind_code = 'probe'
  AND r.status_code = 'done'
  AND NOT EXISTS (
      SELECT 1
      FROM probe_finding pf2
      JOIN run r2 ON r2.id = pf2.run_id
      WHERE r2.kind_code = 'probe'
        AND r2.status_code = 'done'
        AND r2.source_id = r.source_id
        AND pf2.metric_code = pf.metric_code
        AND (r2.started_at > r.started_at
             OR (r2.started_at = r.started_at AND r2.id > r.id))
  );

CREATE VIEW v_anchor_candidates AS
SELECT source_id, run_id, run_key, started_at, metric_code, value_numeric, unit_code
FROM v_probe_latest
WHERE metric_code IN ('catalog_count', 'category_count', 'export_rows');

CREATE VIEW v_source_activity AS
SELECT
    s.id AS source_id,
    (SELECT MIN(d.retrieved_at) FROM document d WHERE d.source_id = s.id) AS first_retrieved_at,
    (SELECT MAX(d.retrieved_at) FROM document d WHERE d.source_id = s.id) AS last_retrieved_at,
    (SELECT COUNT(*) FROM run r WHERE r.source_id = s.id) AS run_count,
    (SELECT COUNT(*) FROM probe_finding pf JOIN run r ON r.id = pf.run_id WHERE r.source_id = s.id) AS finding_count
FROM source s;
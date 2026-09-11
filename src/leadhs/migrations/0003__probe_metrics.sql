-- 0003__probe_metrics.sql — M0 (v0.1.2, od10): probe metric extension.
-- Adds the per-HS census count metrics and the census_status manual
-- record metric. Codes never renamed, value_type fixed at insert (i4).
-- Redefines v_anchor_candidates to include the new count metrics
-- (dm11 redefinition — recorded here per the migration-plan rule).

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('records_hs3208', 'Records HS 3208', 'rows for HS 3208 in the parameterized query (absent = not queried; 0 = queried, empty)', 'numeric'),
    ('records_hs3209', 'Records HS 3209', 'same, for HS 3209', 'numeric'),
    ('records_hs3213', 'Records HS 3213', 'same, for HS 3213 (census annex)', 'numeric'),
    ('census_status', 'Census status', 'manual/deferral record on a source''s census state (PCN aggregates, deferral notes, manual export mechanics; method=manual)', 'text');

DROP VIEW IF EXISTS v_anchor_candidates;
CREATE VIEW v_anchor_candidates AS
SELECT source_id, run_id, run_key, started_at, metric_code, value_numeric, unit_code
FROM v_probe_latest
WHERE metric_code IN ('catalog_count', 'category_count', 'export_rows',
                      'records_hs3208', 'records_hs3209', 'records_hs3213');

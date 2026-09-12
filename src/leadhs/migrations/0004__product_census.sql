-- 0004__product_census.sql — M0 (v0.1.2 rework, D28; landed by v0.1.3
-- PHASE01). Register slim: prunes the LG-*/LI-* source rows and every
-- row recorded against them (findings, probe_run, documents, runs) in
-- FK-safe order probe_finding -> probe_run -> document -> run -> source.
-- This is the D28-sanctioned prune of reference rows that leave the
-- tool (U12); the register CSV slims in the same change set so the
-- upsert loader cannot resurrect the pruned rows.
-- Adds the product-first walk metrics. Codes never renamed,
-- value_type fixed at insert (i4).
-- Redefines v_anchor_candidates to include products_listed
-- (dm11 redefinition — recorded here per the migration-plan rule).

DELETE FROM probe_finding
 WHERE run_id IN (SELECT r.id FROM run r
                   WHERE r.source_id LIKE 'LG-%' OR r.source_id LIKE 'LI-%');
DELETE FROM probe_run
 WHERE run_id IN (SELECT r.id FROM run r
                   WHERE r.source_id LIKE 'LG-%' OR r.source_id LIKE 'LI-%');
DELETE FROM document
 WHERE source_id LIKE 'LG-%' OR source_id LIKE 'LI-%';
DELETE FROM run
 WHERE source_id LIKE 'LG-%' OR source_id LIKE 'LI-%';
DELETE FROM source
 WHERE id LIKE 'LG-%' OR id LIKE 'LI-%';

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('products_listed', 'Products listed (walk)', 'distinct product detail links from a polite category walk (BFS depth <= 3, page budget <= 12 incl. homepage); a floor, never a market total (D28)', 'numeric'),
    ('doc_links_seen', 'Doc links seen (walk)', 'SDS/TDS-type links encountered during the same walk (D28)', 'numeric'),
    ('walk_budget_exhausted', 'Walk budget exhausted', '0/1 - the page budget stopped the walk; the report flags such floors ">= observed, budget-limited" (ENG review 2A)', 'numeric');

DROP VIEW IF EXISTS v_anchor_candidates;
CREATE VIEW v_anchor_candidates AS
SELECT source_id, run_id, run_key, started_at, metric_code, value_numeric, unit_code
FROM v_probe_latest
WHERE metric_code IN ('catalog_count', 'category_count', 'export_rows',
                      'records_hs3208', 'records_hs3209', 'records_hs3213',
                      'products_listed');

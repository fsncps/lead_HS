-- 0005__priors_metric.sql — M0 (v0.1.3 pe2, landed by v0.2.0 PHASE01;
-- absorption per the B8/D26/d31 precedent). Adds the priors metric:
-- products_registered carries product-unit register counts (SPIN
-- preparations, PCN formulations, national register products);
-- producers_registered follows at 0006 — the split lives in the metric
-- codes, not in notes (nu3). Codes never renamed, value_type fixed at
-- insert (i4). Redefines v_anchor_candidates to include
-- products_registered (dm11 redefinition — recorded here per the
-- migration-plan rule). nu6 correction: this view references no
-- anchor-promotion table — that table ships at 0008 and the
-- promoted-exclusion NOT EXISTS lands there.

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('products_registered', 'Products registered (prior)', 'product-unit register counts used as priors (SPIN preparations, PCN formulations, national register products); N2 sums only this metric, never producers_registered (nu3)', 'numeric');

DROP VIEW IF EXISTS v_anchor_candidates;
CREATE VIEW v_anchor_candidates AS
SELECT source_id, run_id, run_key, started_at, metric_code, value_numeric, unit_code
FROM v_probe_latest
WHERE metric_code IN ('catalog_count', 'category_count', 'export_rows',
                      'records_hs3208', 'records_hs3209', 'records_hs3213',
                      'products_listed', 'products_registered');

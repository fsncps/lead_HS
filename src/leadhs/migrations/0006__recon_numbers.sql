-- 0006__recon_numbers.sql — M0 (v0.2.0): the recon/numbers delta.
-- Adds the AS source class (associations & registers, D31), the recon
-- probe mode (robots-compliant sitemap reconnaissance, counts only),
-- the recon/numbers metrics, and retires CS-1 (swiss-impex) inactive
-- with a supersession note (retire, never delete — dm12; EU-only
-- register scope D31). Codes never renamed, value_type fixed at
-- insert (i4). Redefines v_anchor_candidates to include
-- sitemap_products (dm11 redefinition — recorded here per the
-- migration-plan rule). nu3: producers_registered (industry-structure
-- counts) is kept separate from products_registered (product-unit
-- counts) at the metric-code level; N2 sums products_registered only.

INSERT INTO source_class (code, label, description) VALUES
    ('AS', 'Associations & registers', 'CEPE/national association member lists; national product registers with public statistics — manufacturer and product-count anchors without scraping (D31)');

INSERT INTO probe_mode (code, label, description) VALUES
    ('recon', 'Reconnaissance', 'robots-compliant, counts-only sitemap reconnaissance (no scraping; bounded index expansion <= 5 children)');

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('sitemap_products', 'Products sitemap-visible', 'product-URL pattern matches in robots-declared sitemap(s); a floor, never a market total; index-cap hits render the floor partial', 'numeric'),
    ('sds_library_visible', 'SDS library visible (manual)', '0/1 — manual-web landing-page check: SDS/TDS library visibly reachable without scraping (method=manual)', 'numeric'),
    ('producers_registered', 'Producers registered (prior)', 'industry-structure counts (association members, SBS enterprises); NEVER summed into N2 (nu3)', 'numeric'),
    ('trade_kg_hs3208', 'EU imports HS 3208 (kg)', 'full-year extra-EU import mass, HS 3208 (Eurostat Comext aggregation; flow + resolved year pinned in run parameters_json)', 'numeric'),
    ('trade_eur_hs3208', 'EU imports HS 3208 (EUR)', 'full-year extra-EU import value, HS 3208 (same query family)', 'numeric'),
    ('trade_kg_hs3209', 'EU imports HS 3209 (kg)', 'full-year extra-EU import mass, HS 3209 (same query family)', 'numeric'),
    ('trade_eur_hs3209', 'EU imports HS 3209 (EUR)', 'full-year extra-EU import value, HS 3209 (same query family)', 'numeric');

UPDATE source
   SET active = 0,
       notes = COALESCE(notes || '; ', '') || 'out of scope D31 (EU-only; TLS wall documented 2026-09-12)'
 WHERE id = 'CS-1';

DROP VIEW IF EXISTS v_anchor_candidates;
CREATE VIEW v_anchor_candidates AS
SELECT source_id, run_id, run_key, started_at, metric_code, value_numeric, unit_code
FROM v_probe_latest
WHERE metric_code IN ('catalog_count', 'category_count', 'export_rows',
                      'records_hs3208', 'records_hs3209', 'records_hs3213',
                      'products_listed', 'products_registered',
                      'sitemap_products');

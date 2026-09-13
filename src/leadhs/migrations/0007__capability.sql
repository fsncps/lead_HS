-- 0007__capability.sql — M0 (v0.2.1, cap1/cap7): the source-level
-- capability sounding-out delta. Adds the capability probe mode and the
-- six capability probe_metrics (the "is a product URL a product" test
-- against the study's product model). Codes never renamed, value_type
-- fixed at insert (i4). No view change — the capability profile is a
-- report-time derivation (nu5 precedent); v_probe_latest gives the
-- current profile per source x metric. Product data only (D27); the
-- real-product-source predicate (cap_manufacturer=1 AND
-- cap_product_ident=1 AND cap_cn8_linkage!='none' AND cap_depth_tier>=2)
-- is derived at report time, never stored (i17).

INSERT INTO probe_mode (code, label, description) VALUES
    ('capability', 'Capability', 'register-capability sounding-out: fetch an official register export (CSV/API) and inspect its shape against the product model (manufacturer / product-ident / CN8 linkage / depth) — volume + depth, reconnaissance only (D31, no scraping)');

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('products_identifiable', 'Products identifiable', 'volume — how many products the source features, against the product model', 'numeric'),
    ('cap_manufacturer', 'Capability: manufacturer field', '0/1 — source exposes a manufacturer/org field', 'numeric'),
    ('cap_product_ident', 'Capability: product-ident field', '0/1 — source exposes a product-ident (licence no / UFI / article code / SKU / GTIN)', 'numeric'),
    ('cap_cn8_linkage', 'Capability: CN8 linkage', 'mechanism to the 13 CN8 codes: category / prodcom / eupcs_proxy / manual / none', 'text'),
    ('cap_depth_tier', 'Capability: depth tier', '1 name-only | 2 name/ident+technical | 3 deep+internal docs | 4 standardized specs+MSDS', 'numeric'),
    ('cn8_reachable', 'CN8 codes reachable', 'how many of the 13 CN8 codes reachable (0-13)', 'numeric');

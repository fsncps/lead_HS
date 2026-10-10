-- v0.3.4 r02 (D51): HS completion over the canonical products. The
-- products.hs_code column exists since 0013 and stays nullable; this
-- run needs only its run-kind vocabulary row. The curated map is a
-- repo dictionary (src/leadhs/dict/hs_group_map.csv), not a DB table.

INSERT INTO run_kind (code, label, description) VALUES
    ('hs_apply', 'HS completion',
     'apply the curated group-to-HS4 map to products.hs_code (deterministic, idempotent)');

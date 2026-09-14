-- 0010__as_source_probe.sql — v0.2.4 addendum (D37): the AS-class
-- source probe. Lookup seeds only, no new tables (i4 vocabulary
-- extension path). The `as_source_probe` mode labels the runs of
-- `leadhs probe as-source-probe` (all 30 AS rows: 9 product/label
-- databases + 21 trade associations). Four metrics, per source:
-- exact product rows obtained (numeric), the exact-or-estimated
-- record count with basis + access date (text), the honest reason no
-- product rows are obtainable plus what is available instead (text),
-- and the association finding (text — member-list pointer, liveness).

INSERT INTO probe_mode (code, label, description) VALUES
    ('as_source_probe', 'AS-class source probe', 'per-source probe across all AS rows (D37): try to obtain a product-row CSV per register; where none exists record why and what is available instead, plus exact-or-estimated record counts — associations get member-list findings, registries bounded export discovery (≤5 GETs)');

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('as_probe_rows', 'AS probe product rows obtained', 'product rows actually obtained and written as CSV for a registry source (exact count; includes same-day csv-sample reuse copies)', 'numeric'),
    ('as_probe_records', 'AS probe record count', 'exact or estimated record count for a source without a downloadable CSV — the note carries the basis (parsed rows / visible page count / documented figure), the method and the access date; unknown is a valid outcome', 'text'),
    ('as_probe_unavailable', 'AS probe unavailable', 'why a registry delivers no product rows — reason with citation plus what is available instead (web database, PDF lists, per-product downloads, auth-gated API)', 'text'),
    ('as_probe_assoc', 'AS probe association finding', 'trade-association source: no product register by design — what is available instead (member list, member count where visible), liveness recorded', 'text');

-- 0009__csv_sample.sql — v0.2.4 (D36): the management CSV sample
-- delta. Lookup seeds only, no new tables — the i4 vocabulary
-- extension path (0003/0005/0006/0007 precedent): codes never
-- renamed, value_type fixed at insert. The `csv_sample` probe mode
-- labels the runs of `leadhs probe download-csv-sample`; the two
-- metrics record, per registry, the rows actually drawn (numeric)
-- or the honest reason no product-row sample is possible (text —
-- verified finding + citation, or a should-deliver failure record;
-- the manifest always tells the truth per source, review 1A).
-- Samples are review artifacts, not measurement rows: no staging
-- writes, no view change (D27/D31).

INSERT INTO probe_mode (code, label, description) VALUES
    ('csv_sample', 'Management CSV sample', 'per-registry reproducible product-row samples for management review (D36): what fields per product item, which identifier columns, cross-identification candidates; honest no-product-rows records for the registers that publish none — recon-only (D31)');

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('csv_sample_rows', 'CSV sample rows drawn', 'rows actually written to the per-registry sample CSV (seeded draw, clamped to the in-scope pool)', 'numeric'),
    ('csv_sample_unavailable', 'CSV sample unavailable', 'why a registry delivers no product-row sample — verified reason with citation (expected, exit 0) or a should-deliver failure record (exit 2)', 'text');

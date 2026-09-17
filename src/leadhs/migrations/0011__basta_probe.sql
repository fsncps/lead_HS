-- 0011__basta_probe.sql — v0.2.4 addendum (D40): the BASTA special
-- probe. Lookup seeds only, no new tables (i4 vocabulary extension
-- path). The `basta_special_probe` mode labels the runs of
-- `leadhs probe basta-probe` (AS-33 bastaonline.se, the D39
-- consultant-queue candidate): pin the anonymous search route behind
-- the /sok client shell, record counts + field structure, deliver a
-- seeded random sample of 100 articles as CSV. Two metrics, per the
-- D37/D36 extension idiom: rows actually drawn (numeric) and the
-- honest reason nothing is obtainable (text). Exact counts ride the
-- existing `catalog_count` metric (0001; notes carry route + access
-- date) — no third metric needed.

INSERT INTO probe_mode (code, label, description) VALUES
    ('basta_special_probe', 'BASTA special probe', 'per-source probe of BASTA online (AS-33, D40): pin the anonymous search route behind the /sok client shell, characterize data availability (article/company counts, field schema, identity tuple), and deliver a seeded random 100-article sample CSV with the identity columns and the BK04/BSAB category proxy — recon-only (D31), no accounts/agreements (D4), robots crawl-delay honored');

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('basta_special_rows', 'BASTA sample rows drawn', 'articles actually written to the seeded sample CSV from the pinned anonymous route (draw clamped to the pool; the notes carry the route, the pool method, seed, shortfall and the field schema)', 'numeric'),
    ('basta_special_unavailable', 'BASTA special unavailable', 'why BASTA delivers no sample — pin-not-found after the bundle budget, auth-gated route (401/403), or a should-deliver network-failure record; the note documents the agreement route as why-not only (D4), never contacted', 'text');

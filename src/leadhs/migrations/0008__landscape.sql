-- 0008__landscape.sql — M0 (v0.2.2, fu3): the three-question-funnel
-- schema delta. Adds the structural export anchors to the source
-- register (export_url / export_format — pinned per source, not in
-- free-text notes) and the sds_doc_urls probe_metric (SDS/technical
-- document URLs visible per PE site, sitemap-derived — the Q3 reach
-- input). Codes never renamed, value_type fixed at insert (i4). No
-- view change; no new probe_mode — the v0.2.2 waves compose the
-- existing census/recon/capability modes (fu3). Product data only
-- (D27).

ALTER TABLE source ADD COLUMN export_url TEXT;
ALTER TABLE source ADD COLUMN export_format TEXT;

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('sds_doc_urls', 'SDS document URLs visible', 'count of SDS/TDS document URLs visible per PE site (sitemap/index-page derived; counts only, no URL harvesting)', 'numeric');

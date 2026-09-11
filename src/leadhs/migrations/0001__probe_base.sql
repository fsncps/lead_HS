-- 0001__probe_base.sql — M0 (v0.1.1): the 10 lookup tables.
-- Common shape: code TEXT PK, label TEXT NOT NULL, description TEXT.
-- probe_metric adds value_type. Seeds pinned to metrics.py by a sync
-- test (t6) — 0001 is static SQL and cannot call Python.

CREATE TABLE source_class (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO source_class (code, label, description) VALUES
    ('CS', 'Customs & trade statistics', 'CH swiss-impex / Eurostat Comext — structures the market by origin'),
    ('PE', 'Product & SDS evidence (web)', 'manufacturer/brand sites, B2B portals, DIY-chain catalogs, marine chandlers, art-supply shops'),
    ('LG', 'Legal & regulatory texts', 'THG, VIPaV, ChemRRV, SECO Negativliste, REACH Annexes, OJ decisions, ECHA registers'),
    ('ST', 'Structural & product statistics', 'ECHA PCN, Nordic SPIN, Eurostat PRODCOM/SBS — population proxies and scaling anchors'),
    ('LI', 'Literature & industry', 'peer-reviewed studies, IPEN, CEPE');

CREATE TABLE access_method (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO access_method (code, label, description) VALUES
    ('api', 'Public API', 'official machine-readable endpoint'),
    ('scrape', 'Polite web scraping', 'HTML retrieval respecting robots/terms and rate limits'),
    ('download', 'Official download', 'export/PDF/Access-DB retrieved as a file'),
    ('manual', 'Manual retrieval', 'hand-retrieved subset (e.g. blocked site manual fallback, D4)');

CREATE TABLE verification_status (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO verification_status (code, label, description) VALUES
    ('verified', 'Verified', 'confirmed against primary source'),
    ('partially_verified', 'Partially verified', 'some elements confirmed, others open'),
    ('open', 'Open', 'not yet probed/confirmed'),
    ('unverified', 'Unverified', 'probe failed or contradicting evidence');

CREATE TABLE language (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO language (code, label, description) VALUES
    ('de', 'German', 'ISO 639-1'),
    ('fr', 'French', 'ISO 639-1'),
    ('it', 'Italian', 'ISO 639-1'),
    ('rm', 'Romansh', 'ISO 639-1'),
    ('en', 'English', 'ISO 639-1'),
    ('nl', 'Dutch', 'ISO 639-1'),
    ('sv', 'Swedish', 'ISO 639-1'),
    ('da', 'Danish', 'ISO 639-1'),
    ('no', 'Norwegian', 'ISO 639-1'),
    ('fi', 'Finnish', 'ISO 639-1'),
    ('es', 'Spanish', 'ISO 639-1'),
    ('pl', 'Polish', 'ISO 639-1'),
    ('pt', 'Portuguese', 'ISO 639-1');

CREATE TABLE document_status (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO document_status (code, label, description) VALUES
    ('archived', 'Archived', 'raw file in the store (raw_hash set)'),
    ('manual', 'Manual', 'no raw file; retrieved by hand'),
    ('derived', 'Derived', 'generated artifact'),
    ('not_found', 'Not found', 'referenced but never retrieved');

CREATE TABLE run_kind (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO run_kind (code, label, description) VALUES
    ('probe', 'Probe', 'small polite test visit recording what a source delivers'),
    ('acquire', 'Acquire', 'bulk retrieval (M2)'),
    ('import', 'Import', 'data import (M1 trade statistics / SPIN)'),
    ('sampling', 'Sampling', 'reproducible sample draw (M1)');

CREATE TABLE run_status (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO run_status (code, label, description) VALUES
    ('planned', 'Planned', 'row created, not yet started'),
    ('running', 'Running', 'in progress'),
    ('done', 'Done', 'completed with findings'),
    ('failed', 'Failed', 'unrecoverable network error'),
    ('blocked', 'Blocked', 'wholly inaccessible (robots deny / 403 / persistent 429 / paywall)'),
    ('aborted', 'Aborted', 'interrupted by the user; inserted findings persist');

CREATE TABLE probe_mode (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO probe_mode (code, label, description) VALUES
    ('census', 'Census', 'record what the source delivers (counts, constraints)'),
    ('format_check', 'Format check', 'export/download format and extraction path check'),
    ('access_check', 'Access check', 'reachability / free-access / blocking check');

CREATE TABLE quantity_unit (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

INSERT INTO quantity_unit (code, label, description) VALUES
    ('count', 'count', 'count of items'),
    ('chf', 'Swiss franc', 'CHF'),
    ('eur', 'Euro', 'EUR'),
    ('kg', 'Kilogram', 'kg'),
    ('t', 'Tonne', 'tonne'),
    ('l', 'Litre', 'litre'),
    ('percent', 'Percent', '%'),
    ('ppm', 'Parts per million', 'mg/kg'),
    ('year', 'Year', 'calendar year');

CREATE TABLE probe_metric (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT,
    value_type TEXT NOT NULL CHECK (value_type IN ('numeric', 'text'))
);

INSERT INTO probe_metric (code, label, description, value_type) VALUES
    ('catalog_count', 'Catalog product count', 'total products listed site-wide', 'numeric'),
    ('category_count', 'Category product count', 'products in one category (value_text = category path)', 'numeric'),
    ('category_list', 'Categories exposed', 'JSON list of category names/paths', 'text'),
    ('format', 'Export/download format', 'observed layout of official exports', 'text'),
    ('granularity', 'Statistics granularity', 'dimensions available (e.g. CN8 × partner × year)', 'text'),
    ('coverage_years', 'Coverage years', 'year range available (e.g. 2019–2025)', 'text'),
    ('export_rows', 'Export rows', 'rows returned by a test export/query', 'numeric'),
    ('robots', 'Robots policy', 'robots.txt summary for our paths', 'text'),
    ('terms', 'Site terms', 'terms relevant to access/scraping', 'text'),
    ('rate_limit', 'Rate limit', 'observed or documented limit', 'text'),
    ('languages', 'Languages', 'languages offered (JSON list)', 'text'),
    ('page_sample_ok', 'Sample pages retrievable', 'n_ok/n_sample', 'numeric'),
    ('sds_sample_ok', 'SDS on sample pages', 'n_with_sds/n_sample', 'numeric'),
    ('extraction_path', 'Extraction path', 'result of an extraction-tooling check (e.g. mdbtools/SPIN)', 'text'),
    ('access_blocked', 'Access blocked', 'detail when blocked (403/429/paywall/login)', 'text'),
    ('robots_denied', 'Robots denial', 'detail when robots.txt disallows', 'text'),
    ('free_access', 'Free access confirmed', '0/1 — no account/paywall needed', 'numeric');
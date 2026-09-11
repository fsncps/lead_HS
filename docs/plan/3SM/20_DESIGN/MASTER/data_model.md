---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-11
---

# Data model — normalized evidence database (Design)

## Abstract

One SQLite database (`data/leadhs.sqlite`) holds everything the study
collects and produces. This document is the Design-level schema: a
table-by-table specification precise enough that the SQL migration
files can be written from it without new decisions. It refines the
Strategy schema (10_STRATEGY/DATA_MODEL.md) into a fully **normalized**
form. Normalization here means: every fact is stored exactly once —
provenance (source, URL, retrieval date, raw-file hash) lives in one
`document` backbone instead of being repeated on every evidence row;
classifications (origin, stratum …) are small lookup
tables instead of free text; multi-valued facts (synonyms, identifiers,
H-codes, category assignments) are junction tables; what a safety data
sheet literally says is kept separate from what we interpret it to
mean; and every derived number (prevalence rates) is a database *view*,
never a stored column. **Product data only (Strategy MASTER D27):** the
schema carries no legal-category dimension, no compound legal-status or
Swiss-relevance fields, no legal-coded signal lookups and no legal-text
documents — lawful/illegal assessment and ban relevance stay
documentation-layer (10_STRATEGY/LEAD_SDS.md).
The schema is written to port to PostgreSQL with two documented
variances (id generation, one partial index) and to be reusable for
future substance-in-products studies via a `study` discriminator.

## Design principles

1. **3NF core** — no repeating provenance groups, no transitive
   dependencies; stable keys (10_STRATEGY/MASTER.md D17).
2. **Provenance backbone** — `document` is the single home of
   url/source/retrieved_at/raw_hash; all evidence references it
   (CEO review 2026-09-10).
3. **Lookups over free text** — every enumeration is a lookup table
   keyed by a stable code; extensible by inserting rows.
4. **Junctions for multi-valued facts** — synonyms, identifiers,
   H-codes, product–org roles, category assignments, anchor links.
5. **Verbatim vs interpretation split** — `sds_ingredient` (what the
   sheet says) vs `sds_finding` (what we matched it to).
6. **Derived values are views** — consistency scores, prevalence;
   recomputable, never stale. No legal-derived views: the
   ban-engagement assessment stays documentation-layer
   (Strategy MASTER D27).
7. **Append-only evidence, updatable reference data** — evidence rows
   (documents, findings, runs, sightings) are never deleted or
   value-updated; corrections are new rows or review-status
   transitions. Reference rows (source register, lookups, dictionary,
   study) evolve in place and are never deleted.
8. **Portability** — SQLite now (WAL, foreign keys ON); the DDL stays
   standard SQL except two documented variances (rowid-alias ids, one
   partial index), listed in the portability section.
9. **Reuse** — `study` discriminator + study-agnostic substance
   dictionary: a second study (e.g. another substance group in
   consumer products) reuses the database with zero migration.

## Conventions

- Entity tables: `id INTEGER PRIMARY KEY` (rowid alias; no
  AUTOINCREMENT — PostgreSQL port swaps to IDENTITY; variance).
- Lookup tables: `code TEXT PRIMARY KEY` (stable, human-readable in
  the released artifact; renumbering impossible).
- Foreign keys: `… REFERENCES x (y) ON DELETE RESTRICT` — nothing
  cascades; append-only by construction.
- Timestamps/dates: ISO 8601 TEXT, UTC.
- Booleans: INTEGER 0/1 (`BOOLEAN` when porting).
- JSON: TEXT (PostgreSQL port: JSONB — recorded variance).
- Naming: strategy vocabulary kept (`source`, `product`, `sighting`,
  `sds_document`, `sds_finding`, `frame_stratum` …); FK columns end in
  `_code` (lookup) or `_id` (entity).
- Charset UTF-8; CHECK constraints where they carry meaning.

## Migration plan

Forward-only, numbered, **milestone-gated** (10_STRATEGY/MASTER.md
D19/D20; rollout M0–M4 in 10_STRATEGY/ARCHITECTURE.md). The migration
runner (db.py) creates `schema_version` itself and applies pending
files in order, each in one transaction; a timestamped backup of the
database file is taken before applying to an existing DB (default on,
`db init --no-backup` to skip).

Rule: **views ship with the migration that completes their
dependencies**; a later migration may redefine a view (recorded in its
header comment).

Seed channels: (a) migrations seed lookups and the `study` row;
(b) repo CSVs seed the source register (`source load`) and, at M1, the
substance dictionary (`dict load` — 10_STRATEGY/DATA_MODEL.md D6);
(c) evidence arrives only through runs (probe/acquire/import/sampling).

| Migration | Milestone | Tables | Views |
|---|---|---|---|
| `0001__probe_base.sql` | M0 (v0.1.1) | 10 lookups | — |
| `0002__probe_core.sql` | M0 (v0.1.1) | source, document, run, probe_run, probe_finding | v_probe_latest, v_anchor_candidates, v_source_activity |
| `0003__probe_metrics.sql` | M0 (v0.1.2) | — (probe_metric INSERTs: records_hs3208/3209/3213, census_status) | v_anchor_candidates (redefined) |
| `0004__dictionary.sql` | M1 | substance, compound_synonym, compound_identifier + 5 lookups | — |
| `0005__catalog_frame.sql` | M1 | study, org, product, product_org, product_classification, category, product_category, population_anchor, frame_stratum, frame_stratum_anchor, cn_code + 8 lookups | v_anchor_candidates (redefined), v_product_current |
| `0006__sampling.sql` | M1 | sampling_run, sample_selection + 2 lookups | — |
| `0007__trade_stats.sql` | M1 | trade_stat + flow lookup | — |
| `0008__sds.sql` | M2 | sds_document, product_ufi, sds_ingredient, sds_finding, sds_finding_hcode, sds_section15 + 6 lookups | — |
| `0009__evidence.sql` | M2–M3 | sighting, corroboration + 2 lookups | — |
| `0010__views.sql` | M4 | — | v_finding_full, v_product_dossier, v_trade_ch, v_census_3213 |

Renumbering note (unit v0.1.2, od10): the probe metric extension took
`0003` — the cheapest moment, before any design-ahead file exists; the
design-ahead migrations shifted one number (`0003__dictionary` → `0004`
… `0009__views` → `0010`). Future probe-era metric INSERTs repeat this
shift; accepted (docs-only, pre-build).

Two corrections vs the session draft of this plan: `trade_stat` moves
into the M1 set (frame weighting by EZV import shares happens at M1,
before any scraping), and the Strategy's `sighting` entity — dropped
from the session draft by mistake — is restored at M2.

## Probe-era schema (v0.1.1 — implemented now)

### Lookups (0001)

Common shape: `code TEXT PK, label TEXT NOT NULL, description TEXT`;
`probe_metric` adds `value_type TEXT NOT NULL CHECK (value_type IN
('numeric','text'))`.

- **source_class** — CS, PE, LG, ST, LI (10_STRATEGY/DATA_SOURCE.md D1).
- **access_method** — api, scrape, download, manual. Reused as the
  per-fetch retrieval method on `document` and the per-finding method
  on `probe_finding`.
- **verification_status** — verified, partially_verified, open,
  unverified.
- **language** — ISO 639-1 codes (de, fr, it, en, nl, sv, da, no, fi …).
- **document_status** — archived (raw file in store), manual (no raw
  file; retrieved by hand), derived (generated artifact), not_found.
- **run_kind** — probe, acquire, import, sampling.
- **run_status** — planned, running, done, failed, blocked, aborted.
- **probe_mode** — census, format_check, access_check.
- **quantity_unit** — count, chf, eur, kg, t, l, percent, ppm, year.
- **probe_metric** — the census metric vocabulary; authoritative list
  and extension rule in interfaces.md. Seeds: catalog_count,
  category_count, category_list, format, granularity, coverage_years,
  export_rows, robots, terms, rate_limit, languages, page_sample_ok,
  sds_sample_ok, extraction_path, access_blocked, robots_denied,
  free_access.

### Core tables (0002)

**source** — reference data (updatable, never deleted); mirrors the
register in 10_STRATEGY/DATA_SOURCE.md.
- id TEXT PK — register ID (`CS-1`), CHECK `^[A-Z]{2}-[0-9]+$`
- class_code → source_class; name TEXT NOT NULL; url TEXT NOT NULL
- access_method_code → access_method; license_note TEXT
- verification_status_code → verification_status (default `open`)
- active INTEGER NOT NULL DEFAULT 1; notes TEXT
- (`first_retrieved` from the Strategy schema is derivable — provided
  by v_source_activity, not stored.)

**document** — the provenance backbone: one row per retrieved
artifact (web page, PDF, CSV export, manual save). The raw store holds
the bytes at `data/raw/<source_id>/<sha256>.<ext>`; filenames are
hash-only (security rule, interfaces.md P5).
- id INTEGER PK; source_id → source NOT NULL
- run_id → run NOT NULL (retrieved inside a run — P1/R9 hold for
  documents by construction)
- url TEXT NOT NULL; retrieved_at TEXT NOT NULL
- raw_hash TEXT UNIQUE — sha256 of raw bytes; CHECK
  (status_code != 'archived' OR raw_hash IS NOT NULL)
- content_type TEXT; language_code → language; title TEXT
- size_bytes INTEGER; retrieval_method_code → access_method
- status_code → document_status NOT NULL DEFAULT 'archived'; notes TEXT
- Index: (source_id), (run_id); UNIQUE (raw_hash).

**run** — one audit-trail row per operation, any kind.
- id INTEGER PK; run_key TEXT UNIQUE NOT NULL — deterministic,
  `<kind>-<YYYYMMDD>-<slug>` (e.g. `probe-20260910-cs1`); same-day
  re-runs append `-2`, `-3` (ids.py)
- kind_code → run_kind NOT NULL; source_id → source — CHECK
  (kind_code != 'probe' OR source_id IS NOT NULL): **probe runs are
  per-source** (CEO review), so partial failure is visible per source
- started_at TEXT NOT NULL; finished_at TEXT
- status_code → run_status NOT NULL DEFAULT 'planned' (initial state
  per the run lifecycle; the engine moves it to running/done)
- parameters_json TEXT; seed INTEGER; notes TEXT
- Index: (source_id), (kind_code), (status_code),
  (source_id, status_code, started_at) — covering v_probe_latest.

**probe_run** — typed detail of a probe run.
- run_id INTEGER PK → run; mode_code → probe_mode NOT NULL

**probe_finding** — one census observation. Provisional by definition;
promotion to population_anchor/frame_stratum is a manual method
decision (10_STRATEGY/MASTER.md D20).
- id INTEGER PK; run_id → run NOT NULL (via probe_run)
- metric_code → probe_metric NOT NULL
- value_numeric REAL; value_text TEXT — CHECK (value_numeric IS NOT
  NULL OR value_text IS NOT NULL); presence follows
  probe_metric.value_type (audit rule R4)
- unit_code → quantity_unit; method_code → access_method NOT NULL
  (how this finding was obtained)
- document_id → document (evidence sample page / export)
- notes TEXT
- Index: (run_id, metric_code), (document_id).
- Normalization note: the Strategy schema's inline `source_id` and
  `raw_hash` are dropped — reached via `run.source_id` and
  `document.raw_hash` (no transitive dependencies).

### Probe-era views (0002)

- **v_probe_latest** — the current finding per (source, metric):
  latest **done** run (status_code='done'; by started_at, then run
  id) per source × metric; aborted/failed/blocked runs keep their
  findings but never shadow the current census.
- **v_anchor_candidates** — latest findings with metric in
  (catalog_count, category_count, export_rows) — candidate population
  anchors for manual promotion. Redefined by 0003 (adds the
  records_hs* metrics) and by 0005 to also exclude
  findings already promoted (NOT EXISTS on
  population_anchor.promoted_from_finding_id).
- **v_source_activity** — per source: first/last document retrieved_at,
  run count, finding count.

## Full schema (designed now; migrations 0004–0010)

### Dictionary group (0004, M1)

**substance** — the Strategy `lead_compound` dictionary, generalized:
study-agnostic, lead-target flagged.
- id INTEGER PK; name TEXT NOT NULL (canonical)
- function_code → substance_function
- sds_visible_floor_ppm REAL; verification_status_code →
  verification_status NOT NULL
- is_lead_target INTEGER NOT NULL DEFAULT 0; notes TEXT
- Seeded from `src/leadhs/dict/substances.csv` (10_STRATEGY/LEAD_SDS.md
  dictionary v0.1; unverified CAS stay flagged — D6 there).

**compound_synonym** — multilingual synonyms.
- id INTEGER PK; substance_id → substance NOT NULL; language_code →
  language (NULL = language-neutral/Latin); synonym TEXT NOT NULL;
  is_preferred INTEGER NOT NULL DEFAULT 0
- UNIQUE (substance_id, language_code, synonym)

**compound_identifier** — CAS/EC/Index/CI as rows, not columns.
- id INTEGER PK; substance_id → substance NOT NULL;
  identifier_type_code → identifier_type NOT NULL; value TEXT NOT NULL;
  is_primary INTEGER NOT NULL DEFAULT 0; verification_status_code →
  verification_status
- UNIQUE (identifier_type_code, value) — handles multi-CAS substances
  (e.g. lead sulfate 7446-14-2 / 15739-80-7).

Lookups: **substance_function** (pigment, drier, anticorrosive,
extender, intermediate, other, unknown); **identifier_type** (cas_rn,
ec_number, index_number, ci_number);
**hcode** (code, statement, severity_class) — H-statements as data,
extensible without migration. No legal-status lookups — EU legal
status and Swiss relevance stay columns of the LEAD_SDS.md
documentation table (Strategy MASTER D27).

### Catalog & frame group (0005, M1)

**study** — the reuse discriminator (CEO review decision).
- id INTEGER PK; code TEXT UNIQUE NOT NULL (`lead_hs`); name TEXT;
  description TEXT; active INTEGER NOT NULL DEFAULT 1
- Seeded by this migration.

**org** — subsumes the Strategy `manufacturer` and the "retailer"
strings on sightings.
- id INTEGER PK; name TEXT NOT NULL; country_code → country; website
  TEXT; notes TEXT

**product** — formulation-level unit of analysis (Strategy D2).
- id INTEGER PK; study_id → study NOT NULL
- name_base TEXT NOT NULL (normalized; rules open — pilot);
  name_display TEXT; primary_org_id → org
- origin_code → origin NOT NULL DEFAULT 'unknown'
- census_flag INTEGER NOT NULL DEFAULT 0 (3213 annex)
- first_seen TEXT; last_seen TEXT; delisted INTEGER NOT NULL DEFAULT 0;
  notes TEXT
- Index: (study_id), (name_base).
- Classifications (stratum, CN) are NOT inline — they
  live in product_classification with history.

**product_org** — product ↔ organization relationships.
- id INTEGER PK; product_id → product NOT NULL; org_id → org NOT NULL;
  role_code → org_role NOT NULL; source_id → source; document_id →
  document; first_seen TEXT; notes TEXT
- UNIQUE (product_id, org_id, role_code)

**product_classification** — history-preserving classification
(stratum, CN inference).
- id INTEGER PK; product_id → product NOT NULL; stratum_code →
  stratum; cn_code_id → cn_code;
  confidence_code → confidence; method_note TEXT; source_id → source;
  document_id → document; assessed_at TEXT; active INTEGER NOT NULL
  DEFAULT 1; notes TEXT
- Partial UNIQUE index: (product_id) WHERE active = 1 — one current
  classification, full history retained (partial-index syntax is the
  second PostgreSQL variance).

**category** — catalog categories as discovered by probing.
- id INTEGER PK; source_id → source NOT NULL; parent_id → category
  (self); name TEXT; name_normalized TEXT; path TEXT; product_count
  INTEGER; last_counted_at TEXT; notes TEXT

**product_category** — product ↔ category assignments.
- id INTEGER PK; product_id → product NOT NULL; category_id →
  category NOT NULL; document_id → document; assigned_at TEXT;
  confidence_code → confidence
- UNIQUE (product_id, category_id)

**population_anchor** — triangulation inputs; kept separate from
frame_stratum so estimates stay auditable (resolves the Strategy open
item; SPIN counts arrive here as anchor_code='spin').
- id INTEGER PK; study_id → study NOT NULL; anchor_code → anchor_kind
  NOT NULL; value REAL NOT NULL; unit_code → quantity_unit; year
  INTEGER; provenance TEXT; source_id → source; document_id →
  document; **promoted_from_finding_id → probe_finding** (the manual
  promotion pointer — lives here, not on probe_finding, keeping
  findings immutable); pinned_at TEXT; notes TEXT

**frame_stratum** — the pinned frame: one row per stratum × origin per
study.
- id INTEGER PK; study_id → study NOT NULL; stratum_code → stratum
  NOT NULL; origin_code → origin NOT NULL; population_estimate REAL;
  method_code → frame_method; provenance TEXT; source_id → source;
  document_id → document; pinned_at TEXT; notes TEXT
- UNIQUE (study_id, stratum_code, origin_code)

**frame_stratum_anchor** — junction: which anchors a frame estimate
was triangulated from.
- frame_stratum_id → frame_stratum, population_anchor_id →
  population_anchor; PK (frame_stratum_id, population_anchor_id)

**cn_code** — versioned nomenclature (reference data).
- id INTEGER PK; code TEXT NOT NULL (CN8); heading TEXT NOT NULL
  (3208/3209/3213); description TEXT; valid_from INTEGER NOT NULL;
  valid_to INTEGER
- UNIQUE (code, valid_from) — CN 2025 vs 2026 etc.

Lookups: **org_role** (producer, importer, private_label, retailer,
brand_owner, distributor); **origin** (CH, EU, THIRD, unknown — EU =
marketed in the EU/EEA);
**confidence** (high, medium, low, manual); **stratum** (S1–S8,
CENSUS_3213 with cn_prior/lead_prior description fields from
10_STRATEGY/METHODOLOGY.md); **anchor_kind** (pcn, spin, prodcom,
comext, sbs, literature, catalog_census); **frame_method**
(catalog_count, triangulated, spin_proxy); **country** (code = ISO-2
PK, iso3, name, name_de, name_fr).

### Sampling group (0006, M1)

**sampling_run** — typed detail of a sampling run; parameters and seed
live on `run` (single home).
- run_id INTEGER PK → run; study_id → study NOT NULL; scope_json TEXT;
  computed_n_total INTEGER; computed_n_per_stratum_json TEXT

**sample_selection** — the reproducible draw.
- id INTEGER PK; run_id → run NOT NULL; product_id → product NOT NULL;
  stratum_code → stratum; origin_code → origin; selected_at TEXT;
  screen_code → screen_status NOT NULL DEFAULT 'pending';
  exclusion_code → exclusion_reason; screener_note TEXT
- UNIQUE (run_id, product_id)

Lookups: **screen_status** (pending, no_sds, not_a_paint, duplicate,
screened_ok); **exclusion_reason** (no_sds_found, not_a_paint,
duplicate_product, delisted, out_of_scope, other).

### Trade statistics group (0007, M1)

**trade_stat** — EZV + Comext rows.
- id INTEGER PK; run_id → run (import provenance); source_id → source
  NOT NULL; year INTEGER NOT NULL; cn_code_id → cn_code NOT NULL;
  partner_code → country NOT NULL; flow_code → flow NOT NULL
- value_chf REAL; net_weight_kg REAL; quantity REAL; quantity_unit_code
  → quantity_unit
- UNIQUE (source_id, year, cn_code_id, partner_code, flow_code)

Lookup: **flow** (import, export).

### SDS group (0008, M2)

**sds_document** — an SDS is a typed document (document_id subtype).
- document_id INTEGER PK → document; product_id → product NOT NULL;
  revision_date TEXT; format_vintage_code → sds_format_vintage;
  parse_status_code → parse_status NOT NULL DEFAULT 'pending'; ufi
  TEXT (verbatim from that sheet); notes TEXT

**product_ufi** — the UFI join key across markets/versions (format and
validation rules open — pilot).
- id INTEGER PK; product_id → product NOT NULL; ufi TEXT NOT NULL;
  document_id → document; source_id → source; first_seen TEXT;
  confidence_code → confidence; verification_status_code →
  verification_status
- UNIQUE (product_id, ufi)

**sds_ingredient** — verbatim Section 3 lines (evidence).
- id INTEGER PK; sds_document_id → sds_document NOT NULL; line_no
  INTEGER NOT NULL; name_as_written TEXT NOT NULL; cas_raw TEXT;
  ec_raw TEXT; concentration_raw TEXT; function_raw TEXT
- UNIQUE (sds_document_id, line_no)

**sds_finding** — the interpretation: dictionary match + review.
- id INTEGER PK; sds_document_id → sds_document NOT NULL;
  ingredient_id → sds_ingredient; substance_id → substance (NULL =
  non-dictionary hit kept for review); match_code → match_method NOT
  NULL; function_code → substance_function; concentration_min REAL;
  concentration_max REAL — CHECK (concentration_min IS NULL OR
  concentration_max IS NULL OR concentration_min <= concentration_max);
  concentration_type_code → concentration_type NOT NULL; review_code →
  review_status NOT NULL DEFAULT 'auto'; notes TEXT
- Index: (sds_document_id), (substance_id).

**sds_finding_hcode** — classification codes as junction.
- sds_finding_id → sds_finding, hcode_code → hcode; PK pair

**sds_section15** — Section 15 statements as anomaly signal
(10_STRATEGY/MASTER.md D5), normalized to document level.
- id INTEGER PK; sds_document_id → sds_document NOT NULL;
  statement_raw TEXT NOT NULL (the sheet's own text — kept as document
  content; no legal-coded classification of it, Strategy MASTER D27)

Lookups: **concentration_type** (exact, range, declared_ge_0.1,
none_listed — the declared-vs-total blind-spot taxonomy,
10_STRATEGY/MASTER.md D15; `none_listed` ≠ lead-free); **match_method**
(cas_exact, ec_exact, name_synonym, manual); **parse_status** (pending,
parsed, failed, manual); **review_status** (auto, confirmed, corrected,
rejected); **sds_format_vintage** (pre_2020_878, post_2020_878,
unknown — staleness flag).

### Evidence group (0009, M2–M3)

**sighting** — one product appearance at one place/time; the dedup
layer (Strategy D2/D17). Restored here after being dropped from the
session draft.
- id INTEGER PK; product_id → product NOT NULL; document_id →
  document NOT NULL (the listing page); retailer_org_id → org; price
  REAL; currency TEXT (ISO 4217); packaging TEXT (verbatim, e.g.
  "750 ml"); sighted_at TEXT; notes TEXT
- Index: (product_id), (document_id).

**corroboration** — cross-document checks for suspected positives
(no laboratory; 10_STRATEGY/MASTER.md D7).
- id INTEGER PK; product_id → product NOT NULL; sds_finding_id →
  sds_finding; document_id → document NOT NULL; document_type_code →
  document_type; agrees_code → agree_state; note TEXT

Lookups: **document_type** (sds, tds, label, listing, older_sds,
cross_market, declaration, sample_page, export,
statistics); **agree_state** (yes, no, partial).

### Views (0005 adds; 0010 completes)

- **v_product_current** (0005) — latest active classification per
  product.
- **v_finding_full** (0010) — finding joined through sds_document,
  product, current classification, substance, hcodes: the report join
  (single join, no per-row queries — N+1 guard); lead-finding filter
  on an is_lead_target substance with concentration_type in
  (exact, range, declared_ge_0.1). Derived, never stored; the
  declared-vs-total caveat (D15) is part of its definition.
- **v_product_dossier** (0010) — per-product evidence dossier
  (sightings, SDS documents, findings, corroborations, provenance) —
  source of the M4 dossier annex (CEO review decision).
- **v_trade_ch** (0010) — trade_stat joined cn_code/country for report
  tables.
- **v_census_3213** (0010) — census-flagged products with their
  findings (artists' colours annex).

## db audit

The audit rule set (R1–R9) is specified authoritatively in
interfaces.md; it is code-enforced (db.py), walking the tables that
exist per applied migrations.

## Reuse & portability

- **Second study, zero migration:** insert a `study` row; its
  products, anchors, frames, sampling runs live under that study_id.
  Substance dictionary, documents, sources, lookups are shared.
- **PostgreSQL port:** documented variances only — BOOLEAN, JSONB, id
  generation (`INTEGER PRIMARY KEY` rowid alias → IDENTITY/BIGSERIAL),
  and the `product_classification` partial-index syntax; no other
  SQLite-only constructs in migrations (no AUTOINCREMENT, no PRAGMA —
  pragmas are runtime connection settings in db.py).
- **Export artifact (M4, designed now):** frozen snapshot
  (backup API/VACUUM INTO), generated schema doc + data dictionary,
  CSV dumps per table, and a raw-hash manifest so the released
  evidence database stays hash-verifiable (interfaces.md).

## DECISIONS (design-level; consolidated in 20_DESIGN/MASTER.md)

- dm1: lookups keyed by stable TEXT codes; entities INTEGER PK.
- dm2: `document` provenance backbone replaces per-table
  url/source/retrieved_at.
- dm3: unified `run` + typed detail tables (probe_run, sampling_run;
  acquire/import details deferred to their milestones).
- dm4: probe_finding drops the Strategy's inline source_id/raw_hash
  (reached via run/document).
- dm5: anchor-promotion pointer on population_anchor, not on
  probe_finding — findings stay immutable.
- dm6: product classifications history-preserving (active flag), not
  inline on product.
- dm7: verbatim (sds_ingredient) vs interpretation (sds_finding) split.
- dm8: substance generalization with is_lead_target.
- dm9: `study` discriminator now (CEO review).
- dm10: trade_stat in the M1 set (frame weighting precedes scraping);
  sighting restored at M2 — session-draft corrections.
- dm11: views ship with the dependency-completing migration;
  redefinition allowed and recorded.
- dm12: append-only evidence; reference data updatable, never deleted.
- dm13: ON DELETE RESTRICT everywhere.
- dm14: run lifecycle in schema — initial status `planned`;
  v_probe_latest restricted to `done` runs (ENG review 2026-09-11).
- dm15: document.run_id NOT NULL — the provenance backbone is
  run-complete; P1/R9 hold for documents by construction.

## OPEN ITEMS

- name_base normalization/dedup rules — Phase-1 pilot (inherited).
- UFI format, validation, collision handling — pilot (inherited).
- swiss-impex export shape → trade_stat ingest mapping — the v0.1.1
  probe answers this.
- SPIN table structure → import mapping; 0007/import tooling may
  adjust after the probe checks mdbtools extraction.
- Export format: CSV is stdlib; Parquet would add a dependency —
  default CSV, Parquet only if a consumer requires it (M4).
- org dedup/merge workflow (same chain, name variants) — M2 ingest
  design.
- run.parameters_json schema per kind — probe fixed now
  (interfaces.md); others defined at their milestones.
- Backup target directory — propose `data/backups/` (gitignored);
  confirm at implementation.
- trade_stat.run_id nullable vs P1 — confirm import-only provenance
  (manual trade-stat entry would need a run or an exception rule).

## REFERENCES

- 10_STRATEGY/DATA_MODEL.md — the Strategy schema this refines
- 10_STRATEGY/MASTER.md — D2, D7, D15–D20 (principles anchored)
- 10_STRATEGY/DATA_SOURCE.md — source register, provenance discipline
- 10_STRATEGY/METHODOLOGY.md — strata table, taxonomies
- 10_STRATEGY/LEAD_SDS.md — dictionary v0.1, legal statuses
- 10_STRATEGY/ARCHITECTURE.md — rollout M0–M4
- CEO review session 2026-09-10 (mode EXPANSION): document backbone,
  unified runs, study discriminator, export path, dossier — user
  decisions recorded in 20_DESIGN/MASTER.md.

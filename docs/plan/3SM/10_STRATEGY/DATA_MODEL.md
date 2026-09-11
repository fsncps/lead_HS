---
unit: v0.1.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-11
---

# Data model — the evidence database

## Abstract

One SQLite database (`data/leadhs.sqlite`) holds everything the study
collects and produces: sources, manufacturers, products (formulation
level), safety data sheets and their parsed findings, the lead-compound
dictionary, corroboration records, trade statistics, and sampling runs
with parameters and selections. The design encodes three project-specific
needs: provenance on every record, reproducible sampling, and an honest
distinction between *declared* lead (what an SDS shows) and *total* lead
(what the Swiss ban regulates — unmeasurable here). The schema is given
at strategy altitude: entities, fields and keys, not final DDL.

## Design principles

1. **Provenance-first:** every row links to `source` + `retrieved_at`;
   raw documents live in the raw store, referenced by hash.
2. **Formulation as the unit** (MASTER decision 2): colour/size variants
   collapse into one `product`; SKU sightings are separate rows, not
   products.
3. **Declared ≠ total:** findings store the *declared* concentration
   (value/range/floor); Swiss-ban relevance is a documentation-layer
   conclusion, never a stored field and never a measurement
   (MASTER D27).
4. **Reproducibility:** every sampling run stores its parameters and
   seed; the same run ID re-yields the same selection.
5. **Verification flags:** unverified CAS/EC stay flagged. The
   dictionary carries **no legal-status fields** (MASTER D27) — EU
   legal status and Swiss relevance stay columns of the LEAD_SDS.md
   documentation table only.
6. **Multilingual by default:** product names and SDS text keep their
   language; the compound dictionary carries DE/FR/IT/EN synonyms.

## Entities (strategy-level schema)

**source** — id, class (CS/PE/LG/ST/LI), name, url, access_method
(api/scrape/download/manual), license_note, verification_status,
first_retrieved, notes. Mirrors DATA_SOURCE.md.

**probe_run** — id, source_id, started_at, finished_at, mode
(census/format_check/access_check), parameters_note, status
(running/done/failed/blocked), notes. (Unit v0.1.1; the source-census
instrument — MASTER D19/D20.)

**probe_finding** — id, probe_run_id, source_id, metric
(catalog_count/category_count/format/granularity/coverage_years/
robots/terms/rate_limit/languages/sds_sample_ok/extraction_path/…),
value, unit, method, url, raw_hash (nullable — sample pages), notes.
Provisional by definition; promotion to `population_anchor` /
`frame_stratum` is a manual method decision, never automatic.

**manufacturer** — id, name, brand_family, country (ISO-2), website,
type (producer/importer/private_label), source_id, notes.

**product** — id, manufacturer_id, name_base (normalized), name_display,
segment_stratum (S1–S8 | CENSUS_3213), cn_code (inferred) +
cn_confidence (high/medium/low/manual), origin (CH/EU/THIRD/unknown),
census_flag, first_seen, last_seen, delisted, source_id. Product data
only — no legal category, no ban-engagement flag (MASTER D27); the
lawful/illegal lens lives in the study documentation.

**sighting** — id, product_id, url, retailer/context, price, packaging,
date, source_id. (One product, many sightings — the dedup layer.)

**sds_document** — id, product_id, url, raw_hash, language, revision_date,
format_vintage (pre/post-2021 Reg 2020/878 — staleness flag), retrieved_at,
parse_status (pending/parsed/failed/manual), source_id.

**sds_finding** — id, sds_document_id, cas_rn, ec_number, name_as_written,
match_method (cas_exact/ec_exact/name_synonym/manual), compound_id →
lead_compound (nullable — non-dictionary hits kept for review), function
(pigment/drier/anticorrosive/extender/other/unknown), concentration_raw
(text as in sheet), concentration_min, concentration_max,
concentration_type (exact/range/declared_ge_0.1/none_listed),
classification_codes (H-codes), ufi (Sec 1.1), section15_notes,
review_status (auto/confirmed/corrected/rejected).

**lead_compound** (dictionary, seeded from LEAD_SDS.md) — cas_rn (key
where available), ec_number, name, synonyms (multilingual), ci_number,
function_class, sds_visible_floor, verification_status
(verified/ECHA-pending), notes. No legal-status fields (MASTER D27) —
EU legal status and Swiss relevance stay columns of the LEAD_SDS.md
documentation table only.

**corroboration** — id, product_id, finding_ref, document_type
(tds/label/listing/older_sds/cross_market/declaration), url, raw_hash,
agrees (yes/no/partial), note, source_id. Consistency score derived.

**trade_stat** — id, year, cn8, partner_country, flow (import/export),
value_chf, net_weight_kg, quantity_unit, source_id. (EZV + Comext rows.)

**frame_stratum** — id, stratum, origin, population_estimate, method
(catalog_count/triangulated/spin_proxy), provenance note, source_id,
pinned_at. (Phase-0/2 output; feeds sample-size computation.)

**sampling_run** — id (e.g. `2026-09-pilot-01`), created_at, scope
(strata × origins included), parameters_json (p, precision, confidence,
FPC on/off, per-stratum overrides), seed, computed_n_total,
computed_n_per_stratum_json, status (planned/drawn/screened/analyzed).

**sample_selection** — id, run_id, product_id, stratum, origin,
selected_at, screen_status (pending/no_sds/not_a_paint/duplicate/
screened_ok), exclusion_reason, screener_note.

**population_anchor** — id, anchor (pcn/spin/prodcom/comext/sbs/
literature), value, unit, year, provenance, source_id. (Triangulation
inputs for population estimates, kept separately so estimates stay
auditable.)

## Enumerations (taxonomies)

- origin: CH | EU | THIRD | unknown (EU = marketed in the EU/EEA).
- concentration_type: exact | range | declared_ge_0.1 | none_listed —
  the blind-spot taxonomy: `none_listed` ≠ lead-free.
- match_method: cas_exact | ec_exact | name_synonym | manual.
- screen_status / exclusion_reason: fixed list, extensible via review.

## Storage & lifecycle decisions

- SQLite, single file, WAL mode; `schema_version` table + plain SQL
  migration files; no ORM (stdlib sqlite3 + dataclasses).
- Migrations land per milestone: v0.1.1 creates the probe-era subset
  (`schema_version`, `source`, `probe_run`, `probe_finding`); remaining
  tables arrive with M1–M4 (v0.1.1.md U2).
- `data/leadhs.sqlite` and `data/raw/` are gitignored; code, migrations,
  seed dictionaries (`src/leadhs/dict/*.csv`) and final generated
  reports are in git.
- Append-only: corrections are new rows / review_status changes, never
  destructive deletes — the audit trail is preserved.

## Rendered diagrams

The strategy-level ER rendering (`data-model-er`) is archived under
`../_archive/10_STRATEGY/charts/` (superseded 2026-09-11); the
authoritative schema is this document and the design-level
normalization in 20_DESIGN/MASTER/data_model.md.

## DECISIONS

- D1: single SQLite file, no server, no ORM (fits cost constraint,
  Slackware/no-systemd, single researcher).
- D2: formulation-level `product` + `sighting` dedup layer (MASTER
  decision 2; PCN/KemI co-notification logic).
- D3: `concentration_type` taxonomy encodes the declared-vs-total-Pb
  blind spot at schema level (MASTER decision 15).
- D4: sampling runs are first-class, seeded, reproducible entities.
- D5: append-only corrections.
- D6: dictionary maintained as seed CSV in repo → `lead_compound` table;
  unverified CAS stay flagged until ECHA EC-inventory check.
- D7: probing has first-class entities (`probe_run`, `probe_finding`)
  with full provenance; counts are provisional — anchor promotion is
  manual (MASTER D20).
- D8: milestone-gated migrations — v0.1.1 migrates the probe-era subset
  only (MASTER D19).

## OPEN ITEMS

- Exact dedup/normalization rules for `name_base` — calibrate in the
  Phase-1 pilot (likely brand + core name minus colour/size tokens).
- UFI as join key: format, validation, collision handling — pilot.
- Whether `population_anchor` merges into `frame_stratum` provenance —
  decide at Design.
- CN-inference confidence taxonomy refinement (borderline
  3208 10/20/90 polymer-solution cases).
- SPIN-derived counts: own table vs `population_anchor` rows — Design.
- Category→stratum mapping for catalog counts — frame decision at M1
  (v0.1.1.md U3).

---
unit: global
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-17
---

# RAW_SOURCING — bulk source tables, seed CLI and repeatable acquisition

## Abstract

Before the study can consolidate or match anything (MATCHING.md), the
bulk sources must be downloaded and copied into **raw source tables** —
verbatim, unfiltered ("copy whatever we can get"; filtering happens at
the analysis layer, never at ingest). This topic fixes the strategy
shape for that layer: SQLite stays the engine; one raw table per
source, created from a committed **source manifest** (probe output,
reviewable before data flows); idempotent seed runs with resume and
change detection; a per-record byte budget whose overflow spills to the
existing raw store instead of being dropped; list-endpoint-first
crawling as a politeness gate. Converged with the user 2026-09-17
(engine, history model, oversize policy confirmed); local decisions
R1–R9, adoption as MASTER decisions at the next strategy turn / the
product-DB unit's Design. Immediate driver: BASTA (AS-33, 195,390
articles) as the third bulk source next to ECAT (17,013 distinct) and
Nordic Swan (2,322).

## Problem statement

The v0.3-era product-DB build needs bulk copies of source catalogs in
the evidence database. Requirements: repeatable (interrupt and resume
without restarting or overwriting), incremental (rerun updates only
missing/changed records), extensible (a future source becomes a new raw
table without code changes for a same-shape source), and honest
(provenance on every record, nothing silently dropped or truncated).

## Engine

SQLite stays (re-confirmed over a Postgres proposal, with numbers):
realistic ceiling ≈ 1M records / 0.2–2 GB — single-writer, single-user,
local analysis; batched WAL transactions beat a server round-trip for
bulk loads; no server process (D1), no install burden on Slackware or
vanilla Windows (D32), dependency set unchanged (D16). Hedge without
cost: raw-layer SQL stays portable (standard types, no SQLite-only
tricks) so a later dump-and-reload to Postgres stays possible if any
source ever outgrows SQLite (~5 GB / latency checkpoint — no trigger
built, evaluation would be explicit).

## Core fields (per record, always kept, uncapped)

- `manufacturer` — as written by the source (normalization happens
  downstream, MATCHING.md Stage 1);
- `product_ident` — the source's unique product id / article number
  (the natural key); variant discriminator column where the source
  needs one;
- `group_code` — the source's own product-group identifier, **nullable
  and verbatim**; not all sources carry an HS-linkable group (BASTA:
  BK04/BSAB, not HS — D40 relaxation). Any group→HS mapping lives in a
  separate per-source reference table, never inside raw rows;
- `name_display`, `url`, `retrieved_at` (provenance, D17), run bookkeeping.

Additional fields per source: as available, declared in the manifest.

## Table creation — manifest-driven

Probe produces a committed **source manifest** (JSON per source):
field list + types, natural key (+ variant discriminator), per-field
priorities for the payload budget, pagination shape, politeness params
(delay, per-domain budget), endpoints. `raw init <source>` creates the
table *from the manifest* — idempotent (create-if-not-exists), recorded
in a `raw_table_registry` (source, manifest hash, created_at) so the
forward-only migration discipline (ARCHITECTURE failure behavior)
stays intact. Every table shape is reviewable in git before any data
flows; no schema decided implicitly by the scraper.

## Seed semantics (repeatable + incremental)

1. **Upsert on natural key** with a **content hash** (sha256 over the
   normalized payload): missing key → insert; hash equal → skip; hash
   different → update + change journal.
2. **History model — upsert + change journal** (confirmed over
   append-per-run and current-state-only): raw rows hold current state;
   a `raw_change` journal records rows whose hash changed (old hash,
   run, field delta where cheap). Content changes (SDS revisions,
   specs) are themselves evidence — preserved without duplicating
   ~200k rows per rerun. Per record: `first_seen_run`,
   `last_seen_run`, `last_changed_run` — presence history (delisted
   detection) falls out for free.
3. **Checkpointed batches**: commit every N records with a cursor
   checkpoint (page/offset cursor per source); an interrupted run
   resumes at the last committed batch — no re-fetch hammering
   (politeness), no partial-batch loss (transaction).
4. **Run journal**: every seed run gets a run_key (existing staging
   run_key pattern); `raw status <source>` reports counts, last run,
   hash-changes, spilled/oversize counts, coverage vs the source's
   pinned total (keyfigures anchors, D40 pattern).

## Oversize policy — spill, not drop (confirmed)

- Core fields above: never capped.
- Payload: per-record byte budget (order 1 KB inline; value set per
  manifest) with the manifest's **per-field priority list** deciding
  deterministically what stays inline — same run always truncates the
  same way (reproducibility, D4).
- Overflow → **spill to the existing raw store** (`data/raw/`,
  sha256-named files, content-deduped); the record keeps the hash
  reference and a `payload_status` flag (`inline` | `spilled` |
  `unavailable`). Nothing is lost at ingest; spilling is reversible at
  analysis, dropping is not. Every record still carries url +
  retrieved_at, so even an `unavailable` remains re-fetchable.

## Politeness gate — list-endpoint-first

Data-side math (D40): BASTA robots Crawl-delay is 10 s. Per-article
fetching of 195,390 articles ≈ 22.6 days of continuous crawling;
list pages of ~50–100 articles ≈ 2,000–4,000 requests ≈ 6–11 hours.
Therefore: **bulk-copy from listing/search routes; per-article detail
fetches only for sampled subsets** (the 100-row CSV pattern, v0.2.4).
A source whose bulk copy would require per-article fetching at scale
fails the de5 entry gate in practice — the feasibility check belongs
in the probe pass, not mid-seed. Rate limiting + per-domain backoff
live in the seed driver, resuming the existing acquire discipline
(ARCHITECTURE stage 2).

## CLI / Make surface (extends the existing `leadhs` CLI)

    leadhs raw init <source>     # create table from manifest (idempotent)
    leadhs raw seed <source>     # list-endpoint walk → upsert;
                                 #   --cap --resume --limit --dry-run
    leadhs raw status <source>   # counts, runs, hash-changes, spill stats
    leadhs raw export <source>   # later: feed the matching layer
    leadhs db healthcheck        # extend existing db status/audit + doctor

Make targets wrap these one-call-per-target under the existing `GO=1`
network guards (v0.1.2 pattern). Existing commands (db init/status/
audit, source load/list, probe run) continue unchanged.

## Raw-layer storage sketch (strategy altitude)

    raw_table_registry — source, table_name, manifest_hash, created_at
    raw_<source>       — natural key, core fields, source-specific
                         fields, payload (inline part), payload_status,
                         payload_refs (hashes of spilled fields),
                         content_hash, first/last/changed run
    raw_change         — source, natural key, old_hash, new_hash, run,
                         note
    group_map_<source> — source group code → HS/CN mapping (nullable,
                         per-source, manual, versioned seed CSV in repo)

## DECISIONS

*(local numbering R1…; promotion to MASTER decisions at the next
strategy turn / unit Design — nothing frozen.)*

- **R1 (confirmed):** SQLite stays the engine for raw source tables;
  Postgres rejected again (D1/D16/D32 stand); portable-SQL hedge.
- **R2 (confirmed):** history model = upsert + change journal; never
  append-per-run, never history-free.
- **R3 (confirmed):** oversize = spill to the raw store with hash ref +
  status flag; never a silent drop; core fields uncapped.
- **R4 (proposed):** table creation is manifest-driven and idempotent,
  registered against the migration discipline; probe output is the
  committed contract.
- **R5 (proposed):** list-endpoint-first crawling is a de5-style design
  gate; per-article-at-scale sources need an explicit feasibility pass
  in probe before seed is built.
- **R6 (proposed):** core field triple = manufacturer, product_ident
  (natural key), group_code (nullable, verbatim); HS mapping lives in
  per-source reference tables, never in raw rows.
- **R7 (proposed):** seed runs are idempotent upserts keyed on natural
  key + content hash; interrupted runs resume from committed batch
  checkpoints.
- **R8 (proposed):** new source onboarding = manifest + priority seed
  CSV + `raw init` + `raw seed` — no pipeline-code changes for
  same-shape sources.
- **R9 (OPEN, → Design):** `raw_change` granularity (row-level vs
  field-level delta), checkpoint cursor representation per pagination
  shape, `raw export` shape feeding MATCHING.md, and the exact
  registry/migration reconciliation.

## OPEN ITEMS

- Field priority lists and inline budget values per source (manifest
  seeds) — set per source at onboarding, validated against the 100-row
  samples already on disk (ECAT/Nordic Swan/BASTA).
- BASTA anonymous list-route proof (D40's one unproven assumption) —
  PHASE01 of the basta-addendum pins it before any seed build.
- Whether group_code→HS mappings exist at all for BASTA BK04/BSAB
  (likely no direct HS equivalent) — affects how BASTA rows join the
  paint frame (documented at probe time, decided at next strategy turn).
- `raw status` coverage checks vs pinned keyfigures anchors — reuse the
  D40 keyfigures snapshot (195,390 / 1,925) as drift detectors.
- Sampled-subset detail fetches (per-article) — politeness budget and
  resume cursor for the detail walk (small scale, but same rules).
- Adoption order: raw layer before matching layer (MATCHING.md) — the
  product-DB unit phases sequence these.

## REFERENCES

- ARCHITECTURE.md — D1 (no-server SQLite — Postgres rejected there
  first), stage 2 raw store, acquire politeness principles, D8 make
  wrapper, D32 vanilla-Windows v0.2.4 context.
- DATA_MODEL.md — provenance-first principle, D5 append-only, D8
  milestone migrations, staging run_key pattern (v0.2.3 PHASE05).
- MATCHING.md — consumer of this layer (normalization/joins read raw
  rows); evidence tiers presuppose verbatim raw records.
- 10_STRATEGY/MASTER.md — D38 data_sources.csv registry + de5 entry
  gate, D40 BASTA keyfigures (195,390 articles, 1,925 companies,
  2026-09-17) and robots Crawl-delay 10 s.
- INPUT-source-expansion-MSE.md — bulk-source queue context; overreach
  warning: raw layer is sourcing infrastructure only, the MSE turn is a
  separate decision.
- 20_DESIGN/units/v0.2.4-basta-addendum.md — anonymous-search-route
  assumption (PHASE01) and article identity fields.

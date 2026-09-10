---
unit: v0.1.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-11
---

# Architecture — pipeline, CLI, reporting

## Abstract

The study's light data-engineering side is a single-user, no-server
pipeline: acquire documents → archive raw → ingest → parse SDS → build
the frame → draw reproducible samples → screen and corroborate → analyze
→ generate the report. One CLI (`leadhs`) drives all stages; state lives
in one SQLite database plus a raw-file store; every number in the final
report is generated from the database — nothing hand-copied. This
document fixes the strategy-level shape; detailed module design belongs
to 20_DESIGN.

## Stack (decided at strategy altitude)

- **Python ≥ 3.11**, stdlib-first (sqlite3, dataclasses, pathlib).
- Small dependency set: `requests`, `beautifulsoup4`, `click` (CLI),
  `jinja2` (reports), `pypdf` (PDF text; `pdftotext`/poppler preferred
  backend when available).
- Optional: `matplotlib` (charts), mdbtools route for the SPIN Access DB.
- **No servers, no services, no daemons** — fits Slackware/no-systemd
  and the minimal-cost constraint; every stage is a CLI step.
- Persistence: SQLite + raw store (DATA_MODEL.md).

## Pipeline stages

    probe → acquire → raw store → ingest → parse → frame → sample →
    screen → corroborate → analyze → report

0. **probe** (unit v0.1.1) — source census before any collection:
   per-source counts (catalogs, categories), access constraints
   (robots/terms/rate limits/languages), format checks (swiss-impex
   export, SPIN extraction path), sample pages as raw evidence;
   results land in `probe_run`/`probe_finding` and feed provisional
   population anchors (DATA_MODEL.md).

1. **acquire** — per-source fetchers (CS exports, PE polite scraper, LG/ST
   downloads); rate-limited, per-domain queues, robots-aware; official
   APIs/exports preferred (DATA_SOURCE.md discipline).
2. **raw store** — documents archived as retrieved (sha256-named); the DB
   references hashes: auditability before parsing.
3. **ingest** — sightings/products/manufacturers upserted with dedup;
   sources registered.
4. **parse** — SDS PDF → text → sections (multilingual DE/FR/IT/EN);
   Section 3 compound extraction against the dictionary (CAS/EC/synonyms);
   concentration ranges; UFI; Section 15 flags; confidence-tagged.
5. **frame** — stratum × origin population counts from catalogs +
   triangulation anchors → `frame_stratum`.
6. **sample** — parameterized, seeded draws.
7. **screen** — review queue for selected products (no SDS? not a paint?
   duplicate?) — manual decisions with CLI support.
8. **corroborate** — cross-document checks for suspected positives
   (TDS/labels/listings/older SDS/cross-market variants) with consistency
   scoring.
9. **analyze** — prevalence per stratum × origin (Wilson CIs), FPC, trade
   overlay, census annex tables.
10. **report** — templates rendered from the DB.

## CLI surface (`leadhs`)

    leadhs db init|status|audit          # schema, counts, provenance check
    leadhs source load|list|add          # seed register from repo CSV; manage
    leadhs probe run --source PE-1|--all # source census → probe_finding
    leadhs probe report                  # census summary + anchor candidates
    leadhs acquire run --source PE-1     # rate-limited fetch → raw store
    leadhs ingest sightings --file …     # upsert products/sightings
    leadhs parse sds [--product ID|all]  # parse queue → findings
    leadhs review next|decide ID …       # screening & parse-confidence queue
    leadhs frame set --stratum S3 --origin EU --population N --method …
    leadhs sample plan --p 0.05 --precision 0.015 --confidence 0.95 \
                       --fpc --strata S2,S3 --seed 42   # computes n, stores run
    leadhs sample draw --run RUN_ID      # reproducible selection
    leadhs analyze prevalence --run RUN_ID
    leadhs report build --run RUN_ID --lang de|fr|en --out docs/report/

The core user flow — set sampling parameters, run, get a report — is:
`sample plan` → `sample draw` → (screen/corroborate) → `analyze` →
`report build`.

## Rollout (implementation order; v0.1.1 = M0)

- **M0 — probe (unit v0.1.1):** `db init/status`, `source load/list`,
  `probe run/report`. Schema subset: `schema_version`, `source`,
  `probe_run`, `probe_finding`. Delivers the source census and
  provisional population anchors; nothing else is implemented.
- **M1 — frame & sample:** `frame set`, `sample plan`, `sample draw`
  (probe counts + trade stats → strata; parameters p/precision/
  confidence/FPC/seed).
- **M2 — acquire & parse:** `acquire run`, `ingest sightings`,
  `parse sds`, `review` — pilot on 1–2 strata (lead driers first),
  then full n.
- **M3 — corroborate & analyze:** `corroborate`, `analyze prevalence`.
- **M4 — report:** `report build` (DE/FR/EN), database freeze.

Remaining tables migrate with their milestone (probe results may
reshape frame/sample entities); the full schema stays as designed in
DATA_MODEL.md.

## Repository layout (target)

    src/leadhs/            # package: cli, db, acquire/, parse/, frame,
                           # sample, analyze, report/ (templates), dict/
    data/raw/              # gitignored raw store
    data/leadhs.sqlite     # gitignored database
    docs/report/           # generated reports (final ones committed)
    tests/                 # pytest: parse fixtures, seed reproducibility,
                           # CLI smoke
    pyproject.toml

## Report concept

- **Generated technical report** (jinja2 → Markdown; PDF via pandoc when
  available): title/abstract; regulatory frame (static text, verified
  references); Swiss trade analysis (tables from `trade_stat`);
  prevalence per stratum × origin with confidence intervals; the
  blind-spot/limitations section (mandatory — MASTER decision 15);
  corroboration findings; 3213 census annex; evidence-database
  description; annexes (compound dictionary, product evidence table).
  Every figure rendered from the DB, cited with run ID + seed.
- **Languages:** DE primary (federal actors), FR secondary, EN optional
  (EU leg). The hand-maintained bilingual `docs/management_summary.md`
  is never overwritten by generated artifacts.
- Intermediates are regenerated freely; final report versions are
  committed with their run IDs.

## Testing & quality (light but real)

- pytest; golden-file SDS parse fixtures (real sheets, anonymized);
  seed-reproducibility test (same run → same selection); CLI smoke
  tests; `db audit` checks provenance completeness (no finding without
  source/hash).

## Failure behavior (principles)

- acquire: per-domain backoff, resume; blocked sites → recorded manual
  fallback, never hammering.
- parse: confidence-tagged, nothing silently dropped — low-confidence
  extractions queue for manual review.
- db: append-only corrections; forward-only migrations.

## Rendered diagrams

`charts/architecture-components` — the `leadhs` system (module detail
per 20_DESIGN):

![The leadhs system: CLI, modules, raw store, SQLite](charts/architecture-components.png)

`charts/probe-process` — the M0 probe workflow (re-rendered 2026-09-11
to match the reviewed run semantics):

![Probe workflow per source class: robots/terms check, polite fetch, blocked/format decisions, sampling, raw archive](charts/probe-process.png)

Strategy diagrams are proposals — the written documents win. Index:
`charts/README.md`; superseded charts (pipeline data flow, run states,
data-model ER) are archived under `../_archive/10_STRATEGY/charts/`.

## DECISIONS

- D1: no-server, single-user CLI pipeline; SQLite + raw store
  (alternatives — Postgres, workflow engines, web app — rejected as
  cost/complexity).
- D2: one CLI (`leadhs`, click) drives all stages; parameters and seeds
  are first-class run attributes.
- D3: reports are generated from the DB only — no hand-copied numbers;
  hand-maintained and generated documents never mix.
- D4: raw store before parsing (auditability); official exports over
  scraping.
- D5: stdlib-first, small dependency set, Python ≥ 3.11.
- D6: probe-first rollout — M0 (v0.1.1) ships probing tools only; the
  full surface is implemented progressively (MASTER D19).
- D7: probing is a first-class pipeline stage with its own entities
  (`probe_run`/`probe_finding`), not an ad-hoc script (MASTER D20).

## OPEN ITEMS

- PDF text extraction backend (pdftotext vs pypdf) — decide on a real
  CH/EU SDS corpus in Phase 1.
- Multilingual section-detection heuristics (SDS layouts vary by vendor)
  — pilot calibration.
- swiss-impex export format → `trade_stat` ingest path (Phase 0; probe
  target of v0.1.1).
- Chart rendering (matplotlib vs table-first) — Design.
- Report PDF route (pandoc availability on Slackware) — Design.

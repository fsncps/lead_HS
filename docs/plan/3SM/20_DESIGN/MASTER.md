---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-10
---

# Design MASTER — lead_HS

## Abstract

This is the dashboard of the Design stage: the detailed technical
HOW for the `leadhs` tool and its evidence database, distilled from
the Strategy (10_STRATEGY/) and the CEO review session of
2026-09-10 (mode EXPANSION). It records the consolidated design
decisions, the open items, and the readiness for implementation.
The active build unit is v0.1.1 (source probing, slim CLI); the full
normalized schema and the M1–M4 surfaces are designed ahead in the
topic documents below.

## State

- Unit **v0.1.1** — in DESIGN (design docs LIVE; strategy converged
  for the slim scope).
- Unit v0.1 (feasibility & study design) — foundational strategy
  pass, LIVE in STRATEGY.
- Full-pipeline design: **present but not frozen** — freeze awaits
  the v0.1.1 probe results and the legal-verification open items
  (10_STRATEGY/MASTER.md readiness split).

## Documents

- `MASTER/data_model.md` — the fully normalized schema: probe-era
  subset (implemented now) + full M1–M4 schema, views, migrations
- `MASTER/architecture.md` — modules, runtime, probe engine,
  report/export tooling, diagrams
- `MASTER/interfaces.md` — CLI contracts, provenance/adapter
  contracts, metric vocabulary, audit rules R1–R9, export contract
- `MASTER/testing.md` — test matrix, key tests, flakiness rules
- `units/v0.1.1.md` — the design delta for the active unit

(The canonical "design" subject is covered by architecture +
interfaces together — consolidation decision, no separate
design.md.)

## Scope boundaries

- **Built in v0.1.1:** migrations 0001–0002 + views; db/source/
  probe/doctor commands; three adapters; report md/csv/json.
- **Designed ahead, built M1–M4:** dictionary/catalog/frame/sampling/
  trade/sds/evidence tables (0003–0009); acquire/parse/analyze/
  report surfaces; db query; db export (frozen artifact + manifest);
  per-product dossier.
- **Out of scope:** servers/daemons (hard constraint), Postgres now
  (portability only), Parquet dependency (CSV default), second-study
  data (discriminator only), web interfaces (static artifacts at
  most, M4 decision).

## DECISIONS (consolidated; detail codes in the topic docs)

- **d1** SQLite + PostgreSQL-portable DDL (CEO review; strategy D1
  kept).
- **d2** `document` provenance backbone — url/source/retrieved_at/
  raw_hash live once (dm2, a-series).
- **d3** unified `run` table + typed detail tables (dm3).
- **d4** full schema designed now; probe-era subset implemented
  (milestone-gated migrations 0001–0009) (dm10, dm11).
- **d5** `study` discriminator now — second study reuses the DB with
  zero migration (dm9; CEO review).
- **d6** export path + read-only query surface designed now, built
  M4; per-product evidence dossier in the report (i6; CEO review).
- **d7** per-source probe runs; abort/resume; latest-per-metric view
  (a2, ud1).
- **d8** raw-store security: hash-only filenames + source-id
  allowlist (a5, P5).
- **d9** probe_metric vocabulary fixed in v0.1.1, extended only by
  migration (i4, ud7).
- **d10** single fetch seam with injectable clock; three-adapter
  contract; adapters never write the DB (a1, a3, a4, i3).
- **d11** lookups keyed by stable TEXT codes (dm1).
- **d12** classification history (product_classification, active
  flag) (dm6).
- **d13** verbatim vs interpretation split (sds_ingredient vs
  sds_finding) (dm7).
- **d14** substance generalization, is_lead_target (dm8).
- **d15** promotion pointer on population_anchor — findings stay
  immutable (dm5).
- **d16** append-only evidence vs updatable reference data (dm12).
- **d17** audit rules R1–R9 as the binding provenance contract (i5).
- **d18** exit-code convention 0/1/2/3 (i1).
- **d19** register of record = repo CSV; `source add` deferred (i2,
  ud8).
- **d20** backup-before-migration default on (a8, ud6).

## OPEN ITEMS

- **Frontmatter convention:** persistent cross-unit docs may carry
  `unit: global` per the 3SM canon; repo practice is the active unit.
  Currently uniform `unit: v0.1.1` — normalize (or not) by explicit
  user decision.
- swiss-impex export mechanics — answered by the unit's own probe.
- SPIN structure → import mapping; mdbtools on Slackware.
- Export dump format: CSV default, Parquet only on consumer demand.
- org dedup/merge workflow — M2 ingest design.
- acquire queue design — M2.
- PDF text backend, chart rendering, pandoc route — M2–M4
  (inherited from Strategy).
- name_base dedup rules, UFI validation — Phase-1 pilot (inherited).
- parameters_json schemas per future run kind — at their milestones.

## Readiness for IMPLEMENTATION

- **v0.1.1: ready.** Design converged (schema fixed to column level,
  contracts and test matrix written). Next step per 3SM: engineering
  review of this design (optional), then 30_IMPLEMENTATION/v0.1.1/
  PHASE##.md when explicitly instructed.
- **Full pipeline: not ready.** Freeze awaits probe results (source
  counts, swiss-impex format, SDS corpus quality) and the
  legal-verification items in 10_STRATEGY/MASTER.md.

## Handoff note

Writing these documents implies no lifecycle transition. Strategy
freeze for v0.1.1, root-MASTER stage updates, LOG entry, and
AGENTS/README pointers to 20_DESIGN all await explicit user
instruction (3SM process rules).

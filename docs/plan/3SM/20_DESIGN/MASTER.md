---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-12
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

- Unit **v0.1.1** — built: PHASE01–07 done and gate-verified
  2026-09-11 (101 passed); the PHASE08 census feasibility pass was
  executed 2026-09-11 and its close-out is transferred to v0.1.2
  (D26). Design docs LIVE.
- Unit **v0.1.2** (operator layer + census close-out: make, CLI
  operability, report routing, structured source reports) — design
  converged (units/v0.1.2.md, od1–od10; second-pass CEO review
  HOLD SCOPE; D25/D26 absorbed, D27 applied);
  **built 2026-09-11** — implementation trail rescoped to od8–od10 at
  activation, PHASE01–06 done (155 offline tests), PHASE07 census
  execution awaits explicit go (`GO=1 make census`). **The D28
  rework (register slim 0004, walk metrics, product-first report)
  and PHASE07 are absorbed into unit v0.1.3's PHASE01–02** (B8
  precedent; transfer marked in both trails).
- Unit **v0.1.3** (data-landscape map, strategy refocus D29) —
  design converged 2026-09-12 (units/v0.1.3.md, pe1–pe6; CEO review
  HOLD SCOPE 2026-09-12): enumeration register model (per-site
  rows, load validation, notes convention), priors metric
  (migration 0005 products_registered), landscape-map report
  extensions (aggregate floors, bridge), budget marker; absorbs the
  v0.1.2 close-out. Implementation plan written (ENG review
  2026-09-12, SMALL CHANGE); build awaits explicit go; the census
  phases additionally need the real-network go-ahead.
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
- `units/v0.1.2.md` — design delta for the census close-out unit
- `units/v0.1.3.md` — design delta for the data-landscape map unit

(The canonical "design" subject is covered by architecture +
interfaces together — consolidation decision, no separate
design.md.)

## Scope boundaries

- **Built in v0.1.1:** migrations 0001–0002 + views; db/source/
  probe/doctor commands; three adapters; report md/csv/json.
- **Built in v0.1.2:** repo Makefile (operator entrypoint, GO=1
  guard), CLI exit-code enforcement + DB-init preflight, `source
  list`/doctor/`--data-dir` fixes, report routing, housekeeping;
  migration 0003 records_hs3208/3209/3213 + census_status (od10);
  structured census report content (od8/D25); census completion
  mechanics (od9); the census close-out execution. Schema carries
  product data only (d27).
- **Deferred from v0.1.2:** M1–M4 stages (stub targets only), wheel
  release mechanics (first external use). DE/FR README sync resolved:
  same change set (B6).
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
  raw_hash live once (dm2, dm15).
- **d3** unified `run` table + typed detail tables (dm3).
- **d4** full schema designed now; probe-era subset implemented
  (milestone-gated migrations 0001–0009) (dm10, dm11).
- **d5** `study` discriminator now — second study reuses the DB with
  zero migration (dm9; CEO review).
- **d6** export path + read-only query surface designed now, built
  M4; per-product evidence dossier in the report (i6; CEO review).
- **d7** per-source probe runs; abort/resume; latest-per-metric view
  (a2, ud1, a11, dm14, i9).
- **d8** raw-store security: hash-only filenames + source-id
  allowlist (a5, P5).
- **d9** probe_metric vocabulary fixed in v0.1.1, extended only by
  migration (i4, ud7, t6).
- **d10** single fetch seam with injectable clock; three-adapter
  contract; adapters never write the DB (a1, a3, a4, i3, i8).
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
- **d20** backup-before-migration default on (a8, ud6, t6).
- **d21** operator layer in make — thin wrapper, `guard-%` GO=1
  prerequisite (census guard precedes setup), params as make vars
  until M1, clobber GO=1 + typed confirm (a12; strategy D21,
  U1–U4).
- **d22** CLI exit-code enforcement in `main()` (standalone_mode
  False; usage errors → 1; Abort/interrupt → 130) + DB-init
  preflight guided error (i10, i11; od2, od3).
- **d23** report routing implemented — `data/report/` intermediates,
  `report-publish` copies to `docs/report/` (a13, od5; strategy D22).
- **d24** `--data-dir` for installed use, exclusive with `--db`
  (od4; strategy D24).
- **d25** report content layer — one DB-only assembly, three
  renderers (md narrative + matrix, csv summary matrix, json full
  structure); run status incl. blocked/failed visible; dry-runs
  excluded; legend "—" (not queried) vs 0 (queried, empty); framing
  states source-feasibility ≠ product/lead metrics (i12, od8;
  strategy D25).
- **d26** census close-out design — migration 0003
  (records_hs3208/3209/3213 + census_status; v_anchor_candidates
  redefined; design-ahead migrations renumbered 0004–0010), census
  mechanics (parameterized CS-2 query with recorded params, PE
  category depth ≤ 3, manual records via census_status) (od9/od10,
  dm16; strategy D26/U8–U10).
- **d27** product data only in tool, database and reports — schema
  drops the legal-category dimension, substance legal-status/
  Swiss-relevance fields, the legal-coded sds_signal lookup and the
  legal_text document kind; LG register rows stay inactive and carry
  no findings — they appear in the summary matrix only as inactive
  register rows, never as legal content (strategy D27; supersedes
  the D14-derived fields).
- **d28** enumeration register model — enumerated sites as per-site
  `source` rows (PE-10+), PE-1..4 retired inactive, structured
  notes convention documented once (stringly until M1 accepted),
  `source load` validation (id pattern, http(s) url, duplicate
  active-host check), budget-exhausted flagged via the numeric
  metric `walk_budget_exhausted` (i13/a16; v0.1.3 HOLD-SCOPE
  review; ENG review 2A).
- **d29** landscape map = od8 content-layer extensions — aggregate
  floors (sums over latest done runs of **active** sources only —
  ENG review 1A; blocked/failed/not-yet-walked excluded and
  counted; budget-limited flagged; channel-facet subtotals +
  overlap caveat; explicit no-floors line), trade-context lines,
  priors lines, frame-decision bridge md-only with deferred line
  (i14/a17; strategy D29).
- **d30** coarse priors as one generic metric `products_registered`
  via migration 0005; v_anchor_candidates redefined; anchor
  promotion manual (D20) (a18/i4; v0.1.3).
- **d31** v0.1.3 PHASE01–02 absorb the outstanding v0.1.2 D28
  rework + census execution (B8 precedent; transfer marked in both
  implementation trails).

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
  contracts and test matrix written); engineering review done
  2026-09-11 (critical + ENG review; findings applied per
  FIXPLAN_2026-09-11.md). Next step per 3SM:
  30_IMPLEMENTATION/v0.1.1/PHASE##.md when explicitly instructed.
- **v0.1.2: ready — implementation plans written.** Design converged
  (operator layer + census close-out; CEO review 2026-09-11 HOLD
  SCOPE + ENG review 2026-09-11 SMALL CHANGE; OD-A resolved as
  migration 0003). Phase plans:
  30_IMPLEMENTATION/v0.1.2/PHASE01–07. Build awaits explicit go;
  PHASE07 (census execution) additionally requires the real-network
  go-ahead. **D28 rework + PHASE07 transferred to v0.1.3
  PHASE01–02 (d31).**
- **v0.1.3: ready — implementation plans written.** Design converged
  (pe1–pe6; CEO review 2026-09-12 HOLD SCOPE; ENG review 2026-09-12
  SMALL CHANGE). Phase plans: 30_IMPLEMENTATION/v0.1.3/PHASE01–07.
  Build awaits explicit go; PHASE02/PHASE06 additionally require
  the real-network go-ahead. Convergence of the underlying strategy
  (DRAFT) stays gated on the executed census — the phase plans
  deliver exactly those floors.
- **Full pipeline: not ready.** Freeze awaits probe results (source
  counts, swiss-impex format, SDS corpus quality) and the
  legal-verification items in 10_STRATEGY/MASTER.md.

## Handoff note

Writing these documents implies no lifecycle transition. Strategy
freeze for v0.1.1, root-MASTER stage updates, LOG entry, and
AGENTS/README pointers to 20_DESIGN all await explicit user
instruction (3SM process rules).

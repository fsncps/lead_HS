---
unit: global
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-19
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

All units designed under this stage — v0.1.1 … v0.2.4 (+ the
v0.2.4-basta-addendum) — are COMPLETE: built, executed, merged to
`main` (state table: `../MASTER.md`). The per-unit design deltas
(`units/v0.1.1.md` … `units/v0.2.4-basta-addendum.md`, decision codes
od/cap/nu/fu/tr/s-series) live in the legacy v1 tree
`docs/plan/3SM/20_DESIGN/units/` (read-only); the distilled history is
`../CONCEPT/DEV_HISTORY.md`. The persistent T-docs below carry the
current engineering truth of the built tool; the design review
history (CEO HOLD SCOPE, ENG reviews, FIXPLAN_2026-09-11 — DONE) is
part of the legacy record.

## Documents

Persistent T-docs (this directory, engineering-authoritative):

- `data_model.md` — the fully normalized schema: probe-era subset
  (built) + full M1–M4 schema, views, migration plan
- `architecture.md` — modules, runtime, probe engine, report/export
  tooling, diagrams
- `interfaces.md` — CLI contracts, provenance/adapter contracts,
  metric vocabulary, audit rules R1–R9, export contract
- `testing.md` — test matrix, key tests, flakiness rules

Legacy (read-only): per-unit design deltas in
`docs/plan/3SM/20_DESIGN/units/`; the closed work order
`docs/plan/3SM/20_DESIGN/FIXPLAN_2026-09-11.md` (marked DONE).
Concept summaries: `../CONCEPT/`; public study detail: `docs/study/`.

(The canonical "design" subject is covered by architecture +
interfaces together — consolidation decision, no separate design.md.)

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
- **d32** recon machinery — probe_mode recon; PE adapter branch;
  bounded sitemap-index expansion ≤ 5 children (user decision 1A);
  counts only, no URL harvesting; ElementTree; product_pattern
  notes token (nu1/i15/a19; v0.2.0 HOLD-SCOPE review).
- **d33** CS-2 full-year import aggregation as four per-HS numeric
  metric codes; export context + partner tops in notes; raw
  archived (nu2/a20).
- **d34** AS register model — URL-pinned candidate rows, active=0
  manual-web default; producers_registered vs products_registered
  split keeps N1 industry counts out of the N2 sum (nu3).
- **d35** numbers-report layout — N1 headline (md method sheet +
  DB-cited anchors), N2/N3 access tiers with explicit zero-states,
  matrix column gains, bridge; i14 walk-floor sections deferred
  with spec on file (nu4/nu5/i16/a21).
- **d36** migration set — 0005 absorbed with the corrected view
  (no population_anchor reference; promoted-exclusion lands 0008);
  v0.2.0 delta takes 0006; design-ahead renumber 0007–0013; CS-1
  retire-inactive (dm12 — differs from the D27-driven LG/LI prune);
  CSV slim ordered after the migration (nu6).
- **d37** absorption/supersession — v0.1.3 pe1/pe2/pe6 groundwork
  into v0.2.0 PHASE01/PHASE03; walk execution and i14 render
  superseded/deferred; transfer markers in the v0.1.3 trail (nu7).
- **d38** C1/C2 lessons carried — active-only sums, numeric
  metrics over note substrings (nu8).
- **d39** ENG review (2026-09-12, BIG CHANGE) — e1–e8 folded:
  chain tolerance for expected exit 2 (a22); one-dimension
  JSON-stat decode (e2/2A); per-call fetch size cap (e3/3A); gzip
  + namespace handling (e4/e5); robots-unknown proceeds (e6);
  nested-index / year-step-back / dry-run mechanics (e7); record
  mode parameter (e8); plain census_status matrix column (nu9).
- **d40** capability profile (v0.2.1, cap1–cap7) — six new
  probe_metrics + probe_mode `capability`; register-capability branch
  (CSV/API automated, D3; XLSX/auth-gated + PE universe manual);
  real-product-source predicate + preliminary N2 numerator as
  report-time derivations; branch under AS; migration 0007 +
  renumber 0008–0014; no new CLI commands (i17/i18, a23/a24).
- **d41** the three-question funnel (v0.2.2, fu1–fu10) — three
  measurement layers (evidence facts / staging observations /
  derived analyses), reconciliation by construction (run-close
  derivation from staging rows); staging DB `data/testdata.sqlite`
  fed only from archived documents, idempotent per (source_id,
  run_key), rebuildable from the archive; four-wave run under a
  60-min default budget with a test-backed disposition invariant;
  migration 0008 (export anchors + sds_doc_urls) + renumber
  0009–0015; identity normalization shared module; jsonstat module
  lift (TODOS item); report extensions i19/i20 (a25–a28).

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

## Readiness for ENGINEERING

Historical: every unit v0.1.1 … v0.2.4 passed its planning gates and
was built and merged (per-unit detail: legacy readiness prose and
implementation trails in `docs/plan/3SM/`; distilled:
`../CONCEPT/DEV_HISTORY.md`). Current readiness is per-unit and set
by the next unit's own design pass — nothing is pending here.

## Handoff note

Writing these documents implies no lifecycle transition (3SM process
rules). The v1→v2 migration itself was user-ordered (2026-09-18) and
moved no live lifecycle state; current readiness is per-unit, set by
each unit's own design pass.

Terminology note (2026-09-19, v2.1 stage rename): the stage formerly
named STRATEGY is now CONCEPT, and IMPLEMENTATION is ENGINEERING;
"Strategy …" citations in older prose (e.g. "Strategy D27") point to
today's CONCEPT decision register, and `10_STRATEGY/` paths denote the
read-only legacy v1 tree.

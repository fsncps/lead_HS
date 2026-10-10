---
unit: global
stage: GLOBAL
lifecycle: LIVE
updated: 2026-10-09
---
# lead_HS — 3SM Plan MASTER

Global state: active unit, per-unit stage, roadmap, skill-record trail.
Stage detail lives in the stage M-docs (`plan/CONCEPT/MASTER.md`,
`plan/DESIGN/MASTER.md`); the distilled development history of all
pre-migration units is `plan/CONCEPT/DEV_HISTORY.md`.

## STATE

- **Active unit: none** — v0.3.4 shipped 2026-10-10 (early close; r02/r03 →
  follow-up units v0.3.5/v0.3.6, NEXT-UP in the PIPELINE).
  Predecessor v0.3.0 (instruction-driven raw source layer)
  is the first v2-tree unit: completed and archived 2026-10-09
  (branch waiver — ran on main; ship = archive + pipeline flip + tag,
  no merge). All earlier units are legacy-v1 (see UNITS).
- Current tool state: `leadhs` at 0.3.0 (pyproject), 461 offline tests
  green, `db audit` clean, migrations 0001–0012 applied; raw whole-loads
  live: AS-2 ECAT 89,396 + AS-33 BASTA 198,742.
- Design pass: `3sm-design-unit` started 2026-10-10 — see the unit dir.

## UNITS

All historical (v1-era) units; all merged to `main`, records in the
legacy tree, distilled in DEV_HISTORY:

| unit | theme | stage | lifecycle | where |
|---|---|---|---|---|
| v0.1 | feasibility & study design (foundational strategy pass) | COMPLETE | ARCHIVED | legacy `10_STRATEGY/` + DEV_HISTORY |
| v0.1.1 | source probing — slim CLI | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.1.2 | operator layer + census close-out | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.1.3 | data-landscape map (walk execution superseded, D31) | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.2.0 | market scale & data availability (numbers unit) | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.2.1 | source-level capability sounding-out | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.2.2 | the three-question funnel | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.2.3 | pool estimate v2 (meta-benchmarking) | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.2.4 | management CSV sample (+ D37–D40 addenda) | COMPLETE | ARCHIVED | legacy + DEV_HISTORY |
| v0.3.0 | instruction-driven raw source layer + first bulk loads | COMPLETE | ARCHIVED | `DESIGN/_archive/v0.3.0` · `ENGINEERING/_archive/v0.3.0` |
| v0.3.4 | canonical identity layer | ENG | SHIPPED 2026-10-10 (early close, r01; archived) | merge 2c73aea, tag `v0.3.4` |

## ROADMAP

Per CONCEPT MASTER D42/D43 (adopted 2026-10-03) and the 2026-10-09
identity-layer directive:

- **v0.3.4 (INIT-READY)** — deterministic normalization + matching;
  Stage 0 identity layer user-directed (manufacturer/product canonical
  tables, MA10–MA16); MA1–MA9 + MA8 pin at Design.
- **v0.3.8** — generic bulk-import source expansion (retail batch,
  html_pages walker; D45 access modes).
- **v0.4** — vanilla-Windows installer + deferred preliminaries (D42).
- **INPUT-source-expansion-MSE.md**: consultant handover — input, not
  adopted policy; decision points deferred.
- Standing open threads: BASTA paint-subset filter (de5 gate),
  ECAT 17,838-vs-38,233 reconciliation, legal-text verification items
  (ChemRRV/VIPaV consolidated texts), lead-driers empirical question.

## DECISIONS

- **M1 (2026-09-18, user-ordered):** migrate the v1 planning tree to
  the v2 `.3SM/` structure. M-docs and T-docs copied (adapted); unit
  records NOT copied wholesale — distilled into
  `plan/CONCEPT/DEV_HISTORY.md`; the legacy tree stays in place as a
  read-only historical reference (PROCESS.md § Project exceptions).
- **M2 (2026-09-18):** pre-migration units are recorded COMPLETE —
  they were built, executed, and merged to `main` under v1 practice;
  no re-run or re-gate is implied by the migration.
- **M3 (2026-09-18):** the v1 LOG is not carried over; this LOG starts
  at the migration entry. History: legacy `docs/plan/3SM/LOG.md` and
  git.

## OPEN ITEMS

- Next unit id + theme (v0.3 double-booked) — user decision at the
  next concept turn.
- Adoption verdicts for MATCHING / RAW_SOURCING / INPUT-MSE — user
  decisions at the next concept turn.
- `docs/plan/3SM/` disposition (keep as reference vs archive later) —
  user decision at housekeeping; until then it stays untouched.
- AGENTS.md full thin-pointer conversion (content migration into
  PROJECT.md/PROCESS.md) — proposed, awaiting user approval; the
  startup pointer is already repointed.

## SKILL RECORDS

### 3sm-setup fresh-scaffold + v1 migration — 2026-09-18
scope: full `.3SM/` scaffold (law, facts, skeletons) + M/T-doc
migration from `docs/plan/3SM/`
checklist:
- [x] detection — v1 layout found (`docs/plan/3SM/`), no `.3SM/`; migration user-ordered (explicit instruction) — OK
- [x] law files (PROCESS + 3 stage files) from packaged templates + project exceptions — OK
- [x] PROJECT.md facts filled from repo evidence (Makefile, pyproject, TODOS.md, LOG, AGENTS) — OK (TODOs: lint/format/typecheck commands, tag scheme)
- [x] plan/MASTER.md + plan/LOG.md skeletons — OK
- [x] M/T-doc migration STRATEGY (MASTER + 8 T-docs + inputs/) — OK
- [x] M/T-doc migration DESIGN (MASTER + 4 T-docs) — OK
- [x] AGENTS.md startup pointer repoint (minimal edit; full conversion proposed, not executed) — OK
- [x] scaffold audit — OK
findings: CRITICAL GAP 0 · WARNING 0 · unresolved 0
carries: housekeeping may skip structure re-verification until templates
change; v1-era docs need no lifecycle normalization (exempt legacy tree)
valid-until: template upgrade or canonical pair change
commit: ad077af (law) · 4f9c698 (facts) · ef317c0 (skeletons) · 2084177 (AGENTS pointer)

### 3sm-housekeeping REPAIR — 2026-09-18
scope: full `.3SM/` tree (22 files) post-migration hygiene pass
checklist:
- [x] discover — 22 files inventoried, classified (law/facts/M/T-docs/S-rec pending) — OK
- [x] structure compare — canonical layout, lazy dirs correct, stage nesting correct — OK
- [x] doc integrity — FIXED 2 frontmatter defects (DESIGN/MASTER `unit: v0.2.2`→global; INPUT digest `unit: next-unit input`/`lifecycle: INPUT`→global/LIVE) + 3 stale refs + plan/MASTER stage GLOBAL + LOG frontmatter — OK
- [x] skill-record audit — setup record had no SHA → FIXED (4 SHAs appended); no other records — OK
- [x] bubble & consolidate — STRATEGY top level 9 entries (≤10 incl. pending DEV_HISTORY at 10); DESIGN 5 — OK
- [x] instruction conflicts — none critical; AGENTS.md full conversion stays OPEN ITEM — OK
- [x] facts/law separation — holds (PROJECT facts; PROCESS law only) — OK
- [x] lifecycle coherence — units COMPLETE/ARCHIVED; M-docs LIVE; no anomalies — OK
findings: CRITICAL GAP 0 · WARNING 0 (all fixed inline; verbatim handover file intentionally frontmatter-free — preserved-verbatim input)
carries: nothing (housekeeping is cheap); DEV_HISTORY compilation follows this pass
valid-until: next canonical/template change or tree change
commit: 7f8ebb8

### 3sm-housekeeping REPAIR — 2026-09-19
scope: full `.3SM/` tree (24 files) + AGENTS.md — v2-legacy stage names →
v2.1 canonical (STRATEGY→CONCEPT, IMPLEMENTATION→ENGINEERING), user-ordered
checklist:
- [x] startup — canonical pair (v2.1) + PROCESS* + PROJECT + plan/MASTER read; mode REPAIR (user-ordered update) — OK
- [x] discover — 24 files inventoried + AGENTS.md pointer; rename-pattern classification (live vs legacy-tree vs historical) — OK
- [x] structure compare — FOUND plan/STRATEGY/ + plan/IMPLEMENTATION/ + PROCESS_STRATEGY/IMPLEMENTATION files — FIXED (rename executed)
- [x] doc integrity — stage tokens ×10 → CONCEPT; live-path refs fixed; `updated` bumped on edited docs — OK
- [x] skill-record audit — 2 prior records, SHAs present, untouched (append-only); their valid-until ("canonical pair change") fired → this pass is the response — OK
- [x] bubble & consolidate — CONCEPT 9 top entries (≤10), DESIGN 5 — OK
- [x] instruction conflicts — law files renamed (roles, states, process map, docs map, records map, exceptions); AGENTS.md pointer repointed — OK
- [x] facts/law separation — holds (PROJECT.md facts only; D41 prose updated) — OK
- [x] lifecycle coherence — no active unit, all units COMPLETE/ARCHIVED — OK
- [x] migration steps — plan/CONCEPT (cdd00c9) · PROCESS_CONCEPT (d29446e) · PROCESS_ENGINEERING (24e97e4) · PROCESS.md (ace3647) · plan/MASTER+LOG (2881122) · DESIGN+PROJECT (69acb6d) · AGENTS.md (b2a7cb7) · PROCESS_DESIGN fix (e05f2dc) — OK
- [x] sessions — 1 S-rec (2026-09-18 migration), current, kept verbatim (historical record) — OK
- [x] integrity re-check — automated verify: zero stale live-path/skill tokens; expected remainder = LOG entry, DESIGN terminology note, S-rec, legacy-tree paths — OK
findings: CRITICAL GAP 0 · WARNING 0 · unresolved 0
carries: rename-residue verification may be skipped by the next skill passes
until the canonical pair changes again; legacy-tree paths (`10_STRATEGY/`,
`30_IMPLEMENTATION/`) intentionally unchanged
valid-until: next canonical/template change
commit: cdd00c9 · d29446e · 24e97e4 · ace3647 · 2881122 · 69acb6d · b2a7cb7 ·
e05f2dc (this record lands in the commit that follows)

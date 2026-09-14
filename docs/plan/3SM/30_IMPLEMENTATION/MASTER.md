---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# Implementation MASTER — lead_HS

## Abstract

Dashboard of the IMPLEMENTATION stage: finalized, executable phase
plans (the `PHASE##.md` files) per unit. Per the 3SM canon this stage
contains ONLY phase tracking and finalized executable plans — no
brainstorming, research, reviews or provisional designs; those live
in 10_STRATEGY/ and 20_DESIGN/. The active unit is **v0.1.3** (data-landscape map, D29; converged
2026-09-12 on D30 — the three-number deliverable N1/N2/N3; strategy
FROZEN). Unit **v0.1.1** (source probing, slim CLI) is built and
gate-verified (PHASE01–07 + PHASE08 feasibility pass, 2026-09-11;
ENG-reviewed SMALL CHANGE). Unit **v0.1.2** (operator layer + census
close-out) is built (PHASE01–06, 2026-09-11; ENG-reviewed SMALL
CHANGE, findings recorded as B1–B8); its D28 rework + PHASE07 census
execution transferred to v0.1.3 PHASE01–02 (2026-09-12, d31). For
v0.1.3 the baseline census ran 2026-09-12 (3 done / 1 blocked / 3
failed; audit clean). PHASE01 (the D28 rework) is built 2026-09-12
(165 offline tests, audit clean); PHASE02+ await explicit go.

Unit **v0.2.0** (market scale & data availability — the numbers
unit, D31 turn) is built 2026-09-12 (all seven phases done; 205
offline tests; probe report published; N1 anchors / N2 = 204,693 /
N3 = 9 sites documented). The active planning unit is now
**v0.2.1** (source-level capability sounding-out, D33) — design
converged 2026-09-14 (cap1–cap7 + CEO/ENG reviews HOLD SCOPE;
A1–A2, C1–C3 folded; cap5 → new ASAdapter); implementation plan
drafted 2026-09-14 (`v0.2.1/PHASE01–06`); **built 2026-09-14** (all
six phases done; 231 offline tests; capability report published;
preliminary N2 numerator = 17.838, EU Ecolabel ECAT — a floor).

The active planning unit is now **v0.2.2** (product-identity and
granularity sounding-out, D34 — the three-question funnel) — design
converged 2026-09-14 (fu1–fu10 + CEO review HOLD SCOPE c1–c6; ENG
review BIG CHANGE e1–e8 folded); implementation plans drafted
2026-09-14 (`v0.2.2/PHASE01–07`); build awaits explicit go, PHASE05
additionally the real-network go-ahead.

## Units

| Unit | Stage | Status |
|---|---|---|
| v0.1.1 (source probing — slim CLI) | IMPLEMENTATION | PHASE01–07 done (gate-verified 2026-09-11); PHASE08 feasibility pass executed; census close-out transferred to v0.1.2 (D26) |
| v0.1.2 (operator layer + census close-out) | IMPLEMENTATION | PHASE01–06 done 2026-09-11 (155 offline tests); **D28 rework + PHASE07 transferred to v0.1.3 PHASE01–02 (2026-09-12, d31)** |
| v0.1.3 (data-landscape map, D29) | IMPLEMENTATION | strategy converged on D30 2026-09-12 (re-reviewed CEO HOLD + ENG SMALL CHANGE; E1/E2 folded); PHASE01 (D28 rework) built 2026-09-12 (165 offline tests, audit clean); baseline census 2026-09-12 (3/1/3, audit clean); PHASE02+ await explicit go, PHASE02/06 additionally the real-network go-ahead |
| v0.2.0 (market scale & data availability, D31) | IMPLEMENTATION | built 2026-09-12 (PHASE01–07 done; 205 offline tests; probe report published; N1/N2/N3 documented) |
| v0.2.1 (source-level capability sounding-out, D33) | IMPLEMENTATION | built 2026-09-14 (PHASE01–06 done; 231 offline tests; capability report published; preliminary N2 numerator 17.838 — EU Ecolabel ECAT, a floor) |
| v0.2.2 (product-identity & granularity sounding-out, D34) | IMPLEMENTATION | design converged 2026-09-14 (fu1–fu10; CEO HOLD SCOPE c1–c6; ENG BIG CHANGE e1–e8); plans drafted (PHASE01–07); build awaits explicit go, PHASE05 additionally GO=1 |

## Phase tracking (v0.1.1 — summary)

| Phase | Focus | Status | Exit gate (summary) |
|---|---|---|---|
| PHASE01 | scaffold | done | installable package; `leadhs --help`; metrics/ids/errors/log helper |
| PHASE02 | persistence | done | migrations clean + idempotent; backup restores; audit exit 0 |
| PHASE03 | network & env | done | fetch/doctor semantics on fake clock; dry-run zero network |
| PHASE04 | register | done | 14-row CSV loads; malformed CSV → exit 1 |
| PHASE05 | probe | done | outcome-based run semantics green on fixture site |
| PHASE06 | reporting | done | md/csv/json render from views (golden) |
| PHASE07 | tests | done | full matrix green offline; smoke + hostile + chaos (101 passed) |
| PHASE08 | census run (execution) | planned | real census delivered; every OPEN row probed or manual |

Per-phase status, dependencies and detail: `v0.1.1/MASTER.md` and
`v0.1.1/PHASE01..08.md`.

## Phase tracking (v0.1.2 — summary)

| Phase | Focus | Status | Exit gate (summary) |
|---|---|---|---|
| PHASE01 | CLI operability (main() exit mapping, no_args_is_help, list fix, doctor --net, --data-dir, version 0.1.2) | planned | exit-code contract holds; existing suite green |
| PHASE02 | DB-init preflight (7 commands) | planned | guided error, exit 1, never `bug:`; `db init` exempt |
| PHASE03 | operator layer (Makefile, .gitignore, report routing) | planned | `make help` 0; GO guard before side effects; stubs exit 1 |
| PHASE04 | tests (operability, preflight, make wiring, net-marked doctor test) | planned | offline suite green incl. new files; `pytest -m net` collects ≥ 1 |
| PHASE05 | census capability (migration 0003 per-HS metrics, structured report per D25) | planned | sync test 0001+0003 green; structured sections + matrix on fixtures |
| PHASE06 | docs & distribution (README EN/DE/FR, wheel verification) | planned | wheel installs into throwaway uv env; READMEs current |
| PHASE07 | census close-out (execution) | planned | every row probed/manual; report published; audit exit 0 |

Per-phase status, dependencies and detail: `v0.1.2/MASTER.md` and
`v0.1.2/PHASE01..05.md`.

## Phase tracking (v0.1.3 — summary)

| Phase | Focus | Status | Exit gate (summary) |
|---|---|---|---|
| PHASE01 | D28 rework (migration 0004, walk metrics + walk_budget_exhausted, product-first report) | done 2026-09-12 | suite green incl. sync 0001+0003+0004; two numbers + matrix on fixtures |
| PHASE02 | Census execution (absorbs v0.1.2 PHASE07; GO=1, phased) | planned | baseline floors exist; report published; audit exit 0 |
| PHASE03 | Enumeration register (load validation, per-site rows, version 0.1.3) | planned | validation named-row exits; enumerated register loads; probe-dry covers all |
| PHASE04 | Priors metric (migration 0005 products_registered) | planned | 0005 applies; recordable; v_anchor_candidates extended |
| PHASE05 | Landscape-map render (aggregate floors active-only, trade/priors lines, bridge) | planned | i14 sections incl. C1 case on fixtures; goldens reviewed |
| PHASE06 | Walks + priors execution (GO=1, phased) | planned | floors over enumerated register; priors recorded/blocked; audit exit 0 |
| PHASE07 | Docs & close-out (README, management summary three numbers (N1–N3), register statuses) | planned | docs carry the real three numbers (N1–N3); translations drift-marked or updated |

Per-phase status, dependencies and detail: `v0.1.3/MASTER.md` and
`v0.1.3/PHASE01..07.md`.

## Phase tracking (v0.2.1 — summary)

| Phase | Focus | Status | Exit gate (summary) |
|---|---|---|---|
| 01 | Migration 0007 (capability mode + 6 capability metrics + metrics.py seeds + sync) | planned | 0007 applies; sync 0001+0003+0004+0005+0006+0007 green |
| 02 | ASAdapter + register-capability branch (CSV/API fetch → shape inspect → row count), `make capability`/MODE, version 0.2.1, t11 | planned | t11 fixture paths green; audit exit 0; wheel 0.2.1 builds |
| 03 | Register expansion (AS/CS/ST/PE rows, EU-only, active flags) + CSV batch | planned | register loads clean; probe-dry plans every active row |
| 04 | Capability execution (automated exports + manual records; GO=1) | planned | every capability source recorded or documented-blocked; audit exit 0 |
| 05 | Capability report (matrix + N2 numerator) render + publish + audit | planned | report per i18 on real data; published; audit exit 0 |
| 06 | Docs & close-out (management summary DE/FR, register tables, drift markers, LOG, goldens) | planned | docs current; goldens regenerated + reviewed; audit exit 0 |

Per-phase status, dependencies and detail: `v0.2.1/MASTER.md` and
`v0.2.1/PHASE01..06.md`.

## Phase tracking (v0.2.2 — summary)

| Phase | Focus | Status | Exit gate (summary) |
|---|---|---|---|
| 01 | Migration 0008 (export columns + sds_doc_urls) + jsonstat module lift + TODOS retirement | planned | 0008 applies; sync 0001–0008 green; CS fixtures on the module |
| 02 | Staging DB + normalize + xlsx modules; engine ingest path (staging-first, run-close derivation) | planned | staging idempotent/rebuildable; ingest paths green per t12 |
| 03 | Register expansion to census shape (~150–250 rows, export anchors, PE enumeration) + version 0.2.2 | planned | register loads clean; probe-dry plans every active row |
| 04 | Wave harness (`--wave`/`--budget`/`--staging-db`, `make landscape`) + W1/W2 adapter extensions + t12 | planned | wave tests green (budget/resume/invariant); GO=1 guard |
| 05 | Landscape execution (GO=1, wave by wave; W4 manual records) | planned | every register row dispositioned; staging populated; audit exit 0 |
| 06 | Report extension (funnel, CN8, identity, depth, pool, census) + publish + audit | planned | report per i19/i20 on real data; published; audit exit 0 |
| 07 | Docs & close-out (README EN/DE/FR, management summary DE/FR, LOG, goldens, wheel) | planned | docs carry the real landscape numbers; wheel 0.2.2 |

Per-phase status, dependencies and detail: `v0.2.2/MASTER.md` and
`v0.2.2/PHASE01..07.md`.

## Governing references

- Strategy: `../10_STRATEGY/v0.1.1.md` (unit scope),
  `../10_STRATEGY/DATA_SOURCE.md` (register, discipline),
  `../10_STRATEGY/MASTER.md` (D19/D20 rollout, anchor promotion);
  unit v0.1.2: `../10_STRATEGY/v0.1.2.md` (D21/D22, U1–U7);
  unit v0.1.3: `../10_STRATEGY/v0.1.3.md` (D29 refocus, W1–W8);
  unit v0.2.0: `../10_STRATEGY/v0.2.md` (D31 numbers-first);
  unit v0.2.1: `../10_STRATEGY/v0.2.1.md` (D33 source-level expansion,
  U1–U6); unit v0.2.2: `../10_STRATEGY/v0.2.2.md` (D34 funnel, U1–U8).
- Design: `../20_DESIGN/MASTER.md` (consolidated decisions d1–d31)
  and topic docs `MASTER/{data_model,architecture,interfaces,testing}.md`
  (review semantics applied 2026-09-11 per
  `../20_DESIGN/FIXPLAN_2026-09-11.md` — DONE); unit deltas
  `../20_DESIGN/units/v0.1.1.md`, `../20_DESIGN/units/v0.1.2.md`,
  `../20_DESIGN/units/v0.1.3.md`.

## Retention (hot-history policy)

Active units plus the latest two completed units stay in place; older
completed units move to `_archive/30_IMPLEMENTATION/` (3SM canon).

## Handoff note

Writing these plans implies no lifecycle transition, freeze, or stage
advancement. Build executes PHASE files only on explicit instruction.
LOG entry, root-MASTER stage pointer, README/AGENTS pointers,
commit/push — all await explicit user instruction (3SM process).

---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
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

## Units

| Unit | Stage | Status |
|---|---|---|
| v0.1.1 (source probing — slim CLI) | IMPLEMENTATION | PHASE01–07 done (gate-verified 2026-09-11); PHASE08 feasibility pass executed; census close-out transferred to v0.1.2 (D26) |
| v0.1.2 (operator layer + census close-out) | IMPLEMENTATION | PHASE01–06 done 2026-09-11 (155 offline tests); **D28 rework + PHASE07 transferred to v0.1.3 PHASE01–02 (2026-09-12, d31)** |
| v0.1.3 (data-landscape map, D29) | IMPLEMENTATION | strategy converged on D30 2026-09-12 (re-reviewed CEO HOLD + ENG SMALL CHANGE; E1/E2 folded); PHASE01 (D28 rework) built 2026-09-12 (165 offline tests, audit clean); baseline census 2026-09-12 (3/1/3, audit clean); PHASE02+ await explicit go, PHASE02/06 additionally the real-network go-ahead |

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

## Governing references

- Strategy: `../10_STRATEGY/v0.1.1.md` (unit scope),
  `../10_STRATEGY/DATA_SOURCE.md` (register, discipline),
  `../10_STRATEGY/MASTER.md` (D19/D20 rollout, anchor promotion);
  unit v0.1.2: `../10_STRATEGY/v0.1.2.md` (D21/D22, U1–U7);
  unit v0.1.3: `../10_STRATEGY/v0.1.3.md` (D29 refocus, W1–W8).
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

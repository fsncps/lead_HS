---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# Implementation MASTER — lead_HS

## Abstract

Dashboard of the IMPLEMENTATION stage: finalized, executable phase
plans (the `PHASE##.md` files) per unit. Per the 3SM canon this stage
contains ONLY phase tracking and finalized executable plans — no
brainstorming, research, reviews or provisional designs; those live
in 10_STRATEGY/ and 20_DESIGN/. The active unit is **v0.1.1** (source
probing, slim CLI). Its engineering plan was ENG-reviewed on
2026-09-11 (SMALL CHANGE mode; 3 findings, all resolved — recorded in
the unit MASTER).

## Units

| Unit | Stage | Status |
|---|---|---|
| v0.1.1 (source probing — slim CLI) | IMPLEMENTATION | active — PHASE01–07 done (build gate-verified 2026-09-11); PHASE08 (census run) planned |

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

## Governing references

- Strategy: `../10_STRATEGY/v0.1.1.md` (unit scope),
  `../10_STRATEGY/DATA_SOURCE.md` (register, discipline),
  `../10_STRATEGY/MASTER.md` (D19/D20 rollout, anchor promotion).
- Design: `../20_DESIGN/MASTER.md` (consolidated decisions d1–d20)
  and topic docs `MASTER/{data_model,architecture,interfaces,testing}.md`
  (review semantics applied 2026-09-11 per
  `../20_DESIGN/FIXPLAN_2026-09-11.md` — DONE); unit delta
  `../20_DESIGN/units/v0.1.1.md`.

## Retention (hot-history policy)

Active units plus the latest two completed units stay in place; older
completed units move to `_archive/30_IMPLEMENTATION/` (3SM canon).

## Handoff note

Writing these plans implies no lifecycle transition, freeze, or stage
advancement. Build executes PHASE files only on explicit instruction.
LOG entry, root-MASTER stage pointer, README/AGENTS pointers,
commit/push — all await explicit user instruction (3SM process).

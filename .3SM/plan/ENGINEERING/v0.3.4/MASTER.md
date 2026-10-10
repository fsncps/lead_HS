# v0.3.4 — engineering unit MASTER

---
unit: v0.3.4
stage: ENG
lifecycle: LIVE
updated: 2026-10-10
branch: v0.3.4
---

Run details + phase status per run. `3sm-eng-run` owns this file's
currency; `/init-unit` registers the unit here (one row below); build
appends execution state at the moment of truth.

## STATE
current run: r02 (HS completion)    branch: v0.3.4    base: main@f0ac0e6 (reopened post-ship)

## RUNS

| run | status | SHA | tests |
|---|---|---|---|
| r01 | DELIVERED 2026-10-10 (executed; public report docs/report/report-0.3.4-r01.md) | 4a661e6 + 6b429f0 | 461 passed; real-data gates green; rebuild + chaos → FINAL |

## DECISIONS

Unit design decisions live in `../../DESIGN/v0.3.4/MASTER.md` §
DECISIONS (single source; il1–il17). Run-level pins live in
`r01/PHASE01.md` § REVIEW PINS.

## CLOSURE

Closed early by user decision 2026-10-10 after r01; ship gate evidence
and the ship skill record live in `../../DESIGN/v0.3.4/RUNS.md` §
CLOSURE. Archive: `../_archive/v0.3.4/`.

## OPEN ITEMS

- legal_forms.csv + ident_prefixes.csv (il11 seed CSVs): move from
  hardcoded `_LEGAL_FORM_TOKENS` / add prefix table at r03 — rides the
  normalization scrutiny of calibration; behavior-identical config
  churn, no r01 delta. (Deferred at r01 Step 0, user-visible here.)

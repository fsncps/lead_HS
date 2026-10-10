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
current run: r01    branch: v0.3.4    base: f039b26

## RUNS

| run | status | SHA | tests |
|---|---|---|---|
| r01 | PLANNED (plan: r01/PHASE01.md, review-complete) | — | run gate = user test plan |

## DECISIONS

Unit design decisions live in `../../DESIGN/v0.3.4/MASTER.md` §
DECISIONS (single source; il1–il17). Run-level pins live in
`r01/PHASE01.md` § REVIEW PINS.

## OPEN ITEMS

- legal_forms.csv + ident_prefixes.csv (il11 seed CSVs): move from
  hardcoded `_LEGAL_FORM_TOKENS` / add prefix table at r03 — rides the
  normalization scrutiny of calibration; behavior-identical config
  churn, no r01 delta. (Deferred at r01 Step 0, user-visible here.)

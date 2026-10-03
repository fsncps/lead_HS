---
unit: v0.3.0
stage: ENGINEERING
lifecycle: LIVE
updated: 2026-10-03
branch: main (unit-branch init waived by user, 2026-10-03)
---

# v0.3.0 — implementation

## STATE
current run: (none — all runs CLOSED 2026-10-03)    branch: main (init waived)    base: 47b7ac8

## RUNS PROGRESS

| run | status | SHA | tests |
|---|---|---|---|
| r01 | CLOSED 2026-10-03 | 1a043db | user test plan pass (scratch DB: 0012 applies, refusals name paths, canonical hash stable) — functional-only per testing economy |
| r02 | CLOSED 2026-10-03 | d098c3e (live fixes ca06e42) | user test plan pass — AS-2/AS-3 scanned live; drafts reviewed + committed; drift honest |
| r03 | CLOSED 2026-10-03 (FINAL folded) | 92408d1 + ca06e42 + 350d275 | 460 passed, 2 deselected; smoke 6 passed; db-audit exit 0 (incl. --unreferenced); live AS-2 89,396 rows, 200/200 verbatim spot-checks |

Build-session note: the user overrode per-run sequencing ("implement
0.3.0" in one pass, then live) — r02/r03 were built without separate
eng-run planning passes; deviations and live-found defects are
recorded in RUNS.md (Build record pointer), `../DESIGN/v0.3.0/
interfaces.md` § Build record, and the unit report
`docs/report/report-0.3.0.md`.

## FINAL CHECKLIST

(mirrors the FINAL gate — walked 2026-10-03 in the build session)

- [x] all runs CLOSED (r01–r03; none deferred)
- [x] every FINAL test-plan input reconciled — 48 new offline tests in
      `tests/test_raw_layer.py` cover: refusal matrix (22 named rows),
      canonical-hash stability, migration chain 0001→0012 +
      idempotence, upsert triple incl. `_truncated` hash flip,
      deterministic truncation (priority order + budget boundary),
      checkpoint resume across a page boundary, register sync
      warnings, guard derivation flood boundary, drift line, UTF-8/BOM
      decode, pinned-table lookup, 404 scan refusal, degraded row-hash
      mode, JSON scalar projection, pacer spacing. Provisional inputs
      from RUNS.md all promoted — none dropped.
- [x] full offline suite green (`make test` — 460 passed)
- [x] `make db-audit` exit 0 after the live loads (incl. --unreferenced)
- [x] `make smoke` green (6 passed)
- [ ] whole-unit diff reviewed (ship-unit pass — pending /finalize-and-merge)
- [x] docs synced: DESIGN interfaces.md § Build record, data_model.md
      § Raw source tables + migration table, PROJECT commands/suites,
      READMEs ×3 (+ report-0.3.0.md); management summary substance
      check — no change needed (study numbers unchanged; AS-3 route
      death recorded in DATA_SOURCE-level docs, not the summary)
- [ ] ship-profile checklists (PROJECT § Ship profile: local channel — ship verifies)

---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE07 — Census close-out (execution, not code)

Status: transferred 2026-09-12 → executed as v0.1.3 PHASE02 (after
its PHASE01 lands the D28 rework; B8 precedent, d31) · Depends on:
PHASE01–06 done + explicit go-ahead · Governs: the unit's
operational deliverable (U8/D26 — M0 close-out).

## Objective

Complete the source census for every register row through the
operator layer — closing the gaps the 2026-09-11 feasibility pass
recorded — and deliver the structured source report (D25). **No new
code: surprises are findings and notes, not patches** (a design
conflict goes back to DESIGN per 3SM regression rules).

## Preconditions

- PHASE01–06 exit gates green (suite green offline; migration 0003
  applied; structured report rendering).
- `GO=1 make doctor` / `leadhs doctor --net` — contact set, data
  dir, reachability; mdbtools presence for ST-2 (or documented
  degraded path).
- **Explicit user go-ahead** — this phase hits the real network
  (polite, multi-minute: ≥ 2 s spacing per domain; re-runs are
  incremental new runs).

## Governing references

- `../../10_STRATEGY/v0.1.2.md` — U8/U9 (census close-out, report),
  §Operator workflow.
- `../../10_STRATEGY/MASTER.md` — D25/D26, ROADMAP Phase 0 (the
  feasibility-pass gap list).
- `../../10_STRATEGY/DATA_SOURCE.md` — access & scraping discipline
  (binding); census metadata set; register of record.
- `../v0.1.1/PHASE08.md` — the feasibility pass this completes
  (empirical record; gaps: CS-1 fetch, CS-2 query parameters, ST-2
  fetch, PE catalog level, manual sources).

## Steps

1. **Dry pass first:** `make probe-dry` — plan every request, zero
   network; sanity-check source selection.
2. **Real pass:** `GO=1 make census` (setup → probe → report →
   audit). Blocked/failed sources re-run individually after
   inspection if transient (new runs, append-only; v_probe_latest
   takes the latest done run).
3. **Feasibility-gap completion:** CS-1 swiss-impex fetch + export
   mechanics (format/granularity/coverage/export_rows as findings,
   export archived); CS-2 query-parameter answer (parameterized
   per-HS queries → records_hs3208/3209/3213; empty result = honest
   0); ST-2 SPIN fetch + extraction path (mdbtools present or
   documented-blocked); PE catalog-level counts (catalog_count/
   category_count/category_list where exposed); per-HS records where
   a source exposes them.
4. **Manual-web work (ST-1 PCN):** locate formulation-level
   aggregates; record via `make record SOURCE=ST-1 METRIC=…` (or
   `leadhs probe record`), attaching pages as documents where useful.
   Deferrals and manual export mechanics (ST-1 aggregates, PE-3
   portal enumeration, CS-1 UI export if hands are needed) are
   recorded as `census_status` records (method=manual) so the report
   shows them.
5. **Deliver the report:** `make report` → `data/report/`; review
   the structured sections + summary matrix; publish with
   `make report-publish WHICH=data/report/probe-report.md` (copies;
   committing is explicit). Review `v_anchor_candidates` — anchor
   promotion stays a manual M1 method decision.
6. **Update the register of record:** DATA_SOURCE.md §Source register
   Status column from the findings (open → verified /
   partially_verified / blocked+manual); new PE seed sites enter as
   CSV rows + `source load` (i2).
7. `make db-audit` — must exit 0 on the real corpus.

## Deliverables

- Census findings for every register row (probed or explicitly
  manual), including the feasibility-gap answers.
- Structured source report (md/csv/json) published to
  `docs/report/`.
- Updated DATA_SOURCE.md register + `sources.csv`.
- Blocked sources documented with manual-fallback notes.

## Exit gate (unit acceptance)

- Every register row probed or explicitly manual (PCN); the
  feasibility-pass gaps closed or documented-blocked.
- Structured report published; `db audit` exit 0.
- The census deliverable of D26 is met — M0 closed.

## Post-run (flagged, not executed here)

Unit completion marking, planning archival, LOG entry, commit/push —
all await explicit user instruction per 3SM process.

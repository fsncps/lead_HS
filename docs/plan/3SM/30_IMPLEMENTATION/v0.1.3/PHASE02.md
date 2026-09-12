---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE02 — Census execution (absorbs v0.1.2 PHASE07; execution, not code)

Status: planned · Depends on: PHASE01 done + explicit real-network
go (`GO=1`) · Governs: the baseline floors every later phase reads.

## Objective

Execute the product-first census over the slimmed register (nine
product rows, seven active) through the operator layer — closing
the feasibility-pass gaps — and deliver the baseline report. **No
new code: surprises are findings and notes, not patches** (design
conflicts go back to DESIGN, 3SM regression rules). Transfer
marker: this phase is v0.1.2 PHASE07 (B8 precedent; both trails
marked).

## Preconditions

- PHASE01 exit gate green; migrations at 0004.
- `leadhs doctor --net` clean (contact set via `LEADHS_CONTACT`;
  mdbtools present for ST-2 or degraded path documented).
- **Explicit user go-ahead** — real network, polite multi-minute
  runs (≥ 2 s spacing per domain; re-runs are incremental new runs).

## Steps

1. `make probe-dry` — plan every request, zero network; sanity-check
   source selection (seven active rows of the nine-row register).
2. **Phased verify (D28):** `GO=1 make probe-single SOURCE=CS-2` and
   `SOURCE=PE-4` first — per-HS parameterized queries (records_hs*)
   and the PE walk behave; inspect findings + archived responses.
3. **Full pass:** `GO=1 make census` (setup → probe → report →
   audit). Transient blocked/failed sources re-run individually
   after inspection (new runs; v_probe_latest takes the latest done).
4. **Feasibility-gap completion:** CS-1 export mechanics (re-probe;
   else manual); ST-2 fetch + extraction path (mdbtools or
   documented-blocked); PE walk metrics on PE-1/PE-2; per-HS records
   where exposed.
5. **Manual records:** census_status via `make record` — CS-1 UI
   mechanics if hands are needed, ST-2 deferral, PE-3 portal
   placeholder deferral; ST-1 PCN aggregates if located (full prior
   push is PHASE06).
6. **Deliver:** review the two numbers + matrix; `make report`;
   `make report-publish WHICH=data/report/probe-report.md`; update
   DATA_SOURCE.md register Status column from findings; `make
   db-audit` exit 0.

## Deliverables

- Census findings for every register row (probed or explicitly
  manual); baseline floors (x, y per source); published report;
  updated register statuses.

## Exit gate

- Every row probed or explicitly manual; gaps closed or
  documented-blocked; the two numbers exist and are provenance-
  cited; report published; `db audit` exit 0. These floors are what
  the D29 strategy convergence (user action) and PHASE03+ read.

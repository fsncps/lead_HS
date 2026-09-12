---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE06 — Walks + priors execution (execution, not code)

Status: planned · Depends on: PHASE03–05 done + explicit
real-network go (`GO=1`) · Governs: the unit's measured deliverable
(W1–W5, W7).

## Objective

Run the polite walks over the enumerated register and record the
coarse priors — producing the map's real numbers.

## Preconditions

- PHASE03–05 exit gates green; enumerated register loaded.
- `leadhs doctor --net` clean; **explicit user go-ahead** for the
  real network (phased, polite: ≥ 2 s spacing per domain; the full
  sweep is a multi-minute-to-hour operation — re-runs are
  incremental).

## Steps

1. `make probe-dry` — plan the full enumerated sweep; sanity-check
   the active row list.
2. **Phased verify:** `GO=1 make probe-single SOURCE=PE-10` and one
   DIY site — walk metrics, budget metric, robots handling behave
   on two real sites before the sweep.
3. **Full pass:** `GO=1 make probe` (all active rows, one run per
   site). Transient blocked/failed re-run individually after
   inspection. Expect documented blocks (paywalled/login-walled
   B2B portals) — findings + notes, never workarounds (D4).
4. **Manual priors (best-effort, W5):**
   - SPIN (ST-2): download + mdbtools extraction → coarse
     preparation counts per country as `products_registered`
     records (lead-CAS incidence stays the D8 pilot prior in
     documentation — not extracted here); persistent failure →
     documented-blocked census_status.
   - PCN (ST-1): manual-web formulation-count aggregates →
     `products_registered` + URL provenance; not locatable →
     documented-blocked.
   - PRODCOM (ST-3): producer counts (NACE 20.30) via the verified
     API or manual record.
   - E2: the three anchors share the `products_registered` code, so
     each record carries a distinct unit_code (`preparations`,
     `formulations`, `producers`) — the priors lines stay
     unambiguous in the matrix.
5. **Deliver the map:** `make report` — review the three numbers
   (N1–N3), subtotals, bridge evidence; `make report-publish WHICH=
   data/report/probe-report.md`; `make db-audit` exit 0.

## Deliverables

- Walk findings per enumerated site (products_listed,
  doc_links_seen, budget flags); priors recorded or
  documented-blocked; published landscape report; audit clean.

## Exit gate

- Floors exist over the enumerated register with per-source
  provenance; priors recorded or documented-blocked; the bridge has
  its evidence lines; report published; `db audit` exit 0.

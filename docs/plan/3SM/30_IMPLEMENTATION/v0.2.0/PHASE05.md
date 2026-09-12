---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE05 — Recon execution (GO=1; robots-compliant, counts only)

## Objective

Access coverage N2/N3 for every enumerated PE channel: the recon
sweep (robots/terms, sitemap product counts) plus manual-web SDS
library visibility and constraint notes.

## Preconditions

- PHASE03–04 done.
- Explicit real-network go (`GO=1`) — robots-compliant structured
  fetches and manual-web only; no scraping (D31; 1A bound: ≤ 5
  sitemap-index children).

## Governing references

- `../../20_DESIGN/units/v0.2.0.md` (nu1)
- `../../20_DESIGN/MASTER/interfaces.md` (i15; run semantics —
  per-source runs, exit 2 = some blocked/failed, findings persist)
- `../../10_STRATEGY/DATA_SOURCE.md` (discipline: robots, UA +
  contact, ≤ 1 req / 2 s)

## Steps

1. **Verify on 1–2 sites:** `GO=1 make probe-single SOURCE=PE-1x
   MODE=recon` — inspect findings, notes (pattern used, cap flags),
   archived sitemap documents (D28 phased-verification precedent).
2. **Full sweep:** `GO=1 make recon` — per-source runs; a failing
   site never aborts the loop; exit 2 expected when sites block or
   fail (findings persist; document which and why).
3. **Manual-web per site:** `make record SOURCE=… MODE=recon
   METRIC=sds_library_visible VALUE=0|1` (landing-page SDS/TDS
   library visibility; MODE=recon labels the run honestly — e8) +
   constraint notes (JS-gated, 403 wall, login wall); census_status
   records for blocked sites with the manual fallback path
   documented (D4).
4. `make db-audit` exit 0.

## Deliverables

Recon coverage over the enumerated register (done/blocked/failed per
site, findings persisted); sds_library_visible per site; constraint
notes; audit clean.

## Exit gate

Every active PE row has a latest done/blocked/failed recon run or an
explicit manual record; cap-flagged floors are annotated; audit
exit 0.

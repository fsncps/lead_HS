---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE04 — Priors metric (migration 0005)

Status: planned · Depends on: PHASE03 · Governs: pe2, d30, i4
extension rule.

## Objective

Add the generic register-prior metric `products_registered`
(numeric, count) so SPIN/PCN/PRODCOM coarse counts land as
machine-comparable findings instead of census_status prose.

## Steps

1. **Migration 0005__priors_metric.sql** — INSERT probe_metric
   `products_registered` ("Products registered (prior)", numeric);
   redefine `v_anchor_candidates` to include it (header comment,
   dm11; priors are precisely anchor candidates — promotion stays
   manual, D20/W3). Backup default on.
2. **metrics.py** — constant + seed; sync test extends to
   0001+0003+0004+0005 == metrics.py.
3. **Matrix** — the summary matrix carries a
   `products_registered` column (ST sources; "—" when absent).
4. **Tests** — test_migrations extends (0005 seeds + view);
   test_engine/test_views: `make record SOURCE=ST-1
   METRIC=products_registered VALUE=…` works on an inactive source
   (method=manual) and surfaces in v_anchor_candidates.

## Deliverables

- Migration 0005; metrics.py; matrix column; tests.

## Exit gate

- 0005 applies on a 0004 DB (backup round-trip); sync test green;
  a recorded products_registered finding appears in the matrix and
  v_anchor_candidates; suite green.

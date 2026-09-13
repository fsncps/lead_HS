---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE01 — Migration 0007: capability mode + capability metrics

## Objective

Land the unit's schema delta, offline-verified: probe_mode
`capability` and the six capability probe_metrics, so the capability
profile vocabulary exists before the adapter/report work.

## Preconditions

- PHASE01 of v0.2.0 done (0006 applied; the design-ahead block is
  already renumbered to 0008–0014 per the v0.2.1 design).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.1.md` (cap1, cap7, capability profile)
- `../../20_DESIGN/MASTER/data_model.md` (migration plan, 0007 row,
  renumbering note 0008–0014)
- `../../20_DESIGN/MASTER/interfaces.md` (i4 vocabulary + extension
  rule; the six metric rows)
- `../../20_DESIGN/MASTER/testing.md` (t11 migration cases; t6 sync)

## Steps

1. **Migration `0007__capability.sql`:** INSERT probe_mode
   `capability`; INSERT six probe_metric rows with the fixed
   value_types — `products_identifiable` (numeric),
   `cap_manufacturer` (numeric), `cap_product_ident` (numeric),
   `cap_cn8_linkage` (text), `cap_depth_tier` (numeric),
   `cn8_reachable` (numeric). No view change.
2. **metrics.py:** add the six constants and six
   `PROBE_METRIC_SEEDS` entries (numeric/text per above) under a
   `# 0007__capability.sql (v0.2.1)` comment, matching the i4
   catalog codes exactly.
3. **tests (t11 migration block, test_migrations.py):** 0007 applies
   — probe_mode `capability` seeded; the six capability metrics
   present with the right value_types; the sync test now requires
   0001+0003+0004+0005+0006+0007 == metrics.py.

## Deliverables

Migration 0007; metrics.py + six capability seeds; extended sync
test.

## Exit gate

`0007` applies cleanly; `test_migrations.py` green incl. the
extended sync assertion (0001+0003+0004+0005+0006+0007 ==
metrics.py); `db audit` exit 0 on the real DB.

---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE01 — Migration 0009: the csv-sample lookup seeds (offline)

## Objective

Land migration `0009__csv_sample.sql` — lookup-seed INSERTs only, no
new tables — plus the matching `metrics.py` constants/seeds and the
two sync-test updates (t6 vocabulary count 41; fresh-apply versions
{1..9}).

## Preconditions

- v0.2.3 built (staging DB + ingest path, adapter package, 341
  offline tests green).
- Design decisions in force: S1–S4 (strategy), de1–de4 +
  Review-outcomes amendments (design).

## Governing references

- `../../20_DESIGN/units/v0.2.4.md` (module placement, review
  outcomes — migration correction)
- `../v0.2.4/MASTER.md` (scope, acceptance criteria)
- `src/leadhs/migrations/0007__capability.sql` (the seed pattern),
  `src/leadhs/metrics.py` (the runtime source of truth, i4)

## Steps

1. **Migration file:** `src/leadhs/migrations/0009__csv_sample.sql`
   — header comment (unit, D36, i4: codes never renamed, value_type
   fixed at insert) + two INSERTs:
   - `probe_mode`: `('csv_sample', 'Management CSV sample',
     'per-registry reproducible product-row samples for management
     review (D36): what fields, which identifiers, cross-ID
     candidates; honest no-product-rows records for the registers
     that publish none')`.
   - `probe_metric`: `('csv_sample_rows', 'CSV sample rows drawn',
     'rows actually written to the per-registry sample CSV
     (clamped to the in-scope pool)', 'numeric')` and
     `('csv_sample_unavailable', 'CSV sample unavailable',
     'why a registry delivers no product-row sample — verified
     reason with citation, or a should-deliver failure record',
     'text')`.
2. **metrics.py:** add `METRIC_CSV_SAMPLE_ROWS` /
   `METRIC_CSV_SAMPLE_UNAVAILABLE` constants + the two seeds under a
   `# 0009__csv_sample.sql (v0.2.4, D36)` comment (house format).
3. **Sync updates:** `tests/test_metrics.py`
   `test_metric_vocabulary_size` → 41 (add the +2 comment);
   `tests/test_migrations.py` `test_fresh_apply_all_migrations` →
   `{1, ..., 9}`; add a `test_0009_csv_sample_seeds_present` in the
   0003/0004 style (codes + value types).

## Deliverables

`0009__csv_sample.sql`; `metrics.py` seeds; the three test updates.

## Exit gate

Migration applies fresh and idempotently; t6 sync green (41);
full offline suite still green.

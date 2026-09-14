---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE01 — Migration 0008 + jsonstat module lift

## Objective

Land the unit's evidence-DB schema delta offline-verified (source
export anchors + the `sds_doc_urls` metric), and land the TODOS.md
jsonstat item: the inline one-dimension decoder lifts into a reusable
`leadhs/jsonstat.py` with multi-dimension coordinate mapping — the
prerequisite for the per-CN8 × per-declarant Comext batches (W1).

## Preconditions

- v0.2.1 PHASE01–06 done (0007 applied; design-ahead block renumbered
  0008–0014).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (fu3, fu10, schema deltas)
- `../../20_DESIGN/MASTER/data_model.md` (migration plan, 0008 row,
  third renumber 0009–0015)
- `../../20_DESIGN/MASTER/interfaces.md` (i4 vocabulary + extension
  rule; i19/i20)
- `../../20_DESIGN/MASTER/architecture.md` (a25)
- TODOS.md (the jsonstat entry — retired by this phase)

## Steps

1. **Migration `0008__landscape.sql`:** ALTER `source` ADD
   `export_url` TEXT, `export_format` TEXT (nullable); INSERT
   probe_metric `sds_doc_urls` (numeric). No view change; no new
   probe_mode.
2. **metrics.py:** add the `SDS_DOC_URLS` constant +
   `PROBE_METRIC_SEEDS` entry under a `# 0008__landscape.sql
   (v0.2.2)` comment; the sync test now requires
   0001+0003+0004+0005+0006+0007+0008 == metrics.py (test_migrations.py).
3. **jsonstat lift:** create `leadhs/jsonstat.py` — lift
   `_jsonstat_one_dim` / `_jsonstat_category_labels` / `_jsonstat_sum`
   from adapters.py; add the multi-dimension coordinate mapping (flat
   value index → N-dim coordinates over `id`×`size`, row-major) needed
   for cn8 × flow × declarant × period payloads; CSAdapter switches to
   the module; the v0.2.0 Comext fixtures port to the module's tests.
4. **TODOS.md:** retire the jsonstat entry with a one-line "landed in
   v0.2.2 PHASE01" marker.
5. **data_model.md** group numbering was aligned in the planning pass;
   verify no stale references remain.

## Deliverables

Migration 0008; metrics.py + `sds_doc_urls` seed + extended sync
test; `leadhs/jsonstat.py` (multi-dimension decoder) with ported
fixtures; TODOS.md entry retired.

## Exit gate

`0008` applies cleanly; sync test green through 0008; CS-2 fixture
tests green against the lifted module (adapters.py imports it; the
inline copies are gone); `db audit` exit 0 on the real DB.

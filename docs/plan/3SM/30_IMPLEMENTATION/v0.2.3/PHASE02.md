---
unit: v0.2.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE02 — Adapters split + Danish staging (the one dev item)

## Objective

Honor the TODOS.md adapters-split trigger (this unit adds the sixth
adapter class) by splitting `probe/adapters.py` into per-class
modules, then land the sixth adapter: the Danish AT CC0 open dataset
staged as real rows (tr3 — user-approved scope addition), with
verify-shape-first, the aggregates-only extraction fallback, the
counted-0 guard (c5) and the ECAT∩DK overlap probe feeding B5.

## Preconditions

- PHASE01 done (benchmarks module green; DK query functions exist
  and consume the new rows).
- TODOS.md split item trigger conditions met (adapters.py at 1,325
  lines; next-unit adapter class confirmed by this unit).

## Governing references

- `../../20_DESIGN/units/v0.2.3.md` (tr3, c5, c6, X3; t13 adapter
  tests)
- `../../20_DESIGN/MASTER/interfaces.md` (i19 staging contract, i15
  recon contract)
- TODOS.md (the split entry — its own instructions; retired by this
  phase)
- `../../10_STRATEGY/DATA_SOURCE.md` (D3 official-export discipline)

## Steps

1. **Verify shape first (P2 gate):** fetch the Danish CKAN resource
   metadata (official export, D3) and confirm the current resource
   URL, format and column layout before writing any adapter code; a
   shape mismatch at build time is a format-finding, not a code
   patch.
2. **Split (mechanical, TODOS's own instructions):** move each
   adapter class into `probe/adapters/<name>.py` with the shared
   helpers (`_sniff`, CSV-shape, `_depth_tier`) in a common module;
   `probe/adapters/__init__.py` re-exports the registration/dispatch
   surface so all imports stay stable; tests move with their
   subjects. DKAdapter then lands in its own module from day one.
3. **DKAdapter:** CSV/XLSX read via the existing helpers;
   **chunked/streaming read if the resource exceeds ~50 MB** (ENG
   performance note — the helper already line-iterates); parse →
   normalize → stage through the existing ingest path (staging-first
   ordered writes), full provenance (source URL + retrieval date per
   record), idempotent replace, per-source transaction.
4. **Register row:** new register row for the Danish AT dataset
   (active=1, export_url = CKAN resource), planned by probe-dry.
5. **Fallback + guards:** aggregates-only resource ⇒ the adapter
   stage is skipped and the dataset's aggregates are extracted as
   manual records instead (tr3 fallback — recorded, not silent); zero
   paint rows ⇒ counted-0 semantics and B2 marked indeterminate
   (c5 — never scale from zero); sparse function-category column ⇒
   B2 range widens with a missingness note (c6).
6. **Overlap probe:** ECAT∩DK over staged DK paints — the empirical
   label-penetration input for B5, labeled **calibration-only**
   (the overlap pilot pattern from v0.2.2).
7. **TODOS.md:** retire the split entry with a "landed in v0.2.3
   PHASE02" marker.
8. **Tests:** fixture built in-test from a real-shaped sample;
   aggregates-only fallback path; counted-0 path; idempotent re-run;
   interrupt mid-ingest → no orphan rows (existing per-source
   transaction, re-tested); dispatch/registration surface unchanged
   (all existing adapter tests green against the split layout).

## Deliverables

Per-class adapter modules + stable dispatch surface; DKAdapter +
Danish staging rows with provenance; register row; overlap-probe
computation; TODOS.md split entry retired.

## Exit gate

Register loads with the DK row and probe-dry plans it; adapter tests
green (fixture, fallback, counted-0, idempotency, interrupt);
adapters package imports stable; full offline suite green.

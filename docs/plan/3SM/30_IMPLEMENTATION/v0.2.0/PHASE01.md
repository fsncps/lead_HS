---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE01 — Absorbed v0.1.3 groundwork: source-load validation + migration 0005

## Objective

Land the un-built v0.1.3 groundwork this unit builds on (B8/D26/d31
absorption precedent): the `source load` row validation (pe6/i13)
and the priors metric migration 0005 (pe2) — with the nu6 view
correction (no population_anchor reference at 0005).

## Preconditions

- v0.1.3 PHASE01 state: migrations 0001–0004 applied; 165 offline
  tests green; register CSV at nine product rows.
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.1.3.md` (pe1/pe2/pe6);
  `../../20_DESIGN/units/v0.2.0.md` (nu6/nu7)
- `../../20_DESIGN/MASTER/interfaces.md` (i13, P1–P7, exit codes)
- `../../20_DESIGN/MASTER/data_model.md` (migration plan; 0005
  correction)
- `../../20_DESIGN/MASTER/testing.md` (t9, t10)

## Steps

1. **Load validation** (`source.py`): per row — id matches
   `^[A-Z]{2}-[0-9]+$`; url non-empty http(s); duplicate host among
   active rows (netloc lowercased, `www.` stripped); inactive rows
   exempt. A failing row is named in the error; exit 1.
2. **Migration `0005__priors_metric.sql`** (absorbed content):
   INSERT probe_metric `products_registered` ("Products registered
   (prior)", numeric, count); redefine v_anchor_candidates (metric
   list gains `products_registered`; **no population_anchor
   reference** — the promoted-exclusion NOT EXISTS lands at 0008
   where the table ships; nu6 correction of the v0.1.3 note).
3. **Renumber design-ahead migrations** in the repo/docs:
   `0006__dictionary` → `0007__dictionary` … `0012__views` →
   `0013__views` (docs-only, pre-build; od10 precedent).
4. **metrics.py** += `products_registered`; extend the sync test:
   0001 + 0003 + 0004 + 0005 == metrics.py.
5. **Tests** (t10): test_source.py — bad id → exit 1 (row named);
   empty/non-http url → exit 1; duplicate active host → exit 1
   listing both ids; duplicate host with one row inactive → loads;
   the 14-row pre-slim register loads via `--file` (inactive
   exemption). test_migrations.py — 0005 seeds present with correct
   value_type; v_anchor_candidates lists products_registered; 0005
   contains no population_anchor reference (hostile case).

## Deliverables

Validated loader; migration 0005; renumbered design-ahead files;
extended sync/validation tests; green suite.

## Exit gate

Full offline suite green (165 + new); `db audit` exit 0 on the real
DB; the v0.1.3 trail carries the transfer marker (pe2/pe6 → v0.2.0
PHASE01). Version stays 0.1.3 until PHASE02.

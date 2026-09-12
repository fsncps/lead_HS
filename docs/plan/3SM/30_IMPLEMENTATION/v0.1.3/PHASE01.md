---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE01 — Land the v0.1.2 D28 rework (code)

Status: done 2026-09-12 · Depends on: — · Governs: the absorbed v0.1.2
rework (U11–U13; pe5/d31) — the base PHASE02–07 build on.

## Objective

Bring the built code up to the D28 product-first census design:
migration 0004 (register slim + walk metrics), the PE category walk
with page budget and the budget metric, and the product-first report
rework. No new CLI commands, no new pipeline stages.

## Preconditions

- Full offline suite green (155 tests); migrations at 0003.
- Design governing: `../../20_DESIGN/units/v0.1.2.md` (od8–od10 as
  amended by D28), `../../20_DESIGN/units/v0.1.3.md` (pe4/pe5),
  interfaces.md i12/i13 + metric vocabulary (0004 rows),
  data_model.md migration plan.

## Steps

1. **Migration 0004__product_census.sql** — single transaction:
   prune the LG-*/LI-* source rows and their runs/findings/documents
   (FK-safe order: probe_finding → probe_run → document → source);
   INSERT probe_metric rows `products_listed`, `doc_links_seen`,
   `walk_budget_exhausted` (all numeric, per interfaces.md); redefine
   `v_anchor_candidates` to include `products_listed` (header comment
   records the redefinition, dm11). Backup default on (a8).
2. **Register slim in `sources.csv` (D28, v0.1.2.md step 6 — must
   ride with the migration):** drop the LG-1..4 and LI-1 rows → the
   register of record keeps the nine product rows (CS-1, CS-2,
   PE-1..4, ST-1..3; seven active). Order matters: the loader is an
   upsert, so a pruned DB plus an unslimmed CSV would resurrect
   LG/LI on the next `sources-load` (every `make census` runs
   `setup`). The old 14-row register stays loadable via
   `source load --file` for the backward-compat test.
3. **metrics.py** — add the three constants + seeds; extend the sync
   test to 0001+0003+0004 == metrics.py.
4. **PE adapter — category walk (od9/D28 mechanics, unchanged) +
   budget metric (C2):** after the landing page, BFS category pages
   depth ≤ 3, page budget ≤ 12 pages incl. homepage, polite spacing
   unchanged; emit `products_listed` (distinct product detail links),
   `doc_links_seen` (SDS/TDS-type links: href/filename/text heuristics
   documented in the adapter), `walk_budget_exhausted` (0/1 — 1 when
   the budget stopped the walk); `catalog_count`/`category_count`
   semantics unchanged (path in finding notes — R4).
5. **report.py — product-first rework (U11):** the two numbers lead
   (Q1 products available — observed listings per source, a floor;
   Q2 reachable SDS-type documentation — walk doc links + sample
   metrics); one summary matrix over all registered sources (active
   flag included; trade rows labelled volume context); execution log
   (latest census run per source incl. blocked/failed + notes);
   compact per-source blocks (access metadata one line; the od8
   long-form sections are superseded); legend "—" vs 0. md/csv/json
   from the same DB-only assembly (csv = matrix; json = full).
6. **Tests** — extend test_adapters_pe (walk metrics, budget metric
   0/1, category failure → note + continue), test_migrations (0004
   prune + INSERTs + view), test_source (slimmed nine-row register
   loads; the pre-slim 14-row register still loads via `--file` —
   inactive dup-host exemption), test_report_content (product-first
   layout: two numbers, matrix, execution log, compact blocks),
   sync test; regenerate goldens with review.

## Deliverables

- Migration 0004 + slimmed `sources.csv` (nine product rows) +
  metrics.py + adapter walk + product-first report; tests green;
  goldens reviewed.

## Exit gate

- Full offline suite green incl. new tests (net/mdbtools
  deselected); sync test 0001+0003+0004 green; 0004 applies on a
  0003 DB (backup round-trip); after `sources-load` the register
  lists the nine product rows and LG/LI appear nowhere (`source
  list`, report matrix); the report on fixtures shows the two
  numbers, one matrix, execution log, compact blocks, legend;
  `db audit` exit 0.

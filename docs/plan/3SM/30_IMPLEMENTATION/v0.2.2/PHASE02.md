---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE02 — Staging DB + normalize + xlsx modules; engine ingest path

## Objective

Build the L2 layer offline: the staging DB (`data/testdata.sqlite`),
the identity normalization module, the stdlib XLSX reader, and the
engine ingest path — staged rows ride `ProbeResult`, the engine
writes staging first then evidence per source, and staged-source
metrics derive at run close from the staging rows (metrics ==
staging by construction).

## Preconditions

- PHASE01 done (0008 applied; jsonstat module live).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (fu1/fu2/fu4, core concept,
  schema deltas, identity & matching; CEO c1–c3, c5; ENG e1/e3/e4)
- `../../20_DESIGN/MASTER/interfaces.md` (i19 staging contract)
- `../../20_DESIGN/MASTER/architecture.md` (a25)
- `../../20_DESIGN/MASTER/testing.md` (t12 additions)

## Steps

1. **`leadhs/staging.py`:** schema init for `stg_source_document`,
   `stg_register_product`, `stg_trade_cn8`, `dict_cn8` (13 codes +
   3213 annex); idempotent replace per `(source_id, run_key)`;
   indexes on `(source_id, run_key)`; rebuild-from-archive entry
   (re-ingest archived documents); **loud failure** when a staging
   row would lack source_id/doc_hash/retrieval_date. Staging columns
   TEXT with explicit cast (leading zeros survive).
2. **`leadhs/normalize.py`:** `norm_manufacturer` (casefold,
   diacritic fold, legal-form suffix strip GmbH/AB/Oy/Ltd/S.A./A/S/…,
   punctuation collapse) and `norm_ident` (strip spaces/dashes) →
   `(ident, ident_type, ident_basis)`; exact-match only — no fuzzy
   matching (design c5/fu7). Shared by ingest and overlap SQL.
3. **`leadhs/xlsx.py`:** minimal XLSX reader on stdlib zipfile +
   ElementTree — workbook → sheets → rows, shared-strings and
   inline-string cells; size cap; corrupt/missing-sheet → typed
   errors. No openpyxl (D24).
4. **Shared parse helpers (adapters.py, module level):** one
   CSV-shape helper (encoding/BOM detection + expected-header
   validation → column-drift `format_finding`) and one `_sniff` gate
   (content-type + first-bytes check before parse — the AS-7
   HTML-as-CSV regression); `_depth_tier` moves here so adapter and
   report share one definition (refined fu8 wording).
5. **Engine ingest path (e1):** `ProbeResult` gains staged product
   rows; `run_one` writes staging first, then evidence, per source
   (per-source transaction boundary); after the writes, staged
   sources get run-close derivation — `products_identifiable` =
   staging count, plus the aggregate findings (distinct
   manufacturers/pairs, completeness, category distribution as
   findings notes); manual sources emit via `record_manual`
   unchanged. A failed write → run failed; re-run replaces
   idempotently.
6. **Tests (t12 staging/ingest block):** staging idempotent re-run
   (counts stable); rebuild-from-archive; missing doc hash → loud
   failure; hash-mismatch detected; leading-zero ident round-trip;
   normalize variant grid (legal forms, umlauts, punctuation);
   xlsx fixture built in-test via zipfile (happy/corrupt/size-cap/
   missing-sheet); ingest staging-before-evidence order; run-close
   derivation == staging count; counted-0 semantics; interrupt
   mid-ingest → no orphan staging rows (chaos).

## Deliverables

`leadhs/staging.py`, `leadhs/normalize.py`, `leadhs/xlsx.py`; shared
CSV/`_sniff` helpers in adapters.py; engine ingest path with run-close
derivation; t12 staging/ingest tests.

## Exit gate

New module tests green; full offline suite green; `db audit` exit 0;
staging DB created on first ingest path use (no migration, no
evidence-DB schema change).

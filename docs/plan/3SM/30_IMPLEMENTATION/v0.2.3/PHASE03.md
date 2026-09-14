---
unit: v0.2.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE03 — Extractions X4 (GO=1: real network, manual records)

## Objective

Retrieve and disposition the document extractions that feed B1–B6:
the BfR-Akademie Sweden 2022 PDF (national register counts), the
JRC145238 §3.4.3 market characterization, the SWD(2022) 435 Annex 16
Poison Centre Notification mixture counts, and the B6 external
literature sweep. Manual records only — one fetch per target, no
scraping (D31/D3), every number URL- and access-dated.

## Preconditions

- PHASE01 done (benchmark input slots defined).
- Explicit real-network go-ahead (`GO=1`) for the retrieval steps.

## Governing references

- `../../20_DESIGN/units/v0.2.3.md` (X4, B1–B6 input columns, c1)
- `../../10_STRATEGY/DATA_SOURCE.md` (source classes; D3)
- `../../10_STRATEGY/v0.2.3.md` (evidence-pass briefs — the retrieval
  targets are already identified and URL-dated there)
- `../../20_DESIGN/MASTER/interfaces.md` (i15 recon contract)

## Steps

1. **BfR-Akademie Sweden 2022 PDF:** extract the Swedish product
   register counts; resolve register-products vs PCN-dossiers
   ambiguity — **unresolvable ⇒ B2-SE stays indeterminate, visibly**
   (c1); record which.
2. **JRC145238 §3.4.3:** extract the market characterization and any
   market-share estimate usable as a B5 denominator input; note the
   vintage/reference year.
3. **SWD(2022) 435 Annex 16:** extract the PCN mixture-count
   methodology and the paint share; decide the B3 non-hazardous
   uplift as an explicit assumption band unless the annex yields a
   constant (tr10).
4. **B6 sweep (bounded):** attempt the external literature anchors
   (other-market product counts — US etc.; cross-industry SKU
   benchmarks; retail-depth scaling) with a bounded number of tries;
   a **documented gap is an acceptable outcome** — record it as such.
5. **SBS verification:** verify SBS NACE 20.30 producer count = 3,200
   directly in the Eurostat databrowser (B4 input).
6. **Records:** each extraction lands as a manual record with source
   URL + access date + the benchmark slot(s) it feeds + its vintage;
   ambiguities flagged, never silently resolved.

## Deliverables

Manual records for all five targets (or documented-gap
dispositions); benchmark input slots filled; open items updated.

## Exit gate

Every extraction target dispositioned (extracted / indeterminate /
documented gap) with provenance; no scraping performed (one fetch
per document); GO=1 was required and given for the network steps.

---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE07 — Addendum (D38): parse/filter correction, evidence archiving, data_sources.csv

## Objective

Correct the published AS-3 record (the "trial-grade 14 distinct"
verdict was a tool defect, not a data defect), close the
estimate-provenance gap, and introduce `data_sources.csv` — the
confirmed-bulk source list — per the 2026-09-14 review. All offline.

## Preconditions

- PHASE01–06 + the D37 addendum done; 385 offline tests green.

## Findings driving this phase

1. The Nordic Swan export parses correctly (semicolon; `_delimiter_of`
   picks `;`). Two tool defects produced the wrong numbers:
   `_in_scope_criterion096` matched whole-record substrings
   ("lack" ⊂ "Black", "paint" ⊂ "painting") and the dedupe identity
   triple looked for ECAT-style column names, collapsing the Nordic
   Swan pool to its 14 distinct Category values. True paint pool:
   2,424 rows / 2,322 distinct items (product+licensee+group) / 53
   licences / 20 licensees.
2. as_probe archived landing pages only for associations — the
   AS-4 ≈70,000 estimate had a URL + date but no stored page.
3. Sample size vs register size read ambiguously ("100 (exact)").

## Steps

1. **csv_sample fixes:** structured AS-3 scope filter (exact
   `product group` ∈ {EU44…, 096 Paints and varnishes});
   source-parameterized dedupe triple (`_KEY_FIELDS_NS` =
   product/licensee/product group); NS-specific manifest
   cross-identification line; licence column in idcols.
2. **Offline re-render:** `--from-store` flag + `fetcher_from_store`
   (StoreFetcher serves the newest archived export per source; zero
   GETs); real re-render executed — AS-2 identical deterministic
   redraw, AS-3 100 rows from the corrected pool, manifest
   regenerated (run 20260914-164304).
3. **as_probe:** archive the landing page (ext `html`) + `doc_hash`
   in the finding when an estimate is derived; reuse entries render
   "N rows (sample of P distinct register products)" (P from the
   newest `csv_sample_rows` finding); `rebuild_summary` +
   `--rebuild-summary` (offline re-render of the AS-probe summary
   from the latest run per source); real rebuild + AS-2/AS-3 reuse
   re-run executed (zero network).
4. **data_sources.csv:** `src/leadhs/dict/data_sources.csv` (review
   artifact, never loaded by `source load`); gate de5 (confirmed
   bulk + identity tuple + HS-derivable scope); initial rows DS-1
   (AS-2) and DS-2 (AS-3) only; well-formedness tests.
5. **Strategy input:** consultant handover (2026-09-14) preserved
   verbatim under `10_STRATEGY/_inputs/`; digest +
   decision-deferral in `INPUT-source-expansion-MSE.md`; ROADMAP
   pointer in `10_STRATEGY/MASTER.md`. Not adopted policy (de7).
6. **Docs close-out:** design addendum (D38), report corrections +
   D38 section, READMEs EN/DE/FR, management summary DE/FR,
   DATA_SOURCE note, dashboards, TODOS correction; full offline
   suite + audit.

## Exit criteria

- Published AS-3 record corrected end-to-end; estimates carry
  archived evidence; data_sources.csv lives behind the confirmed-bulk
  gate; suite green; audit clean.

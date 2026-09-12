---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE05 — Landscape-map render (aggregate floors, trade/priors lines, bridge)

Status: planned · Depends on: PHASE04 · Governs: pe3/pe4/pe7,
d29, i14.

## Objective

Extend the od8 content layer into the data-landscape map: the
aggregate floors section, trade-context and priors lines, and the
frame-decision bridge — same DB-only assembly, three renderers.

## Steps

1. **Aggregate floors section (md, directly after the summary
   matrix, per pe3):** Q1 line — Σ `products_listed`
   over **active** PE sources whose latest census run is done
   (decision 1A/C1; E1 implementation note: `v_probe_latest` alone
   carries no run status — the aggregate query joins `run` on
   `status_code='done'` and `source.active=1`; never sum the view
   unfiltered): "observed floor: N products across M of K
   walked sites (B blocked, F failed, U not yet walked)", citing the
   constituent run_keys; budget-limited sources flagged
   ("≥ observed, budget-limited") via `walk_budget_exhausted`;
   retired inactive rows (PE-1..4) never in the sum — one footnote.
   Channel-facet subtotals (parsed from the notes convention:
   MFR/CH-DIY/EU-DIY/MARINE/ART/B2B) + the W4 overlap caveat
   sentence. Q2 line — Σ `doc_links_seen` (same rule) + the
   `sds_sample_ok` context. Zero completed walks → "no measured
   floors yet — census not executed or no walk completed".
2. **Trade-context lines:** one compact line per CS source from
   records_hs3208/3209/3213 (D28 grain rule — volume context,
   never products; absent = "—").
3. **Priors lines:** one line per ST source from
   products_registered / census_status.
4. **Frame-decision bridge (md only):** qualitative, evidence-cited
   — channel coverage (channels with completed walks), floor
   magnitude vs the 10⁴–10⁵ hypothesis, SDS access rates
   (doc_links_seen / products_listed), blocked share; no invented
   numeric gate. No floors yet → explicit deferred line.
5. **csv/json:** matrix gains `products_listed`, `doc_links_seen`,
   `products_registered`, `walk_note` (budget/blocked marker
   derived from the metric + run status); json carries the full
   structure incl. aggregate dicts (excluded-source lists with
   reasons).
6. **Tests** — test_report_landscape.py: active-only sums; the C1
   hostile case (retired inactive PE-1..4 with done runs excluded,
   footnoted); blocked/failed/not-yet-walked counted; budget flag
   from the metric; channel subtotals; zero-walks deferred line;
   bridge deferred line; "—" vs 0; csv columns; json dicts.
   Regenerate goldens with review.

## Deliverables

- report.py extensions; csv/json field gains; tests + reviewed
  goldens.

## Exit gate

- On fixtures: aggregate sections render per i14 including the C1
  double-count case; deferred lines render when no floors exist;
  csv is the extended matrix; json the full structure; suite green;
  goldens reviewed.

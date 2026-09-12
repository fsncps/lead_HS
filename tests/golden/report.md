# Source feasibility census report

This report answers two study questions: (Q1) how many paint/varnish products each registered source exposes — observed listings, a floor, never a market total — and (Q2) for how many of them SDS-type documentation is reachable. The N1 block adds market-size anchors (trade sums, register counts); the N1 range itself is an estimate stated in the method sheet, never a DB count. Trade-statistics rows are volume context: tariff-line flows, never products. These remain source-feasibility metrics only: product and lead prevalence are M2+ deliverables and are never implied here. The tool, the database and the reports carry product data only (Strategy MASTER D27): inactive register rows appear in the matrix without findings.

## N1 — market-size anchors

Anchor values from the database (every value cites the run it comes from).
The estimate range built from them lives in the method sheet below — the
DB carries anchor values, never a computed range.

_No N1 anchors recorded yet — run the statistics sources (CS-2 aggregation; ST/AS manual records)._

### N1 method sheet (estimate — V2)

The N1 range is an estimate assembled from the anchors below; every
anchor is a DB-cited count. Formula sketch: N1 ≈ (producers in scope)
× (products per producer), bounded by the trade-flow context; the
anchors carry different coverage (EU vs national registers) and are
never summed naively.

- **EU trade (CS-2, Eurostat Comext DS-045409):** extra-EU imports
  (flow IMP), full-year sums across partners, HS 3208 + 3209.
  Coverage: CN8-aggregated chapter imports; caveat: trade volume is
  context, never a product count (D28 grain rule); quantities carry
  the API's supplementary unit (see finding notes). Provenance:
  https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409 (accessed 2026-09-12).
- **Producers (AS-1, CEPE; ST-3, Eurostat SBS):** association member
  counts and NACE 20.30 enterprise counts. Coverage: EU paint
  industry; caveat: membership ≠ full population; assumption bound:
  products-per-producer range stated at M1 with the promoted anchors.
  Provenance: https://www.cepe.org (accessed 2026-09-12);
  https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2 (accessed 2026-09-12).
- **Products registered (priors; ST-2 SPIN, ST-1 PCN, national
  registers):** product-unit register counts as scaling priors.
  Caveat: register populations ≠ market assortments; each prior is
  a floor over its own frame, not over the EU market.

The estimate stays labeled as an estimate; json carries the anchor
values, never a computed range (nu5/P7).


## N2/N3 — access coverage

Tier composition over active sources: **(a)** dataset/register access
counted · **(b)** sitemap-visible counted · **(c)** visible but uncounted
without scraping · **(d)** blocked/unknown.

| tier | meaning | sources | size |
|---|---|---|---|
| a | dataset/register access counted | — | 0 |
| b | sitemap-visible counted | — | 0 |
| c | visible, uncounted without scraping | CX-1, PX-1 | 2 |
| d | blocked/unknown | CX-2, CX-3, CX-4, PX-2, PX-3, PX-4, PX-5, PX-6, PX-7, PX-8, PX-9, SX-1 | 12 |


**N2 (Σ tier a+b counts):** no counted sources yet — run the statistics
and recon sweeps before reading a total here (never a bare 0).


**N3:** no site recorded sds_library_visible = 1 yet (manual-web records pending).


## Trade context (volume only — never products)


_No trade-context lines yet (CS aggregation pending)._

## Priors (registers & associations)


_No priors recorded yet (ST/AS manual records pending)._

### Access-decision bridge

What a scraping go would buy versus its cost — qualitative, cited to the run evidence in this report (i14 bridge semantics, stripped of walk-floor inputs). No decision is taken here; this bridges the recon numbers to the follow-up options.

- Would buy: the tier (c) sources (CX-1, PX-1) — size
  characterized, uncounted without scraping; a scraping go would turn
  these into floors.
- Cost: blocked/failed evidence lives in the execution log (robots
  denials, 403/429 walls, JS-gated libraries); each blocked site keeps
  its manual fallback path (D4).
- The bridge cites run evidence only; no decision is taken in this report.

## Summary matrix

One row per registered source (inactive rows visible, never in sums).
New v0.2.0 columns are numbers-first; the census columns stay (walk
machinery idle since D31). The records_hs*/trade_* columns are volume
context — tariff-line flows, not products.

| source | class | active | tier | status | sitemap | sds lib | products reg. | producers reg. | kg 3208 | EUR 3208 | kg 3209 | EUR 3209 | products | doc links | walk budget | catalog | category | page ok | sds ok | hs3208 | hs3209 | hs3213 | export rows | census status | last run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CX-1 | CS | 1 | c | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | 3 count | — | probe-20260910-cx1 |
| CX-2 | CS | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CX-3 | CS | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CX-4 | CS | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-1 | PE | 1 | c | done | — | — | — | — | — | — | — | — | 6 count | 1 count | 0 | 500 count | 2 count | 2 count | 1 count | — | — | — | — | — | probe-20260910-px1 |
| PX-2 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-3 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-4 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-5 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-6 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-7 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-8 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-9 | PE | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ST-1 | ST | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| SX-1 | ST | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |


## Execution log (latest census/recon run per source)


| source | run_key | status | started | finished | notes |
|---|---|---|---|---|---|
| CX-1 | probe-20260910-cx1 | done | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | — |
| PX-1 | probe-20260910-px1 | done | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | — |



## Sources


### CX-1 — Fixture export

- identity: class CS · active yes · tier c · verification open · http://127.0.0.1:PORT/export.csv
- access: robots — · terms — · rate limit — · free access 1
- content: format CSV; columns: hs_code, year, partner, value · granularity CN8 x partner x year (observed columns) · coverage to confirm (year column present) · languages —
- counts: export rows 3 count
- register note: good csv
- latest run: probe-20260910-cx1 (done)

### CX-2 — Fixture bad export

- identity: class CS · active yes · tier d · verification open · http://127.0.0.1:PORT/export-bad.csv
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: bad layout

### CX-3 — Fixture api

- identity: class CS · active yes · tier d · verification open · http://127.0.0.1:PORT/api.json
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: json

### CX-4 — Fixture 500

- identity: class CS · active yes · tier d · verification open · http://127.0.0.1:PORT/error500
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: network fail

### PX-1 — Fixture catalog

- identity: class PE · active yes · tier c · verification open · http://127.0.0.1:PORT/
- access: robots allowed · terms link present: /terms · rate limit unknown — polite default <= 1 req / 2 s · free access 1
- content: format — · granularity — · coverage — · languages ["de", "fr"]
- counts: catalog 500 count · categories: /cat/wandfarben=2, /cat/grundierung=0 · walk budget: within budget
- register note: census good catalog
- latest run: probe-20260910-px1 (done)

### PX-2 — Robots-denied

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/private/secret
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: robots deny

### PX-3 — Blocked 403

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/forbidden
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 403

### PX-4 — Persistent 429

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/ratelimited-always
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 429

### PX-5 — 429 once

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/ratelimited-once
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 429-then-ok

### PX-6 — Empty page

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/empty.html
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: parse error

### PX-7 — Huge page

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/huge.html
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: hostile

### PX-8 — Non-utf8

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/non-utf8.html
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: hostile

### PX-9 — Missing page

- identity: class PE · active yes · tier d · verification open · http://127.0.0.1:PORT/missing
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 404

### ST-1 — PCN stats

- identity: class ST · active no · tier — · verification open · http://127.0.0.1:PORT/missing
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: manual-web via probe record

### SX-1 — Fixture spin

- identity: class ST · active yes · tier d · verification open · http://127.0.0.1:PORT/spin
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: mdbtools

## Legend

- “—” = metric absent (source not queried for it); 0 = queried, empty result.
- Metric values cite the run_key of the done run they come from.
- Status reflects the latest census/recon run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.
- Access tiers (active sources): (a) dataset/register access counted · (b) sitemap-visible counted · (c) visible but uncounted without scraping · (d) blocked/unknown. N2 sums tiers (a)+(b) only.
- N3 pairs doc-bearing counts with the site count of sds_library_visible = 1 — a site count, not a product count (labeled as such).
- sitemap_products is a recon floor (robots-compliant, counts only; index/size caps render it partial — “floor partial” in the notes).
- records_hs*/trade_* columns are volume context: tariff-line flows, not products (D28 grain rule); trade quantities carry the API's supplementary unit (see finding notes).
- Inactive register rows never enter N2/N3 sums; counted-but-excluded sources are listed explicitly.

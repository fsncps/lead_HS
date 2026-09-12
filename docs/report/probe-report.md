# Source feasibility census report

This report answers two study questions: (Q1) how many paint/varnish products each registered source exposes — observed listings, a floor, never a market total — and (Q2) for how many of them SDS-type documentation is reachable. The N1 block adds market-size anchors (trade sums, register counts); the N1 range itself is an estimate stated in the method sheet, never a DB count. Trade-statistics rows are volume context: tariff-line flows, never products. These remain source-feasibility metrics only: product and lead prevalence are M2+ deliverables and are never implied here. The tool, the database and the reports carry product data only (Strategy MASTER D27): inactive register rows appear in the matrix without findings.

## N1 — market-size anchors

Anchor values from the database (every value cites the run it comes from).
The estimate range built from them lives in the method sheet below — the
DB carries anchor values, never a computed range.


| source | anchor | value | unit | run_key |
|---|---|---|---|---|
| AS-1 | Producers registered (priors) | 800.0 | count | probe-20260912-as1manual |
| CS-2 | EU imports HS 3208 (kg) | 2471311314.0 | kg | probe-20260912-cs2-10 |
| CS-2 | EU imports HS 3208 (EUR) | 12211227434.0 | eur | probe-20260912-cs2-10 |
| CS-2 | EU imports HS 3209 (kg) | 2099166223.9999998 | kg | probe-20260912-cs2-10 |
| CS-2 | EU imports HS 3209 (EUR) | 6221811666.0 | eur | probe-20260912-cs2-10 |
| ST-3 | Producers registered (priors) | 3200.0 | count | probe-20260912-st3manual |



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
| b | sitemap-visible counted | PE-10, PE-11, PE-12, PE-13, PE-14, PE-15, PE-16, PE-17, PE-18, PE-19, PE-20, PE-21, PE-22, PE-23, PE-25, PE-26, PE-27, PE-28, PE-29, PE-30, PE-32, PE-33, PE-34 | 23 |
| c | visible, uncounted without scraping | CS-2, PE-24, PE-31 | 3 |
| d | blocked/unknown | ST-2 | 1 |


**N2 (Σ tier a+b counts): 204693** across
23 counted source(s).


**N3:** 9 site(s) with a visible SDS library
(site count — not a product count); doc-bearing counts observed so far:
0.



## Trade context (volume only — never products)



- **CS-2** trade context: trade_kg_hs3208: 2471311314 kg (year=2024; top: INT_EU27_2020=11062630, DE=2953908, IT=1537397, EXT_EU27_2020=1293926, FR=1285140; quantity converted from QUANTITY_IN_100KG (×100)) · trade_eur_hs3208: 12211227434 eur (year=2024; top: INT_EU27_2020=5318389302, DE=1681115353, EXT_EU27_2020=787224415, IT=684529899, BE=496100145) · trade_kg_hs3209: 2099166223.9999998 kg (year=2024; top: INT_EU27_2020=9478613, DE=2574421, NL=1209558, EXT_EU27_2020=1017218, FR=870095; quantity converted from QUANTITY_IN_100KG (×100)) · trade_eur_hs3209: 6221811666 eur (year=2024; top: INT_EU27_2020=2798057454, DE=882764356, EXT_EU27_2020=312848379, NL=294368451, FR=244552218)



## Priors (registers & associations)



- **AS-1** priors: producers_registered=800 [probe-20260912-as1manual]
- **PE-10** priors: sitemap_products=2 [probe-20260912-pe10-3]
- **PE-11** priors: sitemap_products=146 [probe-20260912-pe11-2]
- **PE-12** priors: sitemap_products=9 [probe-20260912-pe12-2]
- **PE-13** priors: sitemap_products=1953 [probe-20260912-pe13-2]
- **PE-14** priors: sitemap_products=3 [probe-20260912-pe14-2]
- **PE-15** priors: sitemap_products=0 [probe-20260912-pe15-2]
- **PE-16** priors: sitemap_products=0 [probe-20260912-pe16-2]
- **PE-17** priors: sitemap_products=0 [probe-20260912-pe17-2]
- **PE-18** priors: sitemap_products=0 [probe-20260912-pe18-2]
- **PE-19** priors: sitemap_products=1619 [probe-20260912-pe19-2]
- **PE-20** priors: sitemap_products=199354 [probe-20260912-pe20-2]
- **PE-21** priors: sitemap_products=0 [probe-20260912-pe21-2]
- **PE-22** priors: sitemap_products=0 [probe-20260912-pe22-2]
- **PE-23** priors: sitemap_products=0 [probe-20260912-pe23-2]
- **PE-25** priors: sitemap_products=0 [probe-20260912-pe25-2]
- **PE-26** priors: sitemap_products=0 [probe-20260912-pe26-2]
- **PE-27** priors: sitemap_products=0 [probe-20260912-pe27-2]
- **PE-28** priors: sitemap_products=0 [probe-20260912-pe28-2]
- **PE-29** priors: sitemap_products=4 [probe-20260912-pe29-2]
- **PE-30** priors: sitemap_products=60 [probe-20260912-pe30-2]
- **PE-32** priors: sitemap_products=0 [probe-20260912-pe32-2]
- **PE-33** priors: sitemap_products=1541 [probe-20260912-pe33-2]
- **PE-34** priors: sitemap_products=2 [probe-20260912-pe34-2]
- **ST-3** priors: producers_registered=3200 [probe-20260912-st3manual]



### Access-decision bridge

What a scraping go would buy versus its cost — qualitative, cited to the run evidence in this report (i14 bridge semantics, stripped of walk-floor inputs). No decision is taken here; this bridges the recon numbers to the follow-up options.

- Would buy: the tier (c) sources (CS-2, PE-24, PE-31) — size
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
| AS-1 | AS | 0 | — | done | — | — | — | 800 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-as1manual |
| CS-1 | CS | 0 | — | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-cs1-3 |
| CS-2 | CS | 1 | c | done | — | — | — | — | 2471311314 kg | 12211227434 eur | 2099166223.9999998 kg | 6221811666 eur | — | — | — | — | — | — | — | 278 count | 264 count | 228 count | 1 count | — | probe-20260912-cs2-10 |
| PE-1 | PE | 0 | — | done | — | — | — | — | — | — | — | — | 0 count | 0 count | 0 | — | — | — | — | — | — | — | — | — | probe-20260912-pe1-3 |
| PE-10 | PE | 1 | b | done | 2 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe10manual |
| PE-11 | PE | 1 | b | done | 146 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe11manual |
| PE-12 | PE | 1 | b | done | 9 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe12manual |
| PE-13 | PE | 1 | b | done | 1953 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe13manual |
| PE-14 | PE | 1 | b | done | 3 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe14manual |
| PE-15 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe15manual |
| PE-16 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe16manual |
| PE-17 | PE | 1 | b | done | 0 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe17manual |
| PE-18 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe18manual |
| PE-19 | PE | 1 | b | done | 1619 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe19manual |
| PE-2 | PE | 0 | — | blocked | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe2-3 |
| PE-20 | PE | 1 | b | done | 199354 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe20manual |
| PE-21 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe21manual |
| PE-22 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe22manual |
| PE-23 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe23manual |
| PE-24 | PE | 1 | c | done | — | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe24manual |
| PE-25 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe25manual |
| PE-26 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe26manual |
| PE-27 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe27manual |
| PE-28 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe28manual |
| PE-29 | PE | 1 | b | done | 4 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe29manual |
| PE-3 | PE | 0 | — | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe3-3 |
| PE-30 | PE | 1 | b | done | 60 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe30manual |
| PE-31 | PE | 1 | c | done | — | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe31manual |
| PE-32 | PE | 1 | b | done | 0 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe32manual |
| PE-33 | PE | 1 | b | done | 1541 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe33manual |
| PE-34 | PE | 1 | b | done | 2 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe34manual |
| PE-4 | PE | 0 | — | done | — | — | — | — | — | — | — | — | 0 count | 0 count | 0 | — | — | — | — | — | — | — | — | — | probe-20260912-pe4-3 |
| ST-1 | ST | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ST-2 | ST | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-st2-7 |
| ST-3 | ST | 0 | — | done | — | — | — | 3200 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-st3manual |


## Execution log (latest census/recon run per source)


| source | run_key | status | started | finished | notes |
|---|---|---|---|---|---|
| AS-1 | probe-20260912-as1manual | done | 2026-09-12T09:38:25Z | 2026-09-12T09:38:25Z | — |
| CS-1 | probe-20260912-cs1-3 | failed | 2026-09-12T04:52:10Z | 2026-09-12T04:52:16Z | https://swiss-impex.admin.ch/robots.txt: network error after retries |
| CS-2 | probe-20260912-cs2-10 | done | 2026-09-12T09:40:44Z | 2026-09-12T09:40:58Z | — |
| PE-1 | probe-20260912-pe1-3 | done | 2026-09-12T04:52:23Z | 2026-09-12T04:52:26Z | — |
| PE-10 | probe-20260912-pe10manual | done | 2026-09-12T09:38:54Z | 2026-09-12T09:38:54Z | — |
| PE-11 | probe-20260912-pe11manual | done | 2026-09-12T09:38:54Z | 2026-09-12T09:38:54Z | — |
| PE-12 | probe-20260912-pe12manual | done | 2026-09-12T09:38:54Z | 2026-09-12T09:38:54Z | — |
| PE-13 | probe-20260912-pe13manual | done | 2026-09-12T09:38:55Z | 2026-09-12T09:38:55Z | — |
| PE-14 | probe-20260912-pe14manual | done | 2026-09-12T09:38:55Z | 2026-09-12T09:38:55Z | — |
| PE-15 | probe-20260912-pe15manual | done | 2026-09-12T09:39:37Z | 2026-09-12T09:39:37Z | — |
| PE-16 | probe-20260912-pe16manual | done | 2026-09-12T09:39:37Z | 2026-09-12T09:39:37Z | — |
| PE-17 | probe-20260912-pe17manual | done | 2026-09-12T09:39:38Z | 2026-09-12T09:39:38Z | — |
| PE-18 | probe-20260912-pe18manual | done | 2026-09-12T09:39:38Z | 2026-09-12T09:39:38Z | — |
| PE-19 | probe-20260912-pe19manual | done | 2026-09-12T09:39:38Z | 2026-09-12T09:39:38Z | — |
| PE-2 | probe-20260912-pe2-3 | blocked | 2026-09-12T04:52:26Z | 2026-09-12T04:52:26Z | https://www.coop.ch/robots.txt: HTTP 403 |
| PE-20 | probe-20260912-pe20manual | done | 2026-09-12T09:39:39Z | 2026-09-12T09:39:39Z | — |
| PE-21 | probe-20260912-pe21manual | done | 2026-09-12T09:39:39Z | 2026-09-12T09:39:39Z | — |
| PE-22 | probe-20260912-pe22manual | done | 2026-09-12T09:39:39Z | 2026-09-12T09:39:39Z | — |
| PE-23 | probe-20260912-pe23manual | done | 2026-09-12T09:39:39Z | 2026-09-12T09:39:39Z | — |
| PE-24 | probe-20260912-pe24manual | done | 2026-09-12T09:39:40Z | 2026-09-12T09:39:40Z | — |
| PE-25 | probe-20260912-pe25manual | done | 2026-09-12T09:39:40Z | 2026-09-12T09:39:40Z | — |
| PE-26 | probe-20260912-pe26manual | done | 2026-09-12T09:39:40Z | 2026-09-12T09:39:40Z | — |
| PE-27 | probe-20260912-pe27manual | done | 2026-09-12T09:39:41Z | 2026-09-12T09:39:41Z | — |
| PE-28 | probe-20260912-pe28manual | done | 2026-09-12T09:39:41Z | 2026-09-12T09:39:41Z | — |
| PE-29 | probe-20260912-pe29manual | done | 2026-09-12T09:39:41Z | 2026-09-12T09:39:41Z | — |
| PE-3 | probe-20260912-pe3-3 | failed | 2026-09-12T04:52:26Z | 2026-09-12T04:52:32Z | https://example.invalid/robots.txt: network error after retries |
| PE-30 | probe-20260912-pe30manual | done | 2026-09-12T09:39:42Z | 2026-09-12T09:39:42Z | — |
| PE-31 | probe-20260912-pe31manual | done | 2026-09-12T09:39:42Z | 2026-09-12T09:39:42Z | — |
| PE-32 | probe-20260912-pe32manual | done | 2026-09-12T09:39:42Z | 2026-09-12T09:39:42Z | — |
| PE-33 | probe-20260912-pe33manual | done | 2026-09-12T09:39:42Z | 2026-09-12T09:39:42Z | — |
| PE-34 | probe-20260912-pe34manual | done | 2026-09-12T09:39:43Z | 2026-09-12T09:39:43Z | — |
| PE-4 | probe-20260912-pe4-3 | done | 2026-09-12T04:52:32Z | 2026-09-12T04:52:34Z | — |
| ST-2 | probe-20260912-st2-7 | failed | 2026-09-12T08:40:14Z | 2026-09-12T08:41:50Z | http://spin2000.net/robots.txt: network error after retries |
| ST-3 | probe-20260912-st3manual | done | 2026-09-12T09:38:11Z | 2026-09-12T09:38:11Z | — |



## Sources


### AS-1 — CEPE (European paints association)

- identity: class AS · active no · tier — · verification open · https://www.cepe.org
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: producers_registered=800 [probe-20260912-as1manual]
- register note: producers_registered via manual record (member counts / national-association list); URL verified live 2026-09-12; candidate-row semantics nu3
- latest run: probe-20260912-as1manual (done)

### CS-1 — swiss-impex (EZV)

- identity: class CS · active no · tier — · verification open · https://swiss-impex.admin.ch
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: CH imports/exports 3208/3209 (+3213); granularity CN8 x partner x year; free access & granularity high-priority probe target; out of scope D31 (EU-only; TLS wall documented 2026-09-12)
- latest run: probe-20260912-cs1-3 (failed; notes: https://swiss-impex.admin.ch/robots.txt: network error after retries)

### CS-2 — Eurostat Comext DS-045409

- identity: class CS · active yes · tier c · verification verified · https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409
- access: robots — · terms — · rate limit — · free access 1
- content: format JSON-stat dataset · granularity to confirm from JSON structure (probe) · coverage — · languages —
- counts: export rows 1 count
- trade context: trade_kg_hs3208: 2471311314 kg (year=2024; top: INT_EU27_2020=11062630, DE=2953908, IT=1537397, EXT_EU27_2020=1293926, FR=1285140; quantity converted from QUANTITY_IN_100KG (×100)) · trade_eur_hs3208: 12211227434 eur (year=2024; top: INT_EU27_2020=5318389302, DE=1681115353, EXT_EU27_2020=787224415, IT=684529899, BE=496100145) · trade_kg_hs3209: 2099166223.9999998 kg (year=2024; top: INT_EU27_2020=9478613, DE=2574421, NL=1209558, EXT_EU27_2020=1017218, FR=870095; quantity converted from QUANTITY_IN_100KG (×100)) · trade_eur_hs3209: 6221811666 eur (year=2024; top: INT_EU27_2020=2798057454, DE=882764356, EXT_EU27_2020=312848379, NL=294368451, FR=244552218)
- register note: EU27 extra-EU trade; CN8 x partner x year; full-year import aggregation (nu2): trade_kg/eur_hs3208/3209
- latest run: probe-20260912-cs2-10 (done)

### PE-1 — Manufacturer/brand sites (seed)

- identity: class PE · active no · tier — · verification open · https://www.epifanes.com
- access: robots allowed · terms not found · rate limit unknown — polite default <= 1 req / 2 s · free access 1
- content: format — · granularity — · coverage — · languages []
- counts: walk budget: within budget
- register note: superseded by per-site rows PE-10+ (v0.2.0 nu6); site lives on as PE-25
- latest run: probe-20260912-pe1-3 (done)

### PE-10 — AkzoNobel

- identity: class PE · active yes · tier b · verification open · https://www.akzonobel.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=2 [probe-20260912-pe10-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe10manual (done)

### PE-11 — PPG

- identity: class PE · active yes · tier b · verification open · https://www.ppg.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=146 [probe-20260912-pe11-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe11manual (done)

### PE-12 — Sherwin-Williams

- identity: class PE · active yes · tier b · verification open · https://www.sherwin-williams.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=9 [probe-20260912-pe12-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe12manual (done)

### PE-13 — Jotun

- identity: class PE · active yes · tier b · verification open · https://www.jotun.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=1953 [probe-20260912-pe13-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe13manual (done)

### PE-14 — Hempel

- identity: class PE · active yes · tier b · verification open · https://www.hempel.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=3 [probe-20260912-pe14-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe14manual (done)

### PE-15 — Sika

- identity: class PE · active yes · tier b · verification open · https://www.sika.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe15-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe15manual (done)

### PE-16 — Sto

- identity: class PE · active yes · tier b · verification open · https://www.sto.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe16-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe16manual (done)

### PE-17 — Caparol (DAW)

- identity: class PE · active yes · tier b · verification open · https://www.caparol.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe17-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe17manual (done)

### PE-18 — Tikkurila

- identity: class PE · active yes · tier b · verification open · https://www.tikkurila.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe18-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe18manual (done)

### PE-19 — Teknos

- identity: class PE · active yes · tier b · verification open · https://www.teknos.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=1619 [probe-20260912-pe19-2]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260912-pe19manual (done)

### PE-2 — DIY chains (seed)

- identity: class PE · active no · tier — · verification open · https://www.coop.ch
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: superseded by per-site rows PE-20+ (v0.2.0 nu6); CH-DIY seeds dropped (D31 EU-only)
- latest run: probe-20260912-pe2-3 (blocked; notes: https://www.coop.ch/robots.txt: HTTP 403)

### PE-20 — Hornbach DE

- identity: class PE · active yes · tier b · verification open · https://www.hornbach.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=199354 [probe-20260912-pe20-2]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=5
- latest run: probe-20260912-pe20manual (done)

### PE-21 — OBI DE

- identity: class PE · active yes · tier b · verification open · https://www.obi.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe21-2]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=5
- latest run: probe-20260912-pe21manual (done)

### PE-22 — Bauhaus DE

- identity: class PE · active yes · tier b · verification open · https://www.bauhaus.info
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe22-2]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=5; URL corrected 2026-09-12 (bauhaus.de resolves to Bauhaus-Archiv museum)
- latest run: probe-20260912-pe22manual (done)

### PE-23 — Leroy Merlin FR

- identity: class PE · active yes · tier b · verification open · https://www.leroymerlin.fr
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe23-2]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=5
- latest run: probe-20260912-pe23manual (done)

### PE-24 — B&Q (diy.com)

- identity: class PE · active yes · tier c · verification open · https://www.diy.com
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=5
- latest run: probe-20260912-pe24manual (done)

### PE-25 — Epifanes

- identity: class PE · active yes · tier b · verification open · https://www.epifanes.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe25-2]
- register note: channel=marine; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MARINE<=5
- latest run: probe-20260912-pe25manual (done)

### PE-26 — SVB

- identity: class PE · active yes · tier b · verification open · https://www.svb.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe26-2]
- register note: channel=marine; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MARINE<=5
- latest run: probe-20260912-pe26manual (done)

### PE-27 — Toplicht

- identity: class PE · active yes · tier b · verification open · https://www.toplicht.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe27-2]
- register note: channel=marine; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MARINE<=5
- latest run: probe-20260912-pe27manual (done)

### PE-28 — Raseglarhuset

- identity: class PE · active yes · tier b · verification open · https://www.raseglarhuset.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe28-2]
- register note: channel=marine; listed_by=PE-4 seed note (BRAVA SE); listed_date=2026-09-12; inclusion=cap MARINE<=5
- latest run: probe-20260912-pe28manual (done)

### PE-29 — Old Holland

- identity: class PE · active yes · tier b · verification open · https://www.oldholland.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=4 [probe-20260912-pe29-2]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=6
- latest run: probe-20260912-pe29manual (done)

### PE-3 — B2B / trade portals (placeholder)

- identity: class PE · active no · tier — · verification open · https://example.invalid
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: unresolved channel — left OPEN (v0.2.0 nu3/V6); no confirmed portal URL, uncovered-channel line in the report
- latest run: probe-20260912-pe3-3 (failed; notes: https://example.invalid/robots.txt: network error after retries)

### PE-30 — Zecchi

- identity: class PE · active yes · tier b · verification open · https://www.zecchi.it
- access: robots allow-all (404/empty) · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=60 [probe-20260912-pe30-2]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=6
- latest run: probe-20260912-pe30manual (done)

### PE-31 — Kremer Pigmente

- identity: class PE · active yes · tier c · verification open · https://www.kremer-pigmente.com
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=6
- latest run: probe-20260912-pe31manual (done)

### PE-32 — Michael Harding

- identity: class PE · active yes · tier b · verification open · https://www.michaelharding.co.uk
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe32-2]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=6
- latest run: probe-20260912-pe32manual (done)

### PE-33 — Winsor & Newton

- identity: class PE · active yes · tier b · verification open · https://www.winsornewton.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=1541 [probe-20260912-pe33-2]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=6
- latest run: probe-20260912-pe33manual (done)

### PE-34 — Sennelier

- identity: class PE · active yes · tier b · verification open · https://www.sennelier.fr
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=2 [probe-20260912-pe34-2]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=6
- latest run: probe-20260912-pe34manual (done)

### PE-4 — Marine chandlers & art-supply shops (seed)

- identity: class PE · active no · tier — · verification partially_verified · https://www.toplicht.de
- access: robots allowed · terms link present: https://www.toplicht.de/informationen/agb/ · rate limit unknown — polite default <= 1 req / 2 s · free access 1
- content: format — · granularity — · coverage — · languages ["de", "en", "nl"]
- counts: walk budget: within budget
- register note: superseded by per-site rows PE-25+ (v0.2.0 nu6); sites live on as PE-26/PE-27/PE-29+
- latest run: probe-20260912-pe4-3 (done)

### ST-1 — ECHA PCN statistics

- identity: class ST · active no · tier — · verification open · https://echa.europa.eu
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: formulation counts (hazardous mixtures); manual-web via probe record (locate aggregates) - active=0 per ENG review A1

### ST-2 — Nordic SPIN (DK/SE/NO/FI)

- identity: class ST · active yes · tier d · verification partially_verified · http://spin2000.net/?page_id=54
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: preparation counts, lead-CAS incidence; register URL = DB download page ?page_id=54 (od9 fix); extraction path OPEN (mdbtools)
- latest run: probe-20260912-st2-7 (failed; notes: http://spin2000.net/robots.txt: network error after retries)

### ST-3 — Eurostat PRODCOM / SBS

- identity: class ST · active no · tier — · verification verified · https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: producers_registered=3200 [probe-20260912-st3manual]
- register note: NACE 20.30 production values/producer counts; producers_registered via manual record this unit; full PRODCOM/SBS integration deferred (TODOS.md)
- latest run: probe-20260912-st3manual (done)

## Legend

- “—” = metric absent (source not queried for it); 0 = queried, empty result.
- Metric values cite the run_key of the done run they come from.
- Status reflects the latest census/recon run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.
- Access tiers (active sources): (a) dataset/register access counted · (b) sitemap-visible counted · (c) visible but uncounted without scraping · (d) blocked/unknown. N2 sums tiers (a)+(b) only.
- N3 pairs doc-bearing counts with the site count of sds_library_visible = 1 — a site count, not a product count (labeled as such).
- sitemap_products is a recon floor (robots-compliant, counts only; index/size caps render it partial — “floor partial” in the notes).
- records_hs*/trade_* columns are volume context: tariff-line flows, not products (D28 grain rule); trade quantities carry the API's supplementary unit (see finding notes).
- Inactive register rows never enter N2/N3 sums; counted-but-excluded sources are listed explicitly.

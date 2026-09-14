# Source feasibility census report

This report answers two study questions: (Q1) how many paint/varnish products each registered source exposes — observed listings, a floor, never a market total — and (Q2) for how many of them SDS-type documentation is reachable. The N1 block adds market-size anchors (trade sums, register counts); the N1 range itself is an estimate stated in the method sheet, never a DB count. Trade-statistics rows are volume context: tariff-line flows, never products. These remain source-feasibility metrics only: product and lead prevalence are M2+ deliverables and are never implied here. The tool, the database and the reports carry product data only (Strategy MASTER D27): inactive register rows appear in the matrix without findings.

## Funnel — the three questions (v0.2.2)

> ⚠ **Superseded 2026-09-14 (v0.2.3): the funnel-modeled Q1 (M-bounds × uniform products-per-producer) is superseded by the pool estimate v2 section below (7-benchmark vote, dual-level verdict). The funnel block is kept for the publish history — republishes append timestamp-hash snapshots.**



**Q1 — market pool (modeled estimate):** P(cn8) = M × ppp × s(cn8) → range **[85840, 343360]** products
(M bounds: CEPE member count (AS-11 manual record) / Eurostat SBS NACE 20.30 enterprise count (ST-3 prior); ppp = 107.3 = 17170 distinct pairs ÷ 160 licence holders over the largest staged register AS-2). modeled estimate — never a DB count.

Per-CN8 modeled split (s = staged extra-EU kg share):
| CN8 | kg | share s | P low | P high |
|---|---|---|---|---|
| 32091000 | 3371631890 | 0.3185 | 27341 | 109365 |
| 32089091 | 1767791886 | 0.167 | 14335 | 57341 |
| 32099000 | 1486925852 | 0.1405 | 12057 | 48231 |
| 32082090 | 1160497872 | 0.1096 | 9410 | 37642 |
| 32081090 | 1130898392 | 0.1068 | 9170 | 36682 |
| 32089019 | 618748116 | 0.0585 | 5017 | 20070 |
| 32082010 | 345143470 | 0.0326 | 2798 | 11195 |
| 32089099 | 313123376 | 0.0296 | 2539 | 10156 |
| 32081010 | 184436236 | 0.0174 | 1495 | 5982 |
| 32139000 | 103475904 | 0.0098 | 839 | 3356 |
| 32131000 | 94723190 | 0.0089 | 768 | 3072 |
| 32089011 | 7969902 | 0.0008 | 64 | 258 |
| 32089013 | 101656 | 0.0 | 0 | 3 |


**Q2 — definitively identifiable: 17170 (floor)** — definitively identifiable: N (floor) — distinct (manufacturer, ident) pairs over staged registers.

**Q3 — SDS reachable (modeled): 3590** — modeled SDS reach — Σ sitemap products over sites with a visible SDS library; match-rate assumption pending (upper bound shown).

**v0.5 ratio (Q2 ÷ Q1): 0.05 – 0.2** — share of the modeled pool that is definitively identifiable (epistemic label: floor ÷ range).

## Pool estimate v2 (v0.2.3 — benchmark vote, dual-level verdict)

The v0.2.3 pool estimate: seven benchmark quantities vote into the magnitude taxonomy (a 20k–50k · b 50k–100k · c 100k–200k · d 200k–300k · e >300k); the pinned rule converts the vote into a dual-level verdict (SKU = registry/product level, formulation = shade/pack-collapsed). Estimates are bands, never points; indeterminate benchmarks stay visible; confidence is claimed only when ≥3 benchmarks converge at base with no exclusive non-adjacent conflict.

| # | Quantity | Vintage | Band (low–high) | Base class(es) | Notes |
|---|---|---|---|---|---|
| B1 | EU tonnage ÷ per-SKU throughput | 2024 (JRC AHWG; accessed 2026-09-14) | 46,250–210,000 | b (↓a ↑d) | per-SKU throughput scenarios 20000–80000 kg/yr (base 40000); throughput per SKU is the flip assumption — abstracts pin it (X4) |
| B2-SE | national paint count × EU scale × scope | 2022-09-15 (SE PC Echo, BfR-Akademie deck) | 1,812,117–3,020,194 | e | SE PC poison-centre submissions — voluntary-inclusive, upper envelope; population scale ×42.4; scope correction ×0.6–1 |
| B2-DK | national paint count × EU scale × scope | undated web figure (at.dk, accessed 2026-09-14) | 558,516–1,016,316 | e | DK total notified ≈40,000 — hazardous-only; paint split Power-BI-only (not extractable, D31); population scale ×76.3; scope correction ×0.183–0.333 |
| B3 | notified mixtures × paint share × uplift | 2021 (SWD(2022) 435 Annex 16) | 144,429–866,574 | e (↓c ↑e) | paint share of notified mixtures 0.1–0.2 (base 0.15); non-hazardous uplift ×1–3 (base 2) — tr10 assumption band |
| B4 | producers × assortment | 2020 (SBS C2030) / 2026 (CEPE web) | 20,000–495,000 | c (↓a ↑e) | producer count 800–3300; products-per-producer 25–150 (base 60) |
| B5 | certified count ÷ penetration | 03/2025 (JRC final report) | 123,200–739,200 | d (↓c ↑e) | penetration scenarios 0.05–0.3 (base 0.15) — no official market share exists |
| B6 | out-of-pool sanity anchors | 07/2026 (Paint Color HQ; CoatingsTech 02/2021) | 14,700–26,597 | a (↓<a ↑a) | US named-colour catalogs: 26,597 colours / 13 brands, ≈14,700 distinct after ΔE-dedup (Paint Color HQ 07/2026); one major manufacturer's DIY references, one country: >3,000 (AkzoNobel FR, daiteo case study); one major manufacturer's colour range: 3,500+ colours (Benjamin Moore, CoatingsTech 02/2021) |

Base-vote tally: 20k–50k: 1 · 50k–100k: 1 · 100k–200k: 1 · 200k–300k: 1 · >300k: 3.

**Verdict: class >300k** at the sku level.

Confidence: not claimed — divergent benchmark(s) exclusively compatible with a non-adjacent class — confidence withheld, open items recorded (tr4)

Divergent benchmarks (open items): B1 → b, B4 → c, B6 → a.

| # | Quantity | Vintage | Band (low–high) | Base class(es) | Notes |
|---|---|---|---|---|---|
| B1 | EU tonnage ÷ per-SKU throughput | 2024 (JRC AHWG; accessed 2026-09-14) | 4,625–210,000 | <a (↓<a ↑d) | formulation level via compression factor ×1–10 (c2); per-SKU throughput scenarios 20000–80000 kg/yr (base 40000); throughput per SKU is the flip assumption — abstracts pin it (X4) |
| B2-SE | national paint count × EU scale × scope | 2022-09-15 (SE PC Echo, BfR-Akademie deck) | 181,212–3,020,194 | e (↓c ↑e) | SE PC poison-centre submissions — voluntary-inclusive, upper envelope; formulation level via compression factor ×1–10 (c2); population scale ×42.4; scope correction ×0.6–1 |
| B2-DK | national paint count × EU scale × scope | undated web figure (at.dk, accessed 2026-09-14) | 55,852–1,016,316 | c (↓b ↑e) | DK total notified ≈40,000 — hazardous-only; paint split Power-BI-only (not extractable, D31); formulation level via compression factor ×1–10 (c2); population scale ×76.3; scope correction ×0.183–0.333 |
| B3 | notified mixtures × paint share × uplift | 2021 (SWD(2022) 435 Annex 16) | 14,443–866,574 | b (↓<a ↑e) | formulation level via compression factor ×1–10 (c2); paint share of notified mixtures 0.1–0.2 (base 0.15); non-hazardous uplift ×1–3 (base 2) — tr10 assumption band |
| B4 | producers × assortment | 2020 (SBS C2030) / 2026 (CEPE web) | 20,000–495,000 | c (↓a ↑e) | producer count 800–3300; products-per-producer 25–150 (base 60) |
| B5 | certified count ÷ penetration | 03/2025 (JRC final report) | 123,200–739,200 | d (↓c ↑e) | penetration scenarios 0.05–0.3 (base 0.15) — no official market share exists |
| B6 | out-of-pool sanity anchors | 07/2026 (Paint Color HQ; CoatingsTech 02/2021) | 14,700–26,597 | a (↓<a ↑a) | US named-colour catalogs: 26,597 colours / 13 brands, ≈14,700 distinct after ΔE-dedup (Paint Color HQ 07/2026); one major manufacturer's DIY references, one country: >3,000 (AkzoNobel FR, daiteo case study); one major manufacturer's colour range: 3,500+ colours (Benjamin Moore, CoatingsTech 02/2021) |

Base-vote tally: 20k–50k: 1 · 50k–100k: 1 · 100k–200k: 2 · 200k–300k: 1 · >300k: 1.

**Verdict: class 100k–200k** at the formulation level.

Confidence: not claimed — divergent benchmark(s) exclusively compatible with a non-adjacent class — confidence withheld, open items recorded (tr4)

Divergent benchmarks (open items): B1 → <a, B2-SE → e, B6 → a.

formulation-level conversion rides the pinned 1–10 shade-collapse band (assumption — not measurable from registry metadata). X1 measured key-tier structure on the staged ECAT register (17838 rows): ean ×1.266, licence ×89.638, name ×1.049, 199 licences (the licence tier is a catalogue, not a compression).

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
| ST-1 | Products registered (priors) | 1444290.0 | — | probe-20260914-st1manual-2 |
| ST-3 | Producers registered (priors) | 3300.0 | — | probe-20260914-st3manual |
| ST-6 | Products registered (priors) | 40000.0 | — | probe-20260914-st6manual-2 |
| ST-7 | Products registered (priors) | 71231.0 | — | probe-20260914-st7manual |



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
| b | sitemap-visible counted | PE-10, PE-11, PE-12, PE-13, PE-14, PE-15, PE-16, PE-17, PE-18, PE-19, PE-20, PE-21, PE-22, PE-23, PE-25, PE-26, PE-27, PE-28, PE-29, PE-30, PE-32, PE-33, PE-34, PE-36, PE-37, PE-38, PE-39, PE-43, PE-44, PE-55, PE-57, PE-59, PE-60, PE-61, PE-62 | 35 |
| c | visible, uncounted without scraping | AS-6, AS-7, CS-2, PE-53, ST-4 | 5 |
| d | blocked/unknown | AS-2, AS-3, PE-24, PE-31, PE-35, PE-40, PE-41, PE-42, PE-54, PE-56, PE-58, ST-2 | 12 |


**N2 (Σ tier a+b counts): 331644** across
35 counted source(s).


**N3:** 9 site(s) with a visible SDS library
(site count — not a product count); doc-bearing counts observed so far:
0.


Excluded-and-counted (inactive register rows carrying counts — never in
the sums): ST-1, ST-6, ST-7.


## Trade context (volume only — never products)



- **CS-2** trade context: trade_kg_hs3208: 2471311314 kg (year=2024; top: INT_EU27_2020=11062630, DE=2953908, IT=1537397, EXT_EU27_2020=1293926, FR=1285140; quantity converted from QUANTITY_IN_100KG (×100)) · trade_eur_hs3208: 12211227434 eur (year=2024; top: INT_EU27_2020=5318389302, DE=1681115353, EXT_EU27_2020=787224415, IT=684529899, BE=496100145) · trade_kg_hs3209: 2099166223.9999998 kg (year=2024; top: INT_EU27_2020=9478613, DE=2574421, NL=1209558, EXT_EU27_2020=1017218, FR=870095; quantity converted from QUANTITY_IN_100KG (×100)) · trade_eur_hs3209: 6221811666 eur (year=2024; top: INT_EU27_2020=2798057454, DE=882764356, EXT_EU27_2020=312848379, NL=294368451, FR=244552218)



## CN8 trade table (staged; volume context)



| CN8 | flow | Σ kg | Σ EUR | staged rows |
|---|---|---|---|---|
| 32081010 | 1 | 96221280 | 338554554 | 114 |
| 32081010 | 2 | 88214956 | 419938776 | 290 |
| 32081090 | 1 | 508974440 | 2370178364 | 160 |
| 32081090 | 2 | 621923952 | 3223648970 | 378 |
| 32082010 | 1 | 154320056 | 777431560 | 130 |
| 32082010 | 2 | 190823414 | 1041678780 | 346 |
| 32082090 | 1 | 528028188 | 2988188972 | 184 |
| 32082090 | 2 | 632469684 | 3995346462 | 386 |
| 32089011 | 1 | 3611750 | 28164056 | 96 |
| 32089011 | 2 | 4358152 | 27715012 | 232 |
| 32089013 | 1 | 95158 | 1099884 | 36 |
| 32089013 | 2 | 6498 | 69574 | 16 |
| 32089019 | 1 | 249204850 | 1154375786 | 168 |
| 32089019 | 2 | 369543266 | 2059845204 | 368 |
| 32089091 | 1 | 787536896 | 3769228880 | 200 |
| 32089091 | 2 | 980254990 | 5299614964 | 394 |
| 32089099 | 1 | 143309344 | 783744700 | 190 |
| 32089099 | 2 | 169814032 | 882730840 | 368 |
| 32091000 | 1 | 1433611454 | 3671260676 | 218 |
| 32091000 | 2 | 1938020436 | 4971468728 | 382 |
| 32099000 | 1 | 665543716 | 2550327994 | 236 |
| 32099000 | 2 | 821382136 | 3401312414 | 388 |
| 32131000 | 1 | 61175808 | 336092588 | 184 |
| 32131000 | 2 | 33547382 | 281144084 | 330 |
| 32139000 | 1 | 50154936 | 310107402 | 198 |
| 32139000 | 2 | 53320968 | 401244536 | 324 |


per-CN8 observed-products floor not computable from staging: the staged register categories are criteria classes, not CN8 codes — the category→CN8 proxy mapping is not pinnable in v0.2.2 (caveat recorded in PHASE05).


## Identity table (staged registers)



| register | run | entries | distinct mfr | distinct (mfr, ident) pairs | identity completeness | top categories |
|---|---|---|---|---|---|---|
| AS-2 | probe-20260914-as2-3 | 17838 | 160 | 17170 | 16.0% | Decorative paints, varnishes, and related products (2014 criteria): 16001; Decorative paints, varnishes, and related products (2025 criteria): 1817; Performance coatings and related products: 20 |

**Deduped union (Q2 floor): 17170 pairs over 160 manufacturers.**
_overlap pilot not computable — no staged pairs for AS-3._


## Depth matrix counts (fu8 refined tiers)


| tier | meaning | sources |
|---|---|---|
| 1 | name only | PE-10, PE-11, PE-12, PE-13, PE-14, PE-19, PE-20, PE-29, PE-30, PE-33, PE-34, PE-37, PE-43 (13) |
| 2 | name + ident/licence + category (registry metadata, no technical data) | AS-2 (1) |
| 3 | adds technical performance data / downloadable tech docs (SDS/TDS links) | — (0) |
| 4 | standardized full documents (EPD declarations; IATA/CMR MSDS) | — (0) |

tier 4 is assigned only from recorded capability metrics (standardized-doc sources are manual records — capability not probed); absence of a tier is not a zero claim.
Per-site SDS-URL counts (G6): PE-23 = 1133.0; PE-20 = 652.0; PE-43 = 401.0; PE-27 = 5.0; PE-34 = 5.0; PE-29 = 4.0; PE-11 = 3.0; PE-19 = 3.0; PE-10 = 2.0; PE-28 = 2.0; PE-32 = 1.0.

## Source census (enumerated vs probed vs counted)

Enumerated register rows: 103 · probed (≥1 done run): 63 · counted: 35.

| class | channel | rows |
|---|---|---|
| AS | download | 7 |
| AS | manual | 23 |
| CS | api | 1 |
| CS | download | 4 |
| LI | manual | 4 |
| PE | scrape | 57 |
| ST | api | 1 |
| ST | download | 2 |
| ST | manual | 4 |


## Reconciliation flags (c4 — visible, never silent)


- ✓ **AS-2** (ok): staged rows 17838 (no products_registered metric — reconciled against the staged count, run probe-20260914-as2-3)
- ⚠ **ST-1** (staging-absent): metric present but no staged rows
- ⚠ **ST-6** (staging-absent): metric present but no staged rows
- ⚠ **ST-7** (staging-absent): metric present but no staged rows
- ✓ **CS-2** (ok): staged rows 6316 (latest run probe-20260914-cs2-2)



## Priors (registers & associations)



- **AS-1** priors: producers_registered=800 [probe-20260912-as1manual]
- **PE-10** priors: sitemap_products=2 [probe-20260914-pe10-3]
- **PE-11** priors: sitemap_products=146 [probe-20260914-pe11-3]
- **PE-12** priors: sitemap_products=9 [probe-20260914-pe12-3]
- **PE-13** priors: sitemap_products=1953 [probe-20260914-pe13-3]
- **PE-14** priors: sitemap_products=3 [probe-20260914-pe14-3]
- **PE-15** priors: sitemap_products=0 [probe-20260914-pe15-3]
- **PE-16** priors: sitemap_products=0 [probe-20260914-pe16-3]
- **PE-17** priors: sitemap_products=0 [probe-20260914-pe17-3]
- **PE-18** priors: sitemap_products=0 [probe-20260914-pe18-3]
- **PE-19** priors: sitemap_products=1619 [probe-20260914-pe19-3]
- **PE-20** priors: sitemap_products=199354 [probe-20260914-pe20-3]
- **PE-21** priors: sitemap_products=0 [probe-20260914-pe21-3]
- **PE-22** priors: sitemap_products=0 [probe-20260912-pe22-2]
- **PE-23** priors: sitemap_products=0 [probe-20260914-pe23-3]
- **PE-25** priors: sitemap_products=0 [probe-20260914-pe25-3]
- **PE-26** priors: sitemap_products=0 [probe-20260914-pe26-3]
- **PE-27** priors: sitemap_products=0 [probe-20260914-pe27-3]
- **PE-28** priors: sitemap_products=0 [probe-20260914-pe28-3]
- **PE-29** priors: sitemap_products=4 [probe-20260914-pe29-3]
- **PE-30** priors: sitemap_products=60 [probe-20260914-pe30-3]
- **PE-32** priors: sitemap_products=0 [probe-20260914-pe32-3]
- **PE-33** priors: sitemap_products=1541 [probe-20260914-pe33-3]
- **PE-34** priors: sitemap_products=2 [probe-20260914-pe34-3]
- **PE-36** priors: sitemap_products=0 [probe-20260914-pe36-3]
- **PE-37** priors: sitemap_products=22 [probe-20260914-pe37-3]
- **PE-38** priors: sitemap_products=0 [probe-20260914-pe38-3]
- **PE-39** priors: sitemap_products=0 [probe-20260914-pe39-3]
- **PE-43** priors: sitemap_products=126929 [probe-20260914-pe43-3]
- **PE-44** priors: sitemap_products=0 [probe-20260914-pe44-3]
- **PE-55** priors: sitemap_products=0 [probe-20260914-pe55-3]
- **PE-57** priors: sitemap_products=0 [probe-20260914-pe57-2]
- **PE-59** priors: sitemap_products=0 [probe-20260914-pe59-2]
- **PE-60** priors: sitemap_products=0 [probe-20260914-pe60-2]
- **PE-61** priors: sitemap_products=0 [probe-20260914-pe61-2]
- **PE-62** priors: sitemap_products=0 [probe-20260914-pe62-2]
- **ST-1** priors: products_registered=1444290 [probe-20260914-st1manual-2]
- **ST-3** priors: producers_registered=3300 [probe-20260914-st3manual]
- **ST-6** priors: products_registered=40000 [probe-20260914-st6manual-2]
- **ST-7** priors: products_registered=71231 [probe-20260914-st7manual]



### Access-decision bridge

What a scraping go would buy versus its cost — qualitative, cited to the run evidence in this report (i14 bridge semantics, stripped of walk-floor inputs). No decision is taken here; this bridges the recon numbers to the follow-up options.

- Would buy: the tier (c) sources (AS-6, AS-7, CS-2, PE-53, ST-4) — size
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
| AS-10 | AS | 0 | — | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-as10manual-2 |
| AS-11 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-12 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-13 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-14 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-15 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-16 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-17 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-18 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-19 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-2 | AS | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-20 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-21 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-22 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-23 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-24 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-25 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-26 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-27 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-28 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-29 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-3 | AS | 1 | d | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-30 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-4 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-5 | AS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| AS-6 | AS | 1 | c | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-as6manual-2 |
| AS-7 | AS | 1 | c | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-as7manual-2 |
| AS-8 | AS | 0 | — | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-as8manual-2 |
| AS-9 | AS | 0 | — | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-as9manual-2 |
| CS-1 | CS | 0 | — | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-cs1-3 |
| CS-2 | CS | 1 | c | done | — | — | — | — | 2471311314 kg | 12211227434 eur | 2099166223.9999998 kg | 6221811666 eur | — | — | — | — | — | — | — | 278 count | 264 count | 228 count | 1 count | — | probe-20260912-cs2-10 |
| CS-3 | CS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CS-4 | CS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CS-5 | CS | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| LI-2 | LI | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| LI-3 | LI | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| LI-4 | LI | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| LI-5 | LI | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-1 | PE | 0 | — | done | — | — | — | — | — | — | — | — | 0 count | 0 count | 0 | — | — | — | — | — | — | — | — | — | probe-20260912-pe1-3 |
| PE-10 | PE | 1 | b | done | 2 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe10-3 |
| PE-11 | PE | 1 | b | done | 146 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe11-3 |
| PE-12 | PE | 1 | b | done | 9 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe12-3 |
| PE-13 | PE | 1 | b | done | 1953 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe13-3 |
| PE-14 | PE | 1 | b | done | 3 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe14-3 |
| PE-15 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe15-3 |
| PE-16 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe16-3 |
| PE-17 | PE | 1 | b | done | 0 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe17-3 |
| PE-18 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe18-3 |
| PE-19 | PE | 1 | b | done | 1619 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe19-3 |
| PE-2 | PE | 0 | — | blocked | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe2-3 |
| PE-20 | PE | 1 | b | done | 199354 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe20-3 |
| PE-21 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe21-3 |
| PE-22 | PE | 1 | b | blocked | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe22-3 |
| PE-23 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe23-3 |
| PE-24 | PE | 1 | d | failed | — | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe24-3 |
| PE-25 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe25-3 |
| PE-26 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe26-3 |
| PE-27 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe27-3 |
| PE-28 | PE | 1 | b | done | 0 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe28-3 |
| PE-29 | PE | 1 | b | done | 4 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe29-3 |
| PE-3 | PE | 0 | — | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-pe3-3 |
| PE-30 | PE | 1 | b | done | 60 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe30-3 |
| PE-31 | PE | 1 | d | blocked | — | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe31-3 |
| PE-32 | PE | 1 | b | done | 0 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe32-3 |
| PE-33 | PE | 1 | b | done | 1541 count | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe33-3 |
| PE-34 | PE | 1 | b | done | 2 count | 1 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe34-3 |
| PE-35 | PE | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe35-3 |
| PE-36 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe36-3 |
| PE-37 | PE | 1 | b | done | 22 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe37-3 |
| PE-38 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe38-3 |
| PE-39 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe39-3 |
| PE-4 | PE | 0 | — | done | — | — | — | — | — | — | — | — | 0 count | 0 count | 0 | — | — | — | — | — | — | — | — | — | probe-20260912-pe4-3 |
| PE-40 | PE | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe40-3 |
| PE-41 | PE | 1 | d | blocked | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe41-3 |
| PE-42 | PE | 1 | d | blocked | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe42-3 |
| PE-43 | PE | 1 | b | done | 126929 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe43-3 |
| PE-44 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe44-3 |
| PE-45 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-46 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-47 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-48 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-49 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-50 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-51 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-52 | PE | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PE-53 | PE | 1 | c | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe53-3 |
| PE-54 | PE | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe54-3 |
| PE-55 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe55-3 |
| PE-56 | PE | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe56-3 |
| PE-57 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe57-2 |
| PE-58 | PE | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe58-2 |
| PE-59 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe59-2 |
| PE-60 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe60-2 |
| PE-61 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe61-2 |
| PE-62 | PE | 1 | b | done | 0 count | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-pe62-2 |
| ST-1 | ST | 0 | — | done | — | — | 1444290 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-st1manual-2 |
| ST-2 | ST | 1 | d | failed | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260912-st2-7 |
| ST-3 | ST | 0 | — | done | — | — | — | 3300 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-st3manual |
| ST-4 | ST | 1 | c | done | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-st4manual-2 |
| ST-5 | ST | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ST-6 | ST | 0 | — | done | — | — | 40000 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-st6manual-2 |
| ST-7 | ST | 0 | — | done | — | — | 71231 | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | probe-20260914-st7manual |


## Capability profile

Per registered source, the source-level capability sounding-out (v0.2.1):
is an entry actually a real product per the study's model — (CN8 code,
manufacturer, manufacturer product-ident) — and at what volume and
depth? A source is a **real product source** when it exposes a
manufacturer field, a product-ident field, a non-`none` CN8-linkage
mechanism, and data depth >= 2. `—` = capability metric not recorded.

Preliminary N2 numerator (official registers, floor): sum of products_identifiable over the real-product sources below. Official registers are certified/declared subsets of the market, never a market total — a floor, cited to the run it comes from.

**N2 numerator (official registers, floor):** 17838 over 1 real-product source(s).

| source | class | active | run_key | status | identifiable | mfr | product-ident | cn8-linkage | depth | cn8-reachable | real product source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AS-1 | AS | 0 | — | — | — | — | — | — | — | — | no |
| AS-10 | AS | 0 | probe-20260914-as10-2 | done | — | — | — | manual | — | — | no |
| AS-11 | AS | 0 | probe-20260914-as11manual | done | — | — | — | — | — | — | no |
| AS-12 | AS | 0 | probe-20260914-as12manual | done | — | — | — | — | — | — | no |
| AS-13 | AS | 0 | probe-20260914-as13manual | done | — | — | — | — | — | — | no |
| AS-14 | AS | 0 | probe-20260914-as14manual | done | — | — | — | — | — | — | no |
| AS-15 | AS | 0 | probe-20260914-as15manual | done | — | — | — | — | — | — | no |
| AS-16 | AS | 0 | probe-20260914-as16manual | done | — | — | — | — | — | — | no |
| AS-17 | AS | 0 | probe-20260914-as17manual | done | — | — | — | — | — | — | no |
| AS-18 | AS | 0 | probe-20260914-as18manual | done | — | — | — | — | — | — | no |
| AS-19 | AS | 0 | probe-20260914-as19manual | done | — | — | — | — | — | — | no |
| AS-2 | AS | 1 | probe-20260914-as2-3 | done | 17838 count | 1 | 1 | category | 2 | 0 count | yes |
| AS-20 | AS | 0 | probe-20260914-as20manual | done | — | — | — | — | — | — | no |
| AS-21 | AS | 0 | probe-20260914-as21manual | done | — | — | — | — | — | — | no |
| AS-22 | AS | 0 | probe-20260914-as22manual | done | — | — | — | — | — | — | no |
| AS-23 | AS | 0 | probe-20260914-as23manual | done | — | — | — | — | — | — | no |
| AS-24 | AS | 0 | probe-20260914-as24manual | done | — | — | — | — | — | — | no |
| AS-25 | AS | 0 | probe-20260914-as25manual | done | — | — | — | — | — | — | no |
| AS-26 | AS | 0 | probe-20260914-as26manual | done | — | — | — | — | — | — | no |
| AS-27 | AS | 0 | probe-20260914-as27manual | done | — | — | — | — | — | — | no |
| AS-28 | AS | 0 | probe-20260914-as28manual | done | — | — | — | — | — | — | no |
| AS-29 | AS | 0 | probe-20260914-as29manual | done | — | — | — | — | — | — | no |
| AS-3 | AS | 1 | probe-20260914-as3-3 | done | — | — | — | manual | — | — | no |
| AS-30 | AS | 0 | probe-20260914-as30manual | done | — | — | — | — | — | — | no |
| AS-4 | AS | 0 | probe-20260914-as4manual | done | — | — | — | — | — | — | no |
| AS-5 | AS | 0 | probe-20260914-as5manual | done | — | — | — | — | — | — | no |
| AS-6 | AS | 1 | probe-20260914-as6-3 | done | — | — | — | manual | — | — | no |
| AS-7 | AS | 1 | probe-20260914-as7-3 | done | — | — | — | manual | — | — | no |
| AS-8 | AS | 0 | probe-20260914-as8-2 | done | — | — | — | manual | — | — | no |
| AS-9 | AS | 0 | probe-20260914-as9-2 | done | — | — | — | manual | — | — | no |
| CS-1 | CS | 0 | — | — | — | — | — | — | — | — | no |
| CS-2 | CS | 1 | probe-20260914-cs2-2 | done | — | — | — | — | — | — | no |
| CS-3 | CS | 0 | probe-20260914-cs3manual | done | — | — | — | — | — | — | no |
| CS-4 | CS | 0 | probe-20260914-cs4manual | done | — | — | — | — | — | — | no |
| CS-5 | CS | 0 | probe-20260914-cs5manual | done | — | — | — | — | — | — | no |
| LI-2 | LI | 0 | probe-20260914-li2manual | done | — | — | — | — | — | — | no |
| LI-3 | LI | 0 | probe-20260914-li3manual | done | — | — | — | — | — | — | no |
| LI-4 | LI | 0 | probe-20260914-li4manual | done | — | — | — | — | — | — | no |
| LI-5 | LI | 0 | probe-20260914-li5manual | done | — | — | — | — | — | — | no |
| PE-1 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-10 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-11 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-12 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-13 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-14 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-15 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-16 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-17 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-18 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-19 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-2 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-20 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-21 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-22 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-23 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-24 | PE | 1 | probe-20260914-pe24manual | done | — | — | — | — | — | — | no |
| PE-25 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-26 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-27 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-28 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-29 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-3 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-30 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-31 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-32 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-33 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-34 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-35 | PE | 1 | probe-20260914-pe35manual | done | — | — | — | — | — | — | no |
| PE-36 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-37 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-38 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-39 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-4 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-40 | PE | 1 | probe-20260914-pe40manual | done | — | — | — | — | — | — | no |
| PE-41 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-42 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-43 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-44 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-45 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-46 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-47 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-48 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-49 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-50 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-51 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-52 | PE | 0 | — | — | — | — | — | — | — | — | no |
| PE-53 | PE | 1 | probe-20260914-pe53manual | done | — | — | — | — | — | — | no |
| PE-54 | PE | 1 | probe-20260914-pe54manual | done | — | — | — | — | — | — | no |
| PE-55 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-56 | PE | 1 | probe-20260914-pe56manual | done | — | — | — | — | — | — | no |
| PE-57 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-58 | PE | 1 | probe-20260914-pe58manual | done | — | — | — | — | — | — | no |
| PE-59 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-60 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-61 | PE | 1 | — | — | — | — | — | — | — | — | no |
| PE-62 | PE | 1 | — | — | — | — | — | — | — | — | no |
| ST-1 | ST | 0 | probe-20260914-st1manual | done | — | — | — | — | — | — | no |
| ST-2 | ST | 1 | probe-20260914-st2manual | done | — | — | — | — | — | — | no |
| ST-3 | ST | 0 | — | — | — | — | — | — | — | — | no |
| ST-4 | ST | 1 | probe-20260914-st4-2 | done | — | — | — | — | — | — | no |
| ST-5 | ST | 0 | probe-20260914-st5manual | done | — | — | — | — | — | — | no |
| ST-6 | ST | 0 | — | — | — | — | — | — | — | — | no |
| ST-7 | ST | 0 | — | — | — | — | — | — | — | — | no |


## Execution log (latest census/recon run per source)


| source | run_key | status | started | finished | notes |
|---|---|---|---|---|---|
| AS-1 | probe-20260912-as1manual | done | 2026-09-12T09:38:25Z | 2026-09-12T09:38:25Z | — |
| AS-10 | probe-20260914-as10manual-2 | done | 2026-09-14T08:39:27Z | 2026-09-14T08:39:27Z | — |
| AS-6 | probe-20260914-as6manual-2 | done | 2026-09-14T08:39:20Z | 2026-09-14T08:39:20Z | — |
| AS-7 | probe-20260914-as7manual-2 | done | 2026-09-14T08:39:21Z | 2026-09-14T08:39:21Z | — |
| AS-8 | probe-20260914-as8manual-2 | done | 2026-09-14T08:39:21Z | 2026-09-14T08:39:21Z | — |
| AS-9 | probe-20260914-as9manual-2 | done | 2026-09-14T08:39:26Z | 2026-09-14T08:39:26Z | — |
| CS-1 | probe-20260912-cs1-3 | failed | 2026-09-12T04:52:10Z | 2026-09-12T04:52:16Z | https://swiss-impex.admin.ch/robots.txt: network error after retries |
| CS-2 | probe-20260912-cs2-10 | done | 2026-09-12T09:40:44Z | 2026-09-12T09:40:58Z | — |
| PE-1 | probe-20260912-pe1-3 | done | 2026-09-12T04:52:23Z | 2026-09-12T04:52:26Z | — |
| PE-10 | probe-20260914-pe10-3 | done | 2026-09-14T08:23:38Z | 2026-09-14T08:23:42Z | — |
| PE-11 | probe-20260914-pe11-3 | done | 2026-09-14T08:23:42Z | 2026-09-14T08:23:56Z | — |
| PE-12 | probe-20260914-pe12-3 | done | 2026-09-14T08:23:56Z | 2026-09-14T08:24:00Z | — |
| PE-13 | probe-20260914-pe13-3 | done | 2026-09-14T08:24:00Z | 2026-09-14T08:24:14Z | — |
| PE-14 | probe-20260914-pe14-3 | done | 2026-09-14T08:24:14Z | 2026-09-14T08:24:18Z | — |
| PE-15 | probe-20260914-pe15-3 | done | 2026-09-14T08:24:18Z | 2026-09-14T08:24:37Z | — |
| PE-16 | probe-20260914-pe16-3 | done | 2026-09-14T08:24:37Z | 2026-09-14T08:24:41Z | — |
| PE-17 | probe-20260914-pe17-3 | done | 2026-09-14T08:24:41Z | 2026-09-14T08:24:47Z | — |
| PE-18 | probe-20260914-pe18-3 | done | 2026-09-14T08:24:47Z | 2026-09-14T08:25:02Z | — |
| PE-19 | probe-20260914-pe19-3 | done | 2026-09-14T08:25:02Z | 2026-09-14T08:25:07Z | — |
| PE-2 | probe-20260912-pe2-3 | blocked | 2026-09-12T04:52:26Z | 2026-09-12T04:52:26Z | https://www.coop.ch/robots.txt: HTTP 403 |
| PE-20 | probe-20260914-pe20-3 | done | 2026-09-14T08:25:07Z | 2026-09-14T08:25:22Z | — |
| PE-21 | probe-20260914-pe21-3 | done | 2026-09-14T08:25:22Z | 2026-09-14T08:25:28Z | — |
| PE-22 | probe-20260914-pe22-3 | blocked | 2026-09-14T08:25:28Z | 2026-09-14T08:25:32Z | https://www.bauhaus.info/sitemap.xml: HTTP 403 |
| PE-23 | probe-20260914-pe23-3 | done | 2026-09-14T08:25:32Z | 2026-09-14T08:25:57Z | — |
| PE-24 | probe-20260914-pe24-3 | failed | 2026-09-14T08:25:57Z | 2026-09-14T08:26:15Z | https://www.diy.com/sitemap.xml: HTTP 503 after retries |
| PE-25 | probe-20260914-pe25-3 | done | 2026-09-14T08:26:15Z | 2026-09-14T08:26:19Z | — |
| PE-26 | probe-20260914-pe26-3 | done | 2026-09-14T08:26:19Z | 2026-09-14T08:26:33Z | — |
| PE-27 | probe-20260914-pe27-3 | done | 2026-09-14T08:26:33Z | 2026-09-14T08:26:40Z | — |
| PE-28 | probe-20260914-pe28-3 | done | 2026-09-14T08:26:40Z | 2026-09-14T08:26:44Z | — |
| PE-29 | probe-20260914-pe29-3 | done | 2026-09-14T08:26:44Z | 2026-09-14T08:26:59Z | — |
| PE-3 | probe-20260912-pe3-3 | failed | 2026-09-12T04:52:26Z | 2026-09-12T04:52:32Z | https://example.invalid/robots.txt: network error after retries |
| PE-30 | probe-20260914-pe30-3 | done | 2026-09-14T08:26:59Z | 2026-09-14T08:27:11Z | — |
| PE-31 | probe-20260914-pe31-3 | blocked | 2026-09-14T08:27:11Z | 2026-09-14T08:27:15Z | https://www.kremer-pigmente.com/sitemap.xml: HTTP 403 |
| PE-32 | probe-20260914-pe32-3 | done | 2026-09-14T08:27:15Z | 2026-09-14T08:27:20Z | — |
| PE-33 | probe-20260914-pe33-3 | done | 2026-09-14T08:27:20Z | 2026-09-14T08:27:35Z | — |
| PE-34 | probe-20260914-pe34-3 | done | 2026-09-14T08:27:35Z | 2026-09-14T08:27:39Z | — |
| PE-35 | probe-20260914-pe35-3 | failed | 2026-09-14T08:27:39Z | 2026-09-14T08:27:57Z | https://www.alpina-farben.de/sitemap.xml: network error after retries |
| PE-36 | probe-20260914-pe36-3 | done | 2026-09-14T08:27:57Z | 2026-09-14T08:28:12Z | — |
| PE-37 | probe-20260914-pe37-3 | done | 2026-09-14T08:28:12Z | 2026-09-14T08:28:16Z | — |
| PE-38 | probe-20260914-pe38-3 | done | 2026-09-14T08:28:16Z | 2026-09-14T08:28:30Z | — |
| PE-39 | probe-20260914-pe39-3 | done | 2026-09-14T08:28:30Z | 2026-09-14T08:28:35Z | — |
| PE-4 | probe-20260912-pe4-3 | done | 2026-09-12T04:52:32Z | 2026-09-12T04:52:34Z | — |
| PE-40 | probe-20260914-pe40-3 | failed | 2026-09-14T08:28:35Z | 2026-09-14T08:28:54Z | https://www.castorama.fr/sitemap.xml: HTTP 503 after retries |
| PE-41 | probe-20260914-pe41-3 | blocked | 2026-09-14T08:28:54Z | 2026-09-14T08:29:00Z | https://www.gamma.nl/sitemap.xml: persistent 429 after one capped backoff |
| PE-42 | probe-20260914-pe42-3 | blocked | 2026-09-14T08:29:00Z | 2026-09-14T08:29:04Z | https://www.praxis.nl/sitemap.xml: HTTP 403 |
| PE-43 | probe-20260914-pe43-3 | done | 2026-09-14T08:29:04Z | 2026-09-14T08:29:19Z | — |
| PE-44 | probe-20260914-pe44-3 | done | 2026-09-14T08:29:19Z | 2026-09-14T08:29:33Z | — |
| PE-53 | probe-20260914-pe53-3 | done | 2026-09-14T08:29:33Z | 2026-09-14T08:29:38Z | UnexpectedFormat: sitemap unparseable: undefined entity: line 9, column 164 |
| PE-54 | probe-20260914-pe54-3 | failed | 2026-09-14T08:29:38Z | 2026-09-14T08:30:23Z | https://www.boeroyachting.com/sitemap.xml: network error after retries |
| PE-55 | probe-20260914-pe55-3 | done | 2026-09-14T08:30:23Z | 2026-09-14T08:30:32Z | — |
| PE-56 | probe-20260914-pe56-3 | failed | 2026-09-14T08:30:32Z | 2026-09-14T08:30:50Z | https://www.de-ijssel-coatings.com/sitemap.xml: network error after retries |
| PE-57 | probe-20260914-pe57-2 | done | 2026-09-14T08:30:50Z | 2026-09-14T08:30:54Z | — |
| PE-58 | probe-20260914-pe58-2 | failed | 2026-09-14T08:30:54Z | 2026-09-14T08:31:13Z | https://www.talens.com/sitemap.xml: network error after retries |
| PE-59 | probe-20260914-pe59-2 | done | 2026-09-14T08:31:13Z | 2026-09-14T08:31:17Z | — |
| PE-60 | probe-20260914-pe60-2 | done | 2026-09-14T08:31:17Z | 2026-09-14T08:31:36Z | — |
| PE-61 | probe-20260914-pe61-2 | done | 2026-09-14T08:31:36Z | 2026-09-14T08:31:45Z | — |
| PE-62 | probe-20260914-pe62-2 | done | 2026-09-14T08:31:45Z | 2026-09-14T08:32:00Z | — |
| ST-1 | probe-20260914-st1manual-2 | done | 2026-09-14T07:09:38Z | 2026-09-14T07:09:38Z | — |
| ST-2 | probe-20260912-st2-7 | failed | 2026-09-12T08:40:14Z | 2026-09-12T08:41:50Z | http://spin2000.net/robots.txt: network error after retries |
| ST-3 | probe-20260914-st3manual | done | 2026-09-14T07:04:58Z | 2026-09-14T07:04:58Z | — |
| ST-4 | probe-20260914-st4manual-2 | done | 2026-09-14T08:39:27Z | 2026-09-14T08:39:27Z | — |
| ST-6 | probe-20260914-st6manual-2 | done | 2026-09-14T07:10:15Z | 2026-09-14T07:10:15Z | — |
| ST-7 | probe-20260914-st7manual | done | 2026-09-14T07:05:52Z | 2026-09-14T07:05:52Z | — |



## Sources


### AS-1 — CEPE (European paints association)

- identity: class AS · active no · tier — · verification open · https://www.cepe.org
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: producers_registered=800 [probe-20260912-as1manual]
- register note: producers_registered via manual record (member counts / national-association list); URL verified live 2026-09-12; candidate-row semantics nu3; v0.2.2: member-association rows AS-11+ enumerated from cepe.org/list-of-national-associations (pinned 2026-09-14)
- latest run: probe-20260912-as1manual (done)

### AS-10 — EPD Norway (EPD-Norge / EPD-Global)

- identity: class AS · active no · tier — · verification partially_verified · https://digi.epd-norge.no/
- access: robots — · terms — · rate limit — · free access —
- content: format EPD Norway (EPD-Global): digi portal live (per-EPD pages verified 2026-09-14); no bulk export pinned — count deferred · granularity — · coverage — · languages —
- counts:
- register note: public EPD database (digi portal verified live 2026-09-14 via Jotun EPD pages); export shape pinned at W2
- latest run: probe-20260914-as10manual-2 (done)

### AS-11 — FCiO (Austrian paints association)

- identity: class AS · active no · tier — · verification open · https://fcio.at
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org/list-of-national-associations (pinned 2026-09-14)

### AS-12 — IVP Coatings (Belgian paints association)

- identity: class AS · active no · tier — · verification open · https://ivp-coatings.be
- access: robots — · terms — · rate limit — · free access —
- content: format unreachable from desk egress (PHASE03 verification); member list deferred to crawl pass · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14); desk env could not reach (egress) — CEPE-pinned

### AS-13 — Dansk Industri — paint section (DK)

- identity: class AS · active no · tier — · verification open · https://danskindustri.dk
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-14 — Varieteollisuus (Finnish paints association)

- identity: class AS · active no · tier — · verification open · https://variteollisuus.fi
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-15 — FIPEC (French paints federation)

- identity: class AS · active no · tier — · verification open · https://fipec.org
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); strategy-named (v0.2.2 source-expansion table); listed_by=cepe.org national-associations list (2026-09-14)

### AS-16 — VdL (German paints association)

- identity: class AS · active no · tier — · verification open · https://wirsindfarbe.de
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); strategy-named (v0.2.2 source-expansion table); listed_by=cepe.org national-associations list (2026-09-14)

### AS-17 — VdMI (German printing-ink association)

- identity: class AS · active no · tier — · verification open · https://vdmi.de
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; printing inks — marginal; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-18 — Hellenic Coatings (GR)

- identity: class AS · active no · tier — · verification open · https://hellenicoatings.gr
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-19 — MAFEOSZ (Hungarian paints association)

- identity: class AS · active no · tier — · verification open · https://mafeosz.hu
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-2 — EU Ecolabel Product Catalogue (ECAT)

- identity: class AS · active yes · tier d · verification verified · https://data.europa.eu/data/datasets/eu-ecolabel-products
- access: robots — · terms — · rate limit — · free access —
- content: format HTML landing page — not a CSV/JSON export; export mechanics to confirm · granularity — · coverage — · languages —
- counts:
- register note: certified subset (non-exhaustive, licence holders register products); paints & varnishes group 044; CSV download + API (D3 official export); host data.europa.eu distinct from CS-2; v0.2.2 W1: full export ingest (88920 rows, group 044 filter) → staging

### AS-20 — IDSCA (Irish decorative paints association)

- identity: class AS · active no · tier — · verification open · https://idsca.ie
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-21 — AVISA (Italian paints association)

- identity: class AS · active no · tier — · verification open · https://avisa.federchimica.it
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-22 — Assovernici (Italian varnish makers)

- identity: class AS · active no · tier — · verification open · https://assovernici.it
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-23 — VVVF (Dutch paints association)

- identity: class AS · active no · tier — · verification open · https://vvvf.nl
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-24 — MALINGOGLAKK (Norwegian paints association)

- identity: class AS · active no · tier — · verification open · https://malingoglakk.no
- access: robots — · terms — · rate limit — · free access —
- content: format unreachable from desk egress (PHASE03 verification); member list deferred to crawl pass · granularity — · coverage — · languages —
- counts:
- register note: channel=association; EEA market; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14); URL unreachable from the desk env (egress) — CEPE-pinned

### AS-25 — PZPFiK (Polish paints association)

- identity: class AS · active no · tier — · verification open · https://pzpfik.pl
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-26 — APINTAS (Portuguese paints association)

- identity: class AS · active no · tier — · verification open · https://aptintas.pt
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-27 — AIVR (Romanian paints association)

- identity: class AS · active no · tier — · verification open · https://aivr.ro
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-28 — ASEFAPI (Spanish paints association)

- identity: class AS · active no · tier — · verification open · https://asefapi.es
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-29 — SVFF (Swedish paints association)

- identity: class AS · active no · tier — · verification open · https://sveff.se
- access: robots — · terms — · rate limit — · free access —
- content: format member-manufacturer list is the Q1 crawl target for the next pass; site reachable per PHASE03 desk check · granularity — · coverage — · languages —
- counts:
- register note: channel=association; member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-3 — Nordic Swan Ecolabel product database

- identity: class AS · active yes · tier d · verification verified · https://www.svanen.se/en/search-for-ecolabelled-products-and-services/
- access: robots — · terms — · rate limit — · free access — · access_blocked: Nordic Swan product search is a JS app (737 KB shell, no embedded data); CSV/Excel export not GET-able; browser session needed — count deferred
- content: format HTML landing page — not a CSV/JSON export; export mechanics to confirm · granularity — · coverage — · languages —
- counts:
- register note: paints & varnishes criterion 096; CSV/Excel export visible; host svanen.se distinct; export mechanics (GET vs form-POST) pinned at W1 — manual-record fallback built in

### AS-30 — EuACA (European artists' colours association)

- identity: class AS · active no · tier — · verification open · https://artists-colours.org
- access: robots — · terms — · rate limit — · free access —
- content: format artists-colours association (annex 3213 channel); member list deferred to crawl pass · granularity — · coverage — · languages —
- counts:
- register note: channel=association; artists' colours (3213 census annex); member counts via manual record (W4); listed_by=cepe.org national-associations list (2026-09-14)

### AS-4 — Blue Angel (Blauer Engel)

- identity: class AS · active no · tier — · verification partially_verified · https://www.blauer-engel.de/en/products
- access: robots — · terms — · rate limit — · free access —
- content: format product database is a web app; XLSX export mechanics to pin (deferred); DE-UZ 118 mark list pending · granularity — · coverage — · languages —
- counts:
- register note: XLSX export; pure-Python reader (xlsx.py) ready; sheet layout pinned at W1; characterize via probe record --mode capability

### AS-5 — INIES (French EPD register)

- identity: class AS · active no · tier — · verification partially_verified · https://www.inies.fr/
- access: robots — · terms — · rate limit — · free access —
- content: format INIES declarations portal (FR law-mandated); bulk access login-gated — count deferred · granularity — · coverage — · languages —
- counts:
- register note: auth-gated; manual-record this unit; account registration = TODOS.md user action; optional API probe in a later pass

### AS-6 — IBU (Institut Bauen und Umwelt EPD)

- identity: class AS · active yes · tier c · verification partially_verified · https://ibu-epd.com/en/
- access: robots — · terms — · rate limit — · free access —
- content: format IBU EPD: register is a web app; per-product EPD PDFs downloadable; no bulk export pinned — count deferred to a browser pass · granularity — · coverage — · languages —
- counts:
- register note: published EPD declarations; EPD file downloads; export shape pinned at W2 (real format check, not landing-page-only)
- latest run: probe-20260914-as6manual-2 (done)

### AS-7 — environdec (International EPD System)

- identity: class AS · active yes · tier c · verification partially_verified · https://environdec.com/library
- access: robots — · terms — · rate limit — · free access —
- content: format environdec: EPD library is a web app; no bulk export pinned; the v0.2.1 unrecorded library-size claim is hereby softened to 'not obtained' (provenance repair) · granularity — · coverage — · languages —
- counts:
- register note: published EPDs; library with downloads; export shape pinned at W2; the unrecorded claim from v0.2.1 recorded-or-softened here (provenance repair)
- latest run: probe-20260914-as7manual-2 (done)

### AS-8 — NF Environnement (AFNOR Certification)

- identity: class AS · active no · tier — · verification open · https://certification.afnor.org/marque/nf-environnement
- access: robots — · terms — · rate limit — · free access —
- content: format NF Environnement: certified-product lists are per-criteria PDFs (NF130 peintures); no bulk CSV — count deferred to a PDF pass · granularity — · coverage — · languages —
- counts:
- register note: NF130 peintures/vernis; certified-product PDF lists; export shape pinned at W2; v0.2.2 addition (strategy source-expansion table)
- latest run: probe-20260914-as8manual-2 (done)

### AS-9 — natureplus quality label

- identity: class AS · active no · tier — · verification open · https://www.natureplus.org
- access: robots — · terms — · rate limit — · free access —
- content: format natureplus: certified-product database is a web app; no bulk export pinned — count deferred · granularity — · coverage — · languages —
- counts:
- register note: building products incl. coatings; certified-product database; export shape pinned at W2
- latest run: probe-20260914-as9manual-2 (done)

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
- register note: EU27 extra-EU trade; CN8 x partner x year; full-year import aggregation (nu2): trade_kg/eur_hs3208/3209; v0.2.2 W1: per-CN8 batches (13 codes x flows) via jsonstat module
- latest run: probe-20260912-cs2-10 (done)

### CS-3 — Destatis GENESIS (DE foreign trade)

- identity: class CS · active no · tier — · verification open · https://www-genesis.destatis.de
- access: robots — · terms — · rate limit — · free access —
- content: format GENESIS-Online bulk API (guest access) exists; query shape + CN8 export pin deferred to the next pass · granularity — · coverage — · languages —
- counts:
- register note: German foreign trade 3208/3209 (national cross-check); manual-web characterization at W1; national cross-check rows v0.2.2

### CS-4 — Datacomex (ES foreign trade)

- identity: class CS · active no · tier — · verification open · https://datacomex.comercio.es
- access: robots — · terms — · rate limit — · free access —
- content: format Coeweb unreachable from desk egress (PHASE03 verification); IT CN8 trade deferred · granularity — · coverage — · languages —
- counts:
- register note: Spanish foreign trade 3208/3209 (national cross-check); manual-web characterization at W1

### CS-5 — Coeweb (IT foreign trade)

- identity: class CS · active no · tier — · verification open · https://coeweb.istat.it
- access: robots — · terms — · rate limit — · free access —
- content: format Datacomex web app; API shape to pin — deferred to the next pass · granularity — · coverage — · languages —
- counts:
- register note: Italian foreign trade 3208/3209 (national cross-check); manual-web characterization at W1; desk env could not reach (egress) — verify at W1

### LI-2 — IPEN lead-paint campaign

- identity: class LI · active no · tier — · verification open · https://ipen.org/our-work/lead-paint
- access: robots — · terms — · rate limit — · free access — · access_blocked: 403-walled from desk egress; role = context citation (lead-paint status reports); no count expected
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: lead-paint prevalence studies; country database; product counts as context/prior only (D27 product-data-only; no legal content)

### LI-3 — UNEP/SAICM lead paint status

- identity: class LI · active no · tier — · verification open · https://saicm.org
- access: robots — · terms — · rate limit — · free access —
- content: format context citation (lead paint law status per country); no count expected · granularity — · coverage — · languages —
- counts:
- register note: global lead-paint law status reports; context/prior only (D27)

### LI-4 — EEA (European Environment Agency)

- identity: class LI · active no · tier — · verification open · https://www.eea.europa.eu
- access: robots — · terms — · rate limit — · free access —
- content: format context citation (EU environment statistics); no count expected · granularity — · coverage — · languages —
- counts:
- register note: environmental indicators touching paints/metals; context only (D27)

### LI-5 — ILZSG (lead & zinc study group)

- identity: class LI · active no · tier — · verification open · https://ilzsg.org
- access: robots — · terms — · rate limit — · free access —
- content: format context citation (lead/zinc market statistics); no count expected · granularity — · coverage — · languages —
- counts:
- register note: lead metal supply/demand statistics; context/prior only (D27)

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
- priors: sitemap_products=2 [probe-20260914-pe10-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe10-3 (done)

### PE-11 — PPG

- identity: class PE · active yes · tier b · verification open · https://www.ppg.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=146 [probe-20260914-pe11-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe11-3 (done)

### PE-12 — Sherwin-Williams

- identity: class PE · active yes · tier b · verification open · https://www.sherwin-williams.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=9 [probe-20260914-pe12-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe12-3 (done)

### PE-13 — Jotun

- identity: class PE · active yes · tier b · verification open · https://www.jotun.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=1953 [probe-20260914-pe13-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe13-3 (done)

### PE-14 — Hempel

- identity: class PE · active yes · tier b · verification open · https://www.hempel.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=3 [probe-20260914-pe14-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe14-3 (done)

### PE-15 — Sika

- identity: class PE · active yes · tier b · verification open · https://www.sika.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe15-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe15-3 (done)

### PE-16 — Sto

- identity: class PE · active yes · tier b · verification open · https://www.sto.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe16-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe16-3 (done)

### PE-17 — Caparol (DAW)

- identity: class PE · active yes · tier b · verification open · https://www.caparol.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe17-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe17-3 (done)

### PE-18 — Tikkurila

- identity: class PE · active yes · tier b · verification open · https://www.tikkurila.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe18-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe18-3 (done)

### PE-19 — Teknos

- identity: class PE · active yes · tier b · verification open · https://www.teknos.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=1619 [probe-20260914-pe19-3]
- register note: channel=mfr; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MFR<=12
- latest run: probe-20260914-pe19-3 (done)

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
- priors: sitemap_products=199354 [probe-20260914-pe20-3]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe20-3 (done)

### PE-21 — OBI DE

- identity: class PE · active yes · tier b · verification open · https://www.obi.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe21-3]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe21-3 (done)

### PE-22 — Bauhaus DE

- identity: class PE · active yes · tier b · verification open · https://www.bauhaus.info
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260912-pe22-2]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=10 (widened v0.2.2); URL corrected 2026-09-12 (bauhaus.de resolves to Bauhaus-Archiv museum)
- latest run: probe-20260914-pe22-3 (blocked; notes: https://www.bauhaus.info/sitemap.xml: HTTP 403)

### PE-23 — Leroy Merlin FR

- identity: class PE · active yes · tier b · verification open · https://www.leroymerlin.fr
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe23-3]
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe23-3 (done)

### PE-24 — B&Q (diy.com)

- identity: class PE · active yes · tier d · verification open · https://www.diy.com
- access: robots — · terms — · rate limit — · free access —
- content: format sitemap recon deferred: timed out twice from desk egress · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe24-3 (failed; notes: https://www.diy.com/sitemap.xml: HTTP 503 after retries)

### PE-25 — Epifanes

- identity: class PE · active yes · tier b · verification open · https://www.epifanes.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe25-3]
- register note: channel=marine; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MARINE<=10 (widened v0.2.2)
- latest run: probe-20260914-pe25-3 (done)

### PE-26 — SVB

- identity: class PE · active yes · tier b · verification open · https://www.svb.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe26-3]
- register note: channel=marine; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MARINE<=10 (widened v0.2.2)
- latest run: probe-20260914-pe26-3 (done)

### PE-27 — Toplicht

- identity: class PE · active yes · tier b · verification open · https://www.toplicht.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe27-3]
- register note: channel=marine; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap MARINE<=10 (widened v0.2.2)
- latest run: probe-20260914-pe27-3 (done)

### PE-28 — Raseglarhuset

- identity: class PE · active yes · tier b · verification open · https://www.raseglarhuset.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe28-3]
- register note: channel=marine; listed_by=PE-4 seed note (BRAVA SE); listed_date=2026-09-12; inclusion=cap MARINE<=10 (widened v0.2.2)
- latest run: probe-20260914-pe28-3 (done)

### PE-29 — Old Holland

- identity: class PE · active yes · tier b · verification open · https://www.oldholland.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=4 [probe-20260914-pe29-3]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe29-3 (done)

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
- priors: sitemap_products=60 [probe-20260914-pe30-3]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe30-3 (done)

### PE-31 — Kremer Pigmente

- identity: class PE · active yes · tier d · verification open · https://www.kremer-pigmente.com
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe31-3 (blocked; notes: https://www.kremer-pigmente.com/sitemap.xml: HTTP 403)

### PE-32 — Michael Harding

- identity: class PE · active yes · tier b · verification open · https://www.michaelharding.co.uk
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe32-3]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe32-3 (done)

### PE-33 — Winsor & Newton

- identity: class PE · active yes · tier b · verification open · https://www.winsornewton.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=1541 [probe-20260914-pe33-3]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe33-3 (done)

### PE-34 — Sennelier

- identity: class PE · active yes · tier b · verification open · https://www.sennelier.fr
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=2 [probe-20260914-pe34-3]
- register note: channel=art; listed_by=v0.1.1 seed list; listed_date=2026-09-12; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe34-3 (done)

### PE-35 — Alpina

- identity: class PE · active yes · tier d · verification open · https://www.alpina-farben.de
- access: robots — · terms — · rate limit — · free access —
- content: format sitemap recon deferred: connection refused twice from desk egress · granularity — · coverage — · languages —
- counts:
- register note: channel=mfr; listed_by=DATA_SOURCE.md tier A (brand site); listed_date=2026-09-14; inclusion=cap MFR<=40 (widened v0.2.2); desk env could not reach (egress) — verify at W3
- latest run: probe-20260914-pe35-3 (failed; notes: https://www.alpina-farben.de/sitemap.xml: network error after retries)

### PE-36 — Farrow & Ball

- identity: class PE · active yes · tier b · verification open · https://www.farrow-ball.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe36-3]
- register note: channel=mfr; listed_by=DATA_SOURCE.md tier A; listed_date=2026-09-14; inclusion=cap MFR<=40 (widened v0.2.2)
- latest run: probe-20260914-pe36-3 (done)

### PE-37 — Beckers Group

- identity: class PE · active yes · tier b · verification open · https://www.beckers-group.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=22 [probe-20260914-pe37-3]
- register note: channel=mfr; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; inclusion=cap MFR<=40
- latest run: probe-20260914-pe37-3 (done)

### PE-38 — Flügger

- identity: class PE · active yes · tier b · verification open · https://www.flugger.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe38-3]
- register note: channel=mfr; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; inclusion=cap MFR<=40
- latest run: probe-20260914-pe38-3 (done)

### PE-39 — Rust-Oleum

- identity: class PE · active yes · tier b · verification open · https://www.rustoleum.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe39-3]
- register note: channel=mfr; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; inclusion=cap MFR<=40
- latest run: probe-20260914-pe39-3 (done)

### PE-4 — Marine chandlers & art-supply shops (seed)

- identity: class PE · active no · tier — · verification partially_verified · https://www.toplicht.de
- access: robots allowed · terms link present: https://www.toplicht.de/informationen/agb/ · rate limit unknown — polite default <= 1 req / 2 s · free access 1
- content: format — · granularity — · coverage — · languages ["de", "en", "nl"]
- counts: walk budget: within budget
- register note: superseded by per-site rows PE-25+ (v0.2.0 nu6); sites live on as PE-26/PE-27/PE-29+
- latest run: probe-20260912-pe4-3 (done)

### PE-40 — Castorama FR

- identity: class PE · active yes · tier d · verification open · https://www.castorama.fr
- access: robots — · terms — · rate limit — · free access —
- content: format sitemap recon deferred: timed out twice from desk egress · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=DATA_SOURCE.md tier C; listed_date=2026-09-14; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe40-3 (failed; notes: https://www.castorama.fr/sitemap.xml: HTTP 503 after retries)

### PE-41 — Gamma NL

- identity: class PE · active yes · tier d · verification open · https://www.gamma.nl
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=DATA_SOURCE.md tier C; listed_date=2026-09-14; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe41-3 (blocked; notes: https://www.gamma.nl/sitemap.xml: persistent 429 after one capped backoff)

### PE-42 — Praxis NL

- identity: class PE · active yes · tier d · verification open · https://www.praxis.nl
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=DATA_SOURCE.md tier C; listed_date=2026-09-14; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe42-3 (blocked; notes: https://www.praxis.nl/sitemap.xml: HTTP 403)

### PE-43 — Toom DE

- identity: class PE · active yes · tier b · verification open · https://www.toom.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=126929 [probe-20260914-pe43-3]
- register note: channel=diy; listed_by=DATA_SOURCE.md tier C; listed_date=2026-09-14; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe43-3 (done)

### PE-44 — Hagebau DE

- identity: class PE · active yes · tier b · verification open · https://www.hagebau.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe44-3]
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; inclusion=cap EU-DIY<=10 (widened v0.2.2)
- latest run: probe-20260914-pe44-3 (done)

### PE-45 — Hellweg DE

- identity: class PE · active no · tier — · verification open · https://www.hellweg.de
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the DIY=10 cap (W3 selects the active subset)

### PE-46 — Bricomarché FR

- identity: class PE · active no · tier — · verification open · https://www.bricomarche.fr
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the DIY cap

### PE-47 — Bauhaus AT

- identity: class PE · active no · tier — · verification open · https://www.bauhaus.at
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the DIY cap

### PE-48 — Hornbach AT

- identity: class PE · active no · tier — · verification open · https://www.hornbach.at
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the DIY cap

### PE-49 — OBI AT

- identity: class PE · active no · tier — · verification open · https://obi-at.at
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; URL unverified (desk); listed_date=2026-09-14; enumerated, beyond the DIY cap

### PE-50 — K-Rauta FI

- identity: class PE · active no · tier — · verification open · https://www.k-rauta.fi
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the DIY cap

### PE-51 — Byggmax SE

- identity: class PE · active no · tier — · verification open · https://www.byggmax.se
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the DIY cap

### PE-52 — Biltema (SE/EEA)

- identity: class PE · active no · tier — · verification open · https://www.biltema.se
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: channel=diy+marine; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; enumerated, beyond the caps

### PE-53 — Veneziani (Boero Group)

- identity: class PE · active yes · tier c · verification open · https://www.veneziani.it
- access: robots allowed · terms — · rate limit — · free access —
- content: format sitemap unparseable: undefined entity: line 9, column 164 · granularity — · coverage — · languages —
- counts:
- register note: channel=marine; listed_by=DATA_SOURCE.md tier B (lead-relevant niche); listed_date=2026-09-14; inclusion=cap MARINE<=10 (widened v0.2.2)
- latest run: probe-20260914-pe53-3 (done; notes: UnexpectedFormat: sitemap unparseable: undefined entity: line 9, column 164)

### PE-54 — Boero Yachting

- identity: class PE · active yes · tier d · verification open · https://www.boeroyachting.com
- access: robots — · terms — · rate limit — · free access —
- content: format sitemap recon deferred: connection refused twice from desk egress · granularity — · coverage — · languages —
- counts:
- register note: channel=marine; listed_by=DATA_SOURCE.md tier B; listed_date=2026-09-14; inclusion=cap MARINE<=10 (widened v0.2.2); desk env could not reach (egress) — verify at W3
- latest run: probe-20260914-pe54-3 (failed; notes: https://www.boeroyachting.com/sitemap.xml: network error after retries)

### PE-55 — Seajet

- identity: class PE · active yes · tier b · verification open · https://www.seajetpaint.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe55-3]
- register note: channel=marine; listed_by=DATA_SOURCE.md tier B; listed_date=2026-09-14; inclusion=cap MARINE<=10 (widened v0.2.2)
- latest run: probe-20260914-pe55-3 (done)

### PE-56 — De IJssel Coatings

- identity: class PE · active yes · tier d · verification open · https://www.de-ijssel-coatings.com
- access: robots — · terms — · rate limit — · free access —
- content: format sitemap recon deferred: connection refused twice from desk egress · granularity — · coverage — · languages —
- counts:
- register note: channel=marine; listed_by=DATA_SOURCE.md tier B; URL unverified (desk); desk env could not reach (egress) — verify at W3; listed_date=2026-09-14; inclusion=cap MARINE<=10
- latest run: probe-20260914-pe56-3 (failed; notes: https://www.de-ijssel-coatings.com/sitemap.xml: network error after retries)

### PE-57 — Schmincke

- identity: class PE · active yes · tier b · verification open · https://www.schmincke.de
- access: robots allow-all (404/empty) · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe57-2]
- register note: channel=art; listed_by=DATA_SOURCE.md tier B (artists' colours); listed_date=2026-09-14; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe57-2 (done)

### PE-58 — Royal Talens

- identity: class PE · active yes · tier d · verification open · https://www.talens.com
- access: robots — · terms — · rate limit — · free access —
- content: format sitemap recon deferred: connection refused twice from desk egress · granularity — · coverage — · languages —
- counts:
- register note: channel=art; listed_by=DATA_SOURCE.md tier B; listed_date=2026-09-14; inclusion=cap ART<=15 (widened v0.2.2); desk env could not reach (egress) — verify at W3
- latest run: probe-20260914-pe58-2 (failed; notes: https://www.talens.com/sitemap.xml: network error after retries)

### PE-59 — Maimeri

- identity: class PE · active yes · tier b · verification open · https://www.maimeri.it
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe59-2]
- register note: channel=art; listed_by=DATA_SOURCE.md tier B; listed_date=2026-09-14; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe59-2 (done)

### PE-60 — Blockx

- identity: class PE · active yes · tier b · verification open · https://www.blockx.be
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe60-2]
- register note: channel=art; listed_by=DATA_SOURCE.md tier B; URL unverified (desk); listed_date=2026-09-14; inclusion=cap ART<=15
- latest run: probe-20260914-pe60-2 (done)

### PE-61 — Gerstaecker

- identity: class PE · active yes · tier b · verification open · https://www.gerstaecker.de
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe61-2]
- register note: channel=art; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe61-2 (done)

### PE-62 — Boesner

- identity: class PE · active yes · tier b · verification open · https://www.boesner.com
- access: robots allowed · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: sitemap_products=0 [probe-20260914-pe62-2]
- register note: channel=art; listed_by=v0.2.2 desk enumeration; listed_date=2026-09-14; inclusion=cap ART<=15 (widened v0.2.2)
- latest run: probe-20260914-pe62-2 (done)

### ST-1 — ECHA PCN statistics

- identity: class ST · active no · tier — · verification open · https://echa.europa.eu
- access: robots — · terms — · rate limit — · free access —
- content: format ECHA PCN format statistics (dossier counts): figure not obtained this unit; page pin deferred · granularity — · coverage — · languages —
- counts:
- priors: products_registered=1444290 [probe-20260914-st1manual-2]
- register note: formulation counts (hazardous mixtures); manual-web via probe record (locate aggregates) - active=0 per ENG review A1
- latest run: probe-20260914-st1manual-2 (done)

### ST-2 — Nordic SPIN (DK/SE/NO/FI)

- identity: class ST · active yes · tier d · verification partially_verified · http://spin2000.net/?page_id=54
- access: robots — · terms — · rate limit — · free access —
- content: format SPIN substance statistics: product-number figure not obtained this unit; page pin deferred · granularity — · coverage — · languages —
- counts:
- register note: preparation counts, lead-CAS incidence; register URL = DB download page ?page_id=54 (od9 fix); extraction path OPEN (mdbtools)
- latest run: probe-20260912-st2-7 (failed; notes: http://spin2000.net/robots.txt: network error after retries)

### ST-3 — Eurostat PRODCOM / SBS

- identity: class ST · active no · tier — · verification verified · https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: producers_registered=3300 [probe-20260914-st3manual]
- register note: NACE 20.30 production values/producer counts; producers_registered via manual record this unit; full PRODCOM/SBS integration deferred (TODOS.md)
- latest run: probe-20260914-st3manual (done)

### ST-4 — Eurostat PRODCOM annual production (DS-059358)

- identity: class ST · active yes · tier c · verification open · https://ec.europa.eu/eurostat/web/prodcom
- access: robots allowed · terms — · rate limit — · free access 1
- content: format PRODCOM: dedicated API not pinnable by desk probing (dissemination API 404 for DS-059358/DS-066342; prodcom web app JS-rendered); bulk URL + layout pin deferred to the API docs (next pass); SBS producer counts ride ST-3 · granularity — · coverage — · languages — · extraction path: mdb-export exit 1: option parsing failed: Unknown option -1
Usage:
  mdb-export [OPTION…] <file> <table> - export data from MDB file

Help Options:
  -h, --help                        Show help options

Application Opti
- counts:
- register note: production values for paints (NACE 20.30); bulk TSV sidesteps the dissemination-API size limit (413 observed 2026-09-14); NACE-to-CN8 via the official correspondence, NACE-proxy fallback with caveat (design c5); exact bulk-URL pinned at W1
- latest run: probe-20260914-st4manual-2 (done)

### ST-5 — KEMI Swedish Products Register statistics

- identity: class ST · active no · tier — · verification open · https://www.kemi.se
- access: robots — · terms — · rate limit — · free access —
- content: format KEMI Swedish Products Register statistics: notified-product figure not obtained this unit; page pin deferred · granularity — · coverage — · languages —
- counts:
- register note: Swedish products-register public statistics (product counts per use category); verify-first note (strategy OPEN); manual-record either way (W2)

### ST-6 — Danish AT "Kemiske produkter og stoffer i tal" (CKAN)

- identity: class ST · active no · tier — · verification verified · https://datavejviser-indtastning.digst.govcloud.dk/dataset/kemiske-produkter-og-stoffer-i-tal
- access: robots — · terms — · rate limit — · free access —
- content: format aggregates only (Power BI embed; no machine-readable export) — extraction fallback per tr3 · granularity — · coverage — · languages —
- counts:
- priors: products_registered=40000 [probe-20260914-st6manual-2]
- register note: aggregate product counts by branch/function/hazard-label/year, coverage 2014-2022 (modified 2023-10-06); verify-shape-first verdict (v0.2.3 PHASE02 gate): aggregates ONLY, exposed via an embedded Power BI report (publicdata.at.dk), CKAN resources have no download URL — no product rows to stage; extraction fallback per tr3: paint function counts land as manual records; landing page https://at.dk/arbejdsmiljoe-i-tal/kemiske-produkter-i-tal/
- latest run: probe-20260914-st6manual-2 (done)

### ST-7 — Swedish PC "Echo" notification statistics (BfR-Akademie 2022 deck)

- identity: class ST · active no · tier — · verification open · https://www.bfr-akademie.de/media/wysiwyg/2022/NKPM2022/product-notifications-according-to-article-45-clp-in-sweden.pdf
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- priors: products_registered=71231 [probe-20260914-st7manual]
- register note: poison-centre notification counts by EuPCS category (deck verified 2026-09-14: pc-pnt-2 decorative 36843, pc-pnt-3 protective/functional 23822, pc-pnt-oth other paints/coatings 10566; Echo initial 333591, update 91333, withdrawal 1718, 2022-09-15); semantics RESOLVED (v0.2.3 PHASE03): CLP Art.45 PCN + voluntary PC submissions — NOT KemI register products; paints+coatings sum 71231
- latest run: probe-20260914-st7manual (done)

## Legend

- “—” = metric absent (source not queried for it); 0 = queried, empty result.
- Metric values cite the run_key of the done run they come from.
- Status reflects the latest census/recon run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.
- Access tiers (active sources): (a) dataset/register access counted · (b) sitemap-visible counted · (c) visible but uncounted without scraping · (d) blocked/unknown. N2 sums tiers (a)+(b) only.
- N3 pairs doc-bearing counts with the site count of sds_library_visible = 1 — a site count, not a product count (labeled as such).
- sitemap_products is a recon floor (robots-compliant, counts only; index/size caps render it partial — “floor partial” in the notes).
- records_hs*/trade_* columns are volume context: tariff-line flows, not products (D28 grain rule); trade quantities carry the API's supplementary unit (see finding notes).
- Inactive register rows never enter N2/N3 sums; counted-but-excluded sources are listed explicitly.

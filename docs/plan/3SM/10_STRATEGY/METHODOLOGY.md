---
unit: v0.1.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-12
---

# Methodology — population, sampling, corroboration

## Abstract

This document explains how the study measures the market — using only
documents, at minimal cost, with no laboratory. The setting: paints under
customs headings 3208 (solvent-borne) and 3209 (water-borne) on the **EU
market** (the primary object, with an implicit expectation of none), plus a
complete count of artists' oil colours (heading 3213). In plain terms:
Swiss trade statistics show what is imported, from
where and in what quantities; producer and retailer catalogues — collected
systematically from their websites and de-duplicated — provide the list of
products to draw from (the "sampling frame"); because no official register
counts paint products, the size of that list is estimated by combining
several independent sources (triangulation). The market is divided into
eight groups, each split by origin; a few hundred products per group are
checked via their safety data sheets (SDS — the standardized
hazard-information sheets that accompany professional chemical products).
A key regulatory fact shapes the design: Switzerland bans paints with
≥ 0.01% total lead (100 ppm — parts per million), while EU safety data
sheets only declare classified lead compounds from 0.1% — so the method
has a blind spot exactly at the regulatory seam, which is stated openly in
all results. Suspected findings are corroborated — cross-checked against
independent documents about the same product — instead of being tested in
a lab. Technical terms are glossed at first use and summarized in the
glossary below; the implementation-mapping table near the end is for the
engineering reader and may be skipped.

## DECISIONS (condensed; authoritative list in MASTER.md)

- Unit of analysis = base formulation; SKU counting rejected (MASTER D2).
- Precision-based stratified sampling, ~2,000–3,000 products, FPC where
  frames are small (MASTER D4).
- Corroboration instead of laboratory — hard constraint (MASTER D7).
- HS 3213 artists' colours as full census annex, not a sample (MASTER D13).
- Implementation: `leadhs` CLI pipeline per ARCHITECTURE.md; data sources
  per DATA_SOURCE.md; schema per DATA_MODEL.md.

## OPEN ITEMS

- EZV/swiss-impex granularity and free access (Phase 0) — gates frame
  weighting by origin; probe target of unit v0.1.1.
- Population triangulation inputs to be pinned (Phase 0) — provisional
  counts arrive with the v0.1.1 source census.
- Multilingual SDS parsing and dedup rules — calibrate in Phase-1 pilot.

## Terms used (plain-language glossary)

- **SDS (safety data sheet / Sicherheitsdatenblatt / fiche de données de
  sécurité):** the standardized information sheet that must accompany
  professional chemical products in the EU and Switzerland; Section 3
  "Composition" lists classified hazardous ingredients from 0.1% by weight.
- **Formulation (base formulation):** one paint recipe, however many colour
  shades or tin sizes are sold from it — the study's unit of counting.
- **SKU (stock keeping unit):** one shop item (colour × tin size × brand);
  counting SKUs would inflate the numbers 10–1000× without adding
  information — rejected.
- **CN8 / HS code:** the 8-digit customs tariff number under which a
  consignment is declared (3208 solvent-borne paints, 3209 water-borne,
  3213 artists' colours); "CN" = Combined Nomenclature, the EU tariff
  nomenclature.
- **ppm:** parts per million by weight (10 000 ppm = 1%).
- **Sampling frame:** the list of products from which the sample is drawn —
  here: catalogues, de-duplicated to formulation level.
- **Stratum (plural: strata) / stratified sampling:** a market segment with
  a similar lead expectation; sampling within each segment separately, so
  rare segments are not drowned out.
- **Census:** a complete count of every member of a (small) population, as
  opposed to a sample — used for artists' oil colours (3213).
- **Prevalence:** the share of products in a group that contain lead.
- **Margin of error / 95% confidence interval:** how close a share measured
  on a sample is expected to be to the true share; the interval contains
  the true value in 95 of 100 such samples.
- **FPC (finite population correction):** a small discount on the sample
  size when the population itself is small.
- **Triangulation:** estimating one quantity by combining several
  independent sources that each see part of it.
- **Corroboration:** cross-checking a suspected finding against independent
  documents about the same product.
- **PCN (poison centre notification):** the EU register of hazardous
  mixtures notified to poison centres — formulation-level, but covering
  only hazardous mixtures and not openly published.
- **SPIN:** the Nordic product-register database (DK/SE/NO/FI); reports
  counts of preparations containing a given substance.
- **UFI:** a 16-character code on an EU SDS that identifies the specific
  formulation to poison centres.
- **NACE 20.30:** the statistical classification code for "manufacture of
  paints, varnishes and similar coatings".

## Regulatory frame (background)

- **Cassis de Dijon (CH — autonomous, not bilateral):** products lawfully
  marketed in the EU/EEA may be placed on the Swiss market without Swiss
  re-approval (THG Art. 16a, autonomously adopted 1 July 2010; one of
  three THG instruments — MRAs under THG Art. 14 are separate and out of
  scope). Exceptions (Federal Council; THG Art. 16a Abs. 2 lit. e i.V.m.
  Art. 4 Abs. 3–4: overriding public interests, e.g. health protection),
  defined at the principle's inception, are catalogued in VIPaV
  (SR 946.513.8) Art. 2; **Bst. a Ziff. 1 = lead-containing paints and
  varnishes and treated articles (referring to ChemRRV Anhang 2.8)** — in
  force since 2010, still listed in the SECO Negativliste of 1 Jan 2026.
  Institutional chain: requester/owner = BBL (commissioning context
  2026-09-10; verify before naming in deliverables), responsible for
  implementation, monitoring, revision; enforcement authority BAFU;
  **SECO reviews the entire exception catalogue every five years**
  (VIPaV Art. 3; 2023: keep; next ~2028); list-keeping statutory basis
  THG Art. 31 Abs. 2 (verified, Lexaris SR 946.51). The study supplies
  the decision basis within that cycle, outcome-neutral.
- **Swiss substance ban:** ChemRRV Anhang 2.8 (2005 wording; current text
  OPEN) defines lead paints as those with total Pb ≥ 0.01% (100 ppm) and
  bans placing them (and treated articles) on the market — stricter than the
  EU, which bans only lead carbonates/sulfates *in paints* (Annex XVII 16/17)
  and ended lawful lead-chromate supply via authorisation refusal (17 Mar 2022).
- **Chemicals/CdD boundary (Anmeldestelle Chemikalien):** a product enters
  the market either under Swiss chemicals law or under CdD — not mixed;
  follow-up duties (product register, SDS) survive CdD.
- **Design consequence — product data only (MASTER D27):** every
  database record carries: HS/CN code (inferred) and origin
  (CH/EU/third-country). No legal-category field and no ban-engagement
  flag are stored — the lawful/illegal lens and the Swiss-ban
  relevance are analytical conclusions drawn in this documentation
  (LEAD_SDS.md), never database fields. The SDS method cannot measure
  total Pb regardless.
- **Headline caveat:** Swiss ban threshold 100 ppm total Pb < EU SDS
  declaration floor 0.1% (1000 ppm, classified compounds). EU-lawful,
  fully documented products can still exceed the Swiss ban invisibly to
  this study. Stated in every deliverable; not experimentally boundable
  (no lab).

## Population and definition

- Target population: distinct paint/varnish formulations (HS 3208/3209)
  available on the **EU market** — the study's object. Swiss figures
  are not a metric: the Swiss market is of little concern (D31,
  2026-09-12); Switzerland stays the regulatory frame (the Swiss 100
  ppm rule sits on top of EU-lawful presence as framing context).
  EU/EEA population estimates also serve as scaling anchors.
- **No registry counts these** — population size must be triangulated.
- Unit = base formulation: colour shades co-notified as one (KemI practice);
  point-of-sale tinting variants are not separate PCN entries (Reg (EU)
  2020/1676). SKU-level counting is explicitly rejected (inflates N by 1–3
  orders of magnitude without adding information).
- Working hypothesis: **10⁴–10⁵ formulations EEA-wide** (estimate;
  D31 — accepted as an estimate, not the operational target).
  EU-side anchors: ~3,200 EU27 producers (NACE 20.30, Eurostat SBS 2019–20);
  CEPE ~800 members ≈ 85% of €17 bn; EU27 extra-EU trade €1.1 bn in /
  €4.3 bn out, ~860 kt (2023, Comext DS-045409, CN8 sums computed).
- **Census annex — HS 3213 artists' oil colours:** lead-pigment artists'
  colours (lead/Cremnitz white PW1, Naples yellow PY41, lead-tin yellow,
  red lead) are outside 3208/3209 (CN 2026: 3213 10 00 / 3213 90 00) and
  invisible in trade-statistics frames, yet are the clearest documented
  case of lead colours lawfully on the EU market (Old Holland NL; Zecchi
  IT; Michael Harding UK→EU unverified). Population is small (dozens of
  brands) → **full census, not a sample**: enumerate brands, check
  catalogues/SDS per country, record lead pigments and any national
  restrictions (SE professional-only regimes etc.).

## Frame construction

1. **Swiss trade statistics (EZV/swiss-impex):** imports/exports at CN8 level
   by partner country, multi-year — structures the market by origin and
   weights the origin dimension of every stratum. Availability/granularity
   to confirm in Phase 0 (OPEN). Include 3213 for the census annex.
2. **Swiss and EU producer/retailer catalogs** (B2B portals, DIY chains,
   brand sites; DE/FR/IT), scraped and deduped to formulation level — the
   actual sampling frame and database backbone. EU leg uses the same
   method on EU-side catalogs; seed products on file: Epifanes WERDOL
   Bleimennige (DE marine chandlers, SDS 2021), BRAVA blymönja (SE,
   professional-only, permit), Old Holland Cremnitz White No. 3 (PW1),
   Zecchi (biacca, giallorino, minio, PY41 oil paint).
3. **EU-side proxies (context/scaling):** ECHA PCN statistics
   (formulation-level, EEA-wide, hazardous mixtures only; ~19%
   non-notification per ECHA Forum pilot H1-2025 → undercount factor);
   Nordic SPIN (DK/SE/NO/FI product registers; ~1 GB Access DB; counts per
   use category; substance-centric lead-CAS queries possible; product names
   confidential); Eurostat PRODCOM.
4. **Swiss structural statistics** (BFS/SBS): domestic producer counts and
   production values.

### Census-to-landscape handoff (D28; updated 2026-09-12 per D29/D31)

The census (v0.1.2) and the numbers unit (v0.2.0, `v0.2.md`, D31)
deliver the study numbers per source:

- **Q1 — products identifiable:** Σ over enumerated channels of
  observed distinct product listings (`products_listed` walks,
  v0.1.2 mechanics — execution deferred: D31 no-scrape reconnaissance
  until an explicit go; carrying unit v0.2.0) — an observed floor,
  never a market total;
  reported per source and as an aggregate sum with overlap caveats.
  Estimation beyond the floor (bottom-up availability factors,
  top-down trade bounds, ranges) defers to the frame unit; trade
  rows stay volume context (D28 grain rule). The working hypothesis
  of 10⁴–10⁵ formulations EEA-wide is tested against these floors.
  The 3213 artists'-colours annex demotes to a low-priority annex
  (D31; D13 superseded).
- **Q2 — documentation coverage:** for how many of the identified
  products SDS/TDS-type documentation is reachable — measured in
  the walks (`doc_links_seen`, `sds_sample_ok` now; M2 acquisition
  later), never assumed. The SDS declaration-floor blind spot
  (MASTER D15) applies to Q2 interpretations.

Method re-scope (D31, 2026-09-12): the landscape is sounded out
without starting to scrape — reconnaissance-level checks (robots/
terms, API/download endpoints, sitemap product-URL counts,
manual-web) plus count-bearing statistical sources (SPIN, PCN,
PRODCOM/SBS, national product registers) carry the measurable part
of Q1/Q2; catalog walks defer until an explicit go. N1 ("how many
are there") is accepted as an estimate, not the operational target;
the core is access coverage — to how many products we have access in
some form, and for how many we can get detailed data / an MSDS.
Market scope is EU-only; Swiss figures serve as downstream context
only. This work materializes in unit v0.2.0 (`v0.2.md`).

The sampling frame (stratification below, seeded draw) is built only
after the landscape map justifies it — the frame-decision bridge in
`10_STRATEGY/v0.1.3.md` gates that unit. Census counts become frame
strata only by recorded manual promotion (MASTER D20).

## Stratification (draft material for the deferred frame unit: 8 segment strata × origin)

| # | Stratum | CN prior | Lead prior |
|---|---|---|---|
| S1 | Decorative water-borne | 3209 | ~0 |
| S2 | Decorative solvent-borne/alkyd | 3208 | very low (driers possible — key open stream) |
| S3 | Anticorrosive/steel-protective primers | 3208 | **high (red lead; documented EU niche)** |
| S4 | Marine & container coatings | 3208 | high (documented: WERDOL) |
| S5 | Road-marking/traffic paints | 3208 | moderate (legacy PbCrO₄; Turner & Filella 2022: 63% of samples >10 mg/kg) |
| S6 | Industrial OEM (coil, refinish, machinery) | 3208 | moderate (chromates ended 2022) |
| S7 | Third-country imported brands | both | **high** (source-market prevalence) |
| S8 | Residual (wood, floor, specialty) | both | low |

The 3213 artists'-colours annex is low-priority (D31). Each stratum
is split by origin — EU production / third-country import — with
draws weighted by Eurostat (Comext/PRODCOM) shares in the deferred
frame unit; EZV weighting is dropped (D31).

## Sample size (precision-based)

- The standard sample-size formula (n = z²·p(1−p)/e² — in words: the
  number to check depends on the margin of error sought and the expected
  share, **not** on the size of the market) gives: **385** products per
  group for a ±5% margin of error; **≈ 811** for ±1.5% on rarer
  occurrences (95% confidence).
- FPC (finite population correction — a discount when the group itself is
  small): n/(1+n/N).
- Full design ≈ 2,000–3,000 products; pilot ≈ 300–800.
- Note: what matters is how many products are checked, not what fraction
  of the market that represents; if the total population N ≈ 30–50k, the
  design coincidentally lands at 5–10%.

## Lead determination (documents only)

- Primary: SDS Section 3 parsing vs lead dictionary (see `LEAD_SDS.md`);
  record concentration ranges, classification, staleness (pre-2021/878 format
  = red flag), UFI, Section 15 statements. Swiss/EU-market sheets typically
  in DE/FR/IT/EN — language handling required in the pipeline.
- Secondary/counts: SPIN lead-CAS preparation counts (Nordic context
  estimate for the EU register world).
- **Corroboration instead of laboratory (no lab, hard constraint):**
  - every suspected positive cross-checked against independent documents for
    the same product where available: technical data sheets, label text,
    retailer listings, producer declarations, older SDS versions,
    cross-market brand variants;
  - consistency scoring; contradictions between documents are themselves
    reportable findings;
  - consistent silence across several independent documents = weak evidence
    of absence, reported as such.
- **Stated limitations (quantify by assumption, not measurement):** declared
  lead only (≥0.1% classified compounds); the 100–1000 ppm band (Swiss ban
  below EU declaration floor), impurity lead, and under-declaring or stale
  sheets are invisible. The final discussion basis carries an explicit
  limitations section.

## Swiss trade & legal workstream (Phase 0, documents only)

- EZV/swiss-impex extraction: CN8 × partner, 2019–2025, 3208+3209 (+3213).
- Verify current consolidated texts: ChemRRV Anhang 2.8 (SR 814.81) —
  threshold, treated articles, exceptions; VIPaV (SR 946.513.8) — Art. 2
  catalogue and Art. 16 body; FR wording.
- Document the CdD governance chain for the lead exception from public
  sources: requester/owner office, review procedure (VIPaV Art. 3), 2010
  inception record (explanatory report/Botschaft) — BBL role currently per
  commissioning context only.
- EU layer: OJ reference of the 17 Mar 2022 lead-chromate authorisation
  refusal; ECHA guidance (if any) on Annex XVII 16/17 vs artists' colours;
  FR/IT red-lead primer retail sweep.

## Implementation mapping

| Method step (this document) | Pipeline stage | CLI | Data entities |
|---|---|---|---|
| Source census & probing | probe | `probe run`, `probe report` | probe_run, probe_finding → population_anchor |
| Frame construction (catalogs) | acquire, ingest | `acquire run`, `ingest sightings` | product, sighting |
| Trade statistics | acquire, ingest | `acquire run` (CS-1/CS-2) | trade_stat |
| Stratification & populations | frame | `frame set` | frame_stratum, population_anchor |
| Sample size & draw | sample | `sample plan`, `sample draw` | sampling_run, sample_selection |
| Lead determination | parse | `parse sds`, `review` | sds_finding, lead_compound |
| Corroboration | corroborate | `review`, `corroborate` | corroboration |
| Census annex (3213) | ingest, parse | census-flagged products | product |
| Analysis & reporting | analyze, report | `analyze prevalence`, `report build` | derived + all |

## Rendered diagrams

`charts/lead-decision-tree` renders the lead-determination and blind-spot
logic of this document as a decision tree:

![How a product is judged: does its safety data sheet list a lead compound, is it declared at 0.1% or more, does the Swiss 100 ppm ban plausibly apply, and do independent documents agree?](charts/lead-decision-tree.png)

Strategy diagrams are proposals — the written documents win. Index:
`charts/README.md`.

## REFERENCES (accessed 2026-08-31; THG/CdD additions 2026-09-10)

- SECO Negativliste CdD, 1 Jan 2026: seco.admin.ch/dam/de/sd-web/8jJ6a7UYFYzf/Negativliste-SECO-Januar-2026-DE.pdf
- SECO/WBF five-yearly review report, 29 Mar 2023: seco.admin.ch/dam/de/sd-web/jUlHD7NFv0hM/BERICHT_Fünfjährige Überprüfung der CdD-Ausnahmen gemäss Art. 3 VIPaV, 2023.pdf
- SECO Cassis-de-Dijon page: seco.admin.ch/de/cassis-de-dijon-prinzip
- SECO THG page (three instruments): seco.admin.ch/de/bundesgesetz-technische-handelshemmnisse
- THG SR 946.51 full text, stand 1 May 2017 (Lexaris; Art. 4, 16a, 31 Abs. 2): lexaris.de/book/version/documentflat/head/222871
- SECO MRA page (scope delimitation only): seco.admin.ch/de/allgemeine-informationen-mra
- Anmeldestelle Chemikalien, CdD guidance: anmeldestelle.admin.ch/de/cassis-de-dijon
- THG Art. 16a (2010 stand, archived): web.archive.org/web/20101011224435/http://www.admin.ch/ch/d/sr/946_51/a16a.html
- VIPaV SR 946.513.8, Art. 1–2 (2010 stand, archived): web.archive.org/web/20101011224439/http://www.admin.ch/ch/d/sr/946_513_8/a2a.html
- ChemRRV Anhang 2.8 (2005 stand, archived): web.archive.org/web/20060210084345/http://www.admin.ch/ch/d/sr/814_81/app23.html
- EuGH 120/78 Rewe/Cassis de Dijon: eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:61978CJ0120
- CJEU C-389/19 P (25 Feb 2021, effects maintained): iclr.co.uk/document/2021000886/casec38919p/html ; GC T-837/16 (7 Mar 2019): eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62016TJ0837
- ECHA downstream-use register (all lead-chromate authorisations refused): echa.europa.eu/du-66-notifications
- Turner & Filella 2022, road paints, 11 countries: DOI 10.1016/j.envpol.2022.120492
- Epifanes WERDOL Bleimennige (SDS 2021 + listings): toplicht.de/de/farben-bootsbau/farben-konservierung/grundierungen/ueber-wasser/5911/epifanes-werdol-blei-mennige
- BRAVA blymönja (SE, professional-only): raseglarhuset.com/frg-fernissa/blymja
- Old Holland Cremnitz White No. 3 (PW1): oldholland.com/classic_oil_colours/d3-cremnitz-white/
- Zecchi (biacca, giallorino, minio, PY41): zecchi.it/products.php?category=29 ; category=36
- CN 2026 heading 3213: zolltarifnummern.de/2026/3213
- Swiss customs trade platform (planned Phase-0 source): swiss-impex.admin.ch
- Eurostat Comext DS-045409 API: ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409
- Eurostat SBS sbs_na_ind_r2 (NACE C2030): ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2
- CEPE: cepe.org/about-the-industry/
- ECHA Forum PCN pilot (Feb 2026, via secondary): cirs-group.com/en/chemicals/echa-releases-pilot-project-report-on-pcn-enforcement-nearly-20-of-companies-failed-to-meet-compliance-obligations
- SPIN: web.archive.org/web/20250116153625/http://spin2000.net/ ; DB download: web.archive.org/web/20240615081956/http://spin2000.net/?page_id=54
- KemI FAQ (co-notification of shades): web.archive.org/web/20210227095243/https://www.kemi.se/fragor-och-svar/fragor-och-svar-om-produktregistret
- CN 2025 codes: zolltarifnummern.de/2025/3208, /3209 (validated vs Comext codelist)

---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Methodology — population, sampling, corroboration

## Abstract

This document explains how the study measures the market — using only
documents, at minimal cost. The setting: paints under customs headings 3208
(solvent-borne) and 3209 (water-borne) on the Swiss **and** EU markets, plus
a full census of artists' oil colours (3213). Swiss trade statistics show
what is imported, from where, in what quantities; producer and retailer
catalogues (scraped and de-duplicated) become the sampling frame. Because no
official register counts paint products, the population size is estimated by
triangulation. The market is divided into eight groups, each split by
origin; a few hundred products per group are checked via their safety data
sheets. A key regulatory fact shapes the design: Switzerland bans paints
with ≥ 0.01% total lead (100 ppm), while EU safety data sheets only declare
classified lead compounds from 0.1% — so the method has a blind spot exactly
at the regulatory seam, which is stated openly in all results. There is no
laboratory; findings are corroborated across independent documents.

## Regulatory frame and legal categorization

- **Cassis de Dijon (CH):** products lawfully marketed in the EU/EEA may be
  placed on the Swiss market without Swiss re-approval (THG Art. 16a,
  unilaterally adopted 1 July 2010). Exceptions are catalogued in VIPaV
  (SR 946.513.8) Art. 2; **Bst. a Ziff. 1 = lead-containing paints and
  varnishes and treated articles (referring to ChemRRV Anhang 2.8)** — in
  force since 2010, still listed in the SECO Negativliste of 1 Jan 2026;
  enforcement authority BAFU; five-yearly review (2023: keep; next ~2028).
- **Swiss substance ban:** ChemRRV Anhang 2.8 (2005 wording; current text
  OPEN) defines lead paints as those with total Pb ≥ 0.01% (100 ppm) and
  bans placing them (and treated articles) on the market — stricter than the
  EU, which bans only lead carbonates/sulfates *in paints* (Annex XVII 16/17)
  and ended lawful lead-chromate supply via authorisation refusal (17 Mar 2022).
- **Chemicals/CdD boundary (Anmeldestelle Chemikalien):** a product enters
  the market either under Swiss chemicals law or under CdD — not mixed;
  follow-up duties (product register, SDS) survive CdD.
- **Design consequence — legal-category field:** every database record
  carries: HS/CN code (inferred), legal category (Anstrichfarbe /
  Malfarbe / pigment / treated article), origin (CH/EU/third-country), and
  whether the Swiss 100 ppm total-Pb ban is plausibly engaged (declared
  compounds and ranges) — the SDS method cannot measure total Pb.
- **Headline caveat:** Swiss ban threshold 100 ppm total Pb < EU SDS
  declaration floor 0.1% (1000 ppm, classified compounds). EU-lawful,
  fully documented products can still exceed the Swiss ban invisibly to
  this study. Stated in every deliverable; not experimentally boundable
  (no lab).

## Population and definition

- Target population: distinct paint/varnish formulations (HS 3208/3209)
  available on the **Swiss market** (domestic production + imports), with
  the **EU market as a parallel study leg** (the Cassis upstream: what
  EU-lawful lead paints exist that could otherwise enter CH freely). EU/EEA
  population estimates also serve as scaling anchors.
- **No registry counts these** — population size must be triangulated.
- Unit = base formulation: colour shades co-notified as one (KemI practice);
  point-of-sale tinting variants are not separate PCN entries (Reg (EU)
  2020/1676). SKU-level counting is explicitly rejected (inflates N by 1–3
  orders of magnitude without adding information).
- Working hypothesis: **10⁴–10⁵ formulations EEA-wide**; Swiss-market frame
  plausibly one order of magnitude smaller (to be pinned in Phase 0).
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

## Stratification (draft: 8 segment strata × origin)

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

Plus the **3213 census annex** (artists' colours, no sampling). Each stratum
is split by origin — CH production / EU import / third-country import — with
draws weighted by EZV import shares (Phase 0).

## Sample size (precision-based)

- n = z²·p(1−p)/e²: 385 for p=0.5 ±5%; ≈811 for p≈5% ±1.5% (95% CI).
- Apply FPC for small stratum frames (n/(1+n/N)).
- Full design ≈ 2,000–3,000 products; pilot ≈ 300–800.
- Note: sampling fraction is not the precision driver; if N ≈ 30–50k the
  design coincidentally lands at 5–10%.

## Lead determination (documents only)

- Primary: SDS Section 3 parsing vs lead dictionary (see `lead_sds.md`);
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
- EU layer: OJ reference of the 17 Mar 2022 lead-chromate authorisation
  refusal; ECHA guidance (if any) on Annex XVII 16/17 vs artists' colours;
  FR/IT red-lead primer retail sweep.

## REFERENCES (accessed 2026-08-31)

- SECO Negativliste CdD, 1 Jan 2026: seco.admin.ch/dam/de/sd-web/8jJ6a7UYFYzf/Negativliste-SECO-Januar-2026-DE.pdf
- SECO/WBF five-yearly review report, 29 Mar 2023: seco.admin.ch/dam/de/sd-web/jUlHD7NFv0hM/BERICHT_Fünfjährige Überprüfung der CdD-Ausnahmen gemäss Art. 3 VIPaV, 2023.pdf
- SECO Cassis-de-Dijon page: seco.admin.ch/de/cassis-de-dijon-prinzip
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

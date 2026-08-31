---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Methodology — population, sampling, corroboration

## Abstract

This document explains how the study measures the market — using only
documents, at minimal cost. The setting is the Swiss market under customs
headings 3208 (solvent-borne) and 3209 (water-borne paints). First, Swiss
trade statistics show what is imported, from where, and in what quantities;
producer and retailer catalogues (scraped and de-duplicated) become the
sampling frame, with EU registers as comparison anchors. Because no official
register counts paint products, the population size is estimated by
triangulation. The market is divided into eight groups, each split by origin
(Swiss-made / EU / third-country); a few hundred products per group are
checked via their safety data sheets. Since there is no laboratory, findings
are corroborated across independent documents about the same product, and
the blind spots (lead below the 0.1% declaration threshold) are stated as
explicit limitations.

## Population and definition

- Target population: distinct paint/varnish formulations (HS 3208/3209)
  available on the **Swiss market** (domestic production + imports). EU/EEA
  population estimates serve as context and scaling anchors only.
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
- Scope boundary: 3208/3209 = polymer paints only. Non-polymer oil paints and
  artists' colours sit under other headings (3210/3213 — codes to verify in
  Design). Prepared driers sold as such are 3211, out of scope.

## Frame construction

1. **Swiss trade statistics (EZV/swiss-impex):** imports/exports at CN8 level
   by partner country, multi-year — structures the market by origin and
   weights the origin dimension of every stratum. Availability/granularity
   to confirm in Phase 0 (OPEN).
2. **Swiss producer and retailer catalogs** (B2B portals, DIY chains, brand
   sites; DE/FR/IT), scraped and deduped to formulation level — the actual
   sampling frame and database backbone.
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
| S2 | Decorative solvent-borne/alkyd | 3208 | very low (driers possible) |
| S3 | Anticorrosive/steel-protective primers | 3208 | **high (red lead)** |
| S4 | Marine & container coatings | 3208 | high |
| S5 | Road-marking/traffic paints | 3208 | moderate (chromate legacy) |
| S6 | Industrial OEM (coil, refinish, machinery) | 3208 | moderate |
| S7 | Third-country imported brands | both | **high** (source-market prevalence) |
| S8 | Residual (wood, floor, specialty) | both | low |

Each stratum is split by origin — CH production / EU import / third-country
import — with draws weighted by EZV import shares (Phase 0). The origin
split is the study's trade-policy payload: it is what links product-level
findings back to external trade and the bilateral framework.

## Sample size (precision-based)

- n = z²·p(1−p)/e²: 385 for p=0.5 ±5%; ≈811 for p≈5% ±1.5% (95% CI).
- Apply FPC for small stratum frames (n/(1+n/N)).
- Full design ≈ 2,000–3,000 products; pilot ≈ 300–800.
- Note: sampling fraction is not the precision driver; if N ≈ 30–50k the
  design coincidentally lands at 5–10%.

## Lead determination (documents only)

- Primary: SDS Section 3 parsing vs lead dictionary (see `lead_sds.md`);
  record concentration ranges, classification, staleness (pre-2021/878 format
  = red flag), UFI, Section 15 statements. Swiss-market sheets typically in
  DE/FR/IT/EN — language handling required in the pipeline.
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
- **Stated limitations (quantify by assumption, not measurement):** lead
  below the 0.1% declaration threshold, impurity lead, and under-declaring or
  stale sheets are invisible to this design. The final discussion basis must
  carry an explicit limitations section.

## Swiss trade & legal workstream (Phase 0, documents only)

- EZV/swiss-impex extraction: CN8 × partner, 2019–2025, 3208+3209.
- Legal dossier: EU lead restrictions (Annex XVII 16/17, XIV 10–12, entries
  28–30, 63) vs Swiss ChemO/ChemG (REACH-aligned since 2015 — current
  status OPEN); MRA sectoral coverage (OPEN); third-country import control
  (OPEN). Primary sources only; no assertion until verified.

## REFERENCES (accessed 2026-08-31)

- Swiss customs trade platform (planned Phase-0 source): swiss-impex.admin.ch
- Eurostat Comext DS-045409 API (CN8 codelist + EU27/EXT_EU27_2020 trade,
  2023–24): ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409
- Eurostat SBS sbs_na_ind_r2 (NACE C2030 enterprises): ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2
- CEPE: cepe.org/about-the-industry/
- ECHA Forum PCN pilot (Feb 2026, via secondary): cirs-group.com/en/chemicals/echa-releases-pilot-project-report-on-pcn-enforcement-nearly-20-of-companies-failed-to-meet-compliance-obligations
- PCN industrial-share news (17 Jan 2024): web.archive.org/web/20240530033512/https://poisoncentres.echa.europa.eu/ro/-/second-poison-centre-notifications-compliance-date-passed-smoothly
- SPIN: web.archive.org/web/20250116153625/http://spin2000.net/ ; DB download: web.archive.org/web/20240615081956/http://spin2000.net/?page_id=54
- KemI FAQ (co-notification of shades): web.archive.org/web/20210227095243/https://www.kemi.se/fragor-och-svar/fragor-och-svar-om-produktregistret
- VdL statistics: wirsindfarbe.de/statistiken
- CN 2025 codes: zolltarifnummern.de/2025/3208, /3209 (validated vs Comext codelist)

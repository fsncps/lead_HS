---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Methodology — population, sampling, validation

## Abstract

This document explains how the study measures the market. Because no official
register counts how many paint products exist in the EEA, the total must be
estimated by combining several sources (poison-centre notifications, Nordic
product registers, producer and trade statistics). The market is then divided
into eight groups — for example wall paints, anti-rust primers, marine
coatings, imports — and a few hundred products per group are checked, so that
the share containing lead can be estimated with known statistical precision.
A small set of physical samples goes to a laboratory to check what the safety
sheets cannot show (trace lead below the declaration threshold).

## Population and definition

- Target population: distinct paint/varnish formulations (HS 3208/3209)
  placed on the EEA market. **No registry counts these** — the population size
  must be triangulated.
- Unit = base formulation: colour shades co-notified as one (KemI practice);
  point-of-sale tinting variants are not separate PCN entries (Reg (EU)
  2020/1676). SKU-level counting is explicitly rejected (inflates N by 1–3
  orders of magnitude without adding information).
- Working hypothesis: **10⁴–10⁵ formulations EEA-wide** (to be pinned in
  Phase 0). Anchors: ~3,200 EU27 producers (NACE 20.30, Eurostat SBS
  2019–20); CEPE ~800 members ≈ 85% of €17 bn; EU27 extra-EU trade €1.1 bn
  in / €4.3 bn out, ~860 kt (2023, Comext DS-045409, CN8 sums computed).
- Scope boundary: 3208/3209 = polymer paints only. Non-polymer oil paints and
  artists' colours sit under other headings (3210/3213 — codes to verify in
  Design). Prepared driers sold as such are 3211, out of scope.

## Frame construction

1. ECHA PCN statistics (formulation-level, EEA-wide, hazardous mixtures only;
   ~19% non-notification per ECHA Forum pilot H1-2025 → undercount factor).
2. Nordic SPIN (DK/SE/NO/FI product registers; ~1 GB Access DB; counts per
   use category, substance-centric lead-CAS queries possible; product names
   confidential).
3. Producer catalogs (B2B portals + retail), deduped to formulation level —
   becomes the sampling frame and database backbone.
4. Scale-up: Nordic per-capita/GDP scaling to EEA, cross-checked against
   producer count × mean portfolio size.

## Stratification (draft, ~8 strata)

| # | Stratum | CN prior | Lead prior |
|---|---|---|---|
| S1 | Decorative water-borne | 3209 | ~0 |
| S2 | Decorative solvent-borne/alkyd | 3208 | very low (driers possible) |
| S3 | Anticorrosive/steel-protective primers | 3208 | **high (red lead)** |
| S4 | Marine & container coatings | 3208 | high |
| S5 | Road-marking/traffic paints | 3208 | moderate (chromate legacy) |
| S6 | Industrial OEM (coil, refinish, machinery) | 3208 | moderate |
| S7 | Imported/third-country brands | both | high (source-market prevalence) |
| S8 | Residual (wood, floor, specialty) | both | low |

## Sample size (precision-based)

- n = z²·p(1−p)/e²: 385 for p=0.5 ±5%; ≈811 for p≈5% ±1.5% (95% CI).
- Apply FPC for small stratum frames (n/(1+n/N)).
- Full design ≈ 2,000–3,000 products; pilot ≈ 300–800.
- Note: sampling fraction is not the precision driver; if N ≈ 30–50k the
  design coincidentally lands at 5–10%.

## Lead determination

- Primary: SDS Section 3 parsing vs lead dictionary (see `lead_sds.md`);
  record concentration ranges, classification, staleness (pre-2021/878 format
  = red flag), UFI, Section 15 statements.
- Secondary/counts: SPIN lead-CAS preparation counts (Nordic pilot estimate).
- Validation: lab subset (XRF screen; EPA 3050B-style digestion + ICP-OES/MS
  confirmatory; CPSC-CH-E1003-09.1 paint SOP as reference) on ~30–60 samples,
  positives oversampled, to bound the sub-0.1% blind spot. Cost/sample TBD.
- Expectation: consumer decorative ≈ 0% intentional lead (ban structure);
  signal concentrates in S3–S7.

## REFERENCES (accessed 2026-08-31)

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

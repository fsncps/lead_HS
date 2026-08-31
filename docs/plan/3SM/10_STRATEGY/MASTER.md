---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Strategy MASTER — lead_HS

## Abstract

This is the strategy summary for the lead-in-paint study, in plain terms. It
records the main decisions: what counts as one "product" (one base
formulation — not every colour and tin size), which parts of the market we
look at (all of them: DIY, professional and industrial paints, plus imports),
how many products we check (about 2,000–3,000, chosen so the result is
statistically precise — not a fixed percentage of the market), and how we
detect lead (primarily the ingredients section of safety data sheets, backed
by laboratory spot-checks). It also lists the open questions and the phased
roadmap.

## DECISIONS

1. **Deliverable:** prevalence study (report) + reusable product/SDS evidence
   database. The database is the evidence base, not a by-product.
2. **Unit of analysis:** formulation/base product (register-like; colour and
   size variants collapse; point-of-sale tinting variants excluded). Matches
   PCN/SPIN logic and regulatory reality.
3. **Segment scope:** all segments — decorative, industrial/professional
   (anticorrosive, marine, road-marking, coil/OEM), imports.
4. **Sampling:** precision-based stratified design (not a literal 10%):
   n ≈ 385/stratum (p=0.5, ±5%), n ≈ 811 (p≈5%, ±1.5%), with FPC where frames
   are small; full design ≈ 2,000–3,000 products. High-risk strata oversampled.
5. **Lead detection primary source:** SDS (MSDS) Section 3 parsing against a
   CAS/EC/Index lead-compound dictionary; UFI as join key; Section 15
   authorisation statements as anomaly signal.
6. **CN assignment:** inferred per product from SDS composition (medium +
   binder chemistry → CN8), since products carry no tariff codes.
7. **Blind-spot bound:** small lab validation subset (XRF screen + ICP
   confirmatory) to bound sub-0.1% / impurity lead that SDS cannot show.
8. **Pilot-first:** Nordic SPIN data provide an immediate, free pilot estimate
   (preparation counts + lead-CAS incidence for DK/SE/NO/FI) before any
   scraping infrastructure is built.

## OPEN ITEMS

- OPEN/NON-BLOCKING: ECHA PCN universe totals + EuPCS paint share (dashboard
  login-gated; needs extraction via annual report or manual access).
- OPEN/NON-BLOCKING: SPIN Access DB extraction (paints use-category counts,
  lead-compound counts, per country/year).
- OPEN/NON-BLOCKING: PRODCOM sold production 20.30.1x (not on dissemination
  API; bulk files needed).
- OPEN: verify CAS for lead naphthenate (61790-14-5?) and lead neodecanoate
  (27253-29-8?) against ECHA EC inventory before freezing the dictionary.
- OPEN: current Annex XIV authorisation status for lead chromates (post-2019
  annulments); Reg (EU) 2023/1422 (lead in PVC) content unverified.
- OPEN: EEA-EFTA (NO/IS/LI) trade/producer data (reporter-code issue in
  Comext API).
- OPEN: import-channel method (SDS often absent; Safety Gate/RAPEX, customs
  data as alternatives).

## ROADMAP (strategy altitude)

- Phase 0 — close sizing gaps: PCN stats, SPIN extraction, PRODCOM, VdL/KemI
  statistics, retailer category counts (needs shell/scout tooling).
- Phase 1 — pilot: lead dictionary + SDS scrape/parsing on 1–2 strata;
  validate hit-rate prior and CN-assignment heuristics.
- Phase 2 — frame build + stratified draw + SDS collection at full n.
- Phase 3 — lab validation subset.
- Phase 4 — analysis, report, database freeze.

## Topic index

- `methodology.md` — population, frame, stratification, sampling, validation
- `lead_sds.md` — compounds, legal status, SDS feasibility, prior studies

## Readiness for Design

Not yet. Phase 0 numbers should pin the frame hypothesis (10⁴–10⁵
formulations) and Phase 1 should validate the SDS pipeline before Design
commits to architecture.

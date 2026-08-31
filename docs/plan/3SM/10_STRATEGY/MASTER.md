---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Strategy MASTER — lead_HS

## Abstract

This is the strategy summary, in plain terms. The project asks whether
paints on the Swiss market (customs headings 3208/3209) contain lead, using
only documents that can be collected for free from the web. It records the
main decisions: what counts as one "product" (one base formulation — not
every colour and tin size), which parts of the market we look at (all
segments, split by origin: Swiss-made, EU imports, third-country imports),
how many products we check (about 2,000–3,000, chosen for statistical
precision), how we detect lead (the ingredients section of safety data
sheets, cross-checked against other documents about the same product — no
laboratory), and the parallel legal workstream comparing EU and Swiss rules
under the bilateral agreements. Open questions and the phased roadmap
follow.

## DECISIONS

1. **Deliverable:** discussion basis for decision makers (briefing on Swiss
   external trade in 3208/3209 paints, lead prevalence, and the EU/CH
   regulatory seams) + reusable product/SDS evidence database.
2. **Unit of analysis:** formulation/base product (register-like; colour and
   size variants collapse; point-of-sale tinting variants excluded). Matches
   PCN/SPIN logic and regulatory reality.
3. **Segment scope:** all segments — decorative, industrial/professional
   (anticorrosive, marine, road-marking, coil/OEM) — each additionally split
   by **origin** (Swiss production / EU import / third-country import),
   weighted by Swiss trade statistics. EU/EEA serves as market and
   regulatory context.
4. **Sampling:** precision-based stratified design (not a literal 10%):
   n ≈ 385/stratum (p=0.5, ±5%), n ≈ 811 (p≈5%, ±1.5%), with FPC where frames
   are small; full design ≈ 2,000–3,000 products. High-risk strata oversampled.
5. **Lead detection primary source:** SDS (MSDS) Section 3 parsing against a
   CAS/EC/Index lead-compound dictionary; UFI as join key; Section 15
   authorisation statements as anomaly signal.
6. **CN assignment:** inferred per product from SDS composition (medium +
   binder chemistry → CN8), since products carry no tariff codes.
7. **Corroboration instead of laboratory (supersedes the earlier lab
   validation decision):** no lab, no physical samples. Suspected positives
   are cross-checked against independent documents for the same product
   (TDS, label text, retailer listings, older SDS versions, cross-market
   brand variants). Sub-0.1% and impurity lead remain invisible → stated
   limitation of the study, quantified by assumption, not measurement.
8. **Pilot-first:** Nordic SPIN data provide an immediate, free pilot estimate
   (preparation counts + lead-CAS incidence for DK/SE/NO/FI) before any
   scraping infrastructure is built.
9. **Cost constraint (hard):** publicly retrievable documents only — no paid
   databases, no commercial market reports, no sample purchases.
10. **Swiss workstreams are first-class Phase-0 items:** (a) EZV/swiss-impex
    trade extraction at CN8 × partner; (b) legal dossier EU vs CH (ChemO
    REACH-alignment for lead compounds, MRA sectoral coverage, third-country
    import control).

## OPEN ITEMS

- OPEN/NON-BLOCKING: EZV/swiss-impex — confirm free access and granularity
  (CN8 by partner country, multi-year) for 3208/3209; extract 2019–2025.
- OPEN/NON-BLOCKING: Swiss legal dossier — current ChemO/ChemG restriction
  status of lead compounds in paints (vs REACH Annex XVII 16/17, XIV 10–12,
  entries 28–30/63); verify against primary sources, do not assert.
- OPEN/NON-BLOCKING: EU–CH MRA sectoral coverage of paints/chemicals; how
  third-country paint imports are controlled in CH.
- OPEN/NON-BLOCKING: Swiss product-notification landscape (no PCN
  membership; poison-centre/product-register equivalents and any public
  statistics); Swiss producer statistics (BFS).
- OPEN/NON-BLOCKING: ECHA PCN universe totals + EuPCS paint share (dashboard
  login-gated; needs extraction via annual report or manual access) — EU context.
- OPEN/NON-BLOCKING: SPIN Access DB extraction (paints use-category counts,
  lead-compound counts, per country/year).
- OPEN/NON-BLOCKING: PRODCOM sold production 20.30.1x (not on dissemination
  API; bulk files needed).
- OPEN: verify CAS for lead naphthenate (61790-14-5?) and lead neodecanoate
  (27253-29-8?) against ECHA EC inventory before freezing the dictionary.
- OPEN: current Annex XIV authorisation status for lead chromates (post-2019
  annulments); Reg (EU) 2023/1422 (lead in PVC) content unverified.
- OPEN: import-channel method for third-country brands (SDS often absent;
  Safety Gate/RAPEX participation status of Switzerland to verify, customs
  data as alternative).

## ROADMAP (strategy altitude)

- Phase 0 — close gaps: Swiss customs extraction (EZV), EU-vs-CH legal
  dossier, PCN stats, SPIN query, PRODCOM, catalog counts.
- Phase 1 — pilot: freeze lead dictionary + SDS scrape/parsing on 1–2 strata;
  validate hit-rate prior and CN-assignment heuristics.
- Phase 2 — frame build + stratified draw + document collection at full n.
- Phase 3 — cross-document corroboration and quality assurance (replaces
  laboratory validation).
- Phase 4 — analysis; decision-makers' discussion basis; database freeze.

## Topic index

- `methodology.md` — population, frame, stratification, sampling, corroboration
- `lead_sds.md` — compounds, legal status, SDS feasibility, prior studies

## Readiness for Design

Not yet. Phase 0 must pin the Swiss frame (trade structure by origin, catalog
coverage) and the legal dossier's first pass before Design commits to
architecture.

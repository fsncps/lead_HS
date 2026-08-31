---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# Strategy MASTER — lead_HS

## Abstract

This is the strategy summary, in plain terms. The project asks whether
paints on the Swiss and EU markets (customs headings 3208/3209, plus a
census annex for artists' colours under 3213) contain lead, using only
documents collectable for free from the web. It records the main decisions:
what counts as one "product" (one base formulation), which parts of the
market we look at (all segments, split by origin; EU-lawful presence is a
study object in its own right because of the Cassis-de-Dijon import route),
how many products we check (about 2,000–3,000 by statistical precision),
how we detect lead (safety-data-sheet ingredients sections, cross-checked
across documents — no laboratory), and the regulatory frame the evidence
feeds into (Swiss ban at 100 ppm total Pb via ChemRRV Anhang 2.8, shielded
from EU-lawful imports by the VIPaV exceptions catalogue, reviewed every
five years). Open questions and the phased roadmap follow.

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
   weighted by Swiss trade statistics.
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
    REACH-alignment, MRA sectoral coverage, third-country import control).
11. **Regulatory anchoring (neutral, after SECO exchange):** the study
    documents whether the VIPaV Art. 2 Bst. a Ziff. 1 exception (lead paints,
    shielding ChemRRV Anhang 2.8's ≥0.01% total-Pb ban from
    Cassis-de-Dijon imports) has a factual field of application. It informs
    the standing five-yearly review (last 2023: keep; next ~2028) and
    related policy conversations **without presupposing deletion or
    exception outcomes**. SECO's "Art 2a(1)" read as Art. 2 Bst. a Ziff. 1
    (no Art. 2a exists; inference, confirm only if load-bearing). Art. 16
    VIPaV is a list-maintenance provision — context only.
12. **EU-market leg:** EU-lawful presence of lead paints is a first-class
    study object (the Cassis upstream), not just context. Same SDS method on
    EU-side catalogs. Seed products already documented: Epifanes WERDOL
    Bleimennige (DE marine retail), BRAVA blymönja (SE, professional-only),
    Old Holland Cremnitz White PW1 (NL), Zecchi biacca/giallorino/minio (IT).
13. **HS 3213 census annex:** artists' oil colours with lead pigments
    (lead/Cremnitz white, Naples yellow, lead-tin yellow) are added as a
    small full census (not a sample) — population is tiny (dozens of brands),
    and the stream is invisible in 3208/3209 statistics. Core sampling
    design remains 3208/3209.
14. **Legal-category dimension:** the database classifies each product by
    legal category (Anstrichfarbe/Malfarbe/treated article; Swiss total-Pb
    ban threshold relevance), not only by HS/CN code.
15. **Headline caveat:** the Swiss ban threshold (0.01% = 100 ppm total Pb,
    ChemRRV Anhang 2.8, 2005 wording — current text to verify) lies **below**
    the EU SDS declaration floor (0.1% for classified compounds). A paint
    can be EU-lawful and transparently documented yet exceed the Swiss ban,
    invisibly to the SDS method. Carried as an explicit limitation in every
    deliverable.

## OPEN ITEMS

- OPEN/NON-BLOCKING: EZV/swiss-impex — confirm free access and granularity
  (CN8 by partner country, multi-year) for 3208/3209 (+ 3213); extract 2019–2025.
- OPEN: current consolidated ChemRRV Anhang 2.8 (SR 814.81) wording — the
  0.01% threshold, treated articles, and any exceptions verified only on the
  2005 snapshot; verify on fedlex.
- OPEN: current consolidated VIPaV (SR 946.513.8) incl. Art. 16 body text
  and FR wording (fedlex is JS-gated; needs browser/scout extraction).
- OPEN: OJ reference of the 17 Mar 2022 Commission implementing decision
  refusing DCL Corporation (NL) B.V.'s 8 lead-chromate authorisation uses.
- OPEN (high priority, empirical): lead driers (octoate/naphthenate) in
  current EU alkyd paints — neither presence nor absence documented; first
  target of the SDS sampling pilot.
- OPEN (soft): confirm SECO's "Art 2a(1)" ≙ Art. 2 Bst. a Ziff. 1 in writing
  only if the mapping becomes load-bearing; do not build on the deletion
  scenario.
- OPEN/NON-BLOCKING: Swiss legal dossier — ChemO/ChemG restriction status of
  lead compounds in paints; EU–CH MRA sectoral coverage of paints/chemicals;
  third-country import control.
- OPEN/NON-BLOCKING: Swiss product-notification landscape (no PCN membership;
  poison-centre/product-register equivalents and any public statistics);
  Swiss producer statistics (BFS).
- OPEN/NON-BLOCKING: ECHA PCN universe totals + EuPCS paint share (EU context).
- OPEN/NON-BLOCKING: SPIN Access DB extraction; PRODCOM sold production 20.30.1x.
- OPEN: verify CAS for lead naphthenate (61790-14-5?) and lead neodecanoate
  (27253-29-8?) against ECHA EC inventory before freezing the dictionary.
- OPEN: artists' colours vs REACH Annex XVII entries 16/17 — the
  member-state permit mechanism (ILO C13) practice across NL/IT/DE/FR; no
  ECHA guidance document retrieved yet.
- OPEN: FR/IT red-lead primer retail ("minium de plomb"/"minio rosso") —
  unverified; engine capacity, not evidence absence.

## ROADMAP (strategy altitude)

- Phase 0 — close gaps: Swiss customs extraction (EZV); verify current legal
  texts (ChemRRV Anhang 2.8, consolidated VIPaV); 2022 refusal OJ ref; PCN
  stats; SPIN query; PRODCOM; catalog counts.
- Phase 1 — pilot: freeze lead dictionary + SDS scrape/parsing on 1–2 strata
  (lead-driers stream first); validate hit-rate prior and CN-assignment
  heuristics.
- Phase 2 — frame build + stratified draw + document collection at full n;
  run the HS 3213 artists' colours census annex in parallel.
- Phase 3 — cross-document corroboration and quality assurance (replaces
  laboratory validation).
- Phase 4 — analysis; decision-makers' discussion basis; database freeze.

## Topic index

- `methodology.md` — population, frame, stratification, sampling, corroboration
- `lead_sds.md` — compounds, legal status, SDS feasibility, prior studies

## Readiness for Design

Not yet. Phase 0 must pin the Swiss frame (trade structure by origin, catalog
coverage, current legal-text verification) before Design commits to
architecture.

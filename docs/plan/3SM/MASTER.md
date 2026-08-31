---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# lead_HS — MASTER

## Abstract

This project asks whether paints and varnishes on the **Swiss and EU
markets** (customs headings 3208, solvent-borne, and 3209, water-borne,
plus a census annex for artists' colours under 3213) contain lead, and how
the regulatory seam between the EU and Switzerland works in practice: the
Cassis-de-Dijon principle admits EU-lawful products, while the VIPaV
exceptions catalogue (Art. 2 Bst. a Ziff. 1) shields the stricter Swiss
lead-paint ban (ChemRRV Anhang 2.8, ≥ 0.01% total Pb) from imports. It
works purely from documents — chiefly safety data sheets (SDS) and trade
statistics — with no laboratory and at minimal cost. The outcome is a
discussion basis for decision makers plus a reusable database of checked
products. This file is the project dashboard. Current stage: **strategy**
— research and decisions, nothing is being built yet.

**Project:** Identify which paint/varnish products (HS/CN 3208/3209, plus a
3213 artists' colours census annex) on the Swiss and EU markets contain
lead, via documentation-only screening (SDS), framed by Swiss external trade
statistics and the bilateral/Cassis-de-Dijon regulatory frame. Deliverable:
discussion basis for decision makers + reusable product/SDS evidence
database.

**Type:** research study + light data-engineering hybrid (document
scraping, evidence database). Hard constraints: no lab, no physical samples,
no paid data sources, minimal cost.

## State

| Unit | Stage | Notes |
|---|---|---|
| v0.1 (feasibility & study design) | STRATEGY | initial research pass + scope correction done; Phase-0 gap closure pending |

## Documents

- `10_STRATEGY/MASTER.md` — decisions, open items, roadmap
- `10_STRATEGY/methodology.md` — population, frame, sampling, corroboration
- `10_STRATEGY/lead_sds.md` — lead compounds, EU legal status, SDS feasibility

## Key numbers (2026-08-31 research pass)

- CN 2025: only **11 CN8 codes** under 3208+3209 → nomenclature cannot count products.
- EU-side context: ~3,200–3,300 EU27 producers (NACE 20.30); CEPE ~800
  members ≈ 85% of €17 bn; EU27 extra-EU trade (2023) ~€1.1 bn in / €4.3 bn out.
- Swiss trade in 3208/3209 (+3213): **to be extracted** (EZV/swiss-impex, Phase 0).
- **No source counts distinct paint products** — EEA or Switzerland. Best
  proxies: ECHA PCN (gated), Nordic SPIN (extractable), national registers,
  e-commerce catalogs.
- EU-market lead-paint presence (hard findings): lead chromates — no lawful
  supply since 17 Mar 2022; red-lead primers — documented niche (DE marine
  retail, SE professional-only); artists' oil colours (HS 3213) — documented
  (NL/IT); lead driers in alkyds — unknown (key open stream).
- Regulatory frame: Swiss ban ≥ 0.01% total Pb (ChemRRV Anh. 2.8, 2005
  wording — verify current) vs EU SDS declaration floor 0.1% → **blind spot
  at the regulatory seam**; VIPaV Art. 2 Bst. a Ziff. 1 exception; five-yearly
  review (2023: keep; next ~2028).
- Study design: precision-based stratified sample, **~2,000–3,000 products**,
  stratified by segment × origin, plus 3213 census annex.

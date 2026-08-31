---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# lead_HS — MASTER

## Abstract

This project asks whether paints and varnishes on the **Swiss market**
(customs headings 3208, solvent-borne, and 3209, water-borne) contain lead,
and what the bilateral EU–Switzerland framework means for their regulation.
It works purely from documents — chiefly safety data sheets (SDS) and Swiss
trade statistics — with no laboratory and at minimal cost. The outcome is a
discussion basis for decision makers plus a reusable database of checked
products. This file is the project dashboard: it records the current stage,
key numbers, and where the detailed notes live. Current stage: **strategy**
— research and decisions, nothing is being built yet.

**Project:** Identify which paint/varnish products (HS/CN 3208 solvent-borne,
3209 water-borne, polymer-based) available on the Swiss market contain lead,
via documentation-only screening (SDS), framed by Swiss external trade
statistics and the bilateral EU framework. Deliverable: discussion basis for
decision makers + reusable product/SDS evidence database.

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
- Swiss trade in 3208/3209: **to be extracted** (EZV/swiss-impex, Phase 0).
- **No source counts distinct paint products** — EEA or Switzerland. Best
  proxies: ECHA PCN (gated), Nordic SPIN (extractable), national registers,
  e-commerce catalogs.
- Study design: precision-based stratified sample, **~2,000–3,000 products**,
  stratified by segment × origin.

---
unit: v0.1
stage: STRATEGY
lifecycle: LIVE
updated: 2026-08-31
---

# lead_HS — MASTER

## Abstract

This project investigates whether paints and varnishes sold in the European
Economic Area (EEA/EWR) — customs headings 3208 (solvent-borne) and 3209
(water-borne) — contain lead. It does so by systematically reading product
safety data sheets (SDS) and, on that basis, estimating how common lead is in
these products. The outcome will be a research report plus a reusable
database of checked products. This file is the project dashboard: it records
the current stage, the key numbers, and where the detailed notes live.
Current stage: **strategy** — research and decisions, nothing is being built
yet.

**Project:** Identify which paint/varnish products (HS/CN 3208 solvent-borne,
3209 water-borne, polymer-based) on the EEA market contain lead, via a
prevalence study grounded in a reusable product/SDS database.

**Type:** research study + data-engineering hybrid (evidence database).

## State

| Unit | Stage | Notes |
|---|---|---|
| v0.1 (feasibility & study design) | STRATEGY | initial research pass complete; Phase-0 gap closure pending |

## Documents

- `10_STRATEGY/MASTER.md` — decisions, open items, roadmap
- `10_STRATEGY/methodology.md` — population, frame, sampling, validation
- `10_STRATEGY/lead_sds.md` — lead compounds, EU legal status, SDS feasibility

## Key numbers (2026-08-31 research pass)

- CN 2025: only **11 CN8 codes** under 3208+3209 → nomenclature cannot count products.
- EU27 producers (NACE 20.30): ~3,200–3,300; CEPE ~800 members ≈ 85% of €17 bn value.
- EU27 extra-EU trade 3208+3209 (2023): ~€1.1 bn imports / ~€4.3 bn exports.
- **No source counts distinct paint products in the EEA.** Best proxies: ECHA
  PCN (gated), Nordic SPIN (extractable), national registers, e-commerce.
- Study design: precision-based stratified sample, **~2,000–3,000 products**.

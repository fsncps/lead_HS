---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---
# lead_HS — MASTER

## Abstract

This project researches the **EU market** for paints and varnishes
(customs headings 3208, solvent-borne, and 3209, water-borne, plus a
low-priority annex for artists' colours under 3213): how many products
the market holds, for how many of them detailed documentation —
chiefly safety data sheets (SDS) — is obtainable, and what that
documentation shows about lead. The study is situated in the context
of the autonomous Swiss Cassis-de-Dijon frame: the principle admits
EU-lawful products, while the VIPaV exceptions catalogue (Art. 2 Bst. a
Ziff. 1) shields the stricter Swiss lead-paint ban (ChemRRV Anhang 2.8,
≥ 0.01% total Pb) from imports; the entire exception catalogue is
reviewed every five years under SECO's lead, and the study supplies
documented market numbers within that cycle, without taking a position
on the regulation itself. Switzerland is the regulatory frame of the
study, never a studied market (D31). It
works purely from documents — chiefly safety data sheets (SDS) and
statistics — with no laboratory and at minimal cost. The outcome is
documented market numbers for the surrounding decision-making plus a
reusable database of checked products. This file is the project
dashboard. Current stage: **v0.2.0 — market scale & data
availability** (the D31 strategy turn, `v0.2.md`: numbers-first
N1 market size, N2 access coverage, N3 detailed-data reachability;
reconnaissance-only, EU-only; strategy DRAFT pending user validation).
Unit v0.1.1 built (probe CLI gate-verified; census feasibility pass
executed 2026-09-11); unit v0.1.2 — operator layer + census close-out
(D26) — **built 2026-09-11** (PHASE01–06 done; 155 offline tests
pass); unit v0.1.3 — data-landscape map (D29/D30) — built
(walk counters, migration 0004; 165 offline tests; baseline probe
round executed 2026-09-12: 3 done / 1 blocked / 3 failed, audit
clean); its walk-based execution is superseded by v0.2.0 and the unit
stands FROZEN with the walk machinery idle.

**Project:** Establish how many paint/varnish products (HS/CN 3208/3209,
plus a low-priority 3213 artists' colours annex) are on the **EU
market**, for how many of them detailed documentation (SDS) is
obtainable, and what it shows about lead — via documentation-only
screening, situated in the autonomous Swiss Cassis-de-Dijon regulatory
frame (THG/VIPaV; not an EU-bilateral matter). Deliverable:
documented market numbers + reusable product/SDS evidence database.

**Type:** research study + light data-engineering hybrid (document
scraping, evidence database). Hard constraints: no lab, no physical samples,
no paid data sources, minimal cost.

## State

| Unit | Stage | Notes |
|---|---|---|
| v0.1 (feasibility & study design) | STRATEGY | foundational pass; legal-verification open items carried in Strategy MASTER |
| v0.1.1 (source probing — slim CLI) | IMPLEMENTATION | PHASE01–07 built & gate-verified 2026-09-11; PHASE08 feasibility pass executed 2026-09-11; census close-out transferred to v0.1.2 (D26) |
| v0.1.2 (operator layer + census close-out) | IMPLEMENTATION | built 2026-09-11 (PHASE01–06; rescoped to second-pass od8–od10; 155 tests offline); PHASE07 census execution transferred to v0.1.3 PHASE02 (B8/D26) |
| v0.1.3 (data-landscape map) | IMPLEMENTATION | strategy converged on D30 2026-09-12; design pe1–pe7 + PHASE01–07 written (CEO HOLD + ENG SMALL CHANGE re-review 2026-09-12, findings E1/E2 folded); baseline census 2026-09-12 (3/1/3, audit clean); PHASE01 (D28 rework) built 2026-09-12 — 165 offline tests, audit clean; PHASE02+ await explicit go |

## Documents

- `10_STRATEGY/MASTER.md` — decisions, open items, roadmap
- `10_STRATEGY/METHODOLOGY.md` — population, frame, sampling, corroboration
- `10_STRATEGY/LEAD_SDS.md` — lead compounds, EU legal status, SDS feasibility
- `10_STRATEGY/DATA_SOURCE.md` — source register, access & provenance discipline
- `10_STRATEGY/DATA_MODEL.md` — evidence-database schema
- `10_STRATEGY/ARCHITECTURE.md` — pipeline, CLI, reporting concept

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
  at the regulatory seam**; VIPaV Art. 2 Bst. a Ziff. 1 exception
  (autonomous CdD frame, THG; MRA out of scope); five-yearly review of the
  entire catalogue by SECO (2023: keep; next ~2028); requester/owner BBL
  (commissioning context — verify before naming).
- Study design: precision-based stratified sample, **~2,000–3,000 products**,
  stratified by segment × origin, plus 3213 census annex.

---
unit: v0.2.0
built: 2026-09-12
type: unit report (detailed, human-readable)
language: en
---

# Unit v0.2.0 — data-landscape map: market scale & data availability

The numbers unit: before any product data is collected, the study maps
its **data landscape** — which sources cover the EU paints market, at
what scale, and with what access to product documentation. The three
headline numbers N1/N2/N3 were assembled from a reconnaissance-only
probe round run on 2026-09-12 (terms of use and access conditions,
API/download availability, product-URL counts from sitemaps, manual
checks — no product-level collection; catalogue walks await a separate
go-ahead).

> Provenance note: the machine report of this era
> (`docs/report/probe-report.*`) was overwritten by later unit
> republishes — before the publish-history policy (v0.2.2 PHASE07
> addendum) existed. This file is the durable record, reconstructed
> from the planning documents (`docs/plan/3SM/30_IMPLEMENTATION/
> v0.2.0/`) and the evidence database; the numbers were re-verified
> against the DB on 2026-09-14.

## Findings

- **N1 — how many paints are on the EU market:** an order of magnitude
  assembled from official statistics. The 2024 trade anchors (Eurostat
  Comext, EU extra-EU imports, dataset DS-045409) put **HS 3208 at
  ≈2.5 Mt (≈€12.2 bn)** and **HS 3209 at ≈2.1 Mt (≈€6.2 bn)**.
  Register anchors frame the producer side: **CEPE** represents ≈800
  member companies; **Eurostat SBS** counts 3,200 enterprises in NACE
  20.30 (2020; paints + printing inks + mastics). The market-size
  range itself stays an *estimate* — the report gives the anchors and
  the method, never a single number presented as fact.
- **N2 — for how many products we have access to data in some form:**
  **204,693** product URLs observed across **23** counted sources —
  sitemap-visible, a floor, dominated by a few large DIY catalogues.
- **N3 — for how many of those detailed specifications such as an SDS
  are obtainable:** **9** sites visibly expose an SDS/document library
  (a site count, not a product count); no product-level documentation
  has been collected.

Every probe result, including access refusals, is recorded with its
cause in the evidence database; the provenance audit passes.

## Obstacles

- **SPIN** (Nordic substance-preparation register) unreachable in this
  round; the Nordic registers remained open.
- Several DIY/marketplace sites block automated access or load product
  data via JavaScript; recorded as blocked/manual-record rather than
  guessed.
- PRODCOM/SBS full API integration deferred (TODOS.md) — producer
  counts entered via manual record this unit.

## Provenance

- Eurostat Comext DS-045409 (extra-EU imports, CN8 × partner × year):
  <https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409>
  (accessed 2026-09-12).
- Eurostat SBS (`sbs_na_ind_r2`): <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2>
  (accessed 2026-09-12).
- CEPE membership: <https://www.cepe.org> (accessed 2026-09-12).
- Per-source URLs and probe verdicts: source register
  (`src/leadhs/dict/sources.csv`) and the evidence database.

## Links

- Strategy turn: `docs/plan/3SM/10_STRATEGY/v0.2.0.md`
- Build phases: `docs/plan/3SM/30_IMPLEMENTATION/v0.2.0/`
- Follow-ups: v0.2.1 ([report-0.2.1.md](report-0.2.1.md)) went one
  level deeper on the official registers; v0.2.2
  ([report-0.2.2.md](report-0.2.2.md)) replaced the N-questions with
  the three-question funnel.

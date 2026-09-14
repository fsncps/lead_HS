---
unit: v0.2.2
built: 2026-09-14
type: unit report (detailed, human-readable)
language: en
---

# Unit v0.2.2 — the three-question funnel (real-network landscape run)

The unit executes the **real-network landscape run** (2026-09-14;
reconnaissance-only: official exports/APIs, no scraping, no
laboratory, minimal cost) and answers the study's three questions as
an assembled **funnel** — every number a database query result, no
typed literals:

- **Q1 — how many paints are on the EU market** (modeled estimate),
- **Q2 — for how many products the identity triple is definitively
  known** (floor),
- **Q3 — for how many of them an SDS-type document is reachable**
  (modeled).

Machine-readable tables and per-source detail:
[probe-report.md](probe-report.md) (published from the evidence DB;
snapshots under the publish-history policy).

## The funnel

- **Q1 — market pool (modeled estimate):** pool model
  `P(cn8) = M × ppp × s(cn8)` → **[85,840–343,360] products**.
  - *M* — producer-count bounds: **800** (CEPE member companies) to
    **3,200** (Eurostat SBS, NACE 20.30, 2020).
  - *ppp* — **107.3 products per producer** (ECAT staged
    manufacturer/product pairs ÷ licence holders: 17,170 ÷ 160).
  - *s(cn8)* — per-CN8 volume shares from staged extra-EU import
    weights (largest: HS 32091000 ≈32%).
  - Epistemic label: a modeled estimate, never a count.
- **Q2 — definitively identifiable (floor):** **17,170** distinct
  (manufacturer, product-ident) pairs — the deduplicated union over
  the staged official registers (currently ECAT only: 17,838
  staged entries, 160 licence holders, 16.0% identity completeness).
  A floor by construction: staging a second register can only raise
  it.
- **Q3 — SDS reachable (modeled):** **3,590** (upper bound) — Σ
  sitemap product counts over the sites with a visible SDS library;
  the match-rate assumption is still pending, so this number can only
  fall.
- **v0.5 ratio (Q2 ÷ Q1): 0.05–0.2** — one twentieth to one fifth of
  the modeled pool is definitively identifiable today.

## Execution record

- **Waves (wave harness, `--wave`/`--budget`/`--staging-db`):**
  - *W1* — staging ingest of the official exports: **ECAT 17,838
    rows** (reconciling exactly with the v0.2.1 record) and **Comext
    6,316 trade rows covering all 13 CN8 codes**; trade dictionary
    verified 13/13 after U6 verification.
  - *W2* — capability pass over the official registers (deferrals
    recorded where exports are JS-bound).
  - *W3* — PE universe: 25 paint/coatings/DIY/artists'-colour
    producers' sites walked at sitemap/recon level; sitemap product
    counts staged with provenance.
  - *W4* — manual records (producer-association member counts etc.).
- **Register disposition (101 rows):** **36 counted, 48
  manual-recorded, 4 blocked, 13 inactive by design**; census 101
  enumerated / 54 probed / 35 counted-metric.
- **Depth matrix (fu8):** tier 1 (observed listings) — 13 PE sites;
  tier 2 (manufacturer + product-ident) — AS-2 (ECAT); tiers 3–4
  (full documents / standardized declarations) — none assigned this
  pass. Largest SDS collections observed: PE-23 1,133, PE-20 659,
  PE-43 401.
- **Reconciliation flags: zero mismatches** — ECAT staged totals
  equal the v0.2.1 capability counts; Comext per-CN8 sums equal the
  v0.2.0 headline anchors.
- **ECAT ∩ Nordic Swan overlap pilot:** explicitly **not computable**
  until a second register is staged (honest absence, no estimate).

## Obstacles and incidents

- **JS-bound register surfaces** (Nordic Swan, IBU, environdec):
  exports pinned as deferrals, recorded honestly; a browser-assisted
  pass or API anchor remains open work.
- **Pool-model defect (caught and fixed this unit):** the first
  implementation of Q1 dropped the products-per-producer factor,
  producing nonsense ratios > 1; restored to the design form
  `M × ppp × s(cn8)` before publication.
- **HTML-as-CSV repair (v0.2.1 defect):** content-sniffing gate
  (`_sniff`) now rejects non-CSV payloads; seven bogus AS-7 findings
  from the v0.2.1 round deleted (see [report-0.2.1.md](report-0.2.1.md)).
- **Publish-history policy (PHASE07 addendum):** unit republishes had
  overwritten earlier report snapshots; `report-publish` now appends
  a timestamp-hash snapshot per publish.
- Blocked sites (4 register rows) and egress-limited desk checks are
  recorded per row with their cause.

## Provenance

- EU Ecolabel Product Catalogue (ECAT), full export:
  <https://data.europa.eu/data/datasets/eu-ecolabel-products> (CSV at
  the public EU storage endpoint; accessed 2026-09-14).
- Eurostat Comext DS-045409 (extra-EU imports, CN8 × partner, 13 CN8
  codes × flows): <https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409>
  (accessed 2026-09-14).
- Producer anchors: <https://www.cepe.org>;
  <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2>
  (accessed 2026-09-12/14).
- Sitemap product counts and per-source verdicts: source register
  (`src/leadhs/dict/sources.csv`), staging database
  (`data/testdata.sqlite`) and evidence database (`db audit` clean).

## Links

- Strategy turn: `docs/plan/3SM/10_STRATEGY/v0.2.2.md` (DRAFT —
  freeze is an explicit user action)
- Design: `docs/plan/3SM/20_DESIGN/units/v0.2.2.md`; build phases:
  `docs/plan/3SM/30_IMPLEMENTATION/v0.2.2/`
- Predecessors: [report-0.2.0.md](report-0.2.0.md),
  [report-0.2.1.md](report-0.2.1.md)

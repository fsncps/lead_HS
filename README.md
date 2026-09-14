# lead_HS — Lead in Paints on the EU Market (HS 3208 / 3209)

Sprachen / Languages / Langues: **[EN](README.md)** · [DE](README.de.md) · [FR](README.fr.md)

A **document-based study** of the **EU market** for paints and varnishes
under tariff headings **3208** (solvent-borne) and **3209**
(water-borne): how many products are on the market, for how many of
them detailed documentation — chiefly **safety data sheets (SDS)** —
can be obtained, and what that documentation shows about **lead
content**.

The study is situated in the context of the Swiss **Cassis-de-Dijon**
exception for lead-containing paints and the related legislation and
decision-making, to which it contributes documented market numbers. It
works exclusively from publicly retrievable documents: **no laboratory,
no physical samples, no paid data sources.**

> **Kurzfassung / Résumé (DE/FR):**
> [`docs/management_summary.md`](docs/management_summary.md) — bilingual
> management summary for decision makers.

*The methodology and data-sources documents linked below are written in
plain language for non-specialist readers, each with a glossary;
specialist terms are also explained at first use.*

## The questions

1. **How many** paint products are on the EU market under HS
   3208/3209? Customs statistics count tonnes and euros, and no product
   register exists — so the study counts **base formulations** (one
   recipe, however many colour shades or container sizes are sold from
   it) and assembles the market size from several independent official
   sources.
2. **For how many products can detailed documentation be obtained** —
   SDS and comparable specifications — and through which sources?
3. **What does that documentation show about lead** — as colour
   pigment, rust inhibitor or drying agent — across a significant
   sample of products?

## Method

The study proceeds in three steps: size the market, obtain
documentation for a significant sample, analyse.

- Product documents are collected from public sources — manufacturer
  and retailer pages, public registers, official statistics — and each
  SDS is screened against a fixed dictionary of lead compounds.
- Suspected findings are corroborated against independent documents for
  the same product (technical data sheets, label texts, older SDS
  versions). There is no laboratory; documentation is the evidence.
- **One limitation is stated up front:** SDS declare classified lead
  compounds from 0.1%, while the Swiss ban engages at 0.01% (100 ppm —
  parts per million) total lead. The documentation method therefore
  sees *declared* lead, not *total* lead; this blind spot is carried in
  every deliverable.

Full method, in plain language with a glossary:
[methodology document](docs/plan/3SM/10_STRATEGY/METHODOLOGY.md).

## Legal context

The **Cassis-de-Dijon principle** (adopted unilaterally by Switzerland
in 2010, THG Art. 16a): products lawfully sold in the EU may, as a
rule, also be sold in Switzerland. Its exceptions are catalogued in the
**VIPaV** (SR 946.513.8); the first entry concerns **lead-containing
paints**, keeping the stricter Swiss limit applicable to imports
(ChemRRV Anhang 2.8: banned from 0.01% total lead). The catalogue is
reviewed every five years, most recently in 2023, under SECO's lead.

The study supplies documented market numbers in this context; it is a
documentation study and takes no position on the regulation itself.
Switzerland enters the study only as this regulatory frame — the
market under study is the EU's.

## Current stage: pool estimate v2 (v0.2.3)

v0.2.3 replaces the single-model pool headline of v0.2.2 with a
**meta-benchmarking vote**: seven independent benchmark quantities
estimate the EU paint pool; each votes into one of five contiguous
magnitude classes (a 20k–50k … e >300k), and a pinned rule converts
the vote into a **dual-level verdict** — SKU level (registry/product
counting) and formulation level (shade/pack-collapsed). Confidence is
claimed only when ≥3 available benchmarks converge without an
exclusive non-adjacent conflict; ties render a span plus flip
assumptions; the vote is fully visible either way.

- **SKU level: class e (>300k products)** — confidence not claimed
  (three benchmarks sit in non-adjacent classes; recorded as open
  items).
- **Formulation level: class c (100k–200k)** — confidence not
  claimed; the level conversion rides a pinned 1–10 shade-collapse
  band, flagged as an assumption (the measurable ECAT key-tier dedup
  is small: name ×1.049, EAN ×1.266).
- New primary-source extractions feed the benchmarks: Swedish
  poison-centre paints/coatings 71,231 (2022); PCN dossiers
  1,444,290 (2021, SWD(2022) 435 Annex 16 — no paint-share constant
  exists); JRC final Ecolabel report (2026): 36,960 certified
  products 03/2025 and the official confirmation that **no
  market-share data exist**; Danish Produktregistret ≈40,000
  hazardous products (aggregates-only — no adapter possible);
  Eurostat SBS verify: 3,300 enterprises (NACE C2030, 2020).
- The funnel section of the published report now carries a
  supersession banner; its v0.2.2 content is kept for the publish
  history.
- The full probe run of 2026-09-14 (waves 1–3) reproduced every
  headline number (ECAT 17,838 reconciled exactly; Comext 6,316
  rows; the blocked/failed site sets identical) — findings, gaps and
  paths in the companion document
  [benchmarking-0.2.3.md](docs/report/benchmarking-0.2.3.md).

Unit report: [report-0.2.3.md](docs/report/report-0.2.3.md);
machine-readable tables (benchmark vote, verdicts, all prior
sections) in the [probe report](docs/report/probe-report.md).

## Previous units

### v0.2.2 — the three-question funnel (2026-09-14)

v0.2.2 executes the **real-network landscape run** (2026-09-14,
reconnaissance-only: official exports/APIs, no scraping) and assembles
the **three-question funnel** — every number a database query, no
typed literals:

- **Q1 — how many paints are on the EU market (modeled estimate):**
  the pool model `P(cn8) = M × ppp × s(cn8)` gives **[85,840–343,360]
  products** — producer bounds 800 (CEPE) to 3,200 (Eurostat SBS
  NACE 20.30) × **107.3 products per producer** (ECAT staged pairs ÷
  licence holders) × per-CN8 volume shares from the staged extra-EU
  trade (largest: HS 32091000 ≈32%). A modeled estimate, never a
  count. **Superseded 2026-09-14 by the v0.2.3 benchmark vote
  (above); kept for the publish history.**
- **Q2 — for how many products the identity triple is definitively
  known (floor):** **17,170** distinct (manufacturer, product-ident)
  pairs over the staged official registers (ECAT: 17,838 entries,
  160 licence holders, 16.0% identity completeness).
- **Q3 — for how many of them an SDS-type document is reachable
  (modeled):** **3,590** (upper bound: Σ sitemap product counts over
  the sites with a visible SDS library; the match-rate assumption is
  pending). The v0.5 ratio (Q2 ÷ Q1) reads **0.05–0.2**.

The 101-row source register is fully dispositioned: **36 counted,
48 manual-recorded, 4 blocked, 13 inactive by design**; the Comext
staging covers **all 13 CN8 codes** (6,316 trade rows); the EU
Ecolabel ∩ Nordic Swan overlap pilot stays explicitly not computable
until a second register is staged. Unit report:
[report-0.2.2.md](docs/report/report-0.2.2.md); machine-readable
tables (CN8 trade, identity, depth matrix, census, reconciliation
flags) in the [probe report](docs/report/probe-report.md).

### v0.2.1 — source capability sounding-out (2026-09-14)

One level deeper on the **official registers** (EU Ecolabel, Nordic
Swan, Blue Angel, INIES, IBU, environdec), each characterised against
the product model (CN8, manufacturer, product-ident) for volume and
depth. **ECAT confirmed a real-product source** (manufacturer +
GTIN/EAN, CN8 via category, depth 2, downloadable CSV); preliminary
N2 numerator **17,838** certified paint products — a floor, never a
market total. The other registers stayed export-to-anchor / inactive
/ without a product-ident; the round's HTML-as-CSV defect was
repaired in v0.2.2. Details:
[report-0.2.1.md](docs/report/report-0.2.1.md).

### v0.2.0 — data-landscape map (2026-09-12)

Reconnaissance-only probe of the registered sources (official
statistics, a trade-association and industry register, and 25
paint/coatings/DIY/artists'-colour sites). Headline numbers: **N1**
market anchors (2024 extra-EU imports: HS 3208 ≈2.5 Mt / ≈€12.2 bn,
HS 3209 ≈2.1 Mt / ≈€6.2 bn; CEPE ≈800 members; SBS NACE 20.30 = 3,200
enterprises); **N2 = 204,693** sitemap-visible product URLs across 23
counted sources; **N3 = 9** sites with a visible SDS library; the
Nordic registers stayed open (SPIN unreachable). Details:
[report-0.2.0.md](docs/report/report-0.2.0.md).

## What earlier research shows

| Lead use | Documented status on the EU market |
|---|---|
| Lead chromate pigments | no lawful supply since 17 Mar 2022 (last authorisations refused) |
| Red-lead (minium) primers | documented niche presence (marine suppliers in DE; SE professionals only) |
| Lead driers in alkyd paints | unknown — the key open question for the survey |
| Artists' oil colours with lead white | documented (NL, IT) — tariff heading 3213 |

Detail and sources:
[LEAD_SDS.md](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md).

## The tool

Data collection and bookkeeping run on **`leadhs`**, a small
command-line program — no server, one machine, a local SQLite
database. Every fetched document is archived unchanged, with its
source, retrieval date and a content hash; every number in a report
traces back to a specific run and document. The tool stores product
data only.

- In this repository: `make setup` (install, migrate the database,
  load the source register, environment preflight) and `make help`
  (index of all commands).
- Outside the repository: build the wheel (`uv build`) and install it
  with a managed interpreter (`uv tool install dist/leadhs-*.whl`),
  always working with an explicit data directory (`leadhs --data-dir
  ~/leadhs-data …`). This path is build-verified; published release
  assets are still pending. An installer for vanilla Windows (no
  make, no preinstalled Python) is a stated goal for v0.3.
- Operations that touch real sites are gated behind an explicit
  `GO=1`.

Detail: [architecture](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) and
[data model](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md); the reviewed
technical design in [20_DESIGN/](docs/plan/3SM/20_DESIGN/).

## Roadmap

| Phase | Content |
|---|---|
| 0 — current | Map the data landscape; the three numbers N1/N2/N3; probe the official registers' capability |
| 1 | Pilot: freeze the lead dictionary; SDS collection and parsing on a first sample |
| 2 | Frame and sample build; documentation collection at full scale; artists' colours annex (3213), capacity permitting |
| 3 | Cross-document corroboration and quality assurance |
| 4 | Analysis; discussion basis; database freeze |

## Where to read more

| Document | What it covers |
|---|---|
| [`management_summary.md`](docs/management_summary.md) | bilingual (DE/FR) summary for decision makers |
| [`METHODOLOGY.md`](docs/plan/3SM/10_STRATEGY/METHODOLOGY.md) | how the market is measured — plain language, glossary included |
| [`DATA_SOURCE.md`](docs/plan/3SM/10_STRATEGY/DATA_SOURCE.md) | every source and the access rules — plain language, glossary included |
| [`ARCHITECTURE.md`](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) | the collection tool and the reporting concept (semi-technical) |
| [`DATA_MODEL.md`](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md) | the evidence database (technical) |
| [`LEAD_SDS.md`](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md) | lead compounds, EU law, what sheets can and cannot reveal (semi-technical) |
| [`10_STRATEGY/MASTER.md`](docs/plan/3SM/10_STRATEGY/MASTER.md) | strategy decisions, open questions, roadmap |
| [`20_DESIGN/`](docs/plan/3SM/20_DESIGN/) | technical design of tool + database |
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) | build-phase plans for the build units (v0.1.1–v0.1.3, v0.2.0–v0.2.3 built) — phase tracking, exit gates |
| [`charts/`](docs/plan/3SM/10_STRATEGY/charts/) | the diagrams, with their sources (referenced from the detail docs) |
| [`3SM README`](docs/plan/3SM/README.md) | plain-language guide to the planning tree |

## Repository layout

    README.md                  this file
    AGENTS.md                  conventions for AI-assisted work on this repo
    Makefile                   operator entrypoint (make help = index)
    pyproject.toml             Python packaging for the leadhs tool
    src/leadhs/                source code of the tool (v0.1.1 probing, v0.1.2 operator layer, v0.1.3 walk counters, v0.2.x staging + waves)
    tests/                     automated offline test suite
    data/                      local working state (gitignored): database, raw store, report intermediates
    docs/report/               published report finals (committed deliberately)
    docs/management_summary.md bilingual management summary (DE/FR), always current
    docs/plan/3SM/             planning notes (3-stage system)
    ├── README.md              plain-language guide to the planning tree
    ├── MASTER.md, LOG.md      project dashboard, lifecycle log
    ├── 10_STRATEGY/           research findings and decisions (what & why)
    │   └── charts/            rendered diagrams (referenced from the detail docs)
    ├── 20_DESIGN/             technical design (how exactly)
    └── _archive/              superseded material

## Status

Tool units v0.1.1–v0.2.3 are built and tested (341 automated offline
tests): evidence database, source register, source probing,
per-source feasibility reports, counting machinery for catalogue walks
(idle until a collection go-ahead), the data-landscape map with the
three headline numbers, the source-level capability sounding-out of
the official registers, the three-question funnel executed on the
real network (2026-09-14), and the pool estimate v2 — the
meta-benchmarking vote with a dual-level magnitude verdict
(2026-09-14): benchmark engine, adapters package, four new primary
extractions, report section with supersession banner — every number a
query result or a dated extraction. The report is published under
`docs/report/`. The methodology stays open to revision as results
come in.

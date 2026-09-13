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

## Current stage: data-landscape map (v0.2.0) + source capability (v0.2.1)

Before any product data is collected, the study maps its **data
landscape**: which sources cover the EU paints market, at what scale,
and with what access to product documentation. That map is built and
the three headline numbers are documented. Every result, including
access refusals, is recorded with its cause, and the database's
provenance audit passes.

The probe round on 2026-09-12 covered the registered sources (official
statistics, a trade-association and industry register, and 25
paint/coatings/DIY/artists'-colour sites). **N1, N2 and N3** are
reported in the
[probe report](docs/report/probe-report.md) and summarised below:

- **N1 — how many paints are on the EU market:** an order of magnitude
  assembled from official statistics. The 2024 trade anchors (Eurostat
  Comext, extra-EU imports, DS-045409) put **HS 3208 at ≈2.5 Mt
  (≈€12.2 bn)** and **HS 3209 at ≈2.1 Mt (≈€6.2 bn)**. Register anchors
  frame the producer side: CEPE represents ≈800 member companies and
  Eurostat SBS counts 3,200 enterprises in NACE 20.30 (2020, paints +
  inks + mastics). The market-size range itself stays an *estimate* —
  the report gives the anchors and the method, never a single number
  presented as fact.
- **N2 — for how many products we have access to data in some form:**
  **204,693** product URLs observed across **23** counted sources
  (sitemap-visible; a floor, dominated by a few large DIY catalogues).
- **N3 — for how many of those detailed specifications such as an SDS
  are obtainable:** **9** sites visibly expose an SDS/document
  library (a site count, not a product count); no product-level
  documentation has been collected yet — that awaits the collection
  go-ahead.

Method at this stage: reconnaissance only — terms of use and access
conditions, availability of APIs or downloads, product-URL counts from
sitemaps, manual checks. Catalogue walks and any product-level
collection await a separate go-ahead. The Norde registers remain
open (SPIN unreachable this round).

### Source capability probed (v0.2.1, built 2026-09-14)

The data-landscape map (v0.2.0) counted the sources; v0.2.1 goes one
level deeper on the **official registers** — the ecolabel and EPD
registries that publish product-level paint data — and characterises
each against the study's product model (CN8 code, manufacturer,
manufacturer product-ident), at what volume and depth. The capability
profiles are in the [probe report](docs/report/probe-report.md)
(Capability profile section).

- The register now holds **7 official registers** (AS-1–AS-7): the EU
  Ecolabel catalogue (ECAT), Nordic Swan, Blue Angel, INIES, IBU and
  environdec, plus AS-1. Four are active; Blue Angel and INIES are
  inactive (XLSX-only or auth-gated exports).
- Each active register's landing page is HTML — the exports are
  documented as **export URL to anchor** at the next pass, recorded
  honestly rather than mis-read as an export.
- **One register is confirmed a real-product source:** the **EU
  Ecolabel catalogue (ECAT)** — it exposes a manufacturer field, a
  product-ident field (GTIN/EAN), a CN8-linkage mechanism (category)
  and data depth 2; its CSV export is downloadable.
- **Preliminary N2 numerator (official registers, floor): 17,838**
  paints & varnishes + performance coatings from ECAT (16,001 + 1,817
  products under the 2014 and 2025 criteria, plus 20 performance
  coatings). This is a **certified/declared subset** of the market — a
  floor, never a market total, and product data still awaits the
  collection go-ahead.
- The other active registers are not yet real-product sources:
  environdec exposes a manufacturer but no product-ident; Nordic Swan
  and IBU are export-to-anchor.

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
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) | build-phase plans for the build units (v0.1.1–v0.1.3, v0.2.0 and v0.2.1 built) — phase tracking, exit gates |
| [`charts/`](docs/plan/3SM/10_STRATEGY/charts/) | the diagrams, with their sources (referenced from the detail docs) |
| [`3SM README`](docs/plan/3SM/README.md) | plain-language guide to the planning tree |

## Repository layout

    README.md                  this file
    AGENTS.md                  conventions for AI-assisted work on this repo
    Makefile                   operator entrypoint (make help = index)
    pyproject.toml             Python packaging for the leadhs tool
    src/leadhs/                source code of the tool (v0.1.1 probing, v0.1.2 operator layer, v0.1.3 walk counters)
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

Tool units v0.1.1–v0.2.1 are built and tested (231 automated offline
tests): evidence database, source register, source probing,
per-source feasibility reports, counting machinery for catalogue walks
(idle until a collection go-ahead), the data-landscape map with the
three headline numbers, and the source-level capability sounding-out
of the official registers. The probe round ran on 2026-09-12; the
report is published under `docs/report/`. The methodology stays open to
revision as results come in.

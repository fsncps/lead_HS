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
[methodology document](docs/study/METHODOLOGY.md).

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

## Where the study stands (current unit: v0.2.4)

The current unit answers the management question per large register:
**what does a product row look like there** — which fields, which
identifier columns, is cross-identification possible — answered with
real downloaded rows where a register publishes them (seeded,
reproducible, n=100 per register) and a cited structural reason where
it does not. Of the six large registers exactly two publish product
rows at all, and only EU Ecolabel ECAT has per-item identifier
columns ([report-0.2.4.md](docs/report/report-0.2.4.md)):

- **AS-2 — EU Ecolabel (ECAT): 100 of 17,013 distinct products** —
  licence number 100%, company + VAT 86%, EAN13/GTIN 17% of the
  sample; EAN ↔ retail catalogues (the v0.3 seeding path) stands on
  real columns.
- **AS-3 — Nordic Swan: 100 of 2,322 distinct paint items** — a real
  export at `?format=csv` (2,424 paint rows, 53 licences), even
  carrying EU Ecolabel licence numbers.
- **ST-1/3/6/7 — no product rows published** (PCN authorities-only;
  SBS; Danish AT; KemI secrecy) — every reason cited.

A curated **`data_sources.csv`** lists the sources with confirmed bulk
product data meeting the gate (confirmed bulk + identity tuple):
exactly AS-2 and AS-3 today. The full-probe round (D39, 2026-09-15)
registered six consultant-candidate sources and found **no third bulk
source**; the **BASTA special probe (D40, 2026-09-17)** then reversed
that for AS-33 via the site's own anonymous web-client route — exact
public counts **195,391 articles / 1,925 companies** and a seeded
100-article sample (identity tuple 100% complete, GTIN 69.8%; only
2/100 articles in the paint groups) — but the server-side paint
filter stays unpinned, so no third `data_sources.csv` row yet.
Details: [report-0.2.4.md](docs/report/report-0.2.4.md) (D37–D40
addenda), the [source register](docs/study/DATA_SOURCE.md), and the
[detailed addenda in this section's history](docs/report/csv-sample.manifest.md).

## Previous units

### v0.2.3 — pool estimate v2: meta-benchmarking vote (2026-09-14)

Seven independent benchmark quantities estimate the EU paint pool;
each votes into one of five contiguous magnitude classes, a pinned
rule converts the vote into a dual-level verdict. Result: **SKU level
class e (>300k products), formulation level class c (100k–200k) —
confidence withheld in both** (non-adjacent conflicts recorded as
open items). Details:
[report-0.2.3.md](docs/report/report-0.2.3.md),
[benchmarking-0.2.3.md](docs/report/benchmarking-0.2.3.md).

### v0.2.2 — the three-question funnel (2026-09-14)

The real-network landscape run (reconnaissance-only) assembles Q1
pool model **[85,840–343,360]** (superseded by the v0.2.3 vote; kept
for the publish history), Q2 identity floor **17,170** distinct
(manufacturer, product-ident) pairs, Q3 SDS-reachable **≈3,590**
(modeled). Every number a database query; source register fully
dispositioned. Details: [report-0.2.2.md](docs/report/report-0.2.2.md).

### v0.2.1 — source capability sounding-out (2026-09-14)

The official registers characterised against the product model:
**ECAT confirmed as a real-product source** (manufacturer + GTIN/EAN,
CSV export), preliminary N2 numerator **17,838** — a floor, never a
market total. Details: [report-0.2.1.md](docs/report/report-0.2.1.md).

### v0.2.0 — data-landscape map (2026-09-12)

Reconnaissance-only probe: **N1** market anchors (2024 extra-EU
imports ≈ HS 3208 €12.2 bn + 3209 €6.2 bn; ≈3,200 enterprises),
**N2 = 204,693** sitemap-visible product URLs, **N3 = 9** sites with a
visible SDS library. Details: [report-0.2.0.md](docs/report/report-0.2.0.md).

## What earlier research shows

| Lead use | Documented status on the EU market |
|---|---|
| Lead chromate pigments | no lawful supply since 17 Mar 2022 (last authorisations refused) |
| Red-lead (minium) primers | documented niche presence (marine suppliers in DE; SE professionals only) |
| Lead driers in alkyd paints | unknown — the key open question for the survey |
| Artists' oil colours with lead white | documented (NL, IT) — tariff heading 3213 |

Detail and sources:
[LEAD_SDS.md](docs/study/LEAD_SDS.md).

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

Detail: [architecture](docs/study/ARCHITECTURE.md) and
[data model](docs/study/DATA_MODEL.md); the reviewed
technical design in [20_DESIGN/](docs/plan/3SM/20_DESIGN/).

## How the work progressed — a review of v0.1 and v0.2

The study was built bottom-up, in small verified units, and that
process shaped what it can say today.

**v0.1 (units v0.1.1–v0.1.3): build the instrument.** The goal was
never numbers first — it was a trustworthy collection tool. Unit
v0.1.1 delivered a slim command-line toolkit (evidence database,
source register, probing commands); v0.1.2 wrapped it into an
operator layer (a `make` entrypoint, `GO=1` gates for anything that
touches real sites) and probed all registered sources politely —
robots/terms checks, one-finding-per-source feasibility records;
v0.1.3 mapped the data landscape and built the counting machinery for
catalogue walks (deliberately left idle until a collection go-ahead).
Method throughout: every fetched document archived unchanged with
hash and retrieval date; every number traceable to a run; honest
no-data records instead of silent failures; no laboratory, no paid
sources, no scraping beyond an explicit go. By the end of v0.1 the
study knew *which sources exist and what each will yield* — not yet
how big the market is.

**v0.2 (units v0.2.0–v0.2.4): point the instrument at the numbers.**
The goals turned numbers-first: market scale (N1), access coverage
(N2), reachable documentation (N3). v0.2.0 produced the
landscape map on real data. v0.2.1 sounded out the official
registers and found the first real product source (EU Ecolabel ECAT,
with manufacturer + GTIN/EAN identity columns). v0.2.2 executed the
three-question funnel on the staged data — how big is the pool
(modeled), how many product identities are definitively known
(a counted floor), how many SDS are reachable (modeled). v0.2.3
replaced the single-model pool estimate with a meta-benchmarking
vote of independent quantities, yielding magnitude-class verdicts
with confidence discipline. v0.2.4 turned the question down to the
row level: what does one product record actually look like in each
register — and discovered that of the large registers only the two
ecolabel catalogues publish bulk product rows at all, with BASTA
addable through its own anonymous web interface once a structural
question clears.

**What the reviews kept changing.** The scope moved with the
evidence: Swiss-market metrics were dropped early (the market under
study is the EU's; Switzerland is the regulatory frame only), the
"walk everything" plan was superseded by reconnaissance-first
discipline, and the deliverable sharpened from a general data map to
a numbers-first answer for the actors around the Swiss lead-paint
exception. What stayed fixed: the formulation as unit of counting,
the corroboration-instead-of-lab constraint, the declared-vs-total
lead blind spot stated in every deliverable, and provenance on every
number.

## Planned next: from bulk download to one product table (v0.3)

The next build phase turns the confirmed bulk sources into one
consolidated product database, in two layers:

**1. Bulk source download (raw layer).** Each confirmed bulk source —
EU Ecolabel (≈17,013 distinct products), Nordic Swan (≈2,322), and
BASTA (195,391 articles; pinned via its own anonymous web-client
route) — gets downloaded into a **per-source raw table**: verbatim,
unfiltered, one row per source record, with the manufacturer name,
product identifier and product-group code exactly as the source
writes them. The downloads are repeatable (interrupt, resume), incremental
(rerun updates only new/changed records via a change journal) and
manifest-driven (a committed per-source manifest defines the table
shape before any data flows; oversize records spill to the raw store,
nothing is dropped). Politeness: list-endpoint-first crawling with
rate limits and backoff, seeded through the existing `GO=1`-gated CLI
(`leadhs raw init <source>` / `leadhs raw seed <source>`).

**2. Deterministic normalization and merging (matching layer).** To
merge the same product seen in several sources, names and identifiers
are normalized deterministically (no LLM/machine-learning matching —
every match must stay explainable and reproducible): Unicode
diacritic folding, case folding, legal-form token stripping
("Foo-Bar Ltd." ≙ "Foo Bar Limited" → `foo bar`), identifier
uppercasing/padding/prefix cleanup ("ABC-123/B" ≙ "abc00123b" →
`ABC123B`). Records are then linked in tiers: exact keys first
(GTIN/EAN; normalized identifier within the same normalized
manufacturer), then scored near-matches (Jaro-Winkler, token-set
similarity) restricted to small candidate blocks so that 200k+ rows
stay tractable. Each candidate link carries a verdict —
`auto_match` (high score / exact-key backed) / `review` (human
queue) / `no_match` — with method and scores stored per pair, so the
merged product view is fully auditable and corrections are
append-only. The merged output: **manufacturer table and product
table** collapsed to the study's formulation unit, every product
carrying its per-source observations and each match's evidence tier.

Details: the strategy files
[`RAW_SOURCING.md`](docs/plan/3SM/10_STRATEGY/RAW_SOURCING.md) and
[`MATCHING.md`](docs/plan/3SM/10_STRATEGY/MATCHING.md) (norms,
thresholds and library choice are pinned there as the pending
adoption decisions R1–R9 and MA1–MA9).

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
| [`METHODOLOGY.md`](docs/study/METHODOLOGY.md) | how the market is measured — plain language, glossary included |
| [`DATA_SOURCE.md`](docs/study/DATA_SOURCE.md) | every source and the access rules — plain language, glossary included |
| [`ARCHITECTURE.md`](docs/study/ARCHITECTURE.md) | the collection tool and the reporting concept (semi-technical) |
| [`DATA_MODEL.md`](docs/study/DATA_MODEL.md) | the evidence database (technical) |
| [`LEAD_SDS.md`](docs/study/LEAD_SDS.md) | lead compounds, EU law, what sheets can and cannot reveal (semi-technical) |
| [`10_STRATEGY/MASTER.md`](docs/plan/3SM/10_STRATEGY/MASTER.md) | strategy decisions, open questions, roadmap |
| [`20_DESIGN/`](docs/plan/3SM/20_DESIGN/) | technical design of tool + database |
| [`30_IMPLEMENTATION/`](docs/plan/3SM/30_IMPLEMENTATION/) | build-phase plans for the build units (v0.1.1–v0.1.3, v0.2.0–v0.2.4 built) — phase tracking, exit gates |
| [`charts/`](docs/study/charts/) | the diagrams, with their sources (referenced from the detail docs) |
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
    docs/study/                study detail documentation (methodology, sources, architecture,
                               data model, lead background; DE/FR translations, charts/)
    docs/plan/3SM/             planning notes (3-stage system)
    ├── README.md              plain-language guide to the planning tree
    ├── MASTER.md, LOG.md      project dashboard, lifecycle log
    ├── 10_STRATEGY/           research findings and decisions (what & why) —
    │                          slim topic summaries; detail lives in docs/study/
    ├── 20_DESIGN/             technical design (how exactly)
    └── _archive/              superseded material

## Status

Tool units v0.1.1–v0.2.4 are built and tested (412 automated offline
tests): evidence database, source register, source probing,
per-source feasibility reports, counting machinery for catalogue walks
(idle until a collection go-ahead), the data-landscape map with the
three headline numbers, the source-level capability sounding-out of
the official registers, the three-question funnel executed on the
real network (2026-09-14), the pool estimate v2 — the
meta-benchmarking vote with a dual-level magnitude verdict — and the
management CSV sample with per-registry product-row evidence
(2026-09-14): benchmark engine, adapters package, four new primary
extractions, report section with supersession banner — every number a
query result or a dated extraction. The report is published under
`docs/report/`. The methodology stays open to revision as results
come in.

# lead_HS — Lead in Paints: Swiss External Trade and the Cassis-de-Dijon Context (HS 3208 / 3209)

A **document-based** study building a discussion basis for decision makers:
do lead-containing paints under tariff headings **3208** (solvent-borne) and
**3209** (water-borne) reach the **Swiss market**, how common are they — and
does the **Cassis-de-Dijon exception** for lead paints still have a factual
field of application?

Everything rests on publicly retrievable documents — safety data sheets,
customs statistics, legal texts, producer catalogues. **No laboratory, no
purchased samples, no paid market reports.** Minimal cost by design.

> **Kurzfassung / Résumé (DE/FR):**
> [`docs/management_summary.md`](docs/management_summary.md) — bilingual
> management summary for decision makers; a living document, always kept
> current.

*Specialist terms are explained at first use. The deep-dive documents linked
below carry the detail; the methodology and data-sources documents are also
written for non-technical readers, each with a plain-language glossary.*

## The question

Switzerland is not in the EU or the EEA. Its paint market is fed by domestic
production, EU imports and third-country imports — each governed
differently. The study asks:

1. What does Swiss external trade in paints (3208/3209) look like —
   volumes, values, and above all *origins*?
2. Which products on the Swiss market contain lead **according to their own
   documentation** — as pigment, rust-inhibitor or drying agent?
3. What share is that — and where are the seams between EU-lawful goods,
   the Swiss lead exception, and third-country imports?

Lead-in-paint surveys exist for many countries (a 2026 Mexican study found
55% of paints above 90 ppm lead) — **but none for the EU/EEA, and none for
Switzerland**. Europe's "essentially none, it's regulated" assumption has
never been tested against product documentation — and Switzerland sits
partly outside the EU rules that assumption rests on.

## Why lead is (still) plausible

| Role in the paint | Typical compounds | EU legal situation |
|---|---|---|
| Colour pigment | lead chromate ("chrome yellow"), white lead (historic) | banned in paints |
| Rust-inhibiting additive | red lead / minium, in anti-corrosion primers | **not restricted** — the classic remaining use |
| Drying agent | lead octoate, lead naphthenate, in solvent-borne alkyd paints | **not restricted** |

So even inside the EU, the anti-corrosion and drier routes stay open — the
signal, if any, lives in professional and industrial solvent-borne coatings
(3208). And Swiss law is stricter: paints with **0.01% (100 ppm — parts per
million) total lead or more** are banned in Switzerland (ChemRRV,
Anhang 2.8), far below anything the EU prohibits in these uses.

## The regulatory seam: Cassis de Dijon

The **Cassis-de-Dijon principle**: products lawfully sold in the EU may, as
a rule, also be sold in Switzerland without renewed Swiss approval (adopted
unilaterally in 2010, THG Art. 16a). Its exceptions are catalogued in the
**VIPaV** (SR 946.513.8) — and the very first entry is **lead-containing
paints and varnishes**. That entry is why an EU-lawful red-lead primer
(legally sold in Germany, say) cannot simply flow into Switzerland despite
failing the Swiss 100 ppm ban.

The exceptions catalogue is **reviewed every five years** (last review 2023:
keep; next around 2028, SECO's lead; enforcement sits with the BAFU). The
office that requested an exception remains responsible for its regulation's
monitoring and revision — where this study's discussion basis is meant to
land. Whether the lead exception has a **factual field of application** —
whether there are lead paints on the EU market at all — is exactly the
question nobody can currently answer, and the one this study addresses with
documented evidence.

## What we already know (first research pass, 2026-08-31)

| Stream | Status on the EU market |
|---|---|
| Lead chromate pigments | **no lawful supply since 17 Mar 2022** (Commission refused the last authorisations) |
| Red lead / minium primers | **documented presence in niches** (marine suppliers in Germany; Sweden: licensed professionals only) |
| Lead driers in alkyd paints | **unknown** — the key open empirical question |
| Artists' oil colours (lead white) | **documented presence** (NL, IT) — but tariff heading 3213, invisible in paint statistics |
| Legacy road paints | 63% of 236 sampled European road paints contained lead (Turner & Filella 2022) |

One structural problem frames everything: **nobody counts paint products**.
Customs statistics count tonnes and euros, not products; no register exists.
The study therefore counts **base formulations** (one paint recipe, however
many colour shades or tin sizes are sold from it) and estimates how many
exist by combining several independent sources — producer catalogues,
Nordic product registers, production statistics.

## How the study works

1. **Swiss trade statistics** (the customs administration's swiss-impex
   platform, broken down by partner country) structure the market and its
   origins.
2. **Product catalogues** (producers, retailers, B2B portals — web shops
   for professional customers), collected politely and de-duplicated,
   become the list of products to draw from.
3. **Safety data sheets** (SDS — the standardized hazard-information sheets
   that accompany professional chemical products) are checked against a
   fixed dictionary of lead substances. A sheet also reveals whether a
   paint is water- or solvent-borne — in effect the customs code the
   product never carried.
4. **Cross-checking instead of a laboratory**: every suspected lead product
   is corroborated against independent documents about the same product;
   blind spots are stated openly as limitations.
5. **Sampling by precision, not percentage**: roughly 2,000–3,000 products
   across eight market segments, each split by origin (Swiss / EU /
   third-country).

Full detail, in plain language with a glossary:
[methodology document](docs/plan/3SM/10_STRATEGY/METHODOLOGY.md).

How a single product is judged:

![How a product is judged: does its safety data sheet list a lead compound, is it declared at 0.1% or more, does the Swiss 100 ppm ban plausibly apply, and do independent documents agree?](docs/plan/3SM/10_STRATEGY/charts/lead-decision-tree.png)

## The evidence engine: a small, honest program

Collection is automated by a small command-line program ("leadhs") — no
website, no server, one machine. Its job is to keep the evidence trail
airtight: every fetched document is archived as an untouched original,
with its source, retrieval date and a digital fingerprint of its content;
every observation is tied to the run that produced it; nothing is ever
overwritten — corrections are new entries, so every number in the final
report traces back to a specific document.

![The evidence engine: the program's parts, the raw document archive and the evidence database](docs/plan/3SM/10_STRATEGY/charts/architecture-components.png)

Working documents:
[architecture](docs/plan/3SM/10_STRATEGY/ARCHITECTURE.md) and
[data model](docs/plan/3SM/10_STRATEGY/DATA_MODEL.md); the reviewed
technical design in [20_DESIGN/](docs/plan/3SM/20_DESIGN/).

## First step: checking the sources (next up)

Before any large-scale collection, each planned source gets one small,
polite test visit — does the Swiss customs platform deliver usable
exports? Which catalogues can be read? Is the Nordic product-register
database processable? Every check is recorded; a refusal is a documented
finding, never an obstacle pushed through:

![How each source is checked: robots and terms are respected, requests are spaced at least two seconds apart, blocks and surprises are documented as findings, samples are archived untouched](docs/plan/3SM/10_STRATEGY/charts/probe-process.png)

The register of all sources and the access rules, in plain language:
[data sources document](docs/plan/3SM/10_STRATEGY/DATA_SOURCE.md).

## Legal workstream

In parallel, a dossier compiles — purely from public legal texts — the EU
lead restrictions and their status, the Swiss counterparts, the
Cassis-de-Dijon frame and its five-yearly review, and where the seams are.
Substance: [lead & SDS document](docs/plan/3SM/10_STRATEGY/LEAD_SDS.md).

## Roadmap

| Phase | Content |
|---|---|
| 0 | Close research gaps: Swiss customs extraction; verify current legal texts; EU refusal reference; PCN statistics; SPIN query; catalog counts |
| 1 | Pilot: freeze the lead dictionary, test SDS collection and parsing |
| 2 | Build the product frame, draw the sample, collect at full scale; artists' colours census (3213) in parallel |
| 3 | Cross-document corroboration and quality assurance |
| 4 | Analysis; the decision-makers' discussion basis; freeze the database |

## Expected result (hypotheses to test, not conclusions)

- Consumer decorative paints: ≈ 0% intentional lead.
- Professional/industrial solvent-borne segments: niche documented presence;
  lead driers unknown.
- Third-country imports: markedly higher, mirroring source markets.
- Artists' oil colours: the clearest case of lawful lead presence.
- A documented gap map EU vs Switzerland — every claim traceable to a
  public document, including the caveat that the Swiss 100 ppm ban sits
  *below* the EU safety-data-sheet declaration floor (0.1%): a paint can be
  EU-lawful, fully documented, and still exceed the Swiss ban invisibly.

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
| [`charts/`](docs/plan/3SM/10_STRATEGY/charts/) | the diagrams used above, with their sources |
| [`3SM README`](docs/plan/3SM/README.md) | plain-language guide to the planning tree |

## Repository layout

    README.md                  this file
    AGENTS.md                  conventions for AI-assisted work on this repo
    docs/management_summary.md bilingual management summary (DE/FR), always current
    docs/plan/3SM/             planning notes (3-stage system)
    ├── README.md              plain-language guide to the planning tree
    ├── MASTER.md, LOG.md      project dashboard, lifecycle log
    ├── 10_STRATEGY/           research findings and decisions (what & why)
    │   └── charts/            rendered diagrams (three in active use)
    ├── 20_DESIGN/             technical design (how exactly)
    └── _archive/              superseded material

## Status

Strategy for the first build unit is complete; its technical design (tool +
evidence database) is written and has passed a critical and an engineering
review (2026-09-11; findings tracked in the
[fix plan](docs/plan/3SM/20_DESIGN/FIXPLAN_2026-09-11.md)). Next: build the
probing tool and run the source checks (roadmap Phase 0). Nothing is frozen
— the methodology stays open to revision as Phase 0 results come in.

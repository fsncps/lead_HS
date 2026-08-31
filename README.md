# lead_HS — Lead in Paints on the European Market (HS 3208 / 3209)

A research project to find out **which paints and varnishes sold in the
European Economic Area contain lead, and how common they are** — and to build
a reusable database of checked products as the evidence base.

---

## The question

Paints sold in the European Economic Area (EEA; German: *EWR* — the EU
countries plus Iceland, Liechtenstein and Norway) are grouped for customs
purposes under tariff headings:

- **3208** — paints and varnishes based on synthetic or chemically modified
  natural polymers, in a solvent base ("solvent-borne");
- **3209** — the same kind of polymer paints, but water-based.

The study asks three things:

1. **How many distinct paint products** under these two headings are on the
   EEA market at all?
2. **Which of them contain lead** — as pigment, rust-inhibitor or drying
   agent?
3. **What share of the market does that represent**, with what statistical
   confidence?

Nobody has measured this for Europe. Lead-in-paint surveys exist for many
developing and emerging countries (IPEN and others have tested thousands of
paints worldwide — in a 2026 Mexican study, 55% of paints exceeded 90 ppm
lead), but **no EU/EEA-wide market survey exists**. For Europe the answer is
widely assumed to be "essentially none, it's regulated" — but that assumption
has never been tested against product data. That is the gap this project
fills.

## Why lead is (still) plausible in European paints

Lead shows up in paint for three reasons, not one:

| Role | Typical compounds | Legal situation in the EU |
|---|---|---|
| **Colour pigment** | lead chromate ("chrome yellow"), lead sulfochromate, lead chromate molybdate (red-orange); white lead (historic) | banned — subject to authorisation with a 2015 sunset date, banned from consumer sale; white lead and lead sulfates banned *in paints* outright (with an art-restoration exception) |
| **Rust-inhibiting additive** | red lead / minium, in anti-corrosion primers for steel and ships | **not restricted** — the classic remaining use |
| **Drying agent** | lead octoate, lead naphthenate, in solvent-borne alkyd paints | **not restricted** |

In other words: the pigment route into EU paint is legally closed, but the
anti-corrosion and drier routes remain open, and imports from less-regulated
markets are a further possible source. Where the signal plausibly lives:
professional and industrial solvent-borne coatings (3208), much less so
water-borne wall paints (3209).

## The core problem: nobody counts paint products

There is **no register anywhere in the EEA that counts distinct paint
products**. Customs statistics count tonnes and euros, not products — and the
nomenclature itself distinguishes only **11 eight-digit codes** under
3208+3209 (nine solvent-borne, two water-borne). A product does not even
intrinsically "have" a tariff code: the code applies to a customs
consignment, so the study has to assign codes itself (see below).

What we do know so far (first research pass, 2026-08-31):

| Anchor | Number | Source |
|---|---|---|
| Paint/varnish/ink manufacturers in the EU | ~3,200–3,300 companies | Eurostat structural business statistics |
| Industry body (CEPE) coverage | ~800 members ≈ 85% of a ~€17 bn market | CEPE |
| EU trade in 3208+3209 (2023) | ~€1.1 bn imports / ~€4.3 bn exports | Eurostat Comext |
| Distinct products counted by anyone | **none found** | negative research result |

A second problem is definitional: does "one product" mean one **base
formulation** (one recipe, however many colour shades) or one **shop item**
(each colour × tin size × brand)? The difference spans one to three orders of
magnitude. This study counts **base formulations**, the same way official
product registers do.

## Suggested methodology (brainstormed, subject to refinement)

Everything below is the current strategy-level thinking. It is documented in
detail under [`docs/plan/3SM/`](docs/plan/3SM/) and deliberately not final.

### 1. Estimate the population by triangulation

Since no single source counts products, combine several independent ones:

- **Poison-centre notifications (PCN).** Hazardous mixtures sold in the EU
  must be notified to poison centres, formulation by formulation. This is the
  closest thing to a product register, EEA-wide — but it covers only
  *hazardous* mixtures, its statistics are not openly published, and a 2025
  enforcement pilot found ~19% of inspected mixtures were never notified.
- **The Nordic SPIN database.** Denmark, Sweden, Norway and Finland maintain
  comprehensive chemical product registers, merged into one public database
  (~1 GB download). It can say how many "paints"-category preparations
  contain a given lead substance — aggregated counts, no product names. This
  gives a free pilot estimate for a quarter of northern Europe before any
  data collection starts.
- **Producer and trade statistics** (Eurostat PRODCOM/Comext, industry
  associations) to scale and cross-check.
- **Producer catalogues and shops** (B2B portals, DIY chains) — scraped and
  de-duplicated down to formulation level, these become the actual sampling
  list.

Working hypothesis to be pinned down: **tens of thousands of formulations**
EEA-wide (10⁴–10⁵).

### 2. Read safety data sheets (SDS)

For nearly every professional paint there is a safety data sheet
(*Sicherheitsdatenblatt*). EU rules (REACH, as amended by Regulation (EU)
2020/878) force its Section 3 "Composition" to list any classified hazardous
ingredient at **≥ 0.1% by weight** — and the lead compounds of interest carry
severe classifications (carcinogenic / toxic to reproduction). So the plan:

- collect SDS for sampled products (manufacturer websites, B2B portals);
- search them against a **lead dictionary** — a fixed list of lead substances
  identified by their official chemical identifiers (CAS registry numbers,
  EC numbers): lead chromates, red lead, white lead, lead octoate, lead
  naphthenate and so on;
- record what is found: substance, concentration range (sheets may give
  ranges, not exact values), warnings, and the sheet's date (an outdated
  sheet format is itself a warning sign).

A useful side effect: Section 3 also reveals the paint's binder chemistry and
whether it is water- or solvent-borne — exactly the facts that determine its
tariff code (e.g. "water-borne acrylic → 3209"). **The sheet lets the study
assign the customs code the product never carried.**

### 3. Verify in the laboratory what the sheets cannot show

Two blind spots by design:

- lead **below 0.1%** (impurities in pigments, residues) is invisible in a
  sheet;
- sheets are sometimes sloppy — international studies repeatedly find
  hazardous ingredients under-declared or sheets years out of date.

So a small set of physical samples (~30–60 tins, deliberately including any
suspects found) goes to a lab: quick XRF screening (X-ray fluorescence, the
same handheld scanners used for lead paint in housing) plus chemical
digestion and ICP analysis for confirmation. This bounds the error of the
sheet-based results rather than replacing them.

### 4. Sample by precision, not by percentage

The original intuition was "check about 10% of products". The better framing:
**statistical precision depends on how many items you check, not on what
fraction of the market that represents.** Checking 385 products from a group
gives ±5% precision; 811 gives ±1.5% for rarer occurrences — whether the
group holds 4,000 or 400,000 products.

The market is split into eight groups with different lead expectations, and a
few hundred products are drawn from each:

| Group | Type | Lead expectation |
|---|---|---|
| S1 | Decorative water-borne (3209) | near zero |
| S2 | Decorative solvent-borne / alkyd | very low (driers possible) |
| S3 | Anti-corrosion primers | **high (red lead)** |
| S4 | Marine & container coatings | high |
| S5 | Road-marking paints | moderate |
| S6 | Industrial OEM (coil, machinery, refinish) | moderate |
| S7 | Imported brands | high (source-market prevalence) |
| S8 | Everything else (wood, floor, specialty) | low |

Total: **roughly 2,000–3,000 products** — which, if the population guess is
right, coincidentally lands near the original 10% intuition, but for the
right reason.

## Roadmap

| Phase | Content |
|---|---|
| 0 | Close research gaps: extract poison-centre statistics, download and query the Nordic SPIN database, production statistics, shop category counts |
| 1 | Pilot: finalize the lead dictionary, test SDS collection and parsing on 1–2 groups |
| 2 | Build the product frame, draw the sample, collect sheets at full scale |
| 3 | Laboratory validation subset |
| 4 | Analysis, report, freeze the database |

## Expected result (hypotheses to test, not conclusions)

- Consumer decorative paints: ≈ 0% intentional lead (the ban structure works).
- Professional/industrial solvent-borne segments: single-digit percentages.
- Imports: markedly higher, mirroring source-market prevalence (global
  studies show >50% in several countries).

## Repository layout

    README.md                  this file
    docs/plan/3SM/             planning notes (3-stage system)
    ├── README.md              plain-language guide to the planning tree
    ├── MASTER.md              project dashboard
    ├── LOG.md                 lifecycle log
    └── 10_STRATEGY/           research findings and decisions
        ├── MASTER.md          decisions, open questions, roadmap
        ├── methodology.md     population, sampling, validation detail
        └── lead_sds.md        lead compounds, EU law, SDS feasibility

## Status

Planning stage (strategy, unit v0.1). Detailed working documents:
[`docs/plan/3SM/`](docs/plan/3SM/). Nothing is frozen; methodology may still
change as Phase 0 research comes in.

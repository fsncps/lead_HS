# lead_HS — Lead in Paints: Swiss External Trade and the EU Bilateral Context (HS 3208 / 3209)

A **document-based** study building a discussion basis for decision makers:
do lead-containing paints under tariff headings **3208** (solvent-borne) and
**3209** (water-borne) reach the **Swiss market** through external trade, how
common are they, and what does the **bilateral EU–Switzerland framework**
mean for their regulation?

Everything here rests on publicly retrievable documents — safety data sheets,
customs statistics, legal texts, producer catalogues. **No laboratory, no
purchased samples, no paid market reports.** Minimal cost by design.

> **Kurzfassung / Résumé (DE/FR):**
> [`docs/management_summary.md`](docs/management_summary.md) — bilingual
> management summary for decision makers; a living document, always kept
> current.

---

## The question

Switzerland is not a member of the EU or the EEA. Its paint market is fed by
domestic production, imports from the EU, and imports from third countries —
each stream governed differently. The study asks:

1. **What does Swiss external trade in 3208/3209 look like** — volumes,
   values, and above all *origins* (Swiss customs statistics)?
2. **Which products on the Swiss market contain lead according to their own
   documentation** — as pigment, rust-inhibitor or drying agent?
3. **What share does that represent**, and where does the regulatory frame
   have seams — EU rules that apply to EU-made goods but bind third-country
   imports (or the Swiss market itself) differently under the bilateral
   agreements?

Nobody has measured this. Lead-in-paint surveys exist for many developing and
emerging countries (IPEN and others have tested thousands of paints; in a
2026 Mexican study 55% of paints exceeded 90 ppm lead), but **no survey
exists for the EU/EEA — and none for Switzerland**. For Europe the answer is
widely assumed to be "essentially none, it's regulated". That assumption has
never been tested against product documentation — and Switzerland sits
partly outside the EU rules the assumption rests on.

## Why lead is (still) plausible

Lead appears in paint for three reasons, not one:

| Role | Typical compounds | EU legal situation |
|---|---|---|
| **Colour pigment** | lead chromate ("chrome yellow"), lead sulfochromate, lead chromate molybdate (red-orange); white lead (historic) | banned — authorisation sunset 2015, banned from consumer sale; white lead and lead sulfates banned *in paints* outright (art-restoration exception) |
| **Rust-inhibiting additive** | red lead / minium, in anti-corrosion primers for steel and ships | **not restricted** — the classic remaining use |
| **Drying agent** | lead octoate, lead naphthenate, in solvent-borne alkyd paints | **not restricted** |

Two things follow. Even inside the EU, the anti-corrosion and drier routes
remain open — the signal, if any, lives in professional and industrial
solvent-borne coatings (3208), not water-borne wall paints (3209). And
Swiss law runs on its own track: Swiss chemicals legislation has been
substantially aligned with EU REACH/CLP rules, but whether every EU lead
restriction carries over, and how third-country imports are controlled, is
exactly the kind of question this study documents (see the legal workstream
below; details still to be verified).

## The core problem: nobody counts paint products

There is **no register that counts distinct paint products** — not in the
EEA, and not in Switzerland. Customs statistics count tonnes and euros, not
products; the nomenclature itself distinguishes only **11 eight-digit codes**
under 3208+3209 (nine solvent-borne, two water-borne). A product does not
even intrinsically "have" a tariff code — the code applies to a customs
consignment, so the study assigns codes itself (see below).

What the first research pass (2026-08-31) established, as EU-side context:

| Anchor | Number | Source |
|---|---|---|
| Paint/varnish/ink manufacturers in the EU | ~3,200–3,300 companies | Eurostat structural business statistics |
| Industry body (CEPE) coverage | ~800 members ≈ 85% of a ~€17 bn market | CEPE |
| EU trade in 3208+3209 (2023) | ~€1.1 bn imports / ~€4.3 bn exports | Eurostat Comext |
| Swiss trade in 3208+3209 | **to be extracted** (Phase 0) | Swiss customs (EZV/swiss-impex) |
| Distinct products counted by anyone | **none found** | negative research result |

A second problem is definitional: does "one product" mean one **base
formulation** (one recipe, however many colour shades) or one **shop item**
(each colour × tin size × brand)? The difference spans one to three orders
of magnitude. This study counts **base formulations**, the same way official
product registers do.

## Suggested methodology (brainstormed, subject to refinement)

Current strategy-level thinking, documented in detail under
[`docs/plan/3SM/`](docs/plan/3SM/) and deliberately not final.

### 1. Start from Swiss trade statistics

Swiss customs data (the Federal Customs Administration, EZV, publishes trade
statistics via its *swiss-impex* platform) should give imports and exports
at 8-digit code level **by partner country**. That single extract structures
the whole study: it shows which segments matter in Switzerland and which
origins (EU vs third countries) dominate each — the exact seams a bilateral
framework creates. Availability and granularity still to be confirmed in
Phase 0.

### 2. Estimate the product population by triangulation

No single source counts products, so combine:

- **Swiss producer and retailer catalogues** (B2B portals, DIY chains,
  brand sites), scraped and de-duplicated to formulation level — this
  becomes the actual sampling frame for the Swiss market;
- **EU-side proxies for scaling and comparison** (as context, not target):
  poison-centre notifications (PCN — the closest thing to an EU product
  register, but covering only hazardous mixtures and not openly published);
  the Nordic SPIN database (~1 GB public download from the Danish, Swedish,
  Norwegian and Finnish product registers, which can report how many
  "paints"-category preparations contain a given lead substance — counts,
  no names); Eurostat production statistics;
- **Swiss structural statistics** on domestic paint production.

### 3. Read safety data sheets (SDS)

For nearly every professional paint there is a safety data sheet
(*Sicherheitsdatenblatt*; on the Swiss market typically available in German,
French, Italian and/or English from producer portals). EU-format rules
(REACH Annex II, as amended by Regulation (EU) 2020/878) force Section 3
"Composition" to list classified hazardous ingredients at **≥ 0.1% by
weight** — and the lead compounds of interest carry severe classifications.
So the plan:

- collect SDS for sampled products (manufacturer websites, B2B portals);
- search them against a **lead dictionary** — a fixed list of lead
  substances identified by official chemical identifiers (CAS registry
  numbers, EC numbers): lead chromates, red lead, white lead, lead octoate,
  lead naphthenate and so on;
- record what is found: substance, concentration range (sheets may give
  ranges, not exact values), warnings, and the sheet's date (an outdated
  format is itself a warning sign).

A useful side effect: Section 3 also reveals binder chemistry and whether
the paint is water- or solvent-borne — exactly the facts that determine its
tariff code (e.g. "water-borne acrylic → 3209"). **The sheet lets the study
assign the customs code the product never carried.**

### 4. Corroborate between documents — no laboratory

There is no lab in this project, so the two known blind spots cannot be
bounded experimentally:

- lead **below 0.1%** (impurities, residues) is invisible in a sheet;
- sheets are sometimes sloppy — international studies repeatedly find
  hazardous ingredients under-declared or sheets years out of date.

The response is **cross-document corroboration**: for every suspected lead
product, check independent documents about the *same* product — technical
data sheets, label text, retailer listings, producer declarations, older SDS
versions, and the same brand's sheets across national market variants.
Consistent silence across several documents is weak evidence of absence;
contradiction between documents is itself a finding worth reporting. The
blind spots become clearly stated limitations of the discussion basis
rather than quietly ignored risks.

### 5. Sample by precision, not by percentage

The original intuition was "check about 10% of products". The better framing:
**statistical precision depends on how many items you check, not on what
fraction of the market that represents.** Checking 385 products from a group
gives ±5% precision; 811 gives ±1.5% for rarer occurrences — whether the
group holds 4,000 or 400,000 products.

The market is split into eight groups with different lead expectations, and
each group is additionally split by **origin** (Swiss-made / EU import /
third-country import), weighted by the customs statistics from step 1:

| Group | Type | Lead expectation |
|---|---|---|
| S1 | Decorative water-borne (3209) | near zero |
| S2 | Decorative solvent-borne / alkyd | very low (driers possible) |
| S3 | Anti-corrosion primers | **high (red lead)** |
| S4 | Marine & container coatings | high |
| S5 | Road-marking paints | moderate |
| S6 | Industrial OEM (coil, machinery, refinish) | moderate |
| S7 | Third-country imported brands | **high** (source-market prevalence) |
| S8 | Everything else (wood, floor, specialty) | low |

Total: **roughly 2,000–3,000 products** — which, if the population guess is
right, coincidentally lands near the original 10% intuition, but for the
right reason.

## The legal/bilateral workstream (documents only)

Alongside the market study, a dossier compiles — purely from public legal
texts — what decision makers need on the table:

- which EU lead restrictions (REACH Annex XVII/XIV) apply to paints, and
  their status;
- how Swiss chemicals legislation (ChemG/ChemO, substantially REACH/CLP
  aligned since the 2015 harmonization) covers the same compounds —
  gap map EU vs CH;
- what the EU–Swiss bilateral framework (e.g. the Mutual Recognition
  Agreement's sectoral coverage) means for paints moving between the
  markets, and how third-country imports are controlled;
- where the seams are: regulatory gaps, enforcement data, notification
  statistics.

These items are flagged for verification in Phase 0; the strategy documents
track what is sourced versus open.

## Roadmap

| Phase | Content |
|---|---|
| 0 | Close research gaps: Swiss customs extraction (EZV), legal dossier (ChemO alignment, MRA coverage), PCN statistics, Nordic SPIN query, catalog counts |
| 1 | Pilot: freeze the lead dictionary, test SDS collection and parsing on 1–2 groups |
| 2 | Build the product frame, draw the sample, collect documents at full scale |
| 3 | Cross-document corroboration and quality assurance |
| 4 | Analysis; write the decision-makers' discussion basis; freeze the database |

## Expected result (hypotheses to test, not conclusions)

- Consumer decorative paints: ≈ 0% intentional lead.
- Professional/industrial solvent-borne segments: single-digit percentages.
- Third-country imports: markedly higher, mirroring source-market prevalence
  (global studies show >50% in several countries).
- A documented gap map EU vs Switzerland, every claim traceable to a public
  document.

## Repository layout

    README.md                  this file
    AGENTS.md                  conventions for AI-assisted work on this repo
    docs/management_summary.md bilingual management summary (DE/FR), always current
    docs/plan/3SM/             planning notes (3-stage system)
    ├── README.md              plain-language guide to the planning tree
    ├── MASTER.md              project dashboard
    ├── LOG.md                 lifecycle log
    └── 10_STRATEGY/           research findings and decisions
        ├── MASTER.md          decisions, open questions, roadmap
        ├── methodology.md     population, sampling, corroboration detail
        └── lead_sds.md        lead compounds, EU law, SDS feasibility

## Status

Planning stage (strategy, unit v0.1). Detailed working documents:
[`docs/plan/3SM/`](docs/plan/3SM/). Nothing is frozen; methodology may still
change as Phase 0 research comes in.

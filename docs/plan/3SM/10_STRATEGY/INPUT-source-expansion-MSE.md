---
unit: next-unit input
stage: STRATEGY
lifecycle: INPUT
updated: 2026-09-14
type: strategy input digest (consultant handover — not adopted policy)
---

# INPUT — source expansion + capture-recapture (consultant handover, 2026-09-14)

Full text: [`_inputs/consultant-handover-2026-09-14.md`](_inputs/consultant-handover-2026-09-14.md)
(received 2026-09-14, preserved verbatim). This file records what the
handover proposes, how it maps onto the project's verified findings,
and the decision points it defers to the next strategy turn. **It is
input, not adopted policy** — nothing in v0.2.4 rides on it (D38 de7).

## What the handover proposes

1. **New product-level sources** (its §4–§5, priorities): KemiDigi
   (Finnish chemical products register, A+), WINGIS/GefKomm-Bau
   (BG BAU construction SDS ecosystem, A+), BASTA (Swedish
   construction-product article DB, A+, ">200,000 articles" claimed),
   INIES (French FDES/EPD DB, A — with the commercial-references
   expansion: one FDES covers many *références commerciales*), eBVD
   (A−, API after agreement), Quick-FDS (A−/B+, SDS discovery), ECHA
   PT21 antifouling (B+, bulk export), M1 (B), plus auxiliary
   Safety Gate / EBTI.
2. **Methodology turn:** replace/validate the magnitude-benchmark vote
   (v0.2.3) with **multiple-list capture-recapture / MSE** over
   overlapping, differently-selected product lists (log-linear /
   Bayesian, explicit dependency groups, stratification), plus an
   independent **manufacturer-census × measured-assortment** estimator;
   measure SKU→formulation compression empirically instead of assuming
   a fixed band (§16 — endorses our own v0.2.3 shade-collapse
   assumption flag).
3. **Bias discipline for lead prevalence:** ecolabel lists (ECAT,
   Nordic Swan) are the lead-UNLIKELY stratum — sampling frames must
   straddle selection mechanisms; the hazard tail (KemiDigi, WINGIS,
   PT21, marine chandlers) is where lead-containing products surface.

## How it maps onto verified findings

- The confirmed-bulk picture (D38 data_sources.csv) matches its §27:
  today exactly two sources deliver product tables (AS-2, AS-3); the
  national registers it lists alongside ours (KemI, Danish AT, PCN)
  are product-level **gated** — the handover's addition is the
  construction/occupational ecosystem (KemiDigi, WINGIS, BASTA, INIES,
  eBVD), which our register review had not covered.
- **Corrections to the handover (from our verified record):**
  INIES webservice is licensed/auth-gated (AS-probe finding,
  2026-09-14) — its §4.4 limitation concedes this; BASTA's
  ">200,000 articles" is a claim pending probe; KemiDigi public
  enumerability is unverified.
- Its dependency groups (§17: ECAT+Nordic Swan one family; BASTA↔eBVD
  coupled; WINGIS↔manufacturer SDS portals) slot into the
  independence_group column of data_sources.csv.

## Entry gate for any new source

Per D38 (de5): a source enters data_sources.csv only after a probe
**confirms bulk data + manufacturer + product ident-nr** (identity
tuple) with in-scope membership derivable from the source's category
filter. The queue below is therefore a PROBE queue, not a data-source
list.

## Candidate probe queue (next unit, order per handover §18)

| # | Source | Priority | Probe deliverable (handover §19 schema, slimmed) |
|---|---|---|---|
| 1 | KemiDigi (Tukes, FI) | A+ | enumerability, paint filter, in-scope count, 100-row sample, identity/SDS completeness |
| 2 | BASTA (SE) | A+ | paint taxonomy, article count, manufacturer count, sample, article-number completeness, API/export feasibility |
| 3 | WINGIS/GefKomm-Bau (DE) | A+ | enumerability beyond interactive search, product count, article fields, SDS path |
| 4 | INIES (FR) | A | paint/decor FDES count, commercial references per FDES, total reference count (public UI; webservice stays out unless the no-paid constraint changes) |
| 5 | eBVD (SE) | A− | API access under the free/public constraint, category count, sample, BASTA dependency mapping |
| 6 | Quick-FDS (FR/EU) | A−/B+ | supplier enumeration, paint-product enumeration feasibility, SDS accessibility |
| 7 | ECHA PT21 antifouling | B+ | complete structured export, trade-name dedup, authorisation-holder counts |

Auxiliary (not product catalogs; stay out of data_sources.csv): M1,
EPD systems (IBU/environdec/ECO Platform/baubook/DGNB), Safety Gate,
EBTI. National gated registers (KemI ST-5, Danish AT ST-6, PCN ST-1,
Norwegian P-no) remain documented in DATA_SOURCE.md — gated rows never
enter data_sources.csv on claims (de6).

## Decision points deferred to the next strategy turn

- Adopt the source-expansion unit (exit criterion per handover §28:
  ≥3 new sources with complete in-scope export or reproducible
  enumerated sample/count; ≥2 with high-confidence matching) — and its
  unit number (the "v0.3" label is already double-booked: D32
  distribution goal + the provisional product-identification label).
- Adopt/qualify MSE (its assumptions: list independence, linkage
  quality, stratification) vs the v0.2.3 benchmark vote as the
  headline denominator method.
- The estimand split (market size N vs lead prevalence p) and the
  explicit "on the EU market" temporal definition (§23–§24) — both
  worth adopting as terminology at the next METHODOLOGY pass.

## Provenance

- Consultant handover received 2026-09-14 (verbatim copy in
  `_inputs/`); project facts cited from this repository's verified
  record (as-source-probe run 20260914-125322, csv-sample runs
  20260914-111921/164108/164304, DATA_SOURCE.md, v0.2.3 report).

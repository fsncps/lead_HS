---
unit: global
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-18
---

# Topic — Data sources (strategy summary)

## Abstract

The source register (108 rows, classes CS/PE/ST/AS/DS) enumerates
every candidate source of paint product data on the EU market; each
source is characterized by probing (robots/terms, access, counts,
counts provenance) before any collection. Discipline: record source
URL and retrieval date per record, respect site terms, no bulk
hammering, polite crawl-delay, GO=1 gates for costly operations.
Current state of the numbers game: census headline N2 = 331,644 /
floor 17,838 (v0.2.0 rounds); exactly two sources meet the
confirmed-bulk + identity-tuple gate (`data_sources.csv`: AS-2 ECAT,
AS-3 Nordic Swan); the BASTA special probe (D40) pinned the register's
public counts (195,391 articles / 1,925 companies) via its anonymous
same-origin proxy and delivered a seeded 100-article sample — the
paint-subset filter stays open, so no third `data_sources.csv` row.

## DECISIONS

- D9 — cost constraint: publicly retrievable documents only, minimal
  cost.
- D20 probe discipline — probing obeys the register's access rules;
  census counts provisional; promotion to anchors manual (bridge).
- D25/D28 — probe-first source reports; per-source two questions:
  products identifiable, documentation reachable; product data only.
- D31 — no-scrape reconnaissance, EU-only; channels characterized, not
  walked.
- D33 — source-level sounding-out; product identity key (manufacturer,
  manufacturer product-ident) with UFI/GTIN cross-references.
- D36/D38 de5 gate — `data_sources.csv` grows only via confirmed bulk
  + identity tuple (+ in-scope filter) sources.
- D40 (2026-09-17) — BASTA addendum: same-origin anonymous
  `/apiproxy/v3` routes pinned; exact counts; sample delivered; de5
  not met.

## OPEN ITEMS

- BASTA paint-subset filter: enumerate the server-side
  `bk04Code` paint groups (TODOS item) before any third
  `data_sources.csv` row.
- ECAT reconciliation (group-044 17,838 vs Commission 38,233;
  awarded-vs-registered) — v0.2.3 residual.
- Deep per-source pinning of the six probe-queue candidates
  (AS-31..36) stays next-unit work (D39/D40 groundwork in place).

## Detail documentation

The public register document (plain language, glossary, DE/FR
translations — source-by-source access rules and history) lives
outside the plan tree:

- `docs/study/DATA_SOURCE.md` (EN; siblings `DATA_SOURCE.de.md`,
  `DATA_SOURCE.fr.md`).

Raw cross-unit strategy material: `INPUT-source-expansion-MSE.md`,
`MATCHING.md`, `RAW_SOURCING.md` (this directory).

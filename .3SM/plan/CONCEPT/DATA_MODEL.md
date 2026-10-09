---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-09
---

# Topic — Data model (concept summary)

## Abstract

Evidence database = one SQLite file plus a hash-addressed
raw-document store. Principles: provenance on every record (source
URL + retrieval date + content hash); formulation-level products with
a sighting dedup layer; the SDS blind spot encoded as a concentration
taxonomy (`none_listed` ≠ lead-free); seeded, reproducible sampling
runs; append-only corrections; unverified CAS/EC stay flagged; no
legal-status fields anywhere (product data only). The concept-level
entity set (probe_run, probe_finding, product, sighting, trade_stat,
frame/sampling, sds_finding, lead_compound, corroboration) migrates
milestone-gated; the fully normalized registry schema is Design's.

## DECISIONS

- D1/D16 — state = one SQLite file + hash-addressed raw store (both
  gitignored); portable-SQL hedge stands.
- D17 — evidence-database principles (provenance, dedup, taxonomy,
  seeded runs, append-only, flagged identifiers).
- D19/D20 — probe entities with full provenance; census counts
  provisional; anchor promotion manual.
- D27 — product data only; no legal-category, Swiss-relevance or
  legal-status fields anywhere.
- MA10–MA14 (MATCHING.md, 2026-10-09) — canonical identity tables
  (`manufacturer`, `product`, UNIQUE normalized strings) precede the
  sighting layer; raw tables keep verbatim rows plus a product_uuid
  back-link; extension columns per coverage scan.

## OPEN ITEMS

- Migration milestone mapping (which tables arrive at which milestone)
  tracks the tool roadmap — see `../DESIGN/data_model.md` for the
  normalized target schema and migration ledger.

## Detail documentation

The public concept-level schema document (entities, taxonomy,
storage lifecycle) lives outside the plan tree:

- `docs/study/DATA_MODEL.md` (EN).

The engineering truth (normalized schema, migrations, keys) is
`../DESIGN/data_model.md` — Design wins on conflict.

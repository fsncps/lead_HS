# CONCEPT PIPELINE — archive

Shipped + abandoned entries verbatim, with end-dates (PIPELINE.md law).

### v0.3.0 — evidence DB + bulk download of the confirmed sources
status: SHIPPED 2026-10-09 (/finalize-and-merge executed; branch
  waiver held — archive + pipeline flip + local tag; gate green:
  461/smoke 6/db-audit 0).
note: unit dirs `DESIGN/_archive/v0.3.0/` + `ENGINEERING/_archive/v0.3.0/`
  (moved at ship); work landed on main (unit-branch init waived by
  user 2026-10-03, recorded in the unit ENG MASTER — not drift).
  `ENGINEERING/v0.3.0/`; work landed on main (unit-branch init
  waived by user 2026-10-03, recorded in the unit ENG MASTER —
  not drift).
intent: One SQLite evidence DB gains one raw table per bulk source with
  the source's own column headers verbatim; every confirmed bulk source
  (ECAT, Nordic Swan — BASTA when its filter clears) is bulk-downloaded
  completely: each and every record, stubs/nulls/duplicates included,
  maximum data depth within the per-record budget.
decisions:
  - D42 — product-DB turn = v0.3; Windows installer + deferred
    preliminaries → v0.4 (CONCEPT MASTER)
  - D43 — v0.3 sub-roadmap 0.3.0 → 0.3.4 → 0.3.8 → analysis
  - D44 — completeness mandate; verbatim source headers; 1 KB default
    budget; deterministic truncation, never drop (amends R3 spill)
  - R1/R2 — SQLite stays; upsert + change journal (RAW_SOURCING.md)
constraints: GO=1 network discipline; list-endpoint-first + crawl-delay
  politeness; product data only (D27); provenance per record (D17)
non-goals: normalization/matching (v0.3.4), new-source onboarding
  (v0.3.8), any analysis
readiness: none — init-ready (manifest field lists, R9 mechanics pin at
  Design)
updated: 2026-10-03


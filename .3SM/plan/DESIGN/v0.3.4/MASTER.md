# v0.3.4 — design unit MASTER

---
unit: v0.3.4
stage: DSG
lifecycle: LIVE
updated: 2026-10-10
branch: v0.3.4
---

Created by `/init-unit` from the unit's INIT-READY pipeline entry. Design
converges here (unit T-docs, RUNS.md) until the runs-ready gate.

## Starting context (from the PIPELINE entry, verbatim 2026-10-09)

intent: Identity layer first (user-directed 2026-10-09): canonical
manufacturer + product tables built from the raw source tables —
extract → normalize → match-or-create over UNIQUE normalized strings →
link (raw→product back-link FK, product→manufacturer FK); then an
enrichment pass completing canonical fields with the most-common raw
values. Cross-source collapse (exact keys, blocking, scored tiers — no
LLM matching) rides on top of these tables.

decisions carried: MA10–MA14 (MATCHING.md Stage 0 — column contracts,
typed composite ident_string, group-level identity, two-pass CLI,
coverage-scan extension columns); MA1–MA7/MA9 proposed — pin at this
unit's Design; MA13 (enrichment tie rules), MA15 (deterministic uuid5)
and MA16 (GTIN collision → review queue) user-confirmed 2026-10-09.

constraints: deterministic + idempotent (re-run = no-op); product data
only (D27); MA8 dependency call open (rapidfuzz vs stdlib).

non-goals: raw acquisition (v0.3.0, built), source expansion (v0.3.8).

concept source: `../../CONCEPT/MATCHING.md` (Stage 0 + MA register);
`../../CONCEPT/PIPELINE.md` (the v0.3.4 entry — verbatim source of the
context above).

## DECISIONS

## OPEN ITEMS

## SKILL RECORDS

(3sm-design-unit / 3sm-design-master passes; append-only)

---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE03 — Discovery & register rework (manual-web, no scraping)

## Objective

Produce the EU-only register of record for the numbers run: AS-class
source discovery, B2B candidate resolution, the enumerated per-site
PE register (V5 caps), and the CSV rework — loaded and dry-run
verified.

## Preconditions

- PHASE02 done (0006 applied; validation live).
- Manual-web only in this phase — no scraping, no GO required for
  the register work itself.

## Governing references

- `../../10_STRATEGY/DATA_SOURCE.md` (AS class, register scope D31,
  access & scraping discipline, seed lists)
- `../../20_DESIGN/units/v0.2.0.md` (nu3/nu6);
  `../../20_DESIGN/units/v0.1.3.md` (pe1 notes convention +
  product_pattern token, i13)

## Steps

1. **AS-class discovery (manual-web):** CEPE + national paint
   associations (member counts where public, URL + access date
   pinned); national product registers with public statistics (SE
   KemI strongest; DK/NO/FI equivalents verified). Rows enter the
   register only with a pinned real URL; candidates without a
   confirmed URL stay documentation-level OPEN items (V6).
2. **B2B portal candidates:** resolve the PE-3 placeholder or leave
   the channel honestly OPEN (uncovered-channel line in the report).
3. **Enumerated per-site PE rows PE-10+** per V5 caps (MFR ≤ 12,
   EU-DIY ≤ 5, MARINE ≤ 5, ART ≤ 6, B2B OPEN) with the i13 notes
   convention (channel/listed_by/listed_url/listed_date/inclusion)
   plus the `product_pattern=` token where the site's product-URL
   shape is known; caps documented in the CSV batch note.
4. **sources.csv rework (one reviewed change set):** CS-1 row
   REMOVED (migration 0006 already retired it in the DB — ordering
   per nu6); PE-1..4 → active=0 with supersession notes (seeds live
   on as per-site rows); AS candidate rows enter (active=0 default
   per nu3; active=1 only if fetchable-by-class, noted per row);
   CH-DIY seeds appear nowhere.
5. **Load + verify:** `make sources-load` (validation on) →
   `make probe-dry` plans every active row; PE-1..4 inactive with
   supersession notes; `make db-audit` exit 0.

## Deliverables

Reworked register CSV (reviewed change set); loaded DB; dry-run plan
output; batch note with caps and per-row activation decisions.

## Exit gate

`source load` clean (exit 0); `probe-dry` lists every active row;
PE-1..4 retired; CS-1 absent from the CSV and inactive in the DB;
audit exit 0.

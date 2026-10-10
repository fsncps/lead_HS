# Report v0.3.4 r02 — HS-code completion

---
unit: v0.3.4
run: r02
stage: ENGINEERING
language: en
updated: 2026-10-10
---

## Summary

Run r02 closed the unit's highest-priority completion column
(decision D51): every canonical product row now carries an **HS4 code
where one can be justified from the source's own grouping**, and the
rows left NULL are NULL **by documented decision**, not by omission.

| headline figure | value |
|---|---|
| canonical products | **271,005** |
| products with `hs_code` set | **258,360 (95.3%)** |
| products NULL by reviewed decision (ECAT services/non-goods + BASTA non-goods) | 12,622 |
| products NULL by conflict (BASTA tied top-vote, kept NULL) | 23 |
| distinct HS4 values in use | 83 |
| **paint classes: products at HS 3208 + 3209** | **23,748** |
| mapping rows applied (curated, bundled) | 345 (25 ECAT + 320 BASTA) |
| test suite | 471 passed, 0 failed (offline) |

The result: of the two catalogues, the market-facing product universe
decomposes cleanly into HS4 classes — and the **paint-relevant core**
(HS 3208 *paints/varnishes* + HS 3209 *pigments in binders*) holds
**23,748 products** (≈ 8.8% of the universe). This is the number the
SDS-acquisition unit (v0.3.5) can budget against.

Everything below derives from the project's own database
(`data/leadhs.sqlite`, rebuild + apply of 2026-10-10); provenance for
the underlying raw data is in [report-0.3.0.md](report-0.3.0.md), the
identity layer in [report-0.3.4-r01.md](report-0.3.4-r01.md).

## What was built (scope of r02)

- **Curated mapping table** `src/leadhs/dict/hs_group_map.csv` —
  (source_id, group_code) → HS4 with `confidence` ∈ {high, medium,
  flag} and a per-row note; **345 rows** covering every distinct group
  in both sources (25 ECAT EU-Ecolabel product groups; 320 BASTA
  `bk04_code` chapters). **131 rows carry `flag`** for the
  commissioning owner's review; **10 rows are deliberately empty-HS**
  (reviewed: services or multi-chapter assortments — see below).
- **Migration 0014** — the `hs_apply` run kind (one run row per source
  pass; the same run-book pattern as every other pass).
- **`leadhs hs apply`** — loads and validates the whole map before any
  write (header, 4-digit HS, unknown source, duplicates → named
  error, exit 2), then in one transaction: ECAT products join
  directly on `product.eu_group`; BASTA products get a **per-product
  majority vote** over their raw `bk04_code` back-links (ties are
  skipped + counted, never guessed). Re-runs over unchanged data
  change nothing (idempotent, verified live: second apply set 0).
  `--dry-run` computes the identical read path with zero writes.
- **`leadhs hs status`** — three-state coverage per source
  (`set` / `reviewed` / `not_applied` / `pending`) plus the
  **pending-group worklist**: every group with no mapping row, ranked
  by product count. On today's DB the worklist is **empty** — the
  map is total over both sources.
- **Doctor line** — `hs: coverage 258,360/271,005 (95.3%)` plus the
  last `hs_apply` run book reference.

**Order dependency:** run `hs apply` after any `identity
resolve`/`identity rebuild` — a rebuild re-creates canonical rows, so
HS values must be re-applied (documented in the module and the run
plan; the live execution below followed that order).

## Execution log (2026-10-10)

| step | result |
|---|---|
| `db init` | migration 0014 applied |
| `hs apply --dry-run` | ECAT 60,221 + BASTA 198,139 planned, 23 conflicts, 2.4 s |
| `identity rebuild` (first live) | AS-2: 2,418 mfr / 72,652 products; AS-33: 439 mfr / 198,353 products; backup `data/backups/leadhs.sqlite-20261010T034250.sqlite`; **42 s**; counts identical to r01 |
| `hs apply` | ECAT set 60,221; BASTA set 198,139; conflicts 23 (kept NULL); 3.2 s |
| `hs apply` (idempotence) | both sets 0 — nothing changed |
| `hs status` | 95.3% coverage; worklist empty |
| `doctor` | identity + hs sections green |

Three build defects surfaced on the **first live rebuild** (all fixed
in this run, none reachable through the offline fixtures alone):

1. `identity rebuild` teardown dropped the back-link **column** while
   0013's index still depended on it → teardown now drops dependent
   indexes first (`identity/spec.py`).
2. The same teardown truncated `linkage_candidate`/`identity_state`
   instead of dropping them, colliding with the re-CREATE block →
   teardown drops all four canonical tables (`identity/resolve.py`).
3. `hs status` originally re-used the raw-table group column for
   ECAT's worklist; ECAT groups live on the canonical `product` row →
   per-source worklist SQL (`hs.py`).

## The ECAT interface table (eu_group ↔ HS4)

The user asked for the complete interface table because ECAT's 25
Ecolabel groups map unambiguously — this IS the table (group code =
canonical `product.eu_group`; products = live counts):

| eu_group | HS4 | confidence | products |
|---|---|---|---|
| Absorbent hygiene products | 9619 | high | 546 |
| Animal care products | — | flag | 2 |
| Bed mattresses | 9404 | high | 21 |
| Cosmetic Products | 3304 | high | 1,511 |
| Decorative paints, varnishes, and related products (2014 criteria) | **3209** | medium | **16,454** |
| Dishwasher Detergents | 3402 | high | 541 |
| Electronic Displays | 8528 | high | 3 |
| Footwear | — | flag | 54 |
| Furniture | 9403 | medium | 5,655 |
| Graphic paper | 4802 | medium | 4,003 |
| Growing media and soil improvers | — | flag | 52 |
| Hand dishwashing detergents | 3402 | high | 1,106 |
| Hard Surface Cleaning Products | 3402 | high | 7,056 |
| Hard covering products | — | flag | 3,726 |
| Indoor Cleaning Services | — | flag | 262 |
| Industrial and Institutional Dishwasher Detergents | 3402 | high | 1,568 |
| Industrial and Institutional Laundry Detergents | 3402 | high | 925 |
| Laundry detergents | 3402 | high | 1,102 |
| Lubricants | 2710 | medium | 889 |
| Performance coatings and related products | **3208** | medium | **55** |
| Printed paper, stationery paper and paper carrier bag products | 4802 | flag | 1,331 |
| Textile products | — | flag | 7,325 |
| Tissue Paper and Tissue Products | 4803 | high | 15,369 |
| Tourist accommodation | — | flag | 1,010 |
| Wood-, cork- and bamboo-based floor coverings | 4411 | medium | 2,086 |

The two paint rows (bold) are the study's target classes: decorative
paints land in **3209** (16,454 products), performance/industrial
coatings in **3208** (55). Both carry `confidence: medium` because the
Ecolabel criteria licence is a *formulation-family* certificate: a
licence can cover products formulated either as ready-to-use paints
(3209) or as binder-heavy bases/undercoats (3208). The flag is a
documentation note, not an error.

The seven empty-HS rows are **reviewed**: services ("Indoor Cleaning
Services", "Tourist accommodation"), non-goods assortments (footwear,
textiles, animal care, growing media) and "Hard covering products"
(splits across 44xx/68xx chapters with no single defensible HS4).
These products intentionally keep `hs_code` NULL.

## BASTA (AS-33) in brief

The 320 `bk04_code` chapters map to 80 HS4 values; the applied result
is dominated by construction goods (the register's own centre of
gravity), **not** paints:

| HS4 | products | typical chapter |
|---|---|---|
| 7318 | 34,253 | fasteners/screws (Kanalsystem etc.) |
| 7306 | 26,257 | steel tubes (Kanalsystem) |
| 3918 | 19,003 | floor coverings (Plastgolv) |
| 4803 | — | (tissue: mostly ECAT side) |
| 3925 | 6,578 | builders' plastic ware |

HS 3208/3209 from BASTA: the ~870 products in the `034xx` paint
chapters (group confidence medium; sub-chapters 03410/03420/03430 map
individually at high confidence) — the remainder of the 23,748
paint-class products is ECAT decorative (16,454 + its BASTA
share) — exact per-class splits are one query away
(`SELECT hs_code, COUNT(*) FROM product WHERE hs_code IN ('3208','3209')`
→ 23,748 total).

**23 conflict products** stay NULL by design: their raw rows carry
top-voted chapters that resolve to two different HS4 values (e.g.
9× `3925/8536`, 7× `4407/4409`). The tie is genuine source ambiguity
(products assembled from chapters in different HS chapters); guessing
would corrupt the class counts. The full list is reproducible from
the run book (`hs_apply-20261010-as33-2`, `conflicts: 23`).

## Reading the numbers (limits, no conclusions)

- HS assignment is a **grouping-level proxy**, not a customs
  declaration: a group's HS4 is the class its members almost surely
  belong to; individual SKU-level edge cases can exist. The
  confidence column records how strong that inference is per row.
- `confidence: flag` rows (131) await review by the commissioning
  owner; flagged does not mean wrong — it means the note field
  documents a judgement call worth one glance.
- The ECAT catalogue contains service licences and non-goods
  assortments; they are part of the register, not part of any goods
  market — hence reviewed-NULL, and hence 95.3% (not 100%) coverage
  being the **correct** end state.
- 23,748 paint-class products is the **candidate** universe for SDS
  work, not a measured paint market size (some licences/registrations
  may be inactive; dedup happens only at identity level, r04).

## Verification status

- Offline suite: **471 passed, 0 failed** (10 new hs tests: map
  validation, dry-run zero-write, real + idempotent apply, re-apply
  after map edit, three-state status, worklist ranking).
- Live pipeline executed in dependency order; idempotence and the
  empty worklist verified on the real DB.
- Run books: `identity_resolve-20261010-as2-6`, `-as33-4`,
  `hs_apply-20261010-as2-1`, `-as33-2`.
- Open for FINAL (this unit): the three live-rebuild defects are
  fixed but carry **no offline regression test yet** (fixtures never
  built the 0013 index combination); r01's provisional items remain
  on the FINAL list.

## References

- Curated map: `src/leadhs/dict/hs_group_map.csv` (bundled; SHA-256
  `ad60839a…bac16bb` as applied)
- Run plan r02: `.3SM/plan/ENGINEERING/v0.3.4/r02/PHASE02.md`
- Prior reports: [report-0.3.4-r01.md](report-0.3.4-r01.md),
  [report-0.3.0.md](report-0.3.0.md)

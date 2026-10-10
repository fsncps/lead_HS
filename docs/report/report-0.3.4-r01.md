# Report v0.3.4 r01 — the canonical identity layer

---
unit: v0.3.4
run: r01
stage: ENGINEERING
language: en
updated: 2026-10-10
---

## Summary

Unit v0.3.4's first run built and executed the **canonical identity
layer**: the two whole-register raw loads (EU Ecolabel ECAT, BASTA) are
now collapsed into deterministic, re-derivable **manufacturer** and
**product** tables.

| headline figure | value |
|---|---|
| raw rows processed (2 sources, verbatim) | **288,138** |
| canonical **manufacturers** (cross-source collapsed) | **2,857** |
| canonical **products** (identity groups) | **271,005** |
| raw rows back-linked to a product | **288,138 / 288,138 (100.0%)** |
| identity determinism | uuid5, pinned namespace (il4); re-run created 0 rows |
| test suite | 461 passed, 0 failed (offline) |

Everything in this report is derived from the project's own database
(`data/leadhs.sqlite`); provenance for the underlying raw data is in
[report-0.3.0.md](report-0.3.0.md). The run is idempotent — a second
resolve over unchanged raw state created nothing — and every raw row
carries a `product_uuid` back-link, so any canonical row can be traced
to every raw observation behind it and vice versa.

## What was built (scope of r01)

- **Migration 0013** — canonical `manufacturer` / `product` tables
  (unique `name_norm` / typed `ident_string`), `identity_state` (per-
  source manifest-hash drift guard), `linkage_candidate` (the r03
  review-queue surface, empty until matching runs), plus the
  `identity_resolve` run kind.
- **Deterministic normalization pins** — normal forms are sorted-token
  identity keys (order-insensitive, case-/diacritic-folded, legal-form
  stripped; control characters can never enter a key); `norm_gtin`
  canonicalizes 8/12/13/14-digit codes to GTIN-14 so EAN-13 and GTIN-14
  forms of one product collapse into one canonical row.
- **The `identity` package** — per-source adapters (single ordered pass,
  group-level identity per MA12), the typed identity-key election rule,
  the resolve pass (in-memory normalized-key index, 500-row batched
  writes, back-link updates by rowid), and `identity rebuild`
  (timestamped backup → teardown → re-derive; aborts before any
  teardown when the backup fails).
- **CLI verbs** — `leadhs identity resolve [--source ID] [--dry-run]
  [--batch N]`, `identity rebuild`, `identity status`; named errors map
  to the tool's exit-code convention (drift/backup → 2, schema/refusal
  → 1, interrupt → 130).
- **Doctor checks** — read-only identity section: table presence,
  back-link coverage, orphan links, manifest drift (with the
  `identity rebuild` hint).

Design decisions il1–il17 and the run plan are recorded in the
planning tree (`.3SM/plan/DESIGN/v0.3.4/`, `…/ENGINEERING/v0.3.4/r01/`).

## Execution log (2026-10-10)

| step | result |
|---|---|
| `leadhs db init` | 0013 applied (auto-backup taken first, per house rule) |
| `identity resolve --dry-run` | plan lines match design expectations (AS-2: 80,847 groups; AS-33: 198,474); zero writes |
| `identity resolve` | AS-2 `identity_resolve-20261010-as2-4`, AS-33 `identity_resolve-20261010-as33-2`, both done |
| `identity resolve` (again) | **created 0 / 0** — idempotence verified on the real database (il5) |
| `identity status` | both sources hash-ok, no drift, 100.0% back-linked |
| `leadhs doctor` | identity section green (2 sources resolved; 0 orphans) |

One build defect was caught and fixed during the dry-run gate (the
adapter SELECT fetched only the group-key columns; payload columns were
missing — crash before any write, two stuck run rows cleaned and
annotated). The fix commit is `6b429f0`; the implementation commit is
`4a661e6`.

## Key meta figures

### Per-source resolve counts

| metric | AS-2 ECAT | AS-33 BASTA |
|---|---|---|
| raw rows | 89,396 | 198,742 |
| identity groups | 80,847 | 198,474 |
| products created (first pass) | 72,652 | 198,353 |
| manufacturers created (first pass) | 2,418 | 439 |
| rows back-linked | 89,396 | 198,742 |
| multi-code groups (election applied) | 3,884 | 0 |
| — of which multiple distinct GTINs | 2,261 | 0 |
| name-basis keys (no usable code) | 53,557 | 3 |
| refused codes (non-GTIN "GTIN" values) | 7 | 0 |
| skipped groups (no key at all) | 0 | 0 |

Cross-source collapse: the 7 manufacturers that ECAT and BASTA both
name (identical normalized names) share one canonical row — 2,418 +
439 = 2,857 total, not 2,864. Product-level sharing is currently zero
(BASTA has no GTIN column usable for identity by design, il3; its
article numbers are company-internal), so product-level cross-source
merging remains **r03's scored-matching job**, as planned.

### Identity-key basis distribution (271,005 products)

| basis | products | share |
|---|---|---|
| `article:<mfr_norm>:<art-nr>` | 202,511 | 74.7% |
| `gtin:<14 digits>` (global) | 15,735 | 5.8% |
| `name:<mfr_norm>:<name_norm>` (fallback) | 52,759 | 19.5% |

### Largest manufacturers (by canonical product count)

| products | manufacturer |
|---|---|
| 38,072 | Lindab AB |
| 10,212 | Amtico International AB |
| 9,322 | Svenska Fönster AB |
| 7,161 | Nordic Fastening Group AB |
| 6,082 | Arvid Nilsson AB |
| 5,778 | AB Varmförzinkning |
| 4,909 | Forbo Flooring AB |
| 4,352 | Ejot Sverige AB |
| 4,339 | ESSVE Produkter AB |
| 4,243 | Söve AB |
| 4,125 | PPV AB |
| 3,968 | Benders Sverige AB |

### Manufacturers by country (top 10)

| manufacturers | country |
|---|---|
| 467 | France |
| 454 | Italy |
| 439 | (blank — BASTA carries no country column) |
| 334 | Austria |
| 248 | Spain |
| 215 | Germany |
| 76 | Slovenia |
| 73 | Netherlands |
| 72 | Denmark |
| 58 | Poland |

### The 7 refused codes (counted, degraded to name-basis keys)

Alphanumeric values in barcode-typed columns (6× ITF, 1× mislabeled
EAN13): `WWVICA750`, `WWVIFO750`, `WWVIPL1K`, `WWVIMP750`, `WWVIAC750`,
`WWVIMA1K` (IT/020/060, IT/019/040), `ES-MD/052/00003` (ES-MD/052/00003).
None were lost — each group elected its name-basis key; `skipped = 0`.

## Reference query + sample (50 random products)

Query (re-runnable; each draw differs):

```sql
SELECT p.ident_string, p.ident_nr, p.name AS product_name, p.brand,
       p.eu_group, p.url, m.name AS manufacturer, m.country
FROM product p JOIN manufacturer m ON m.uuid = p.manufacturer_uuid
ORDER BY RANDOM() LIMIT 50;
```

Frozen draw (2026-10-10) — long values trimmed for the table; `eu_group`
is ECAT-only, `brand`/`url` are BASTA-carried fields:

| manufacturer | basis | ident_nr | product | brand | eu_group | country |
|---|---|---|---|---|---|---|
| Sika Sverige AB | article | 104551 | Sikaflex-521 FC | Sika | | |
| Ejot Sverige AB | article | 582270 | BORRSKRUV FÖRSÄNKT 4,8X25 | | | |
| Konradssons Kakel AB | article | 7667 | KLINKER KYRA MANDANA RED RÖD (Utgått) | Konradssons Kakel | | |
| Industrie Celtex S.p.A | name | 55800 cod. force wipe, | Force wipe, cod. 55800 | | Tissue Paper and Tissu… | Italy |
| Lindab AB | article | 14114 | RTRA | | Takavvattning | |
| GMS Composite Knitting Ind. Ltd. | name | awnaima noos o-neck ss t-shirt | AWNAIMA SS O-NECK T-SHIRT NOOS | | Textile products | Bangladesh |
| Essity Hygiene and Health AB | name | (472584) 1300 1p 502080 corele… | 502080 Tork Coreless Midsize Uni 1p 1300 (472584) | | Tissue Paper and Tissu… | Sweden |
| SPAX International GmbH & CO KG | article | 1411010400408 | FÖNSTERSKRUV FEX-KS | SPAX | | |
| ARDEX AB | article | 48707 | ARDEX SE manhattan, 310 ml | ARDEX | | |
| Reckitt Benckiser France | name | / 1000 citrus eco force harpic… | Harpic Max toilet / WC Power Plus Eco Citrus Force 1… | | Hard Surface Cleaning … | France |
| Dekora AB | article | 510317 | ARKITEKT FASAD | Dekora | | |
| Klopman International S.r.l | article | 1058 | SUPERBANDMASTER- R-PES BCI | | Textile products | Italy |
| Ets GUILMIN SA | name | 15l : : : : = = and aqua base … | PRODUITS : Finish Aqua Matt wall and ceiling paint … | | Decorative paints, var… | Belgium |
| RENAULAC | name | 3 luxens sage satinato termosi… | Termosifoni Satinato LUXENS SAGE 3 | | Decorative paints, var… | France |
| Saint Gobain Sweden AB - Scanspac | article | 620610 | DALAPRO DM60 12,5 KG | Dalapro | | |
| Industrie Celtex S.p.A | name | 10 170 carta cod. d010124 diss… | Carta igienica Dissolvenza immediata 10 rotoli 170 … | | Tissue Paper and Tissu… | Italy |
| S:t Eriks AB | article | 361512011081 | Blocksteg granit Bohus grå | S:t Eriks | | |
| Paroc AB | article | 8533490 | PAROC Hvac Bend AluCoat T | | | |
| Amtico International AB | article | AG0SCA53CE.UW0BU | Signature Safety Rosa Classic Marble | Amtico Signature Saf… | | |
| Fazzini srl | name | - - - 100% 160x210 cotone cove… | Linea Manor - KUBRIC DUVET COVER - 160x210 Cotone 10… | | Textile products | Italy |
| Svenska Fönster AB | article | 65132212221650 | Trä/alu FD Ut 3-gl | Svenska Fönster | | |
| Lindab AB | article | 913700 | BSFTR | | Transfersystem | |
| Söve AB | article | G718 | The Apple | | | |
| BOA - Bo Andrén AB | article | 231880 | VÄGGSKIVA HUNTONIT FÄRDIGMÅLAD | | | |
| Tikkurila Sverige AB | article | 051335 | SCOTTE 40 SNICKERFINISH - UTGÅTT | Beckers Färg | | |
| Vandeputte s.a. | name | 750ml keuken ontvettende reini… | TWIDO Ontvettende reinigingsspray voor keuken 750ml | | Hard Surface Cleaning … | Belgium |
| Rockwool AB | article | 230573 | TECLIT Pipe Section 159x100 F | ROCKWOOL TECLIT | | |
| Lindab AB | article | 107613 | RCF | | Cirk. kanalsystem | |
| Saint-Gobain Sweden AB - ISOVER | article | 3573891203 | CLIMPIPE Section Alu2 | ISOVER | | |
| Amtico International AB | article | AR0W7660BW.WBXBU | Signature Lime Washed Wood | Amtico Signature | | |
| Industrie Celtex S.p.A | name | 2-lgs 5403 artsenrol cell, cod… | EVEREST ARTSENROL 2-LGS CELL, cod. 5403 | | Tissue Paper and Tissu… | Italy |
| Mira byggeprodukter a/s | article | 104635 | supercolour excellent | | | |
| Aston Sweden AB | article | 12092180000 | Borrskruv | | | |
| Lindab AB | article | 507877 | TVTR30 | | Transfersystem | |
| SITLAND Spa | name | evo_nr_tte3330171csrr strike t… | Team Strike Evo_NR_TTE3330171CSRR | | Furniture | Italy |
| Nordic Fastening Group AB | article | 14071010000105 | ML6M 4 FZB MFV10x1,25 DIN 439/ISO 8675 Vänster | NFGAB | | |
| String Furniture AB | name | 40x30x40, 5002 brackets, cente… | Center Center Module with shelf brackets, right-door… | | Furniture | Sweden |
| ESSVE Produkter AB | article | 61090041 | VAGNSBULT | ESSVE | | |
| Amtico International AB | article | AR0D3000.DC515 | DC515 | Amtico Signature | | |
| Papírna Aloisov a.s. | name | 60-140 papir sedak | Šedák papír 60-140 | | Graphic paper | Czech Republ… |
| Nordic Fastening Group AB | article | 12200500140005 | MSK6SS OB M5x14 DIN 916/ISO 4029 100-pack | NFGAB | | |
| Lindab AB | article | 227647 | RCL | | Cirk. kanalsystem | |
| Lindab AB | article | 853932 | PSV45 | | Cirk. kanalsystem | |
| Lucart Tissue & Soap, S.L.U. | name | (851466j) 2c 500m adial adicel… | ADIAL BOB. CEL. INDUSTRIAL ADICEL+ 500M 2C (851466J) | | Tissue Paper and Tissu… | Spain |
| ITW Construction Products AB | article | 153437 | UTGÅTT Träskruv SPUN+ FH HPS EFZ | NKT | | |
| SA PRODER | name | (5l) magic plus w45 | MAGIC W45 PLUS (5L) | | Industrial and Institu… | Spain |
| KAJO GmbH | name | 46 hees kajo-bio-hydraulikol r | KAJO-BIO-Hydrauliköl HEES 46 R | | Lubricants | Germany |
| Würth Svenska AB | article | 0992900050 | TÄTNINGSTEJP EURASOL GRÖN | | | |
| Lindab AB | article | 276501 | TSTU | | Safe Detalj | |
| ESSVE Produkter AB | article | 61091079 | SKARVMUTTER | ESSVE | | |

Field coverage in the canonical layer: `eu_group` 72,652 (exactly the
ECAT product set), `url` 198,353 (exactly the BASTA set), `brand`
177,093.

## Reading the numbers (limits, no conclusions)

- **These are register universes, not paint-market counts.** BASTA
  spans construction products broadly (screws, boards, textiles appear
  in the sample); ECAT spans all EU Ecolabel licence products. The
  paint-subset question (BASTA "Färgvaror" ≈ 7,339 products) stays with
  the r02 enrichment / r03 matching work — this run deliberately
  collapsed the *whole* registers so identity is complete before any
  subset is cut.
- **Normal forms are keys, not display values.** `name_norm` /
  `ident_nr` for name-basis products are sorted, folded token strings
  (e.g. `15l : : : : = = and aqua base …`); the readable text lives in
  `product.name` / `manufacturer.name`. This is the pinned MA15 trade:
  stable uuids over pretty keys.
- **Name-basis share (19.5% overall, ECAT-driven)** reflects ECAT's
  53,590 code-less rows — known register shape, not a data loss.
- **Election is deterministic, not "best":** multi-GTIN groups elect
  the lexicographically smallest code (2,261 groups) and keep the rest
  raw-side; r03 can revisit with evidence tiers.

## Verification status

- Offline test suite: **461 passed / 0 failed** (2 deselected by
  markers).
- Real-data gates exercised: dry-run zero-write, double-resolve
  hash-identity, 100% back-link coverage, doctor clean, bad-GTIN
  refusals, election determinism.
- Still open for the FINAL gate (provisional tests, by design):
  SIGKILL mid-batch chaos pass, a full `identity rebuild` round,
  SQLite < 3.35 refusal check, staging-norm recompute consistency.

## References

- Raw-layer provenance: [report-0.3.0.md](report-0.3.0.md) (ECAT
  delivery 2026-10-04; BASTA API walk 2026-10-04).
- Design decisions: `.3SM/plan/DESIGN/v0.3.4/MASTER.md` (il1–il17);
  matching contracts: `.3SM/plan/CONCEPT/MATCHING.md` (Stage 0).
- Run plan: `.3SM/plan/ENGINEERING/v0.3.4/r01/PHASE01.md`.
- Tool: `leadhs identity resolve|rebuild|status` (`--help` for flags);
  database `data/leadhs.sqlite`.

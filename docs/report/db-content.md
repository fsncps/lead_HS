---
updated: 2026-10-04
unit: v0.3.0
scope: database content report
---

# Database content report — what the study's database holds

This report describes the **content state of `data/leadhs.sqlite`** as of
**2026-10-04** (commit `eb6423b` lineage, post-AS-33-load). It is a
snapshot of record counts, data fields ("headers"), and per-source key
numbers — everything shown here is reproducible offline from the
database with the queries in §Reproduce.

Terms: a **raw table** is a per-source table holding every downloaded
record unchanged (word-for-word; only shortened when a record exceeds a
declared size budget, flagged in `_truncated`). The **register** is the
list of known data sources (`source` table, mirrored from
`src/leadhs/dict/sources.csv`). **Active** means eligible for probing
or loading; inactive rows are kept for history.

## Headline totals

| What | Count |
|---|---|
| Raw product records loaded (2 sources) | **288,138** |
| — AS-2 ECAT (EU Ecolabel, Nordic product registers export) | 89,396 |
| — AS-33 BASTA (Swedish construction products) | 198,742 |
| Sources registered / active | 109 / 58 |
| Documents archived (raw store) | 477 (426 archived + 51 manual) |
| Probe findings recorded | 1,116 |
| Probe runs / total runs | 661 / 664 |
| Raw source profiles (instruction contracts in force) | 2 (AS-2, AS-33) |
| Raw change-journal rows | 0 (no re-loads yet — first loads stand) |
| Offline test suite | 461 passed |

## Raw loads in detail

| | AS-2 ECAT | AS-33 BASTA |
|---|---|---|
| Table | `raw_as2_ecat` | `raw_as33_basta` |
| Rows | 89,396 | 198,742 |
| Loaded | 2026-09 (export file) | 2026-10-04 (live API walk, ~3 h) |
| Run | `acquire` (v0.3.0) | `acquire-20261004-as33raw` |
| Truncated rows | 0 | 0 |
| Delivery vs table | 89,867 rows → 471 byte-identical duplicates collapse | 198,742 = register total at instruction time (live register drifts; 200,769 at the 2026-09-17 pin) |
| Verbatim verification | 200/200 spot-checks | spot-check vs live API pass (projected columns + JSON containers) |
| Instruction | `raw_sources/AS-2.instruction.json` | `raw_sources/AS-33.instruction.json` |
| Politeness | n/a (file delivery) | 10 s (robots Crawl-delay), 199 pages |

### AS-2 ECAT — key numbers

- 25 use categories; largest: decorative paints/varnishes **17,843**
  (≈ 20%), tissue paper 17,097, furniture 11,680, textiles 11,512,
  hard-surface cleaning 7,768.
- 88,384 PRODUCT vs 1,012 SERVICE rows; 3,375 licences; 2,433 distinct
  companies; 49 licence countries; 80,847 distinct licence×product
  pairs; 76,922 pairs appear once.
- Identifiers: EAN13 code rows 26,225; internal producer IDs 5,220;
  "Other" 4,084; GTIN14 260; **no code on 53,590 rows** (58%).
- `expiration_date` populated on **all** rows.
- Open: the old census key figure 17,013 distinct in-scope vs today's
  80,847 pairs is a counting-unit question (pairs vs in-scope-filtered
  distinct names), reconciled in the concept ledgers.

### AS-33 BASTA — key numbers

- 446 distinct companies, 1,185 brand names, 320 distinct BK04
  construction classes, 564 distinct BSAB codes.
- Identifiers: internal article id on 100% of rows; article number
  100%; **GTIN on 141,711 rows (71%)**; E-number/RSK/eBVD sparse.
- Declaration flags (JSON): 545 products carry
  `hasSubstancesCoveredByInformationRequirements` (the BASTA
  substance-information signal, relevant to the SDS question).
- `article_url` on 100% of rows (every record points at its public
  product page); `expiration_date` only 71 rows (BASTA validity is
  modelled differently — `grades`/`lastModifiedAt` instead).
- Largest classes: canal systems 23,711; plastic flooring 17,495;
  bolts/nuts/washers 7,655; rainwater systems 6,385.
- **Paint family (BK04 034xx "Färgvaror"): 7,526 rows** — facade paint
  exterior 2,100 / wall+ceiling interior 1,884 / other paint 1,044 /
  trim interior 860 / floor paint-oil 696 / primer 301 / oils+wood
  protection 187 / misc 181 / roof 169 / paint accessories 95 / trim
  exterior 7 / parent-code rows 2. (The `färg`-named subset = 7,339.)

### AS-3 Nordic Swan — reserved

`raw_as3_nordic_swan` exists and waits **empty**: the confirmed
`?format=csv` export route died 2026-10-03 (site redesign; re-verified
2026-10-04 — the whole historical export route family is dead live).
The archived 2026-09-14 snapshot (52,543 data rows × 10 columns,
sha256-verified in the raw store) remains the newest existing copy.
Re-acquisition needs the reserved `html_pages` walk interpreter
(`raw_sources/AS-3.instruction.json` records the case; same mode pinned
for environdec, `raw_sources/AS-7.instruction.json`).

## Common data headers across raw tables

Each raw table mirrors its source. The columns that matter for the
study's cross-identification (identity tuple) are marked:

| Common field | AS-2 ECAT | AS-3 Nordic Swan | AS-33 BASTA |
|---|---|---|---|
| Manufacturer / licensee | `company_name` ✓ | `licensee` ✓ | `company_name` ✓ (+ `company_id`) |
| Product name | `product_or_service_name` ✓ | `product` ✓ | `article_name` ✓ (+ `brand_name`) |
| Product number (source's own) | — (licence_number is a licence, not a product id) | — | `article_number` ✓ 100% |
| GTIN / EAN | `code_type`+`code_value` (EAN13 on 29% of rows) | — | `gtin` ✓ 71% |
| Category / product group | `group_name` (25 classes) | `category`, `product_group` | `bk04_code`+`bk04_name` (320), `bsab_code` (564) |
| Validity date | `expiration_date` 100% | — | `expiration_date` (71 rows) |
| Source's record id | `id` (row-level) | — | `source_article_id` ✓ 100% |

Bookkeeping columns on every raw table (never shown as data):
`_row_hash`, `_first_run_id`, `_last_run_id`, `_last_changed_run_id`,
`_truncated`.

Full column lists: AS-2 = 13 columns (`id, product_or_service,
licence_number, group_name, code_type, code_value,
product_or_service_name, decision, expiration_date, company_name,
company_country, vat_number, extract_date`); AS-3 = 10 reserved
(`product, license_number, ecolabel, category, product_group,
criteria_generation, brand, licensee, address, city`); AS-33 = 22
declared (`source_article_id, article_name, article_number, brand_name,
company_id, company_name, gtin, bk04_code, bk04_name, bsab_code,
bsab_name, enumber, ebvd_id, rsk, grade, article_description,
extensive_description, article_url, expiration_date, last_modified_at,
grades, flags`).

## Source register by class

| Class | Registered | Active | Note |
|---|---|---|---|
| AS (associations, registers, ecolabels) | 36 | 10 | 2 loaded (AS-2, AS-33); AS-3 reserved; AS-7 walk-pinned; AS-5 gated-refused; AS-31 blocked |
| PE (product/SDS sites: mfr, DIY, marine, art) | 57 | 45 | recon-characterized; Hornbach storefront template proven (PE-20) |
| ST (structural statistics) | 7 | 2 | SPIN, PRODCOM/SBS |
| CS (customs/trade) | 5 | 1 | Comext (swiss-impex out of scope, D31) |
| LI (literature) | 4 | 0 | manual workstream, never probed (D27) |
| **Total** | **109** | **58** | |

## Reproduce

    sqlite3 data/leadhs.sqlite "SELECT COUNT(*) FROM raw_as33_basta"
    leadhs raw status            # per-source rows, coverage, drift
    leadhs raw explain AS-33     # the instruction contract, rendered
    make db-audit                # provenance rules R1–R9 + orphans

Provenance: all live facts carry their access date (2026-10-04 unless
stated); loaded data is byte-verified against instruction contracts
(`_row_hash` per record; manifest sha256 per instruction file). Source
access rules and history: `docs/study/DATA_SOURCE.md`.

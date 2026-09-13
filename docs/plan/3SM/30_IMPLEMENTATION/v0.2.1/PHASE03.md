---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE03 — Register expansion + CSV batch

## Objective

Expand the source register with the official-register, CS/ST, and
enumerated PE-universe rows, EU-only (D31), with the automated/manual
active flags set so the capability sweep is well-defined.

## Preconditions

- PHASE02 done (ASAdapter live; capability mode works).
- Clean working tree. Real-network go-ahead (`GO=1`) for any live
  verification of candidate URLs.

## Governing references

- `../../20_DESIGN/units/v0.2.1.md` (register-capability machinery;
  cap2/cap5 — active flag splits automated vs manual; PE universe
  enumerated not scraped, U4)
- `../../10_STRATEGY/DATA_SOURCE.md` (six source classes incl. AS;
  access & scraping discipline; D3 official exports)
- `../../10_STRATEGY/v0.2.1.md` (source expansion list; U4)

## Steps

1. **Add AS rows** (class_code `AS`) to `src/leadhs/dict/sources.csv`
   for the official product-level registers and association lists —
   EU Ecolabel ECAT, Nordic Swan, Blue Angel, INIES, IBU, environdec,
   CEPE member list, national paint associations (VdL DE, FIPEC FR,
   …). **`active=1` only where a data export exists** (CSV/API) —
   e.g. ECAT, Nordic Swan, environdec/IBU (shape confirmed in
   PHASE04); **auth-gated or XLSX-only → `active=0`** (Blue Angel,
   INIES) so they ride the manual record path. `access_method_code`
   is `download` or `api` for the automated rows, `manual` for the
   auth-gated ones.
2. **Add CS/ST rows:** PRODCOM (DS-059358), national statistical
   offices; PCN aggregate, SPIN, national product registers (per the
   v0.2.0 register workstream, EU-only). `access_method_code`
   `api`/`download` where a public export exists; `manual` where
   only an aggregate page.
3. **Enumerate the PE universe** (U4 — enumerated, not scraped):
   per-site `PE` rows — CEPE ~800 members → manufacturer sites (with
   an inclusion cap), DIY chains, marine, art — with the
   `channel=`/`inclusion=`/`listed_by=`/`listed_date=` notes idiom
   from the v0.2.0 batch; pin the per-channel inclusion caps and
   product-ident shapes in the CSV notes. No catalog scraping.
4. **CSV batch + load validation (pe6):** `leadhs source load` the
   CSV; the loader must exit 1 naming a bad row (validation live);
   `probe-dry` must plan every active row.
5. **Tests (t11, source-load block):** register loads clean with the
   expanded set; active=0 rows are not planned by probe-dry; AS rows
   dispatch to ASAdapter; duplicate-host guard still fires.

## Deliverables

Expanded `sources.csv` (AS/CS/ST/PE rows, EU-only, active flags);
`db audit` clean; probe-dry plans every active row.

## Exit gate

`leadhs source load` exits 0; `leadhs probe-dry` plans exactly the
active adapter-backed rows and skips active=0; `db audit` exit 0.

---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE06 — Report extension: publish + audit

## Objective

Assemble the compiled landscape report (od8: one DB-only assembly,
three renderers) — funnel summary + CN8 trade table + identity table
+ complete depth matrix + SDS-URL counts + pool model v0 + source
census — every number a staging/evidence query, published to
`docs/report/`.

## Preconditions

- PHASE05 done (dispositions complete; staging populated).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (report extension, granularity
  ladder, pool model, fu9; e5; c4)
- `../../20_DESIGN/MASTER/interfaces.md` (i12 od8; i16 numbers
  contract; i19/i20)
- `../../20_DESIGN/MASTER/architecture.md` (a28)

## Steps

1. **Funnel summary (top):** Q1 pool range per the model form
   `P(cn8) = M × s(cn8)` (method sheet in md; "modeled estimate"
   labels); Q2 = "definitively identifiable: N (floor)" — distinct
   (manufacturer_norm, ident_norm) pairs over staged registers; Q3 =
   SDS-reachable modeled reach (SDS-library recon × match rate;
   EPD registers = standardized-spec class); the v0.5 ratio formula
   (Q2÷Q1) with epistemic labels.
2. **CN8 trade table (G3/G4):** per CN8 — extra-EU imports kg/€,
   exports, intra-EU (flow-code caveat if unverified), production
   (correspondence or NACE-proxy caveat), member-state breakdown
   where cheap, observed-products floor per CN8 (register category
   proxy mapping with caveats).
3. **Identity table (G2/G5):** per register — entries, distinct
   manufacturers, distinct (mfr, ident) pairs, identity completeness
   %, category distribution; deduped union; ECAT ∩ Nordic Swan
   overlap pilot (containment + Jaccard, calibration-only label).
4. **Depth matrix (G1) + SDS counts (G6):** every source with
   tier + identity fields + linkage; counts per refined tier (fu8);
   per-PE-site SDS-URL counts.
5. **Source census (G7):** class × channel × country; enumerated vs
   probed vs counted.
6. **Rendering semantics (e5/c4):** report takes the optional
   staging path; staging sections render conditionally with an
   explicit "staging absent" note; any reconciliation failure renders
   as a visible flag on the affected number; csv/json carry the full
   structure.
7. **Goldens:** regenerate with review; reconciliation tests green
   (report numbers == staging queries).
8. **Publish:** `report-publish` → `docs/report/`; `db audit` exit 0.

## Deliverables

Extended `report.py` content layer; md/csv/json report; published
artifacts; goldens.

## Exit gate

Report renders on real data per i19/i20; every number provenance-cited
(run_key / staging query / URL + access date); reconciliation flags
visible (zero silent failures); published; audit exit 0.

## Execution results (2026-09-14)

Implemented the od8 landscape extension in `report.py` (`_landscape`
assembly: funnel / cn8_trade / identity / depth / census /
reconciliation), the `probe report --staging-db` option (default
`data/testdata.sqlite` if present — an option, not a new command, V9),
and the template sections. Suite: **299 passed, 2 deselected**
(7 new landscape tests in `tests/test_report_landscape.py`); goldens
regenerated with review; published `docs/report/probe-report.{md,csv,
json}`; `db audit` clean.

Real-data funnel (staging `data/testdata.sqlite`, run
probe-20260914-as2-2 / the CS-2 batches):

- **Q1 pool (modeled estimate):** P(cn8) = M × ppp × s(cn8) → range
  **[85,840, 343,360] products** — M bounds 800 (CEPE, AS-11 record) /
  3,200 (SBS NACE 20.30, ST-3 prior); **ppp = 107.3** (17,170 distinct
  pairs ÷ 160 ECAT licence holders); s = staged extra-EU kg share per
  CN8 (largest: 32091000 31.9%, 32089091 16.7%, 32099000 14.1%).
- **Q2 floor: 17,170** distinct (manufacturer, ident) pairs — the
  deduped union over staged registers (only ECAT staged this unit).
- **Q3 SDS reach (modeled): 3,590** — Σ sitemap products over the
  PE sites with sds_library_visible = 1 (match-rate assumption
  pending; upper bound shown).
- **v0.5 ratio (Q2 ÷ Q1): 0.05–0.2** — floor ÷ modeled range.

Section notes:

- **CN8 trade table:** all 13 CN8 × both flows with Σ kg / Σ EUR /
  staged-row counts (e.g. 32091000 flow 1: 1.43 G kg / 3.67 G EUR);
  flow-code caveat rendered (dictionary verified=13/13 → caveat
  cleared); per-CN8 observed-products floor explicitly **not
  computable** (register categories are criteria classes — the
  category→CN8 proxy is not pinnable in v0.2.2).
- **Identity table:** AS-2 — 17,838 entries, 160 mfr, 17,170 pairs,
  16.0% identity completeness, category distribution; union = Q2;
  **overlap pilot not computable** (Nordic Swan not staged — explicit
  zero-state, calibration-only when it computes).
- **Depth matrix (fu8):** tier 1 = 13 PE sites (name only, from recon
  floors), tier 2 = AS-2 (registry metadata), tiers 3/4 = none
  assigned (tier 4 only from recorded capability metrics — absence is
  not a zero claim); per-site SDS-URL counts: PE-23 = 1,133, PE-20 =
  659, PE-43 = 401, then single digits.
- **Census:** 101 enumerated · 54 probed · 35 counted-metric sources;
  class × channel table (PE/scrape 57, AS/manual 23, …).
- **Reconciliation (c4):** AS-2 staged 17,838 rows (no
  products_registered metric — reconciled against the staged count);
  CS-2 6,316 staged trade rows; **zero mismatch flags**.

Implementation notes: the pool model initially dropped the
products-per-producer factor (ratio > 1 nonsense) — fixed to the
design form M × ppp × s(cn8); fu8 tier labels and the no-metric
reconciliation wording polished after the first real render; csv =
matrix block first, landscape blocks appended (supersedes the D28
matrix-only csv contract, test amended).

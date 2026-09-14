---
unit: v0.2.3
built: 2026-09-14
updated: 2026-09-14
type: unit report (detailed, human-readable)
language: en
---

# Unit v0.2.3 — pool estimate v2 (meta-benchmarking with a magnitude verdict)

v0.2.2 answered the pool question (Q1) with a single model,
`P(cn8) = M × ppp × s(cn8)`. v0.2.3 replaces that single-model
headline with a **meta-benchmarking vote**: seven independent
benchmark quantities estimate the same pool; each lands in one of five
contiguous magnitude classes —
a) 20k–50k · b) 50k–100k · c) 100k–200k · d) 200k–300k · e) >300k
(totals below 20k vote as a visible `<a`) — and a pinned rule converts
the vote into a **dual-level verdict** (SKU = registry/product level;
formulation = shade/pack-collapsed). The verdict claims confidence
("reasonable-high") only when ≥3 available benchmarks converge at base
with no exclusive non-adjacent conflict; a tie renders a span plus the
flip assumptions; fewer than three computable benchmarks refuse
visibly. The funnel section of the published report now carries a
supersession banner and is kept for the publish history.

Machine-readable tables and per-source detail:
[probe-report.md](probe-report.md) (published from the evidence DB;
timestamp-hash snapshots per the publish-history policy).

## The verdict on real data

- **SKU level: class e (>300k products)** — confidence **not
  claimed**. Base votes: e ×3 (B2-SE, B2-DK, B3), d ×1 (B5), c ×1
  (B4), b ×1 (B1), a ×1 (B6); three benchmarks (B1, B4, B6) sit
  exclusively in non-adjacent classes and are recorded as divergent
  open items.
- **Formulation level: class c (100k–200k)** — confidence **not
  claimed** (divergences B1 → `<a`, B2-SE → e, B6 → a). The
  conversion rides a **pinned 1–10 shade-collapse band** — an
  assumption, flagged: the measurable key-tier deduplication on the
  staged ECAT register is small (name ×1.049, EAN ×1.266 over 17,838
  rows, 199 licences — the licence tier is a catalogue, not a
  compression), so the shade-collapse is not measurable from registry
  metadata.
- Reading: the >300k SKU-level vote is driven by the
  assumption-heavy rows (national-register scaling with scope
  corrections; PCN mixtures × paint-share × non-hazardous uplift);
  the divergence is reported, never smoothed away.

## The seven benchmarks

| # | Quantity | Vintage | Band |
|---|---|---|---|
| B1 | EU tonnage ÷ per-SKU throughput | 2024 (JRC AHWG) | 46,250–210,000 |
| B2-SE | SE PC paints/coatings (71,231) × EU scale × scope | 2022-09-15 | 1.81M–3.02M |
| B2-DK | DK notified total (≈40,000) × EU scale × paint share × coverage | undated web | 0.56M–1.02M |
| B3 | PCN mixtures (1,444,290; 2021) × paint share × uplift | 2021 | 144,429–866,574 |
| B4 | producers (800–3,300) × assortment (25–150) | 2020/2026 | 20,000–495,000 |
| B5 | certified count (36,960) ÷ penetration scenarios | 03/2025 | 123,200–739,200 |
| B6 | out-of-pool sanity anchors (non-official) | 07/2026 | 14,700–26,597 |

Extraction findings that feed the benchmarks (all primary-source
verified, accessed 2026-09-14):

- **BfR-Akademie Sweden deck:** the Swedish pc-pnt-\* counts
  (36,843 decorative + 23,822 protective/functional + 10,566 other =
  **71,231 paints/coatings**, Echo DB 2022-09-15) are **poison-centre
  notification submissions** (CLP Art. 45 PCN + voluntary), not
  KemI register products — the B2-SE row reads as an upper envelope.
- **SWD(2022) 435 final, Annex 16:** PCNs received 2021 =
  **1,444,290 dossiers** (multi-MS submissions counted once; expanded
  per-MS ≈7.7M); non-notified estimate 252,500–637,500 (in reality
  lower); **no paint share and no non-hazardous constant** — the
  B3 uplift stays an explicit assumption band.
- **JRC final criteria-revision report** (DOI 10.2760/4572222,
  published 2026-01-26; supersedes JRC145238): **no market-share
  data exist** ("exact data in terms of sales values and volumes of
  EU Ecolabel paints are not available") — official confirmation
  that the B5 denominator is an assumption. Official counts: 217
  licences / 36,960 products (03/2025); PRODCOM cross-check: EU-27
  acrylic/vinyl water-based production ≈729 Mkg (2022).
- **Danish CKAN dataset** ("Kemiske produkter og stoffer i tal",
  CC0): aggregates only, via an embedded Power BI report — no
  adapter possible (PHASE02 shape gate); the paint function split is
  not extractable under the D31 constraints. The at.dk on-page total
  (≈40,000 hazardous products) is the B2-DK base.
- **Eurostat SBS verify:** NACE C2030, EU27_2020, 2020, V11110 =
  **3,300 enterprises** (the prior 3,200 was a stale read — vintage
  flagged).
- **B6 anchors** (non-official aggregators, sanity-only): US
  named-colour catalogs 26,597 colours / 13 brands, ≈14,700 distinct
  after ΔE-dedup (Paint Color HQ 07/2026); AkzoNobel FR >3,000 DIY
  references; Benjamin Moore 3,500+ colours. No total-market product
  count exists anywhere — the documented gap stands.

## Code

- `src/leadhs/benchmarks.py` — the pure verdict engine: taxonomy,
  result constructors, named DB query functions (the module's only
  I/O), compute_b1–b6, vote table, dual-level verdict, md renderers.
- `src/leadhs/probe/adapters/` — the former 1,325-line `adapters.py`
  split into a package (cs, pe, as_adapter, st, _common); import
  surface and dispatch order unchanged; the PE monkeypatch target
  moved to the `pe` module.
- Report content layer: the pool estimate v2 section (vote table,
  both verdict blocks, compression note) in md/csv/json; funnel
  supersession banner; goldens regenerated and reviewed.
- Tests: 341 offline (38 benchmark tests on synthetic staging;
  4 report-layer tests incl. staging-absent degradation).

## Execution record

- PHASE01–04 built 2026-09-14 in one session; PHASE02 ran a
  verify-shape-first gate (GO=1) against the Danish CKAN API —
  verdict: no adapter (aggregates-only), tr3 extraction fallback;
  PHASE03 ran GO=1-gated extractions (BfR PDF, SWD(2022) 435 full
  text, JRC final report PDF, Eurostat SBS API) — all records carry
  URL + access date in the evidence DB or the method sheet.
- Evidence DB: four new records (ST-1 1,444,290; ST-3 3,300; ST-6
  40,000; ST-7 71,231 — the last two sources newly registered);
  `db audit --unreferenced` clean; no metric-vocabulary migration
  (i4: migration-extended only — estimate constants live in the
  module + method sheet, never as DB fields).
- Full probe re-run 2026-09-14 (waves 1–3, post-close-out): all
  headlines reproduced exactly (ECAT 17,838; Comext 6,316; verdicts
  unchanged); it caught a report-layer defect — trade queries summed
  across staged runs (CN8 values doubled on re-run) — fixed with
  uniform latest-run scoping + regression test (342 tests). Run,
  findings, benchmarking/comparison considerations, gaps and paths:
  companion document
  [benchmarking-0.2.3.md](benchmarking-0.2.3.md).

## Obstacles and incidents

- **Ad-hoc call errors during PHASE04a** (wrong positional arg,
  missing sqlite3.Row factory) — script-side, not code defects.
- **Two contract bugs caught by the golden/content layer:**
  `compute_b5` ignored its base-penetration scenario (span midpoint
  ≠ base scenario — fixed and asserted); the formulation vote was
  initially built from unconverted rows (fixed: the verdict's
  internally converted rows are the source of truth).
- The B6 anchor set initially mixed per-manufacturer counts into one
  span with landscape counts — bands now carry landscape-scale
  anchors only; per-actor counts ride as labels.

## Provenance

- BfR-Akademie (Östberg, 2022), product notifications according to
  Art. 45 CLP in Sweden:
  <https://www.bfr-akademie.de/media/wysiwyg/2022/NKPM2022/product-notifications-according-to-article-45-clp-in-sweden.pdf>
- SWD(2022) 435 final (full text):
  <https://www.parlament.gv.at/gegenstand/XXIII-II-1120/imfname_11205024.pdf>
- JRC final report on the EU Ecolabel criteria revision for paints
  and varnishes, DOI [10.2760/4572222](https://doi.org/10.2760/4572222)
  (cellar 751ecfef-fbf8-11f0-8da5-01aa75ed71a1)
- Eurostat SBS sbs_na_ind_r2:
  <https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sbs_na_ind_r2>
- Arbejdstilsynet Produktregistret:
  <https://arbejdstilsynet.dk/da/regler/registrering-af-kemiske-produkter/retningslinjer-til-omfattede-virksomheder>
- Paint Color HQ US colour-catalog census (non-official):
  <https://paintcolorhq.com> (accessed 2026-09-14)
- Evidence DB (`data/leadhs.sqlite`) run_keys
  probe-20260914-\*-manual; staging DB (`data/testdata.sqlite`) run
  probe-20260914-as2-2.

## Links

- Strategy turn: `docs/plan/3SM/10_STRATEGY/v0.2.3.md`
- Design: `docs/plan/3SM/20_DESIGN/units/v0.2.3.md`; build phases:
  `docs/plan/3SM/30_IMPLEMENTATION/v0.2.3/`
- Predecessors: [report-0.2.0.md](report-0.2.0.md),
  [report-0.2.1.md](report-0.2.1.md),
  [report-0.2.2.md](report-0.2.2.md)

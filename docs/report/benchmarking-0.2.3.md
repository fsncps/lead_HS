---
unit: v0.2.3
built: 2026-09-14
type: deep-dive (benchmarking and comparison considerations)
language: en
---

# Pool estimate v2 — results and benchmarking considerations (v0.2.3 companion)

Companion to the [unit report](report-0.2.3.md): what the
2026-09-14 full probe run delivered, and — in more depth than the unit
report — the **benchmarking and comparison considerations**: why each
of the seven benchmark quantities sits where it sits, what its
comparison base is worth, where the verdict is fragile, and which gaps
and paths follow. Nothing here changes the verdict; this document is
the reasoning record behind it.

Machine-readable report: [probe-report.md](probe-report.md)
(published; timestamp-hash snapshots per the publish-history policy).

## The run (2026-09-14)

Full real-network landscape run, waves 1–3 (budget 3600 s/wave,
staging `data/testdata.sqlite`; render `probe-report.20260914-083931`,
published snapshots `probe-report.20260914-084007.*`):

- **W1 — official exports:** ECAT re-staged **17,838 rows** (run
  `probe-20260914-as2-3`; reconciles exactly with both prior runs) and
  Comext **6,316 trade rows, all 13 CN8 codes** (run
  `probe-20260914-cs2-2`; per-CN8 sums reconcile with the published
  anchors). AS-3 format-finding; ST-4 pending (manual note restored).
- **W2 — register completion:** the five EPD/certification registers
  (AS-6 AS-7 AS-8 AS-9 AS-10) returned generic export-shape findings;
  the curated manual notes were re-recorded immediately (the pipeline
  itself flags these as "manual fallback required").
- **W3 — PE site walks (45 sources):** **34 counted**, 4 blocked
  (HTTP 403 ×3, persistent 429 ×1 — same sites as every prior run),
  6 failed retryable (503/network — same set as the morning run), 1
  sitemap unparseable (PE-53). The failure profile is **byte-stable
  across runs** — the blockers are deterministic bot-shields, not
  transient outages.
- Only substantive live drift vs the morning run: **PE-20 SDS doc
  links 659 → 652** (−7, register movement). All headline numbers
  unchanged: **Q1 [85,840–343,360] (superseded model, kept for
  history) · Q2 17,170 floor · Q3 3,590 · verdicts SKU class e /
  formulation class c**.

**Defect found and fixed during this run** (the reason the run exists
as a check): re-running a wave appends a new `run_key` — citable
history by design — but the report's trade queries summed across all
runs, **doubling every CN8 value**; the register sections already
scoped to the latest run. Fixed in the report layer (uniform
latest-run-per-source scoping), regression-tested; staged history
kept intact. See the v0.2.3 PHASE05 addendum.

## The verdict, in one paragraph

The EU paint/varnish pool is, on the balance of seven independent
benchmarks, **larger than 300,000 distinct products at the registry
level** (SKU: barcodes/licences/catalogue entries) and **100,000–
200,000 at the formulation level** (distinct recipes after shade/pack
collapse). Neither verdict claims confidence: at SKU level the vote is
3×e against three mutually exclusive smaller classes (b, c, a); at
formulation level the tally is 1·a + 1·b + 2·c + 1·d + 1·e — a spread,
not a convergence. The three e-votes (B2-SE, B2-DK, B3) share one
property: they scale a large register count to the EU with a scope
correction, and their bands' lower reaches overlap class c. The three
divergent votes (B1, B4, B6) are the ones built on assumptions rather
than register observations. **The pool question is settled to within
one order of magnitude at SKU level and much less well at formulation
level.**

## Per-benchmark considerations

### B1 — tonnage ÷ throughput (b at SKU; <a at formulation)

- **Comparison base:** JRC AHWG tonnage anchors 3.7–4.2 Mt/yr
  (apparent EU consumption, 2024) against per-SKU throughput scenarios
  20k–80k kg/yr. The staged Comext sums (2024 extra-EU imports:
  ≈2.47 Mt for HS 3208 + ≈2.10 Mt for 3209, ≈4.57 Mt combined) sit
  **above** the JRC apparent-consumption band — imports alone exceed
  it, which is physically consistent only if a large share of imports
  is base material / trade flows rather than finished consumer
  products, or if the JRC band is production-side. **Consideration:**
  B1 rides the method-sheet constants, never the staged sums — the
  two tonnage universes (trade vs consumption) must not be mixed; the
  CN8 table stays context, not a benchmark input.
- **The flip assumption:** throughput per SKU is the whole benchmark.
  At 40k kg/yr a band of ≈100k SKUs results; the abstraction
  literature (X4) pins the scenario order, but no official per-SKU
  figure exists. B1 is best read as **structure, not magnitude**.

### B2 — national-register scaling (e both levels; the heaviest votes)

- **B2-SE:** 71,231 SE poison-centre paint/coatings submissions
  (Echo DB 2022-09-15) × population scale ×42.4 × scope 0.6–1 →
  1.8–3.0 M. **Considerations:** poison-centre counts are
  **formulation-level by construction** (notified recipes, one per
  product placed on the market) but **voluntary-inclusive** — the
  count is an upper envelope that double-counts across pack sizes and
  includes professional-only products; the scope band 0.6–1 is a
  pinned judgement, not a measurement. The ×42.4 linear population
  scale assumes SE paint-market structure ≈ EU average — plausible
  (SE ≈ EU-mean income/HDI) but unmeasured.
- **B2-DK:** ≈40,000 DK hazardous-product notifications (at.dk,
  undated web figure) × ×76.3 × scope 0.183–0.333 → 0.56–1.0 M. The
  weakest input of the seven: the paint share is **not extractable**
  (Power-BI-only, D31) — the 0.183–0.333 scope band is built from the
  assumption that paints are 15–25% of the hazardous total at an
  82–75% hazardous share, both pinned. **Consideration:** B2-DK's
  vote is e only because the band's low end (558k) is still far above
  300k; its evidential weight should be read as "a hazardous-only
  register with a plausible paint subset already implies e" — the
  direction is robust, the number is soft.
- **Cross-check SE vs DK:** per-capita, the two countries' raw counts
  differ by ~7× (71k vs 40k with 8.7× population ratio) — consistent
  once the voluntary-inclusive vs hazardous-only scopes are applied;
  the two benchmarks are **not independent copies** (both are
  notification registers), so their shared e-vote counts as one
  evidence line with two calibrations.

### B3 — PCN mixture share (e at SKU; b at formulation)

- **Comparison base:** 1,444,290 PCN dossiers (2021, multi-MS counted
  once) × paint share 0.10–0.20 × non-hazardous uplift ×1–3. The
  **paint share is the load-bearing guess** — SWD(2022) 435 Annex 16
  publishes no product-group split (verified this unit); the 0.15
  base is the study's own prior. **Considerations:** PCN covers only
  hazardous mixtures (hence the uplift), counts **dossiers not
  products** (one dossier can cover a product family), and excludes
  non-notifying member states' placements. The b-vote at formulation
  level shows how sensitive the quantity is: one input (uplift 1×)
  moves it two classes.

### B4 — producers × assortment (c at both levels)

- **Comparison base:** 800–3,300 producers (CEPE members; SBS C2030
  3,300 enterprises 2020 — verified this unit) × 25–150
  products-per-producer. **Considerations:** the assortment band is
  pinned, and deliberately **not** derived from the staged PE sitemap
  counts — those are URL-level and dominated by one generalist DIY
  retailer (PE-20: 199,354 URLs of the 204,693 N2 total), which
  measures catalogue breadth of a marketplace, not a producer's paint
  assortment. Sitemap counts therefore **cannot** seed B4 (the reason
  B4's band starts at 25); a tier-1 observed-listings count from
  specialist producers would. B4 is the vote closest to the
  commissioning user's own prior (20k–50k at its low end) — and its
  base (3,300 × 60 = 198k) lands in c, not a: the discrepancy vs the
  prior is assortment, not producer count.

### B5 — ECAT-inverse (d at both levels)

- **Comparison base:** 36,960 EU Ecolabel paint products (03/2025,
  final criteria-revision report — the official confirmation that no
  market-share data exist) ÷ penetration 0.05–0.30 (base 0.15 →
  246,400). **Considerations:** penetration is unmeasurable from
  public sources (that absence is official); ECAT partial-in-scope
  (69% of products registered, EUEB 04/2024) puts a floor under the
  certified count, not the penetration. The X1 refinement measured
  what ECAT itself can say about pool structure: key-tier dedup is
  small (name ×1.049, EAN ×1.266; the 199 licences are a catalogue,
  not a compression) — **the register is already near-SKU-unique**,
  which is why B5's d survives the dual-level conversion unchanged.

### B6 — literature anchors (a; the dissenter by design)

- **Comparison base:** US named-colour catalogues (26,597 colours /
  13 brands; ≈14,700 distinct after ΔE-dedup), one manufacturer's
  country DIY references >3,000, one manufacturer's range 3,500+.
- **Considerations:** these are **colour references, not products** —
  a category mismatch (one product line carries many colours; one
  colour many pack sizes); B6 is a sanity floor that says "even a
  single manufacturer's colour space reaches thousands" — it
  **bounds the debate from below** and exists to catch an
  implausibly low pool. Its a-vote at both levels is the pin: the
  verdict rule records it as an exclusive non-adjacent conflict
  (with the e-votes) and withholds confidence accordingly.

## Cross-benchmark and method considerations

1. **Register-based votes dominate.** B2/B3/B5 (the e/d votes) scale
   register observations; B1/B4/B6 (the divergences) scale
   assumptions. The verdict's direction follows the better-evidenced
   side — but the two groups are not independent (registers need
   scope corrections; assumptions need anchoring), so the meta-vote
   is a structured synthesis, not a poll of independent instruments.
2. **The formulation conversion is the weakest step.** One pinned
   constant (shade/pack compression 1–10) moves every benchmark; its
   midpoint (×5.5) happens to place the SKU verdict's e inside
   formulation class c's neighbourhood. The X1 finding that ECAT is
   near-SKU-unique does **not** measure shade-collapse (categories,
   not shade families) — the 1–10 band stays an assumption, flagged
   in the report.
3. **SKU vs formulation is the difference between "catalogue
   entries" and "recipes".** The study's downstream question (SDS
   reach) lives mostly at the formulation level; the SKU verdict is
   the market-size one. Both are published; neither claims
   confidence.
4. **Reproducibility is high.** Two full runs on 2026-09-14 differ
   only by live drift (−7 SDS links) and run_keys; the blocked/failed
   sets are identical — the pipeline's incident profile is
   deterministic, which makes future re-benchmarks (TODOS cadence
   entry) cleanly comparable.
5. **Vintage discipline held.** Every benchmark's band carries its
   vintage in the vote table; the newest register year is 2022 (SE),
   the oldest 2020 (SBS) — the pool question is answered on data
   older than the question in the worst case (B4), and the vote
   table says so.

## Gaps (unchanged by this run)

- **ECAT reconciliation:** group-044 filter vs Commission category;
  awarded-vs-registered gap (17,838 staged vs 38,233 awarded 03/2026);
  shade/pack variant counting not measurable from registry metadata.
- **Second register for the overlap pilot:** the Danish AT dataset is
  aggregates-only (shape gate, PHASE02); Nordic Swan needs a browser
  pass. The pilot stays explicitly not computable.
- **PE calibration:** the walk machinery idles (D31); B4's assortment
  band and the empirical products-per-producer remain unmeasured.
- **Q3 match-rate:** SDS reach (3,590) is still an upper bound; the
  match-rate assumption is pending (M2).
- **No EU paint product count exists anywhere** — official (JRC final
  report confirms no market-share data), industry, or literature; the
  study's verdict fills a documented gap and its own prior
  (20k–50k) is now the outlier to explain, not the benchmark.

## Paths forward

1. **Re-benchmark cadence** (TODOS.md): re-run B1–B6 when a materially
   better register lands; compare the verdict; append a dated
   supersession note if the class changes.
2. **Second register staging** (Nordic Swan browser pass) → the
   overlap pilot becomes computable and B5's penetration gets its
   first empirical bracket.
3. **Tier-1 observed-listings count** on specialist producers → B4
   trades its pinned assortment band for measured shelf breadth.
4. **Formulation-collapse evidence** (any register carrying both SKU
   and recipe identifiers) → replaces the 1–10 assumption band.
5. **M2 (SDS sampling)** consumes the verdict: the pool it samples is
   class-e at SKU level.

## Provenance

- Run + render: 2026-09-14 (waves 1–3; render `probe-report.20260914-083931`;
  snapshots `probe-report.20260914-084007.{d2d841e7-era}` — hash
  suffixes `0d69f230.md / 6010b9ba.csv / bbdb81a4.json`).
- Benchmark sources (all accessed 2026-09-14): JRC AHWG 2024 tonnage
  band (method sheet); Eurostat Comext DS-045409 via CS-2 (2024,
  staged); BfR-Akademie deck 2022 (SE Echo DB 2022-09-15, pc-pnt-*);
  at.dk Produktregistret page (≈40,000, undated); SWD(2022) 435
  Annex 16 (PCN 2021: 1,444,290; ≈7.7M expanded); Eurostat SBS
  sbs_na_ind_r2 C2030 2020 = 3,300; EU Ecolabel final
  criteria-revision report, DOI 10.2760/4572222 (217 licences,
  36,960 products 03/2025; no market-share data exist);
  Commission Ecolabel facts & figures 03/2026 (38,233 awarded);
  Paint Color HQ 07/2026 (26,597 colours / 13 brands);
  CoatingsTech 02/2021 (Benjamin Moore 3,500+); daiteo case study
  (AkzoNobel FR >3,000); EUEB BEUC-X-2024-078 (ECAT 69% in-scope
  04/2024).
- Vote/verdict mechanics: `src/leadhs/benchmarks.py` (method-sheet
  constants; pure functions); design
  `docs/plan/3SM/20_DESIGN/units/v0.2.3.md` (tr1–tr10).

## Links

- Unit report: [report-0.2.3.md](report-0.2.3.md)
- Published report: [probe-report.md](probe-report.md) ·
  [CSV](probe-report.csv) · [JSON](probe-report.json)
- Unit reports: [0.2.0](report-0.2.0.md) · [0.2.1](report-0.2.1.md) ·
  [0.2.2](report-0.2.2.md)

---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-03
---

# DEV_HISTORY — development history of all units (v0.1 … v0.2.4)

## Abstract

Distilled development history of the lead_HS study, compiled at the
v1→v2 migration (2026-09-18) from the legacy unit documents
(`docs/plan/3SM/10_STRATEGY/v0.*.md`, the v1 LOG, the design MASTER
state tables and git). One section per unit: what it set out to do,
what it delivered, what it changed. This doc is the in-tree record of
the pre-migration units; it is a **distillation, not the authority**
— the verbatim unit records remain in the read-only legacy tree, and
the authoritative decision register is `MASTER.md` (this directory).

## DECISIONS

- **DH1 (2026-09-18):** unit records are distilled here, not copied;
  the legacy v1 tree remains the verbatim record (read-only).
- **DH2:** strategy-decision numbers (D1–D41) referenced below point
  to the DECISIONS register in `MASTER.md` (this directory). Register
  coverage (2026-10-03): D1–D36 + D41 verbatim; D34's full text in
  legacy `v0.2.2.md`; D37–D40 as stub entries there (full text:
  legacy `v0.2.4.md`, distilled in the sections below).

## OPEN ITEMS

- Append one section per completed unit from the first post-migration
  unit onward (this doc stays LIVE across units).

## The arc in one paragraph

The study began (v0.1, 2026-08-31) as a documents-only estimate of
lead in EU paints framed by the Swiss Cassis-de-Dijon exception, then
narrowed twice on corrections (no laboratory; autonomous CdD frame,
not EU-bilateral) and pivoted (2026-09-12, D31) from building
sampling machinery to **measuring the data landscape first** —
numbers-first, reconnaissance-only, EU-only. The v0.2.x units then
walked the funnel from market anchors (v0.2.0) through source
capability (v0.2.1) and product identity (v0.2.2) to a pool-estimate
verdict (v0.2.3) and a per-registry evidence sample plus an
association/register sweep (v0.2.4 + D37–D40 addenda), ending the
era with exactly two confirmed bulk sources, a pinned BASTA surface,
and a pending product-DB turn (raw sourcing → matching → seeding).

## Phase A — v0.1, foundational strategy (2026-08-31 → 2026-09-10)

No build. The initial research pass (population triangulation, SDS
Section 3 lead detection, precision-based stratified sampling design
n ≈ 2,000–3,000) materialized as the strategy stage. Three scope
corrections defined the study's shape:

1. **Documents only (2026-08-31):** laboratory validation abandoned —
   no lab, no physical samples, no paid sources; corroboration
   replaces lab work (D7); cost constraint is hard (D9).
2. **Regulatory frame integrated (2026-08-31):** VIPaV Art. 2 Bst. a
   Ziff. 1 shields the Swiss lead-paint ban (ChemRRV Anhang 2.8,
   ≥ 0.01% total Pb) from EU-lawful imports; headline caveat: the
   Swiss ban sits below the EU SDS declaration floor 0.1% — the
   100–1000 ppm band is method-invisible (D15).
3. **Autonomous CdD, not EU-bilateral (2026-09-10):** THG Art. 16a
   reading verified (Lexaris); MRA out of scope; exceptions have
   institutional owners; for lead paints the requester/owner is BBL
   (verify before naming), BAFU enforces, SECO runs the five-yearly
   catalogue review (2023: keep; next ~2028). The study supplies
   outcome-neutral market numbers within that cycle (D11).
4. **EU-market leg first-class; HS 3213 census annex (2026-08-31,
   D12/D13).** Strategy topics METHODOLOGY/LEAD_SDS/DATA_SOURCE/
   DATA_MODEL/ARCHITECTURE added 2026-09-10; tooling, database and
   reporting principles fixed (D1/D16/D17/D18). Decisions D1–D18.

## Phase B — the probe era, M0 (v0.1.1 → v0.1.3, 2026-09-10 → 2026-09-12)

### v0.1.1 — source probing, slim CLI (built 2026-09-11)

- **Set out (D19/D20):** first bounded unit — `leadhs db init/status`,
  `source load/list`, `probe run/report` and nothing else; probing as
  the Phase-0 instrument converting OPEN register rows into verified
  access metadata; probe counts provisional, anchor promotion manual.
- **Delivered:** probe-era schema (migrations 0001–0002: lookups,
  source, document, run, probe_run, probe_finding + views), the single
  fetch seam (robots, rate limit, honest UA), three adapters
  (CS/PE/ST), the od8 report layer precursor, provenance audit R1–R9,
  exit-code convention. PHASE01–07 gate-verified (101 tests).
- **Empirical record:** the PHASE08 census feasibility pass
  (2026-09-11) found the gaps (CS-1 fetch failure, CS-2 query params,
  ST-2 fetch, PE probed at landing level, manual sources unrecorded);
  census close-out transferred to v0.1.2 (D26).

### v0.1.2 — operator layer + census close-out (built 2026-09-11)

- **Set out (D21–D26):** repo-root Makefile as stable operator
  entrypoint (one target = one `leadhs` call), `GO=1` confirmation
  gates for costly network and destructive targets, report routing
  (`data/report/` intermediates; `docs/report/` publish is explicit,
  D22), i18n policy (D23), distribution (wheel via managed
  interpreter, no PyPI, D24), structured per-source census report
  (D25), M0 close-out in this unit (D26).
- **Delivered:** exit-code enforcement + DB-init preflight, Makefile
  with `guard-%` gates, migration 0003 (per-HS metrics
  `records_hs3208/3209/3213` + `census_status`), od8 report content
  layer (one DB-only assembly, md/csv/json), 155 tests.
- **Changed mid-unit:** **D27** (scope correction — product data only
  in tool/database/reports; no legal referencing; supersedes D14) and
  **D28** (product-first census: the report leads with the two study
  numbers; register slims to product sources, migration 0004 prunes
  LG/LI; PE walk metrics `products_listed`/`doc_links_seen`). The
  D28 rework + census execution transferred to v0.1.3 (B8 precedent).

### v0.1.3 — data-landscape map (converged + FROZEN 2026-09-12)

- **Set out (D29/D30):** map before sizing — what is available from
  which source, at what scale, with what spec access; the
  **three-number deliverable N1/N2/N3** (market size / total data
  pool / detailed-data pool) ratified by the user as "the TOTAL
  PROJECT" (D30); channel enumeration with caps; frame-decision
  bridge; frame/sampling apparatus deferred behind the bridge.
- **Delivered:** PHASE01 (walk counters, migration 0004 = the D28
  rework; 165 tests); baseline census 2026-09-12 (3 done / 1 blocked
  / 3 failed; `db audit` clean).
- **Supersession:** the same-day **D31** user clarification — access
  census is the core, **no scraping (reconnaissance only)**, EU-only
  register, source discovery first-class, 3213 demoted to low-priority
  annex, numbers must be LARGE and visible — materialized as the new
  minor-version unit **v0.2.0**. v0.1.3 stays FROZEN; the walk
  machinery is built but idles (its execution never ran).

## Phase C — the numbers era (v0.2.0 → v0.2.4, 2026-09-12 → 2026-09-17)

### v0.2.0 — market scale & data availability, the numbers unit (built 2026-09-12)

- **Set out (D31, `v0.2.md`):** N1 market-size estimate from official
  statistics; N2/N3 access coverage counted where sources expose
  counts; AS-class source discovery (associations & registers);
  recon-only; EU-only. Design nu1–nu9 (CEO HOLD SCOPE; user 1A
  bounded sitemap-index expansion ≤ 5 children; ENG BIG CHANGE
  e1–e8 folded).
- **Delivered:** migration 0006 (AS class, probe_mode `recon`, 7
  metrics, CS-1 retired); register EU-only at 34 rows (per-site
  PE-10..34); **real anchors:** 2024 EU extra-EU imports — HS 3208
  ≈ 2.47 Mt / ≈ €12.21 bn, HS 3209 ≈ 2.10 Mt / ≈ €6.22 bn (Comext
  DS-045409, JSON-stat decode); SBS NACE 20.30 = 3,200 enterprises;
  CEPE ≈ 800 members; **N2 = 204,693 sitemap-visible product URLs
  across 23 counted sources; N3 = 9 sites with a visible SDS
  library**. 205 tests; report published. D32 (same day): easy
  vanilla-Windows install became the v0.3 distribution goal.

### v0.2.1 — source-level capability sounding-out (built 2026-09-14)

- **Set out (D33):** a product URL is not yet a product. Expand the
  register (ecolabel/EPD registers as official product-level sources;
  associations) and characterize each source against the product
  model **(CN8, manufacturer, manufacturer product-ident)** plus
  volume and depth tier. Strategic research finding: **no official
  EU chemical register publishes product-level paint data publicly**
  (PCN authority-only; SPIN/KemI substance-level; EuPCS taxonomy
  without CN8 mapping) — the ecolabel/EPD registers are the official
  product-level class.
- **Delivered:** probe_mode `capability` + six capability metrics
  (migration 0007), `ASAdapter`, register +AS-2..AS-7 (40 rows),
  capability report; **ECAT confirmed a real-product source —
  17,838 paints & varnishes** (the preliminary N2 numerator, a
  certified-subset floor). 231 tests.
- **Defect & review:** the environdec HTML-as-CSV incident (7 bogus
  findings, deleted; the `_sniff` gate + regression test landed in
  v0.2.2). The review found the headline number unreproducible from
  DB state and 6 of ~10 capability sources unmeasured → v0.2.2.

### v0.2.2 — the three-question funnel (built 2026-09-14)

- **Set out (D34):** answer Q1 pool per CN8 (modeled) / Q2
  definitively identifiable (counted floor) / Q3 SDS reachable
  (modeled reach) under **Product = manufacturer + identnr**; two
  enablers: a 30–60 min runtime budget (real export ingestion) and a
  **test-data staging DB** (`data/testdata.sqlite`) fed only from
  archived documents. Design fu1–fu10: three measurement layers
  (evidence facts / staging observations / derived analyses) with
  reconciliation by construction; "every number is a query result,
  never a typed literal"; four-wave run; test-backed disposition
  invariant (CEO HOLD SCOPE c1–c6; ENG BIG CHANGE e1–e8).
- **Delivered:** staging + normalize + xlsx modules, migration 0008
  (export anchors + `sds_doc_urls`), register at census shape
  (101 rows), wave harness, the real-network landscape run — 101
  rows dispositioned (36 counted / 48 manual / 4 blocked / 13
  inactive); ECAT 17,838 staged rows reconciled exactly; Comext
  6,316 trade rows (all 13 CN8). **Funnel: Q1 [85,840–343,360]
  (modeled) · Q2 17,170 distinct (manufacturer, ident) pairs
  (floor) · Q3 3,590 SDS-reachable (modeled upper bound) · v0.5
  ratio 0.05–0.2.** 299 tests. The overlap pilot (ECAT ∩ Nordic
  Swan) explicitly not computable until a second register is staged.

### v0.2.3 — pool estimate v2, meta-benchmarking (built 2026-09-14)

- **Set out (D35):** the Q1 range was too wide and opaque → replace
  the single model with a **benchmark vote**: six independent
  benchmarks B1–B6 vote into five contiguous magnitude classes
  (20–50k … >300k), dual-level (SKU + formulation), under a pinned
  confidence rule; research-intensive, minimal development. The
  evidence pass resolved open items with primary extractions (all
  URL + access-dated): Swedish pc-pnt-* counts are **poison-centre
  submissions** (71,231 paints/coatings 2022), not register
  products; **PCN 1,444,290 dossiers (2021)** with no paint-share
  constant; the JRC final Ecolabel report — **no market-share data
  exist** (official; 36,960 products 03/2025); Danish Produktregistret
  aggregates-only (≈40,000 hazardous products); SBS verify = 3,300.
  The user's 20k–50k prior was **unsupported**.
- **Delivered:** `benchmarks.py` verdict engine; adapters package
  split; **verdict on real data: SKU level class e (>300k),
  formulation level class c (100k–200k) — both
  confidence-withheld**; the formulation conversion rides a pinned
  1–10 shade-collapse band (flagged assumption; the measurable ECAT
  key-tier dedup is small: name ×1.049, EAN ×1.266 over 17,838 rows).
  341→342 tests; report re-published with supersession banner +
  timestamp-hash snapshots (render history policy addendum); the
  full re-run caught and fixed a trade double-count defect
  (latest-run-per-source scope). Companion:
  `docs/report/benchmarking-0.2.3.md`.

### v0.2.4 — management CSV sample + addenda D37–D40 (built 2026-09-14, executed through 2026-09-17)

- **Set out (D36):** per registry, 100 random 3208/3209 product items
  with all fields as CSV for management review
  (`probe download-csv-sample`, seeded, GO=1). Blunt research
  finding: **of the five benchmark registries only ECAT publishes
  product-level rows publicly** (EAN13/GTIN the only public unique
  identifier column); cross-identification across the five is not
  possible today — realistic paths are ECAT ↔ Nordic Swan and
  ECAT EAN ↔ retail catalogues.
- **Delivered (main unit, 364 tests):** AS-2 ECAT delivered
  100/17,013 distinct (identity: licence 100%, VAT 86%, EAN13 17%);
  AS-3 Nordic Swan `?format=csv` export discovered (9.8 MB); the
  four gated/aggregate registries got honest no-fetch manifest
  records; report `docs/report/report-0.2.4.md`.
- **D37 addendum (as-source-probe):** all 30 AS sources, one finding
  each — 2 delivered (reuse), 2 estimated (Blue Angel ≈70k,
  environdec ≈2k), 5 unavailable-with-why-not, 18 associations live
  + 3 unreachable (385 tests). The AS-class discovery answer became
  evidence-complete.
- **D38 addendum (corrections + source policy):** the AS-3
  "trial-grade 14 distinct" was a **tool defect** (scope filter +
  ECAT-shaped dedupe key) — true pool 2,424 rows / 2,322 distinct /
  53 licences; sample re-rendered offline (`--from-store`); estimates
  carry archived landing-page evidence; **`data_sources.csv`**
  introduced behind the **de5 gate** (probe-confirmed bulk + identity
  tuple + in-scope filter) — initial rows DS-1 AS-2, DS-2 AS-3
  (gated registers never enter on claims — de6); the consultant
  handover filed verbatim as next-unit INPUT (de7). 393 tests.
- **D39 addendum (full-probe round, 2026-09-15):** census (108
  sources) + fresh csv-sample (pools reproduce exactly) +
  as-source-probe over the six consultant-queue candidates
  (AS-31..36): **no third bulk source at URL-guess level** (KemiDigi/
  BASTA/WINGIS/eBVD/Quick-FDS no export surface ≤5 polite GETs;
  ECHA PT21 robots-blocked); data_sources.csv unchanged.
- **D40 addendum (BASTA special probe, 2026-09-17):** the
  "auth-gated API" answer **reversed** — the web client calls a
  same-origin anonymous proxy `<origin>/apiproxy/v3/...`, pinned
  verbatim from the site's generated OpenAPI client bundle; exact
  public counts pinned (**195,391 articles / 1,925 companies**; the
  unfiltered search advertises 200,769 — discrepancy recorded);
  seeded 100-article sample delivered (identity tuple 100%, GTIN
  69.8%); search pagination clusters per manufacturer (pooling
  method recorded honestly); the paint subset is identifiable ex
  post (BK04 03402/03404) but the server-side paint filter stays
  unpinned → **de5 not met, no third data_sources.csv row** (open:
  BK04 paint-code enumeration, TODOS.md). Fetcher learned to honor
  robots Crawl-delay (4B). 412 tests.

## Where the era left the project (state at migration, 2026-09-18)

- **Tool:** `leadhs` v0.2.x; migrations 0001–0011; 412 offline tests;
  `db audit` clean; register 108 rows (AS class 36); wheel builds;
  no release assets published yet.
- **Confirmed bulk sources (`data_sources.csv`):** AS-2 ECAT (17,013
  distinct) and AS-3 Nordic Swan (2,322 distinct); BASTA pinned but
  de5-blocked on the paint filter.
- **Headline numbers:** N1 anchors (trade/production above); census
  headline N2 ≈ 331,644 with floor 17,838 (register-level); pool
  verdict SKU class e / formulation class c (confidence-withheld).
- **Open empirical threads:** lead driers in EU alkyds (undocumented);
  ECAT 17,838-vs-38,233 reconciliation; BASTA BK04 paint enumeration;
  legal-text verification (ChemRRV/VIPaV consolidated texts); red-lead
  retail FR/IT.
- **Pending strategy inputs (none adopted):** MATCHING.md (record
  linkage, MA1–MA9), RAW_SOURCING.md (raw layer, R1–R9), INPUT-
  source-expansion-MSE (consultant queue + capture-recapture). The
  natural next arc: raw sourcing → matching → product-DB seeding —
  the "v0.3" label is double-booked (D32 distribution goal vs the
  product-DB turn); next unit id is a user decision.

## The decision spine (how the turns happened)

| decision | turn | effect |
|---|---|---|
| D26 | 2026-09-11 | M0 census close-out moves from v0.1.1 to v0.1.2 |
| D27/D28 | 2026-09-11 | product data only; product-first census; register slim |
| D29/D30 | 2026-09-12 | landscape map first; three-number deliverable (N1/N2/N3) |
| D31 | 2026-09-12 | the big turn: numbers-first, no-scrape recon, EU-only; v0.2.0 opens; v0.1.3 FROZEN |
| D32 | 2026-09-12 | vanilla-Windows install = v0.3 goal ("v0.3" label booked) |
| D33 | 2026-09-13 | product identity tuple (manufacturer, ident); ecolabel registers = official product-level class |
| D34 | 2026-09-14 | the three-question funnel (Q1/Q2/Q3) |
| D35 | 2026-09-14 | meta-benchmarking replaces the single pool model |
| D36–D38 | 2026-09-14 | csv sample; as-source-probe; de5/de6/de7 source policy |
| D39 | 2026-09-15 | probe-queue reconnaissance: no third bulk source |
| D40 | 2026-09-17 | BASTA surface reversed + pinned; de5 still open |
| D41 | 2026-09-18 | documentation-tree split (docs/study/ vs plan tree) |

Scale progression (offline tests / register rows / migrations):
101/–/0001–02 → 155/–/0003 → 165/14→9/0004 → 205/34/0005–06 →
231/40/0007 → 299/101/0008 → 341–342/101/– → 364–393/102+6/0010 →
412/108/0011.

## REFERENCES

- Legacy unit U-docs (verbatim, read-only):
  `docs/plan/3SM/10_STRATEGY/v0.1.1.md` … `v0.2.4.md` (+ `v0.2.md`)
- Legacy lifecycle log: `docs/plan/3SM/LOG.md` (v1 era)
- Legacy design deltas: `docs/plan/3SM/20_DESIGN/units/`; implementation
  trails: `docs/plan/3SM/30_IMPLEMENTATION/`
- Decision register: `MASTER.md` (this directory); design truth:
  `../DESIGN/`; facts: `../../PROJECT.md`
- Unit reports (public): `docs/report/report-0.*.md`

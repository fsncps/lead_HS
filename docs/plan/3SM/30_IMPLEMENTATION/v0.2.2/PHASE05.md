---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE05 — Landscape execution (GO=1)

## Objective

Run the four waves against the real network — official exports/APIs,
manual-web characterization, robots-compliant recon; no scraping
(D31/D3) — until every register row carries a terminal disposition
and the staging DB holds the W1/W2 observations with provenance.

## Preconditions

- PHASE04 done; **explicit real-network go-ahead (`GO=1`)**.
- Budget: default 60 min total (`--budget` override; maximum a few
  hours per the user direction); resumable per-source.
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (four-wave run, disposition
  state machine, c1/c2)
- `../../20_DESIGN/MASTER/interfaces.md` (i20)
- `../../10_STRATEGY/DATA_SOURCE.md` (access & scraping discipline;
  no bulk hammering)

## Steps

1. **W1 — bulk official exports (~20 min):** ECAT CSV full ingest
   (88,920 rows → group 044 staged with doc hash + retrieval date);
   Nordic Swan export (mechanics pinned; manual-record fallback
   without blocking); Blue Angel XLSX ingest; PRODCOM bulk TSV;
   Comext per-CN8 × flow batches (intra-EU flow codes verified —
   caveat if unclean). Exit: W1 sources `counted` or `blocked`
   +recorded.
2. **W2 — register completion (~10 min):** IBU/environdec real
   export inspection; INIES manual-record (auth-gated this unit);
   NF/natureplus/EPD-Norway/KEMI pinning; manual fallback steps per
   design. Exit: rows dispositioned.
3. **W3 — PE universe (~20 min):** ~75-site robots-compliant recon
   (sitemap product counts + `sds_doc_urls`); per-site fetch caps;
   resumable. Exit: recon dispositions complete.
4. **W4 — manual records & LI (~10 min):** VdL/FIPEC/BCF member
   counts; IPEN/UNEP/EEA/ILZSG product-count context; stragglers;
   every record with URL + access date (U7).
5. **Provenance repairs (from the v0.2.1 review):** ECAT manual
   records superseded by the staged ingest (export URL + access date
   + 16,001/1,817/20 breakdown now DB-cited); environdec claim
   recorded-or-softened (never asserted without a DB record); LOG
   defect note for the v0.2.1 HTML-as-CSV incident (written in
   PHASE07 close-out).
6. **Invariant check:** after each wave — no register row pending or
   format-finding; budget consumed per wave logged (c4).

## Deliverables

Four wave runs (resumable; per-source runs in the evidence DB,
staged rows in testdata.sqlite); disposition-complete register;
wave progress + budget log.

## Exit gate

Every register row dispositioned (counted | manual-recorded |
blocked); staging populated with provenance for all staged sources;
`db audit` exit 0; no silent failures (every non-counted row carries
its recorded reason).

## Execution results (2026-09-14, GO=1)

Ran 2026-09-14 (user-approved full run). Real DB `data/leadhs.sqlite`
(101 source rows: 88 active + 13 retired/capped inactive), staging
`data/testdata.sqlite`. Final dispositions over all 101 rows:
**36 counted, 48 manual-recorded, 4 blocked, 13 pending-by-design**
(the inactive rows — PE-1..4 superseded seeds, PE-45..52 beyond the
DIY caps, CS-1 Swiss-impex retired per D31 — are outside the studied
subset, per their notes). W4 gate: "nothing outstanding", exit 0.
`db audit` clean.

- **W1** (`--wave 1 --budget 1200`):
  - **AS-2 ECAT — counted, 17,838 staged rows** (run
    probe-20260914-as2-2): full CSV export ingested with doc-hash
    provenance; breakdown **16,001** (2014 decorative criteria) +
    **1,817** (2025 criteria) + **20** (performance coatings) —
    **matches the v0.2.1 manual record exactly** (reconciliation by
    construction). Aggregates: 160 distinct manufacturers,
    17,170 distinct name-manufacturer pairs, identity completeness
    16.0% (GTIN coverage is thin in ECAT).
  - **CS-2 Comext — counted, 6,316 staged trade rows**: all **13**
    CN8 codes delivered (per-code 52–624 rows; DS-045409 extra-EU,
    flows 1+2, VALUE_IN_EUROS + QUANTITY_IN_100KG, 52 queries).
    Dictionary U6 verified=13. Disposition rule extended: staged
    trade rows count as `counted` (staging-aware disposition).
  - **AS-3 Nordic Swan — format-finding → manual-recorded**: product
    search is a JS app (737 KB shell, no embedded data; export not
    GET-able) — recorded as documented deferral (browser pass
    deferred).
  - **ST-4 PRODCOM — manual-recorded**: dedicated PRODCOM API not
    desk-pinnable (dissemination API 404 for DS-059358/DS-066342;
    prodcom web app JS-rendered) — deferral recorded; SBS producer
    counts ride ST-3.
- **W2** (`--wave 2 --budget 600`): all five registers (AS-6..10)
  are JS/web-app front ends → format-finding → manual deferrals
  recorded (IBU per-product PDFs; environdec v0.2.1 claim softened
  to "not obtained" — provenance repair; NF per-criteria PDF lists;
  natureplus web app; EPD-Norway digi portal live, no bulk pin).
- **W3** (`--wave 3 --budget 1200` ×2 passes over 45 active PE rows):
  **34 counted** (sitemap product counts + sds_doc_urls recon),
  **4 blocked** (PE-22 bauhaus, PE-31 kremer, PE-41 gamma, PE-42
  praxis — bot walls), **7 deferred**: 6 unreachable from desk
  egress across two passes (PE-24 diy, PE-35 alpina, PE-40
  castorama, PE-54 boero, PE-56 de-ijssel, PE-58 talens) + PE-53
  veneziani (sitemap shape not parseable) — all with recorded
  reasons.
- **W4** (`--wave 4`, no fetches): manual records for AS-4/AS-5,
  the 20 association rows AS-11..30 (Q1 crawl targets; 2
  unreachable: AS-12 ivp, AS-24 malingoglakk), LI-2..5 (IPEN
  403-walled; SAICM/EEA/ILZSG context citations), ST-1/ST-5 (not
  obtained, page pins deferred), and the preset-gap trade sources
  **CS-3 Destatis / CS-4 Coeweb / CS-5 Datacomex / ST-2 SPIN**
  (no wave preset covered them — deferrals recorded; extending the
  W1 preset is follow-up work).
- **Engine fixes made during execution** (suite 292 passed, 2
  deselected; audit clean):
  1. staging-aware `disposition_of` (staged trade rows → counted);
  2. W4 checklist predicate broadened to the real c1 invariant
     (active rows of any class + inactive manual rows);
  3. **method-labeling bug fixed**: automated failure findings
     (UnexpectedFormat/access_blocked/robots_denied/ParseError/
     ExtractionError) were written with method_code="manual" —
     conflating "needs manual follow-up" with "recorded by hand";
     now they carry the observation method, "manual" stays reserved
     for `probe record` (19 existing findings relabelled via
     sample_n-null discriminator; manual runs untouched);
  4. disposition order fixed (a fully-manual run is terminal even
     when its deferral text quotes an automated marker);
  5. U6 dictionary verification wired into the CN8 batch (all 13
     codes delivered → dict verified=1) + 2 new tests.

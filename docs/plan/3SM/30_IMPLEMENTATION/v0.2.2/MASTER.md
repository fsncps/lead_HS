---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# Unit v0.2.2 — Implementation plan: the three-question funnel

> **Drafted 2026-09-14.** Executable phase plan for the D34
> product-identity and granularity sounding-out (strategy
> `../../10_STRATEGY/v0.2.2.md`, DRAFT; design
> `../../20_DESIGN/units/v0.2.2.md`, fu1–fu10 + CEO HOLD SCOPE +
> ENG BIG CHANGE reviews 2026-09-14, findings c1–c6 / e1–e8 folded).
> Seven self-contained PHASE files in the house format (objective,
> preconditions, governing references, steps, deliverables, exit
> gate). This unit rides the v0.2.0/v0.2.1 machinery (probe engine,
> mode dispatch, ASAdapter, od8 report layer, metrics sync test) —
> no new CLI command (V9), no new pipeline stage. PHASE05 touches
> the real network (official exports/APIs, manual-web,
> robots-compliant recon — no scraping, D31) and requires the
> explicit `GO=1`.

## Abstract

The executable phase plan for unit v0.2.2. The unit measures the data
landscape as a three-question funnel under Product = manufacturer +
identnr — Q1 pool per CN8 (modeled), Q2 definitively identifiable
(counted floor), Q3 SDS reachable (modeled reach) — by: ingesting the
bulk official exports into a **staging DB** (`data/testdata.sqlite`,
fed only from archived documents), completing the capability matrix
across the register, running the four-wave probe (bulk exports /
register completion / PE universe / manual+LI) under a 60-min default
budget, and assembling the compiled landscape report (funnel summary,
CN8 trade table, identity table + deduped union, depth matrix, pool
model v0, source census). Every published number is a staging query,
never a typed literal.

## Scope

Migration 0008 (source export anchors + `sds_doc_urls` metric) +
jsonstat module lift (TODOS item) + staging DB (`leadhs/staging.py`,
`normalize.py`, `xlsx.py`; engine ingest path with staging-first
ordered writes and run-close derivation) + register expansion to
census shape (~150–250 rows; PE universe enumerated) + wave harness
(`--wave`/`--budget`, generalized run filter, `make landscape`) +
W1/W2 adapter extensions + landscape execution + report extension.
Product data only (D27); recon-only (D31); official exports/APIs are
legitimate reconnaissance (D3).

## Phase tracking

| # | Focus | Depends on | Exit gate (summary) | Status |
|---|---|---|---|---|
| 01 | Migration 0008 (export columns + sds_doc_urls) + jsonstat module lift + TODOS retirement | — | 0008 applies; sync 0001–0008 green; CS fixtures ported to the module | done 2026-09-14 |
| 02 | Staging DB + normalize + xlsx modules; engine ingest path (staging-first, run-close derivation); tests | 01 | staging idempotent/rebuildable; ingest paths green per t12 | done 2026-09-14 |
| 03 | Register expansion to census shape (CS/ST/AS/LI/PE rows, export_url population, PE enumeration) + version 0.2.2 | 02 | register loads clean (~150–250 rows); probe-dry plans every active row | done 2026-09-14 (100 rows desk-enumerable; PE universe crawl = W3 content) |
| 04 | Wave harness (`--wave`/`--budget`/`--staging-db`, run filter, `make landscape`) + W1/W2 adapter extensions + t12 | 03 | wave tests green (budget/resume/invariant); `make landscape` guarded | done 2026-09-14 |
| 05 | Landscape execution (GO=1, wave by wave; W4 manual records) | 04 | every register row dispositioned; staging populated with provenance; audit exit 0 | done 2026-09-14 (36 counted / 48 manual / 4 blocked / 13 inactive-by-design; ECAT 17,838 staged reconciling exactly; Comext 13 CN8 codes, 6,316 rows; results in PHASE05.md) |
| 06 | Report extension (funnel, CN8, identity, depth, pool, census) + publish + audit | 05 | report per i19/i20 on real data; reconciliation flags visible; published | done 2026-09-14 (299 tests; funnel Q1 [85,840–343,360] / Q2 17,170 / Q3 3,590; published probe-report.{md,csv,json}; audit clean) |
| 07 | Docs & close-out (README EN/DE/FR, management summary DE/FR, LOG, goldens, wheel) | 06 | docs current with the real landscape numbers; wheel 0.2.2 | done 2026-09-14 (README EN/DE/FR + management summary DE/FR with the real funnel numbers; LOG entry incl. the v0.2.1 HTML-as-CSV defect note; wheel 0.2.2 install-verified; + addendum: publish history policy — timestamp-hash snapshots, see PHASE07) |

Statuses: `planned → in-progress → done` (update this table and the
PHASE file header when a phase starts/finishes). Build executes
phases only on explicit user instruction, in order; PHASE05
additionally requires the real-network go-ahead (`GO=1`).

## Acceptance criteria

From `../../20_DESIGN/units/v0.2.2.md` (Acceptance criteria) —
verbatim: migration 0008 applies (columns + `sds_doc_urls`; sync
green through 0008; renumber reflected); staging DB schema/loader in
`leadhs/staging.py`, idempotent replace, rebuildable from the
archive, provenance columns always populated (loud failure
otherwise); register loads at census shape, probe-dry plans every
active row; wave harness budget/resume/disposition-invariant per
t12, `make landscape` guarded (GO=1), no new CLI commands; landscape
run dispositions complete, W1 registers staged with provenance,
identity table + deduped union + overlap pilot computed from
staging, CN8 trade table populated, pool model v0 documented with
range; report carries the funnel summary + five new sections,
staging-conditional rendering, visible reconciliation flags,
published to `docs/report/`, `db audit` exit 0; full offline suite
green incl. t12; goldens regenerated with review; wheel builds at
0.2.2.

## Open items carried into build

- Nordic Swan export mechanics — **resolved at W1 as documented
  deferral**: JS app, export not GET-able; browser pass deferred.
- PRODCOM↔CN8 correspondence — **resolved at W1 as documented
  deferral**: dedicated API not desk-pinnable; SBS proxy rides ST-3.
- Intra-EU flow codes in DS-045409 — flows "1"+"2" verified at W1;
  intra-EU flow codes remain OPEN (batch joins them once verified).
- SPIN `.mdb` extraction — doctor-gated on mdbtools; deferred
  (ST-2 deferral recorded at W4).
- KEMI products-register statistics — **not obtained**; deferral
  recorded at W4.
- EPD export shapes (IBU, environdec, EPD Norway) — **deferred with
  recorded reasons** at W2 (all JS/web-app; browser passes needed).
- Blue Angel XLSX sheet layout — still to pin (AS-4 deferral at W4).
- CEPE member-list shape — pinned at PHASE03 (CSV batch done).
- Staging-DB retention/backup policy — one backup file next to the
  DB; revisit at v0.3 seeding.

## Handoff note

These files were drafted 2026-09-14 and follow the CEO review (HOLD
SCOPE, c1–c6) and ENG review (BIG CHANGE, e1–e8) of the same day —
see the design doc's review sections and the PHASE step texts.
Writing these files implies no freeze, stage advancement, or
execution start. Build executes phases only on explicit instruction,
in order; PHASE05 additionally requires the explicit real-network
go-ahead. Commit/push and any stage advancement await explicit user
instruction (3SM process).

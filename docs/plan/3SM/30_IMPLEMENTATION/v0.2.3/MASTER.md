---
unit: v0.2.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# Unit v0.2.3 — Implementation plan: pool-estimate meta-benchmarking (the magnitude-class verdict)

> **Drafted 2026-09-14.** Executable phase plan for the D35
> pool-estimate unit (strategy `../../10_STRATEGY/v0.2.3.md`, DRAFT
> + design-turn reframe; design `../../20_DESIGN/units/v0.2.3.md`,
> tr1–tr10 + CEO HOLD SCOPE c1–c7 + ENG SMALL CHANGE review
> 2026-09-14, decisions 1A/2A/split-in-P2 + TODO folded). Five
> self-contained PHASE files in the house format (objective,
> preconditions, governing references, steps, deliverables, exit
> gate). This unit rides the v0.2.0–v0.2.2 machinery end-to-end
> (staging DB + ingest path, register-row source model, od8 report
> layer, publish/snapshot policy, audit, jsonstat) — no migration, no
> new CLI command, no new Make targets (V9). PHASE03 touches the real
> network (official documents, manual-web, recon-only — no scraping,
> D31/D3) and requires the explicit `GO=1`.

## Abstract

The executable phase plan for unit v0.2.3. The unit answers "how many
individual paint products/formulas does the EU market hold?" with a
**magnitude-class verdict** — contiguous classes (20k–50k / 50k–100k
/ 100k–200k / 200k–300k / >300k), dual-level (SKU/registration and
formulation), under a pinned confidence rule — by computing six
independent benchmarks B1–B6 (tonnage-Fermi, national-register
scaling, PCN mixture share, bottom-up PE-calibrated, ECAT-inverse
with an empirical ECAT∩DK penetration probe, external literature) and
synthesizing them in a class-vote table. The v0.2.2 refinement
analyses (ECAT category structure with the compression factor per
key tier; PE assortment distribution) are supporting inputs, not a
gate. Benchmark arithmetic lives in a new pure module
(`leadhs/benchmarks.py`, ENG 1A) with named staging-query functions
and one shared synthetic-staging fixture builder (ENG 2A); the
adapters file splits per the TODOS watch trigger before the sixth
adapter (Danish AT CC0 dataset, staged as real rows) lands. Every
published number is a staging query or a dated extraction, never a
typed literal.

## Scope

`leadhs/benchmarks.py` (queries + compute functions + vote/verdict)
+ shared test fixture builder + full verdict-path tests + adapters.py
split into per-class modules (TODOS trigger) + DKAdapter + Danish
staging (register row, verify-shape-first, aggregates-only fallback,
counted-0 guard, chunked read) + X4 extractions (manual records,
GO=1) + benchmark execution on real data + report section
("pool estimate v2") with class-vote table, supersession note,
vintage discipline + close-out (docs EN/DE/FR, management summary,
wheel 0.2.3, LOG, TODOS updates). Product data only (D27);
recon-only (D31); official exports/documents are legitimate
reconnaissance (D3).

## Phase tracking

| # | Focus | Depends on | Exit gate (summary) | Status |
|---|---|---|---|---|
| 01 | `leadhs/benchmarks.py` (named queries, compute_b1–b6, vote_table, verdict) + shared synthetic-staging fixture builder + verdict-path tests | — | module + t13 verdict-path tests green offline (synthetic data only) | **done 2026-09-14** |
| 02 | Adapters split into per-class modules (TODOS trigger) + DKAdapter in its own module + Danish staging (verify-shape-first, fallback, counted-0, chunked read) + ECAT∩DK overlap probe | 01 | register loads with the DK row; adapter tests green (fixture, fallback, idempotency, interrupt) | **done 2026-09-14** (split landed; shape gate: aggregates-only via Power BI → **no adapter, tr3 extraction fallback**; ST-6 registered; overlap probe not computable) |
| 03 | X4 extractions (GO=1): BfR Sweden PDF, JRC145238 §3.4.3, SWD(2022) 435 Annex 16, B6 literature sweep | 01 | every extraction dispositioned with URL + access date; unresolved stays flagged; documented-gap acceptable for B6 | **done 2026-09-14** (BfR semantics resolved — PC submissions; JRC final report supersedes — no market share exists, 217 licences/36,960 products 03/2025; SWD Annex 16 — 1,444,290 dossiers, no paint-share constant; DK total 40,000 recorded, paint split Power-BI-only; SBS verified 3,300/2020; B6 anchors found) |
| 04 | Benchmarks on real data + report section (vote table, verdict, supersession, vintage flags) + goldens + audit | 02, 03 | report renders on real data per c1/c3/c4/c7; all t13 green; `db audit` exit 0 | **done 2026-09-14** (assemble() wired: B1–B6 on real DB inputs — SKU verdict class >300k, formulation class 100k–200k, both confidence-withheld with recorded divergences; pool estimate v2 section + funnel supersession banner in md/csv/json; 341 tests; goldens regenerated + reviewed; audit clean) |
| 05 | Close-out: publish + snapshots, docs (report-0.2.3.md, README EN/DE/FR, management summary), strategy/design/MASTER updates, wheel 0.2.3, LOG, TODOS updates | 04 | wheel 0.2.3 install-verified; docs current; TODOS split entry retired + re-benchmark entry added | **done 2026-09-14** (+ addenda: render history policy; full re-run — trade double-count defect fixed, companion doc benchmarking-0.2.3.md, see PHASE05) |

Statuses: `planned → in-progress → done` (update this table and the
PHASE file header when a phase starts/finishes). Build executes
phases only on explicit user instruction, in order; PHASE03
additionally requires the real-network go-ahead (`GO=1`).

## Acceptance criteria

From `../../20_DESIGN/units/v0.2.3.md` (Acceptance criteria) — X1/X2
computed from the staging DB with the compression factor documented
as a range per key tier; Danish register staged with full provenance
(or the aggregates-only fallback recorded with the extraction
results), paint counts by function/year extracted, ECAT∩DK overlap
probe computed and calibration-only labeled; extractions landed with
URL + access date, ambiguities flagged never silently resolved;
B1–B6 computed with explicit scenario assumptions; vote table +
verdict rendered per the pinned rule including its refusal paths
("insufficient basis", tie → span); divergent benchmarks carry open
items; report section + supersession note published with snapshots;
`db audit` exit 0; full offline suite green incl. t13; wheel builds
at 0.2.3; docs per convention.

## Open items carried into build

From the design doc (OPEN ITEMS) — each phase resolves or
dispositions its own:

- BfR-Akademie 2022 Sweden PDF — register products or PCN dossiers?
  (unresolvable ⇒ B2-SE stays indeterminate, visible per c1.)
- Danish CKAN resource shape — verify before the adapter (PHASE02
  gate); aggregates-only ⇒ extraction fallback (tr3).
- JRC145238 §3.4.3 — market-share estimate for B5 denominators.
- SWD(2022) 435 Annex 16 — mixture-count methodology (B3 dedup).
- B6 sweep — other-market product counts may not exist; a documented
  gap is an acceptable result.
- ECAT awarded-vs-registered semantics — consistency column, still
  open.
- SBS NACE 20.30 = 3,200 — verify in the Eurostat databrowser (B4).
- PE channel mapping (manufacturer-assortment sites) — pinned at
  PHASE01.

## Handoff note

These files were drafted 2026-09-14 and follow the CEO review (HOLD
SCOPE, c1–c7) and ENG review (SMALL CHANGE; 1A benchmarks module, 2A
queries + shared fixtures, split-in-P2, re-benchmark TODO) of the
same day — see the design doc's review sections and the PHASE step
texts. Writing these files implies no freeze, stage advancement, or
execution start. Build executes phases only on explicit instruction,
in order; PHASE03 additionally requires the explicit real-network
go-ahead. Commit/push and any stage advancement await explicit user
instruction (3SM process).

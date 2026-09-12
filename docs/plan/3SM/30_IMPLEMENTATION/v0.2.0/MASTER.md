---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# Unit v0.2.0 — Implementation plan: market scale & data availability (the numbers unit)

> **Built 2026-09-12.** All seven phases are done (phase table below),
> the offline suite is green (205 passed), and the probe report is
> published under `docs/report/probe-report.md`. The data-landscape map
> and the three headline numbers (N1 anchors, N2 = 204,693 sitemap-visible
> URLs across 23 counted sources, N3 = 9 sites with a visible SDS
> library) are documented; full results and the register workstream carry
> on in the Strategy docs and the next unit.

## Abstract

The executable phase plan for unit v0.2.0 (strategy
`../../10_STRATEGY/v0.2.md` — the D31 numbers-first turn, DRAFT;
design `../../20_DESIGN/units/v0.2.0.md`, nu1–nu8; CEO review HOLD
 SCOPE 2026-09-12, user decision 1A — bounded sitemap-index
 expansion). Seven self-contained PHASE files in the house format
 (objective, preconditions, governing references, steps,
 deliverables, exit gate). **The ENG review ran 2026-09-12 (mode
 BIG CHANGE): 3 architecture decisions (1A chain tolerance for
 expected exit 2; 2A one-dimension JSON-stat decode; 3A per-call
 fetch size cap) + 5 stated fixes (gzip sniff, namespace-local
 names, record --mode, year step-back, CS-2 dry-run plans sums) —
 folded as e1–e8 into the design doc (`../../20_DESIGN/units/
 v0.2.0.md`, ENG review section) and the PHASE files.** **PHASE01
 absorbs the un-built v0.1.3 groundwork**
 (source-load validation pe6 + migration 0005, with the corrected
 view — nu6); PHASE03 absorbs the enumeration model (pe1). Walk
 execution stays superseded (V4 — machinery idles); the i14
 walk-floor render defers with spec on file. PHASE04/PHASE05 touch
 the real network (APIs, downloads, manual-web, robots-compliant
 sitemap fetches — no scraping, D31) and require the explicit GO=1.

## Scope

N1 backbone (CS-2 full-year import aggregation, PRODCOM/SBS, PCN
verify, SPIN, AS counts) + N2/N3 access coverage (per-site recon:
robots/terms, sitemap product counts, SDS-library visibility) +
the numbers-first report + the EU-only register rework with the AS
class. No new CLI commands (one probe_mode value, one make target
pair); no new pipeline stages; product data only (D27).

## Phase tracking

| # | Focus | Depends on | Exit gate (summary) | Status |
|---|---|---|---|---|
| 01 | Absorbed v0.1.3 groundwork: source-load validation (pe6/i13) + migration 0005 (corrected view) + tests | — | validation exits 1 with row named; 0005 applies; sync 0001+0003+0004+0005 green | done |
| 02 | Unit machinery: migration 0006, recon mode + PE recon branch (1A), CS-2 aggregation, make probe-recon/recon + MODE var, version 0.2.0 | 01 | fixture paths per t10 green; sync through 0006; audit exit 0; wheel 0.2.0 builds | done |
| 03 | Discovery & register rework (AS/B2B candidates, per-site PE CSV batch, EU-only slim, PE-1..4 retirement) | 02 | register loads clean; probe-dry plans every active row | done |
| 04 | Statistics execution (CS-2 sums, ST-1/2/3 + AS records; GO=1; APIs/downloads/manual-web only) | 03 | count-bearing sources recorded or documented-blocked; audit exit 0 | done |
| 05 | Recon execution (phased GO=1 sweep + manual-web SDS visibility) | 03–04 | every active PE row recon-done/blocked/failed with findings; audit exit 0 | done |
| 06 | Numbers report render + assembly + publish + audit | 04–05 | report per i16 on real data; published; audit exit 0 | done |
| 07 | Docs & close-out (management summary DE/FR, register tables, drift markers, LOG) | 06 | docs current with the real N1–N3; translations drift-marked or updated | done |

Statuses: `planned → in-progress → done` (update this table and the
PHASE file header when a phase starts/finishes). Build executes
phases only on explicit user instruction, in order; PHASE04/PHASE05
additionally require the real-network go-ahead (`GO=1`).

## Acceptance criteria

From `../../20_DESIGN/units/v0.2.0.md` (Acceptance criteria) —
verbatim.

## Open items carried into build

- PCN aggregates — document-blocked acceptable (MASTER OPEN
  carries).
- National registers DK/NO/FI — public-statistics verification
  during discovery (PHASE03).
- B2B portal candidates — resolved or honestly OPEN by the PHASE03
  CSV batch.
- spin2000.net — SPIN download best-effort; documented-blocked
  acceptable (baseline timeout stands).
- product_pattern tokens — pinned per site in the PHASE03 CSV
  batch where known; generic fallback otherwise.
- Strategy convergence — `10_STRATEGY/v0.2.md` stays DRAFT; its
  freeze is a separate explicit user action (3SM process).

## Handoff note

These files were drafted 2026-09-12 and ENG-reviewed the same day
(mode BIG CHANGE; findings e1–e8 folded — see the design doc's ENG
review section and the PHASE step texts). Writing these
files implies no freeze, stage advancement, or execution start.
Build executes phases only on explicit instruction, in order;
PHASE04/PHASE05 additionally require the explicit real-network
go-ahead. Commit/push and any stage advancement await explicit user
instruction (3SM process).

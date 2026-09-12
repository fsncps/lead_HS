---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# Unit v0.1.3 — Implementation plan: data-landscape map (enumeration, priors, aggregate report, census execution)

## Abstract

The executable phase plan for unit v0.1.3 — the data-landscape
mapping unit (strategy `../../10_STRATEGY/v0.1.3.md`, refocused per
D29, converged 2026-09-12 on D30 — the three-number deliverable:
N1 → PHASE04+06 priors; N2/N3 → PHASE01/03/05/06 walks + aggregates;
design `../../20_DESIGN/units/v0.1.3.md`, pe1–pe7). Seven
self-contained PHASE files in the house format (objective,
preconditions, governing references, steps, deliverables, exit
gate). **PHASE01–02 absorb the outstanding v0.1.2 D28 rework and
census execution** (precedent B8/D26): the built code still predates the rework (no migration 0004, no
walk metrics, register 14 rows incl. inactive LG/LI),
and v0.1.2's PHASE07 is transferred here — both trails carry the
transfer marker. The plan was ENG-reviewed on 2026-09-12 (SMALL
CHANGE mode; findings C1–C3 below, folded into design before
finalization). PHASE01 also carries the D28 register slim in
`sources.csv` (nine product rows) — the upsert loader would
otherwise resurrect the pruned LG/LI rows. **PHASE01 is built
2026-09-12** (165 offline tests, goldens reviewed, audit clean on the
real DB); PHASE02+ await explicit go, PHASE02/PHASE06 additionally
the real-network go-ahead (`GO=1`).

## Scope

Land the D28 rework (migration 0004 product census: LG/LI prune +
`products_listed`/`doc_links_seen`/`walk_budget_exhausted` INSERTs +
v_anchor_candidates redefined; PE BFS walk with page budget;
product-first report per U11–U13) and execute the census (PHASE01–02).
Then the v0.1.3 delta: register enumeration with load validation and
per-site PE rows (PHASE03), the priors metric `products_registered`
via migration 0005 (PHASE04), the landscape-map report extensions —
aggregate floors over active sources, trade-context and priors
lines, frame-decision bridge (PHASE05) — execution of the
enumerated walks and manual priors records (PHASE06), and docs
(PHASE07). No new CLI commands, no new pipeline stages; M1–M4
surfaces stay stub targets. Schema carries product data only (D27).

## ENG review (2026-09-12, SMALL CHANGE mode — record)

One combined pass over the drafted plan; findings folded into the
design docs before the PHASE files were finalized:

- **C1 (architecture):** retired PE-1..4 rows still hold done
  landing-page runs and would double-count the Q1/Q2 floors once
  per-site rows exist. **Decision 1A:** aggregate floors sum
  **active** sources only; retired rows stay in the matrix,
  footnoted out of the sums (i14, pe7).
- **C2 (code quality):** the budget marker as a run-notes substring
  repeats the od9 R4 notes-seam mistake. **Decision 2A:** numeric
  metric `walk_budget_exhausted` (0/1) as the third INSERT of
  migration 0004; report reads it like any metric (i13, pe4).
- **C3 (tests, obvious fix):** `test_report_landscape.py` gains the
  hostile case "retired inactive PE-1..4 with done runs excluded
  from the sums" (folded into t9; no separate decision needed).
- Performance: no issue (bounded polite walks, grouped queries).
- Scope: stands (HOLD-SCOPE ratified at the 2026-09-12 CEO review).

## Phase tracking

| # | Focus | Depends on | Exit gate (summary) | Status |
|---|---|---|---|---|
| 01 | D28 rework (migration 0004, register slim CSV, walk metrics + budget metric, product-first report, tests, goldens) | — | suite green incl. sync 0001+0003+0004; two numbers + matrix on fixtures; audit exit 0 | done 2026-09-12 |
| 02 | Census execution (absorbs v0.1.2 PHASE07; real network, GO=1, phased) | 01 + explicit go | every row probed/manual; baseline floors exist; report published; audit exit 0 | planned |
| 03 | Enumeration register (load validation, per-site CSV batch, PE-1..4 retirement, version 0.1.3) | 02 | validation exits 1 with row named; enumerated register loads; probe-dry plans every active row | planned |
| 04 | Priors metric (migration 0005 `products_registered` + sync test) | 03 | 0005 applies; recordable via `make record`; v_anchor_candidates includes it | planned |
| 05 | Landscape-map render (aggregate floors active-only, trade/priors lines, bridge; csv/json; tests, goldens) | 04 | aggregate sections per i14 incl. C1 case on fixtures; goldens reviewed | planned |
| 06 | Walks + priors execution (enumerated register, real network, GO=1 phased; manual priors) | 03–05 + explicit go | floors over enumerated register; priors recorded or documented-blocked; bridge evidence present; audit exit 0 | planned |
| 07 | Docs & close-out (README, management summary three numbers, register statuses, DE/FR drift) | 06 | docs current with the real three numbers (N1–N3); translations drift-marked or updated | planned |

Statuses: `planned → in-progress → done` (update this table and the
PHASE file header when a phase starts/finishes). Build executes
phases only on explicit user instruction, in order.

## Acceptance criteria (from `../../20_DESIGN/units/v0.1.3.md`)

- `source load` rejects malformed rows (id pattern, url scheme,
  duplicate active host) naming the row, exit 1; the pre-slim
  14-row register still loads via `--file` (inactive LG/LI
  exemption).
- Migration 0004 applies (backup taken): LG/LI pruned from DB **and**
  register (sources.csv at nine product rows — the upsert must not
  resurrect them), products_listed/doc_links_seen/walk_budget_
  exhausted in the vocabulary and v_anchor_candidates; sync test
  green.
- Census executed (PHASE02): every row probed or explicitly manual;
  report published; `db audit` exit 0.
- Enumerated register loads; `probe-dry` plans every active row;
  PE-1..4 inactive with supersession notes.
- Migration 0005 applies; `products_registered` recordable via
  `make record`; v_anchor_candidates includes it.
- Map (md): aggregate Q1/Q2 floors with active-only sums, excluded/
  blocked counts, budget-limited flags, channel subtotals + overlap
  caveat, trade-context lines, priors lines, bridge (or deferred
  line); retired PE-1..4 never in the sums; csv/json carry the new
  fields; every number cites run_key/record.
- Full offline suite green incl. t9; goldens regenerated with
  review; version already 0.1.3 (early bump 2026-09-12 at user
  request — verified `--version`, install metadata, wheel).

## Open items carried into build

- PE-3 portal candidates — resolved by the PHASE03 CSV batch.
- CS-1 export mechanics — PHASE02 re-probe, else manual
  census_status record.
- SPIN mdbtools path + coarse counts — PHASE06 best-effort;
  documented-blocked acceptable.
- PCN formulation aggregates — manual-web; MASTER OPEN carries.
- Channel caps per batch — pinned in the CSV batch note (PHASE03).
- Strategy convergence — done 2026-09-12: converged on D30 (baseline
  census + pinned caps sufficed; N1 anchors land via PHASE04/PHASE06
  regardless of field outcomes); freeze recorded in the strategy docs.

## Handoff note

Writing these files implies no freeze, stage advancement, or
execution start. Build executes phases only on explicit instruction,
in order; PHASE02/PHASE06 additionally require the explicit
real-network go-ahead. Commit/push and any stage advancement await
explicit user instruction (3SM process); the LOG entry for this
planning pass is written.

---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# Unit v0.1.1 — Implementation plan: source probing (slim CLI)

## Abstract

The executable phase plan for unit v0.1.1. It formalizes the design
phases P1–P8 (`../../20_DESIGN/units/v0.1.1.md` §Implementation
phases) into eight self-contained `PHASE##.md` files: objective,
governing references, preconditions, steps, deliverables, exit gate.
The design docs carry the full detail; phase files restate only what
a builder needs at hand and cite the governing section for the rest.

## Scope

The probe-era slice of `leadhs` (nothing else; M1–M4 surfaces stay
design-ahead): migrations 0001–0002 + views; `db init|status|audit`,
`source load|list`, `probe run|record|report`, `doctor`; three
adapters (CS/PE/ST); exit codes 0/1/2/3/130; then the real census
run against the register (PHASE08 — execution, not code).

## Phase tracking

| # | Focus | Depends on | Exit gate | Status |
|---|---|---|---|---|
| 01 | scaffold (package, metrics, ids, errors, log helper) | — | `pip install -e .`; `leadhs --help` exit 0; 17-metric list importable; run_key deterministic | done |
| 02 | persistence (migrations 0001/0002, store, db, models) | 01 | fresh migrate clean; re-init idempotent; backup round-trips; audit exit 0 | done |
| 03 | network & env (fetch seam, doctor) | 01 | fake-clock spacing/robots/403/429/retry semantics; dry-run zero network; doctor preflight | done |
| 04 | register (sources.csv, source load/list) | 02 | 14-row load on fresh DB; audit clean; malformed CSV exit 1 | done |
| 05 | probe (engine + CS/PE/ST adapters + record) | 02, 03, 04 | outcome-based done/blocked on fixture site; exit codes; single write path | done |
| 06 | reporting (report.py from views) | 05 | md/csv/json golden render from fixture findings | done |
| 07 | tests (full matrix + fixtures) | 01–06 | suite green offline (net/mdbtools deselected); smoke + hostile + chaos | done |
| 08 | census run (operational execution) | 07 + explicit go | every OPEN register row probed or explicitly manual; report delivered; register Status updated | transferred to v0.1.2 (D26) — feasibility pass executed 2026-09-11; close-out in `../v0.1.2/PHASE07.md` |

Build state: PHASE01–07 implemented and gate-verified 2026-09-11 —
`pytest`: **101 passed, 1 deselected** (mdbtools-gated ST test;
markers net/mdbtools deselected by default), stable across sessions.
The PHASE08 census feasibility pass was executed 2026-09-11 (gaps
recorded); per strategy D26 the census close-out is delivered by unit
v0.1.2 (`../v0.1.2/PHASE07.md`) through the operator layer.

Statuses: `planned → in-progress → done` (per-phase; update this table
and the PHASE file header when a phase starts/finishes). PHASE08 is
post-build execution: it needs `doctor --net` preflight and an
explicit user go-ahead (real network, multi-minute pacing).

## Implementation decisions (ENG review of this plan, 2026-09-11)

- **A1 — ST-1 manual-only:** `sources.csv` sets ST-1 `active=0`
  (PCN is manual-web via `probe record`, which creates its own
  per-source probe run). `probe run --all` = active **and**
  adapter-backed sources only; no engine skip rule needed.
- **A2 — one logging helper:** new `src/leadhs/logutil.py` with a
  single `log_event()` (timestamp, module, event, url, status, ms);
  every module uses it — context-complete lines by construction
  (one-file addition to the design package layout).
- **A3 — adapter no-write test:** `test_adapters_contract.py` — each
  adapter runs against a `PRAGMA query_only=ON` connection and must
  complete draft-only (pins design i3; added to testing.md 2026-09-11).

## Acceptance criteria (from `../../20_DESIGN/units/v0.1.1.md`)

- Migrations apply clean on a fresh DB; re-init idempotent; backup
  taken on upgrade.
- `db audit` exit 0 on the fixture corpus; violations detected in
  negative tests.
- Full test suite green offline (net/mdbtools markers deselected).
- `probe run --dry-run` performs zero network calls (test-enforced).
- `probe report` renders md/csv/json from views.
- Census executed against the real register: every OPEN register row
  probed or explicitly manual (PCN), findings recorded, blocked
  sources documented (the Strategy unit deliverable).

## Open items carried into build

Resolved during implementation (2026-09-11, recorded in PHASE05):

- CS-1 dual mode → single census run recording format findings.
- PE sample-page selection → seeded random (`pe-sample-<source_id>`).
- `sample_n`/`mode` home → typed `probe_run.mode_code`;
  `parameters_json` = `{"sample_n", "dry_run", "contact_set"}`.
- Backup target directory → `data/backups/` (gitignored; confirmed).

Still open (post-build):

- swiss-impex export mechanics — answered by the CS probe at PHASE08.
- PE candidate-site seed list — enumerated during PHASE08; PE-3 has no
  confirmed portal yet (placeholder RFC 2606 URL in the register).
- SPIN mdbtools on Slackware — binary absent; doctor warns, ST adapter
  degrades to an extraction_path finding (tested). mdbtools install or
  alternate extraction path decided at PHASE08.
- PCN formulation-level aggregates — manual-web during PHASE08
  (`probe record`).

## Handoff note

Writing these files implies no freeze, stage advancement, or
execution start. Build executes phases only on explicit instruction,
in order. LOG entry and root-MASTER stage pointer await explicit
user instruction.

---
unit: v0.3.0
stage: DESIGN
lifecycle: LIVE
updated: 2026-10-03
branch: v0.3.0
---

# RUNS — v0.3.0 (instruction-driven raw source layer)

## DEFINITION OF DONE

User terms: a potential source URL goes `probe url` → ballpark; `raw
scan` turns a live delivery into a committed, reviewable JSON
instruction (with derived guards); `GO=1 make raw-run SOURCE=<id>`
registers the source, creates its raw table, and bulk-loads **every
record verbatim** into it — upsert + change journal, checkpoints,
truncation by priority never dropping a record; `raw status` reports
honest coverage vs the scan-derived expected counts. A new same-shape
source onboards with zero code changes. AS-2 (ECAT) and AS-3 (Nordic
Swan) are loaded live as the proof. The existing offline suite stays
green; `db audit` exits 0 after the live loads.

## QUALITY GATES

| Gate | Command | Policy | Runs at |
|---|---|---|---|
| static checks | `python3 -m compileall src tests` | clean | every run |
| user run review | per-run USER TEST PLAN below | pass | every run |
| offline suite | `make test` | green | FINAL (in r03) — **done 2026-10-03: 460 passed, 2 deselected** |
| provenance audit | `make db-audit` | exit 0 (after live loads) | FINAL (in r03) — **done 2026-10-03: audit clean (incl. --unreferenced)** |
| smoke | `make smoke` | green | FINAL (in r03) — **done 2026-10-03: 6 passed** |
| lint/typecheck | — | none configured (PROJECT) | — |

Regular runs gate lean (PROJECT testing economy); all authored testing
concentrates at FINAL.

## RUNS

| run | goal | state | SHA | review |
|---|---|---|---|---|
| r01 | raw schema + instruction foundation | DONE 2026-10-03 | 1a043db | user test plan pass (scratch DB: 0012 applies; refusals name paths; canonical hash stable) |
| r02 | scan + guards → committed instructions (AS-2, AS-3) | DONE 2026-10-03 | d098c3e (+ live fixes ca06e42) | pass — AS-2/AS-3 scanned live; AS-3 route dead → honest instruction; AS-2/AS-3 instruction files committed + reviewed |
| r03 | seed interpreter + live bulk load (+ FINAL folded, rs10) | DONE 2026-10-03 | 92408d1 + ca06e42 + 350d275 | pass — AS-2 loaded live (89,396 rows, 200/200 spot-checks); suite 460 green; smoke green; db-audit 0 |

Build session 2026-10-03 (user directive: single build pass, all runs,
then live). Run details live in the ENGINEERING ledgers; the unit
report is `docs/report/report-0.3.0.md`. Live-found facts recorded in
the Build record section of `interfaces.md` (degraded row-hash mode,
404 scan refusal, UTF-8-first decode, table_name field) and
`data_model.md` § Raw source tables (AS-2 loaded numbers, AS-3 route
death).

## r01 — raw schema + instruction foundation (offline)

dir: `../../ENGINEERING/v0.3.0/r01/` · plans: PHASE##.md…

Migration `0012__raw_layer.sql` (raw_source_profile, raw_export_kind
lookup seed, raw_as2_ecat, raw_as3_nordic_swan, raw_change); instruction
schema v1 module — model, canonical serialization (hash-stable),
fail-closed validation (unknown version/field, empty natural_key, delay
< 2 s, zero budget → named-field refusal); instructions dir convention
(`raw_sources/`, `--instructions-dir`); `raw explain`. No network.

### USER TEST PLAN

- `leadhs db init` applies 0012 on a copy; `db status` shows it; `db
  audit` clean.
- Feed `raw explain` a hand-made instruction — valid one renders; a
  mutated one (renamed field, zero budget, missing natural key) is
  refused with the named field and exit 1.
- Canonical check: re-serialize the valid instruction → byte-identical
  file, stable hash.

### PROVISIONAL TESTS — FINAL test-plan inputs

- Refusal matrix completeness (every fail-closed rule maps to a named
  error row).
- Canonical serialization stability across dict ordering/shuffling.
- Migration 0012 idempotence + forward-only chain integrity (0001→0012).

### SKILL RECORDS

### 3sm-eng-run SMALL (plan authored) — 2026-10-03
scope: r01 only (r02/r03 planning pends their predecessors per ENGINEERING
ROADMAP; guard-formula pin stays with r02 planning)
checklist:
- [x] startup reconcile — OK (git ↔ ledgers clean; `plan/ENGINEERING/`
      was empty → root MASTER + unit I-doc created; quiescence holds:
      all runs PLANNED)
- [x] Step 0 — OK (existing leverage: migration runner, click group
      pattern, exit-code convention, hashlib; minimum change set = 4 code
      files + .gitkeep; under sizing thresholds; no OPEN ITEM blocks r01)
- [x] mode — SMALL (offline, ≤8 files, one increment); batched round
      pre-answered by user directive "write plan, commit, stop" —
      findings encoded in PHASE01, listed in the completion summary
- [x] architecture — 1 finding (1A WARNING): manifest_hash must hash the
      canonical re-serialization, never raw file bytes — encoded in
      PHASE01 STEPS 2
- [x] code quality — 1 finding (2A WARNING): every refusal names its JSON
      path (stable targets for the FINAL refusal-matrix input) — encoded
      in STEPS 2
- [x] test review — functional-only; RUNS.md user test plan + provisional
      list carried verbatim, none new (escape hatch)
- [x] performance — OK (offline, file-sized inputs)
- [x] phase plan authored — r01/PHASE01.md
- [x] failure modes — 6 codepaths registered, all rescued, no silent rows,
      0 CRITICAL GAPS
findings: CRITICAL GAP 0 · WARNING 2 (both encoded) · unresolved 0
carries: build may take for granted — migration runner untouched (file
drop-in), `_ensure_initialized` deliberately absent from `raw explain`,
reserved export kinds render in explain (refusal is scan/run's);
FINAL covers the refusal matrix + canonical-stability + chain-integrity
inputs from RUNS.md r01 as written — no deltas from this pass
valid-until: RUNS.md re-plan, interfaces.md instruction-schema change,
PROJECT.md gate changes
commit: (this commit)

## r02 — scan + guards → committed instructions (AS-2, AS-3)

dir: `../../ENGINEERING/v0.3.0/r02/` · plans: PHASE##.md…

`probe url` (rs5); `raw scan` for `csv_snapshot` + JSON-API
(`single`/`page_param`): exact counts, columns + types + emptiness,
records-per-request, robots crawl-delay; guard derivation (rs4, flood
guard); draft emission; `raw status` (empty-table view). Offline:
fixture files + fixture site drive scan end-to-end. Live (GO=1): scan
the two real endpoints → committed `raw_sources/AS-2.instruction.json`,
`raw_sources/AS-3.instruction.json`, validated against the v0.2.4
samples (column maps, natural keys, priorities) — samples are fixtures,
not feed.

### USER TEST PLAN

- `GO=1 make raw-scan SOURCE=AS-2` (and AS-3): draft written; drift vs
  pinned keyfigures reported if counts moved; user reviews the two
  instruction files (the reviewable-contract gate — nothing flows
  before approval).
- `leadhs probe url <some URL>` prints the ballpark without touching
  the DB.

### PROVISIONAL TESTS — FINAL test-plan inputs

- Guard arithmetic (records-per-request → budget/delay) on synthetic
  scan profiles — the flood-guard boundary.
- AS-3 quirks: multi-licence strings, "." null token in natural-key
  handling.
- Drift reporting: expected_count mismatch surfaces in status/scan
  output, never silently.

### SKILL RECORDS

*(3sm-eng-run pass lands here at run planning; append-only.)*

## r03 — seed interpreter + live bulk load (FINAL folded, rs10)

dir: `../../ENGINEERING/v0.3.0/r03/` · plans: PHASE##.md…, PHASE_FINAL.md

`raw run` — init (source upsert + rs6 sync warning; profile row with
manifest_hash; create-if-not-exists table) + seed interpreter (fetch
honoring politeness, extract, upsert on natural key + sha256, journal,
batch checkpoints, `--cap/--dry-run/--resume`, refuse-on-existing-
checkpoint); `raw run --all`; Makefile targets (`raw-scan`, `raw-run`,
`raw-status`, `raw-explain`). Live (GO=1): full bulk load of AS-2 + AS-3,
verified vs expected counts. Then `PHASE_FINAL.md`: full offline suite,
`db-audit`, smoke, provisional-test reconciliation, whole-unit diff
review, docs sync (persistent `../interfaces.md` CLI surface, READMEs,
PROJECT commands/gates).

### USER TEST PLAN

- `GO=1 make raw-run SOURCE=AS-2` then `SOURCE=AS-3` (or `--all`):
  tables fill; `raw status` shows coverage vs expected; `db audit`
  exit 0.
- Interrupt mid-run (Ctrl-C → 130), rerun with `--resume`: continues
  from checkpoint, no duplicate journal entries, no lost batches.
- `make test` + `make smoke` green.

### PROVISIONAL TESTS — FINAL test-plan inputs

- Upsert triple correctness: new key / unchanged hash (skip) / changed
  hash (update + one journal row) — including `_truncated` changes
  flipping the hash.
- Deterministic truncation: same oversized record always truncates
  identically (priority order, tie-break by array order).
- Checkpoint resume across a page boundary; refuse-to-start with an
  unfinished checkpoint and no `--resume`.
- Register sync warning for an instruction whose source lacks a
  register CSV row (rs6, new-source path).
- Payload-budget edge: record exactly at 1024 bytes (no truncation) and
  1025 (truncated + flag).

### SKILL RECORDS

*(3sm-eng-run pass lands here at run planning; 3sm-eng-final +
3sm-ship-unit records land at finalization; append-only.)*

## CLOSURE (ship, 2026-10-09)

- r04 — unplanned post-FINAL live-operation run (user-directed):
  JSON dot-path projection (`3c1c7c5`), AS-33 payload budget 1024 →
  4096 first-light fix (`50f833c`), AS-33 whole-load verified
  (198,742 rows, 0 truncated), AS-7 reserved record. Booked in the
  unit ENG MASTER runs table at ship; PHASE plans waived per the
  unit's one-pass override, PHASE_FINAL backfilled in `r03/`.
- Ship unit pass executed 2026-10-09 (branch waiver: unit ran on
  main; no merge/branch-delete — archive + pipeline flip + tag
  instead). Skill record in the FINAL section below.

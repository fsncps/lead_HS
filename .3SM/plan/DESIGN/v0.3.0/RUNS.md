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
| offline suite | `make test` | green | FINAL (in r03) |
| provenance audit | `make db-audit` | exit 0 (after live loads) | FINAL (in r03) |
| smoke | `make smoke` | green | FINAL (in r03) |
| lint/typecheck | — | none configured (PROJECT) | — |

Regular runs gate lean (PROJECT testing economy); all authored testing
concentrates at FINAL.

## RUNS

| run | goal | state | SHA | review |
|---|---|---|---|---|
| r01 | raw schema + instruction foundation | PLANNED | — | — |
| r02 | scan + guards → committed instructions (AS-2, AS-3) | PLANNED | — | — |
| r03 | seed interpreter + live bulk load (+ FINAL folded, rs10) | PLANNED | — | — |

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

*(3sm-eng-run pass lands here at run planning; append-only.)*

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

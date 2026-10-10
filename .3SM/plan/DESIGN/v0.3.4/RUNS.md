# v0.3.4 — RUNS

---
unit: v0.3.4
stage: DSG
lifecycle: LIVE
updated: 2026-10-10
branch: v0.3.4
---

The unit's run overview: breakdown, gates, state. Authored by
`3sm-design-unit` at the runs-ready gate; build appends execution state
after each run.

## DEFINITION OF DONE

- `leadhs identity resolve` over the real DB (ECAT + BASTA raw tables)
  populates the canonical `manufacturer`/`product` tables; back-links
  cover every raw row minus counted, visible skips; a second resolve is
  a no-op (hash-identical canonical tables).
- `identity enrich` completes blank canonical fields from raw majority
  values; existing values change only on strict majority; ties never.
- `identity match` produces `linkage_candidate` verdicts with evidence
  tiers; re-runs never touch human decisions; the review queue is
  queryable and report-visible.
- `leadhs doctor` identity checks green; existing 461-test suite still
  green; the unit adds its own tests (target ~40–60).
- All decisions MA10–MA16 (concept) and il1–il15 (design) hold.

## QUALITY GATES

| Gate | Run | FINAL |
|---|---|---|
| lint/typecheck | — | none configured (PROJECT gates table) — run gate = user review |
| offline suite (`make test`) | grows per run as authored | FINAL — full suite green |
| db audit (`make db-audit`) | — | FINAL — exit 0 incl. --unreferenced |
| smoke (`make smoke`) | — | FINAL — green |
| live-op identity pass (real DB) | — | FINAL — user-tested |
| whole-unit diff review | — | FINAL (ship-unit pass) |

## RUNS

| run | scope | status | SHA | notes |
|---|---|---|---|---|
| r01 | canonical identity layer: migration 0013, resolve pass, `identity rebuild`, doctor identity checks | DELIVERED | 4a661e6 + 6b429f0 | 461 passed; real-data gates green (report-0.3.4-r01.md) |
| r02 | enrichment pass (majority fill/replace, MA13 rules) | PLANNED | — | — |
| r03 | matching layer: blocking + scoring + linkage_candidate + review-queue visibility | PLANNED | — | — |
| FINAL | full-suite + live-op verification + reconciliation | PLANNED | — | user decides fold vs FINAL dir at last regular run |

## r01 — canonical identity layer

dir: `../../ENGINEERING/v0.3.4/r01/` · plans: PHASE##.md…

**Goal (user-testable):** running `leadhs identity resolve` on the real
database fills the new manufacturer and product tables from the ECAT and
BASTA raw tables, links each product to its manufacturer, back-links raw
rows, records per-source counts — and running it a second time changes
nothing. `identity rebuild` tears down and re-derives behind a fresh
backup.

### USER TEST PLAN

1. `identity resolve --dry-run` — plans, zero writes, per-source plan
   lines visible.
2. `identity resolve` on the real DB — inspect: known manufacturer rows
   (spot SQL), product count vs ECAT group count, GTIN-collision list
   non-empty and counted (MA16).
3. `identity resolve` again — run summary shows creates=0/linked=0
   (idempotent no-op).
4. `leadhs doctor` — identity section: back-link coverage and manifest
   state green.

### PROVISIONAL TESTS — FINAL test-plan inputs

- Double-resolve hash-identity on the real DB (determinism showcase).
- SIGKILL mid-batch → re-run completes, counts consistent (chaos).
- Real-data blank/odd ECAT rows (empty norms) — skipped/refused counts
  reconcile to raw row counts.
- norm_manufacturer/norm_name behavior change — staging/overlap norm
  recompute consistency (fu7 consumers, il10).
- GTIN canonicalization edges: 8/12/13/14-digit, non-digit reject,
  EAN13 vs GTIN14 of one product → ONE canonical row (il16).
- Mixed-code-type groups (851 ECAT) — election determinism; multi_gtin
  count sane (il17).
- Rebuild on SQLite < 3.35 → named refusal, nothing torn down.
- Dry-run zero-write invariant on a fixture DB.

### EXECUTION RECORD — r01 build (2026-10-10, build session)

- Implemented per PHASE01 + REVIEW PINS; commits `4a661e6` (impl) +
  `6b429f0` (adapter SELECT fix). Migration 0013 applied to the real DB.
- Real run: AS-2 `identity_resolve-20261010-as2-4`, AS-33
  `identity_resolve-20261010-as33-2` — 288,138 raw rows → **2,857
  manufacturers / 271,005 products**, 100.0% back-linked, created=0 on
  re-run (il5 verified), doctor green. Public numbers + sample query
  (50 products): `docs/report/report-0.3.4-r01.md`.
- One defect caught at the dry-run gate: adapters selected only
  group-key columns (crash pre-write; two stuck run rows cleaned +
  annotated).
- PROVISIONAL inputs exercised on real data: double-resolve
  hash-identity ✓, dry-run zero-write ✓ (after fix), bad-GTIN refusals ✓
  (7, degraded to name basis, skipped=0), election determinism ✓
  (3,884 multi-code / 2,261 multi-gtin, ECAT). Still open for FINAL:
  SIGKILL chaos, rebuild round, SQLite<3.35 refusal, staging-norm
  recompute.
- USER TEST PLAN steps 1–6 executed by the build session (db init,
  dry-run, resolve, re-run, status, doctor); step 7 (rebuild) left to
  the user/FINAL. Run gate = user review (no linter configured).

### SKILL RECORDS

(3sm-eng-run pass on this run; append-only)

#### 3sm-eng-run r01 — 2026-10-10
scope: r01 phase plan + ledgers (no code)
checklist:
- [x] ledger reconciliation — 2 drift findings fixed (root ENGINEERING
  registry; RUNS.md gates row: no linter configured per PROJECT) — 7d410e7
- [x] Step 0 — leverage heavy (normalize/interpreter patterns/db/ids
  reused); minimum change (legal_forms CSV move → r03, OPEN ITEM in
  impl MASTER); 8 files exactly — at the smell line, justified (run
  split already maximal); open-items cross-ref clean
- [x] mode BIG (user)
- [x] PHASE01 authored — goal, data-flow + shadow diagrams, 8 steps,
  FILES TOUCHED, user test plan, FINAL inputs (8), failure modes
  (10 rows, 0 silent), NOT-in-scope (6), what-exists
- [x] Sec 1 architecture — issues: 1A canonical GTIN form (CRITICAL
  GAP-class: uuid-minting), 1B multi-code election (WARNING); user A/A
  → il16/il17 in the design MASTER; statements: FK-less back-link
  (SQLite limitation), coupling clean, SPOF unchanged — OK
- [x] Sec 2 quality — 0 questions; 4 statements pinned (quoting dup
  rationale, sorted-token norms as keys, normalize docstring refresh,
  name_norm-only manufacturer identity) — OK
- [x] Sec 3 tests — functional-only honored (no test authoring); user
  test plan executable as written; FINAL inputs registered above — OK
- [x] Sec 4 performance — 1 structural pin: single-pass ordered
  groupby + rowid back-link UPDATEs (never per-group WHERE scans);
  il13 in-memory index confirmed — OK
findings: CRITICAL GAP 1 (1A — resolved, user A) · WARNING 1 (1B —
  resolved, user A) · statements 7 · unresolved 0
carries: build may take the PHASE01 REVIEW PINS as settled (norm_gtin,
election, quoting duplication, single-pass shape, normalize docstring
refresh); FINAL inherits the 8 PROVISIONAL inputs above; r02/r03
planners: election counts + raw-side non-elected codes are the r01
contract, identity report visibility is r03 scope
valid-until: PHASE01 re-planned; il16/il17 revised; a linter gets
configured (PROJECT gates change)
commit: 7d410e7, 5b2da1a, cda8109, + this record's commit

## r02 — enrichment pass

dir: `../../ENGINEERING/v0.3.4/r02/` · plans: PHASE##.md…

**Goal (user-testable):** `leadhs identity enrich` fills blank canonical
fields (country, VAT, name, eu_group, brand, url) from the most common
raw values; an existing value is replaced only on a strict majority;
ties change nothing; a dry-run previews the would-be changes.

### USER TEST PLAN

1. `identity enrich --dry-run` — preview lines (field, old→new,
   majority count) plausible on known records.
2. `identity enrich` — spot-check a known manufacturer: country/VAT
   now filled; a tied field unchanged.
3. Re-run enrich — second pass is a no-op (self-healing converged).

### PROVISIONAL TESTS — FINAL test-plan inputs

- Real tie cases (fields splitting 50/50 across raw rows) — promote a
  fixture test; hand-expensive on live data.
- Dropped-raw-table refusal (SourceMissingError) after a deliberate
  DROP in a fixture DB.

### SKILL RECORDS

(3sm-eng-run pass on this run; append-only)

## r03 — matching layer

dir: `../../ENGINEERING/v0.3.4/r03/` · plans: PHASE##.md…

**Goal (user-testable):** `leadhs identity match` finds cross-source
candidate pairs via blocking, scores them (rapidfuzz, il7), stores
verdicts with evidence tiers, protects human decisions on re-runs
(il9), and the review queue is visible in the report layer.

### USER TEST PLAN

1. `identity match` on the real DB — pair counts per block sane;
   zero-state lines if a source pair yields nothing.
2. Query the review queue — inspect a known ECAT↔BASTA overlap sample.
3. Confirm/reject one review pair by hand — re-run match — the human
   decision survives (protected count reported).
4. Report layer — identity run rows + queue depth visible.

### PROVISIONAL TESTS — FINAL test-plan inputs

- Band-edge stability: pairs scoring exactly at T_high/T_low classify
  deterministically (fixture).
- Synthetic 500k-pair block → BlockTooLarge split + count (il6 cap).
- Calibration sweep output archived (labelled set + thresholds) — the
  first real run pins T_high/T_low via the Section 6 procedure.

### SKILL RECORDS

(3sm-eng-run pass on this run; append-only)

## FINAL — full-suite + live-op verification

dir: `../../ENGINEERING/v0.3.4/FINAL/` (or the recorded fold into r03,
user-directed)

Reconciliation: every PROVISIONAL item above → promoted test, covered
elsewhere, or dropped with reason. Whole-unit diff review; docs sync
(data_model raw-section gains the identity block + renumber note;
interfaces run-kind registry; PROJECT facts). Live-op: definition-of-
done walk on the real DB.

### SKILL RECORDS

(3sm-eng-final + 3sm-ship-unit passes; append-only)

## DECISIONS

(il-decisions live in the unit MASTER § DECISIONS — single source.)

## OPEN ITEMS

(tracked in the unit MASTER § OPEN ITEMS — single source.)

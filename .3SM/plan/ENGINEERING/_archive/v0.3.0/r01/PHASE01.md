---
unit: v0.3.0
stage: ENGINEERING
lifecycle: LIVE
updated: 2026-10-03
branch: main (unit-branch init waived by user, 2026-10-03)
run: r01
---

# r01 / PHASE01 — raw schema + instruction foundation (offline)

## GOAL

After this phase: `leadhs db init` applies migration 0012 — the raw layer
exists in the schema (`raw_source_profile`, `raw_export_kind` lookup with
its four seeded codes, the two pinned tables `raw_as2_ecat` /
`raw_as3_nordic_swan`, `raw_change`); `leadhs raw explain <SOURCE_ID>`
loads any instruction file from `raw_sources/` (or `--instructions-dir`),
validates it fail-closed against schema v1, prints its sha256 canonical
hash, and renders it readably; invalid instructions are refused with a
named JSON path and exit 1. No network, no scan, no seed — those are
r02/r03.

## STEPS

1. **Migration `src/leadhs/migrations/0012__raw_layer.sql`** — DDL per
   `../../../DESIGN/data_model.md` § Raw source tables (schema authority):
   - `raw_export_kind` lookup: `code TEXT PRIMARY KEY`, `description TEXT
     NOT NULL`; seed exactly four rows: `csv_snapshot`,
     `api_endpoint`, `web_query` (reserved), `html_pages` (reserved).
   - `raw_source_profile`: `source_id TEXT PRIMARY KEY REFERENCES
     source(id)`, `table_name TEXT NOT NULL UNIQUE`, `manifest_hash TEXT
     NOT NULL`, `export_kind_code TEXT NOT NULL REFERENCES
     raw_export_kind(code)`, `natural_key_json TEXT NOT NULL`,
     `payload_budget_bytes INTEGER NOT NULL DEFAULT 1024`,
     `created_at TEXT NOT NULL`.
   - `raw_as2_ecat` — the 12 verbatim columns from data_model (all TEXT
     NULL) + bookkeeping: `_row_hash TEXT NOT NULL`,
     `_first_run_id INTEGER`, `_last_run_id INTEGER`,
     `_last_changed_run_id INTEGER`, `_truncated INTEGER NOT NULL
     DEFAULT 0`.
   - `raw_as3_nordic_swan` — the 10 verbatim columns, same bookkeeping.
   - `raw_change`: `id INTEGER PRIMARY KEY`, `source_id TEXT NOT NULL
     REFERENCES source(id)`, `row_key TEXT NOT NULL`, `old_hash TEXT`,
     `new_hash TEXT NOT NULL`, `run_id INTEGER NOT NULL REFERENCES
     run(id)`, `note TEXT`; indexes `(source_id, row_key)` and `(run_id)`.
   - PostgreSQL-portable SQL only (d1/R1 hedge); forward-only file
     following the 0001–0011 pattern; no back-fills.
2. **Module `src/leadhs/raw/__init__.py` + `src/leadhs/raw/instructions.py`**
   — instruction schema v1 (authority: `../../../DESIGN/v0.3.0/interfaces.md`):
   - `InstructionError(Exception)` — message always names the JSON path
     (`politeness.request_budget_per_run: must be > 0`).
   - `Instruction` dataclass (explicit fields mirroring schema v1; frozen).
   - `load(path) -> (Instruction, manifest_hash)` and
     `from_dict(raw) -> Instruction`: parse + validate in one fail-closed
     pass. Refusal matrix (each row a distinct named error):
     unknown `schema_version`; any unknown top-level or nested field
     (typo protection); `natural_key` empty or referencing an undeclared
     column; `columns` empty; duplicate `column` values; column names
     starting with `_` (reserved bookkeeping namespace, data_model
     convention); `payload_budget_bytes <= 0`; `politeness.delay_seconds
     < 2.0`; `politeness.request_budget_per_run <= 0`;
     `export_kind` not one of the four codes; `pagination.kind` not one
     of `single|page_param|offset` (`cursor` reserved → refuse);
     malformed URL in `endpoints.list`.
   - Reserved kinds (`web_query`, `html_pages`): **valid** instructions —
     `raw explain` renders them; the interpreting commands (scan/run,
     r02/r03) refuse them. Validator stores the kind; refusal is not
     r01's job.
   - `to_canonical_json(inst)` — `json.dumps(sort_keys=True,
     indent=2, ensure_ascii=False)` + trailing newline;
     `manifest_hash = sha256(canonical_bytes)` — the hash of the
     **re-serialization**, never of the raw file bytes, so key order and
     whitespace in a hand-edited file do not change the contract version
     (design interfaces.md, rs2).
3. **CLI wiring in `src/leadhs/cli.py`** — `raw` group
   (`no_args_is_help=True`, house pattern) with one command this run:
   - `raw explain SOURCE_ID [--instructions-dir DIR]` — resolves
     `raw_sources/<SOURCE_ID>.instruction.json` (default dir
     `raw_sources/` relative to CWD); file-only command — **no**
     `_ensure_initialized` (like `doctor`); renders: source_id, name,
     class, export_kind, endpoints, pagination, records (expected count
     + count_derivation), the column table (source_header → column, type,
     truncation_priority, description), natural_key, payload budget,
     politeness incl. derivation, notes; prints `manifest_hash: <sha256>`
     last. `InstructionError` / missing file → `ClickException` (error
     line, exit 1); success exit 0.
4. **Convention dir `raw_sources/.gitkeep`** — the repo-committed
   instructions directory exists (real instructions land in r02).

Verification posture: functional-only (testing economy) — the user test
plan below is the run's only verification; all authored testing is
FINAL's.

Load path (four paths traced; error exits named):

    instruction file
      ├─ happy: parse → validate ok → canonical json → sha256 → render → 0
      ├─ nil:   file missing -------------------------- named error → 1
      ├─ empty: unparsable JSON ----------------------- named error → 1
      └─ error: validation refusal (named JSON path) -- refusal   → 1
    (no DB touched; no network; no partial state anywhere)

## FILES TOUCHED

- `src/leadhs/migrations/0012__raw_layer.sql` (new)
- `src/leadhs/raw/__init__.py` (new)
- `src/leadhs/raw/instructions.py` (new)
- `src/leadhs/cli.py` (edit — `raw` group registration)
- `raw_sources/.gitkeep` (new)

## USER TEST PLAN

(verbatim from RUNS.md r01 — executable without reading the plan)

- `leadhs db init` applies 0012 on a copy; `db status` shows it; `db
  audit` clean.
- Feed `raw explain` a hand-made instruction — valid one renders; a
  mutated one (renamed field, zero budget, missing natural key) is
  refused with the named field and exit 1.
- Canonical check: re-serialize the valid instruction (shuffle key
  order) → same `manifest_hash`; byte-identical canonical file.

## FINAL TEST-PLAN INPUTS

(RUNS.md r01 PROVISIONAL TESTS — no new ones this pass)

- Refusal matrix completeness (every fail-closed rule maps to a named
  error row).
- Canonical serialization stability across dict ordering/shuffling.
- Migration 0012 idempotence + forward-only chain integrity (0001→0012).

## LINT SCOPE

No linter/formatter/typechecker configured (PROJECT gates table); the
run gate is the RUNS.md static check: `python3 -m compileall src tests`
— clean on the five touched paths (plus the repo-wide effect of the new
module).

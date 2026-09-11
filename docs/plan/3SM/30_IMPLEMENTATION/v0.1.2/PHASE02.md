---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE02 — DB initialization preflight

Status: planned · Depends on: PHASE01 · Governs: the guided-error
contract for every schema-reading command.

## Objective

An uninitialized database currently surfaces as `bug: no such table`
— a bug label for a normal first-run state. `_ensure_initialized`
turns it into the guided error everywhere it can occur, in one place.

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §DB initialization preflight
  (od3).
- `../../20_DESIGN/MASTER/interfaces.md` — §DB initialization
  contract (i11).
- `../v0.1.2/MASTER.md` — B2 (preflight before connect; `mode=ro`
  check).

## Steps

1. **`_ensure_initialized(ctx, rt)`** in `cli.py` (B2):
   - `os.path.isfile(rt.db_path)` and `os.path.getsize(...) > 0`,
     else fail;
   - then open `sqlite3.connect(f"file:{path}?mode=ro", uri=True)`
     and check `sqlite_master` for `schema_version` (a read-only URI
     connection can never create the file); close in `finally`;
   - on failure print to stderr, exactly:

         error: database not initialized — run `make setup` (repo) or `leadhs db init` then `leadhs source load` first

     then `ctx.exit(1)` (→ `Exit(1)` → `main()` returns 1; never a
     `bug:` label).
2. **Wire as the first statement** (before `dbmod.connect`) in the
   seven schema-reading commands: `db status`, `db audit`,
   `source load`, `source list`, `probe run`, `probe record`,
   `probe report`. Explicit calls, no decorator (MASTER B3).
3. **`db init` stays the only initializer** — no preflight; it
   creates parent dirs and the file itself. `doctor` stays exempt
   (it must run on a fresh clone and only reads the DB under
   `--net`, guarded by its own existence check).

## Deliverables

`_ensure_initialized` + seven call sites in `src/leadhs/cli.py`.

## Exit gate

- Each of the seven commands on a **missing** file, an **empty**
  file, and a **file without `schema_version`** → the guided error,
  exit 1.
- `leadhs db init` on the same states → works (initializes).
- After `db init`, all seven commands proceed normally.
- A directory at `db_path` → guided error (isfile fails), not a
  traceback.
- Existing suite green; PHASE01 exit gate still holds.

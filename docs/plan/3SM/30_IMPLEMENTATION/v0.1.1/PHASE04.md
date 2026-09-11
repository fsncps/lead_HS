---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE04 — Source register

Status: done (implemented + gate verified 2026-09-11) · Depends on: PHASE02 · Governs: register of record
→ DB.

## Objective

The source register as a repo CSV (register of record), loaded and
listed by `leadhs source` — with the active-flag policy from the ENG
review (A1).

## Governing references

- `../../10_STRATEGY/DATA_SOURCE.md` — §Source register (the 14
  rows), §Probing pass, D1/D5.
- `../../20_DESIGN/MASTER/interfaces.md` — §Command contracts
  (`source load|list`), i2 (register of record = repo CSV; `source
  add` deferred).
- `../../20_DESIGN/MASTER/data_model.md` — §source table.
- ENG review 2026-09-11 decision A1 (ST-1 active=0).

## Steps

1. **Author `src/leadhs/dict/sources.csv`** — one row per register
   entry in DATA_SOURCE.md (14 rows: CS-1, CS-2, PE-1..4, LG-1..4,
   ST-1..3, LI-1); columns mirror the `source` table: `id,
   class_code, name, url, access_method_code, license_note,
   verification_status_code, active, notes`. `name`/`url` from the
   register; `notes` carries the register's Provides/Status gist.
2. **Active flags (A1):**
   - `active=1` — adapter-backed probe targets: CS-1, CS-2, PE-1,
     PE-2, PE-3, PE-4, ST-2.
   - `active=0` — **ST-1** (PCN: manual-web via `probe record`, which
     creates its own per-source probe run — its census evidence is a
     run, not an adapter), LG-1..4 (legal workstream — not probed),
     LI-1 (not probed).
   - ST-3 (PRODCOM) and CS-2 are already-verified statistics
     sources: CS-2 stays active (light re-check adapter), ST-3
     active=0 (verified; not a probe target this unit).
3. **`source.py`** — `load(conn, path)`: upsert by id (reference
   data — updatable in place, never deleted; P6); validates id
   format, class code against lookup, URL presence; **malformed CSV
   or bad row → exit 1, error names the row loudly** (hostile-QA
   rule); default path `src/leadhs/dict/sources.csv`, `--file`
   overrides. `list(conn, class=None)`: table of id, class, name,
   status, active; `--class CS|PE|LG|ST|LI` filter.
4. **CLI wiring** — `leadhs source load [--file CSV]`,
   `leadhs source list [--class …]`.

## Deliverables

`dict/sources.csv` (register of record, mirrors DATA_SOURCE.md);
source.py; `source` command group live.

## Exit gate

- Fresh DB → `leadhs db init && leadhs source load` → `db status`
  shows 14 source rows; `db audit` exit 0.
- `source list` renders all 14; `--class PE` shows the 4 PE rows.
- Malformed fixture (bad class, missing URL, duplicate id) → exit 1
  with row-identifying message.
- New PE seed sites discovered later enter as CSV rows + reload
  (i2) — no `source add` command exists.

## Open items resolved here

- A1 active-flag policy encoded in the CSV (ST-1/LG/LI/ST-3 = 0).

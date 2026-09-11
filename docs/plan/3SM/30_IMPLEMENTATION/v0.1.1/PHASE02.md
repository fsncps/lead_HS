---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE02 — Persistence

Status: done (implemented + gate verified 2026-09-11) · Depends on: PHASE01 · Governs: database layer.

## Objective

The probe-era database: both migrations, the raw store, models, and
the `db` command group (init/status/audit) with backup, stale-run
reclaim, and audit rules R1–R9 — all per the reviewed design
semantics.

## Governing references

- `../../20_DESIGN/MASTER/data_model.md` — §Conventions, §Migration
  plan, §Probe-era schema (lookups 0001; core tables + views 0002;
  dm14 `DEFAULT 'planned'`, dm15 `document.run_id NOT NULL`, covering
  index, v_probe_latest done-filter).
- `../../20_DESIGN/MASTER/interfaces.md` — §Command contracts
  (`db init|status|audit`), §db audit rules R1–R9, §Run semantics
  (stale-run reclaim, outcome rule).
- `../../20_DESIGN/MASTER/architecture.md` — §Module contracts
  (db.py, store.py), §Runtime model (pragmas).

## Steps

1. **`migrations/0001__probe_base.sql`** — 10 lookup tables per
   data_model.md §Lookups (0001): source_class (CS, PE, LG, ST, LI),
   access_method (api, scrape, download, manual), verification_status
   (verified, partially_verified, open, unverified), language (ISO
   639-1: de, fr, it, en, nl, sv, da, no, fi …), document_status
   (archived, manual, derived, not_found), run_kind (probe, acquire,
   import, sampling), run_status (planned, running, done, failed,
   blocked, aborted), probe_mode (census, format_check, access_check),
   probe_metric (17 seeds — must equal `metrics.py`
   `PROBE_METRIC_SEEDS`; sync test pins this in PHASE07),
   quantity_unit (count, chf, eur, kg, t, l, percent, ppm, year).
   Common shape: `code TEXT PK, label TEXT NOT NULL, description
   TEXT`; probe_metric adds `value_type TEXT NOT NULL CHECK (… IN
   ('numeric','text'))`.
2. **`migrations/0002__probe_core.sql`** — per data_model.md §Core
   tables (0002), with the reviewed semantics:
   - `source` — id TEXT PK (CHECK `^[A-Z]{2}-[0-9]+$`), class_code →
     source_class, name, url, access_method_code, license_note,
     verification_status_code DEFAULT 'open', active DEFAULT 1, notes.
   - `document` — id INTEGER PK; source_id NOT NULL; **run_id → run
     NOT NULL** (dm15); url, retrieved_at NOT NULL; raw_hash UNIQUE
     (CHECK archived ⇒ raw_hash); content_type, language_code, title,
     size_bytes, retrieval_method_code, status_code DEFAULT
     'archived', notes; index (source_id), (run_id).
   - `run` — id INTEGER PK; run_key UNIQUE; kind_code NOT NULL
     (CHECK kind='probe' ⇒ source_id NOT NULL); source_id;
     started_at NOT NULL; finished_at; **status_code DEFAULT
     'planned'** (dm14); parameters_json, seed, notes; indexes
     (source_id), (kind_code), (status_code), **(source_id,
     status_code, started_at)** covering v_probe_latest.
   - `probe_run` — run_id INTEGER PK → run; mode_code → probe_mode
     NOT NULL.
   - `probe_finding` — id INTEGER PK; run_id → run NOT NULL;
     metric_code NOT NULL; value_numeric/value_text (CHECK one
     present; presence per metric value_type — R4); unit_code;
     method_code NOT NULL; document_id → document; notes; indexes
     (run_id, metric_code), (document_id).
   - Views: **v_probe_latest** (latest **done** run per source ×
     metric, by started_at then run id — aborted/failed/blocked never
     shadow the census), **v_anchor_candidates** (latest findings,
     metric in catalog_count/category_count/export_rows),
     **v_source_activity** (first/last document retrieved_at, run and
     finding counts per source).
   - FKs all `ON DELETE RESTRICT`; standard SQL only (no AUTOINCREMENT,
     no PRAGMA in migrations; documented PG variances: id generation,
     partial-index syntax — the latter not used until 0004).
3. **`db.py`** — `connect(path, readonly=False)` applying pragmas
   (journal_mode=WAL, foreign_keys=ON, busy_timeout=5000);
   `migrate(conn)`: creates `schema_version` itself, applies pending
   files in order, one transaction each, **timestamped backup of an
   existing DB before applying** (default on; `db init --no-backup`
   skips; backups → `data/backups/` — open item, confirm here);
   `status(conn)`: applied/pending migrations, row counts, path+size;
   `audit(conn, store)`: rules R1–R9, human-readable report, exit 3
   on violation; `--unreferenced` lists raw-store orphans (R8);
   **stale-run reclaim**: `db init`/`db status` first mark any
   `running` run whose started_at is older than the current process
   (or > 1 h) as `failed` + note `stale run reclaimed` (a11).
4. **`store.py`** — `put(source_id, data: bytes, ext) -> (hash,
   relpath)`: filename `<sha256>.<ext>` only; source directory =
   source_id lowercased, must match `^[a-z]{2}-[0-9]+$`
   (path-traversal guard); `get(hash)`, `verify(hash)` (re-hash
   round-trip), `orphans()` for audit R8.
5. **`models.py`** — dataclasses: `SourceRef`, `Document`, `Run`,
   `ProbeFinding`, `FindingDraft` (metric, value/unit, method,
   document link, note), `ProbeContext`, `ProbeResult` (documents,
   findings, blocked/failed notes) per the interfaces.md adapter
   contract.
6. **CLI wiring** — `leadhs db init [--no-backup]`, `leadhs db
   status`, `leadhs db audit [--unreferenced]`; exit codes per
   interfaces.md (0 ok; 1 no/invalid DB path; 3 violations).

## Deliverables

Migrations 0001/0002; db.py, store.py, models.py; `db` command group
live.

## Exit gate

- Fresh DB: `leadhs db init` applies 0001→0002 clean; `db status`
  shows both applied; re-init is a no-op (schema_version idempotent).
- Seeded DB + pending migration → timestamped backup exists and
  restores to a working DB (round-trip check; full test in PHASE07).
- `db audit` exits 0 on a fresh/seeded DB; planted violation (R2
  archived doc without file; R4 value/type mismatch) exits 3.
- CHECKs enforced: probe run without source_id rejected; document
  without run_id rejected (dm15); run without status defaults to
  'planned' (dm14).
- `store.put` rejects `../`-style and malformed source ids.

## Open items resolved here

- Backup target directory: confirm `data/backups/` (gitignored).

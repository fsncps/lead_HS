# v0.3.4 r01 — PHASE01 — canonical identity layer

---
unit: v0.3.4
run: r01
phase: PHASE01
updated: 2026-10-10
---

## GOAL

After this phase, `leadhs identity resolve` turns the raw source tables
(AS-2 ECAT 89,396 rows, AS-33 BASTA 198,742 rows) into the canonical
`manufacturer` + `product` tables — deterministic uuid5 identity over
normalized keys, group-level collapse (MA12), one `product_uuid`
back-link per raw row — with `identity rebuild` (backup → teardown →
re-derive), `identity status`, and doctor identity checks. A re-run over
unchanged raw state is a no-op. `identity enrich` (r02) and matching
(r03) consume what this phase builds.

## DATA FLOW (with shadow paths)

```
                        ┌── identity_state: manifest_hash mismatch ──> ManifestDriftError
raw_<source_id> table   │
  │ SELECT *            │ missing table ──> SourceMissingError (skip source)
  ▼                     │
adapter (per source)    │ expected column absent ──> SourceSchemaError (refuse source)
  group rows (MA12)     │
  │                     │
  ▼                     │
normalize               │ blank key parts ──> NormalizeError (skip row + count)
  name_norm / ident     │ norm collapses empty / bad GTIN ──> EmptyNormError (count)
  │                     │
  ▼                     ▼
election (per group: gtin-wins, then min-sorted) ──> ident_string (typed composite)
  │
  ▼
match-or-create  <── in-memory index {name_norm → uuid, ident_string → uuid}  (il13)
  │ new: uuid5(NAMESPACE, domain:key)  (il4)
  ▼
BEGIN IMMEDIATE batch (500) ──> manufacturer / product INSERTs
  │                             └─ UNIQUE violation ──> loud IntegrityError (bug)
  ▼
back-link UPDATE raw.product_uuid per source row (ALTER-ensured column)
  │
  ▼
identity_state upsert (manifest_hash consumed) ──> run row (identity_resolve,
                                                  per-source count details)
shadow: --dry-run executes everything except writes; prints the plan lines
shadow: Ctrl-C ──> committed batches stay (idempotent re-run, il5) ──> exit 130
```

Code-comment diagram note: `resolve.py` embeds the shadow-path flow;
`spec.py` embeds the rebuild state transition (intact → backed-up →
torn-down → re-derived, abort before any teardown on BackupError).

## STEPS

1. **Migration 0013** — `src/leadhs/migrations/0013__identity.sql`,
   additive only (no ALTERs of built schema):
   - `manufacturer(uuid TEXT PRIMARY KEY, name_norm TEXT NOT NULL
     UNIQUE, name TEXT NOT NULL, country TEXT, city TEXT, vat_id TEXT,
     created_run_id INTEGER)`
   - `product(uuid TEXT PRIMARY KEY, ident_string TEXT NOT NULL UNIQUE,
     ident_nr TEXT NOT NULL, manufacturer_uuid TEXT NOT NULL,
     hs_code TEXT, eu_group TEXT, name TEXT, brand TEXT, url TEXT,
     created_run_id INTEGER)`
   - `identity_state(source_id TEXT PRIMARY KEY, manifest_hash TEXT
     NOT NULL, resolved_run_id INTEGER NOT NULL)`
   - `linkage_candidate(id INTEGER PRIMARY KEY, row_a TEXT NOT NULL,
     row_b TEXT NOT NULL, method TEXT NOT NULL, score REAL, band TEXT,
     verdict TEXT NOT NULL, review_status TEXT NOT NULL DEFAULT
     'pending', decided_run_id INTEGER, created_run_id INTEGER,
     UNIQUE(row_a, row_b, method))`
   - indexes: `product(manufacturer_uuid)`,
     `linkage_candidate(verdict)`, `linkage_candidate(review_status)`
     (r03 consumers; created now while the migration is fresh).
   - run-table provenance rides `run` (plain INTEGER run_id columns —
     house style; FK-free like the raw tables, R7 untouched).
   - Verify: `leadhs db init` applies it; `leadhs db status` lists it.

2. **normalize.py extension** (`src/leadhs/normalize.py`, in place):
   - control-character strip (`[\x00-\x1f\x7f]`) before folding in
     `_fold` (il8 — NUL bytes never enter a normalized key);
   - token-set order-insensitivity: `norm_manufacturer` and `norm_name`
     return the sorted-token form (`" ".join(sorted(tokens))`) — the
     identity regime's final shape, pinned NOW so uuids never churn
     (MA15/Stage-1 step 5). Display fields keep raw order; only norms
     sort. `norm_ident` unchanged (case- and zero-preserving).
   - new `norm_gtin(raw) -> str`: strip non-digits; accept 8/12/13/14
     digits (GTIN-8/UPC-12/EAN-13/GTIN-14); zero-pad to 14; anything
     else raises — canonical GTIN-14 form, kills the EAN13/GTIN14 dupe
     class (ECAT: 2,226 multi-EAN groups).
   - Note for build: this changes fu7 staging norms (probe engine
     imports normalize) — accepted by design (il10: staging is
     rebuildable); a staging recompute is a FINAL-test input, not a
     run-gate item.

3. **identity package** `src/leadhs/identity/`:
   - `__init__.py` — package docstring (the two-pass flow + state
     diagram), `NAMESPACE = "https://github.com/fsncps/lead_HS#identity-v1"`
     (il4), `DOMAIN_MFR = "manufacturer:"`, `DOMAIN_PROD = "product:"`,
     `ADAPTERS = {"AS-2": ecat, "AS-33": basta}` (il12 registry;
     imported from adapters to avoid cycles), `uuid_for(domain, key)`
     helper.
   - `errors.py` — named errors with one-line remedies:
     `SourceMissingError`, `SourceSchemaError`, `ManifestDriftError`
     ("run identity rebuild"), `NormalizeError`, `EmptyNormError`,
     `BackupError`.
   - `spec.py` — DDL constants (mirror 0013, used by rebuild's
     re-create), `ensure_backlink_column(conn, table)` (ALTER TABLE ADD
     COLUMN `product_uuid TEXT` + `CREATE INDEX IF NOT EXISTS
     "<table>_puid" ON "<table>"(product_uuid)` — idempotent; quoting
     per interpreter precedent), `sqlite_version_ok()` (DROP COLUMN
     needs ≥ 3.35 — named refusal otherwise).
   - `adapters.py` — plain functions returning groups (il12; resolve
     iterates GROUPS):
     - `ecat(conn)` — validates expected columns up front
       (`licence_number`, `product_or_service_name`, `code_type`,
       `code_value`, `company_name`, `company_country`, `vat_number`,
       `group_name` → SourceSchemaError naming offenders); GROUP BY
       (licence_number, product_or_service_name); per group: codes
       [(code_type, code_value)], manufacturer (company_name,
       company_country, vat_number), eu_group (group_name), name
       (product_or_service_name).
     - `basta(conn)` — columns (`company_id`, `article_number`,
       `company_name`, `article_name`, `brand_name`, `article_url`);
       GROUP BY (company_id, article_number); ident basis always
       `article:` (il3); BASTA `gtin` column NOT read for identity
       (raw-side matching evidence in r03); brand/article_url ride
       into canonical optional fields from the creating record.
     - Rows with blank group-key parts or blank manufacturer →
       NormalizeError (skip + count); codes normalized per il3 map:
       EAN13/GTIN14 → gtin (via norm_gtin), Internal Producer
       ID/Other → article (norm_ident), blank code_value → name basis.

4. **Election rule** (in `adapters.py`, one helper both adapters share;
   Section-1 confirms): per group, canonicalize every code, dedupe;
   - any gtin-class code → `gtin:<14-digit>`; multiple DISTINCT gtins
     in one group → elect min-lexicographic, count group as
     `multi_gtin`;
   - else article-class codes → `article:<mfr_norm>:<min sorted>`;
   - else `name:<mfr_norm>:<norm_name>`.
   Non-elected codes stay raw-side (back-linked rows carry them);
   counts surface in the run summary.

5. **resolve.py** — the pass (mirrors the data-flow diagram):
   - per source: identity_state check (hash mismatch →
     ManifestDriftError BEFORE any write), table-present check,
     adapter, election, match-or-create over the in-memory index
     (il13: bulk-load existing name_norm/ident_string → uuid at run
     start; write-through on create; `executemany` per 500-row batch,
     BEGIN IMMEDIATE per batch, named SQLITE_BUSY message);
   - back-link: ensure_backlink_column, then per group UPDATE the
     member rows' product_uuid;
   - identity_state upsert (hash consumed, resolved_run_id);
   - run row: kind_code `identity_resolve`, run_key
     `identity-resolve-<YYYYMMDD>-<source|all>[-N]` (ids.py builder),
     per-source details JSON: {rows, groups, created_mfr, created_prod,
     linked, skipped, refused, multi_gtin, multi_code};
   - `--dry-run`: identical read path, zero writes, per-source plan
     lines (groups/codes/name-basis counts); dry-run runs get
     status_code 'done' + dry-run note (d25 convention);
   - `rebuild` command path (in resolve.py, not the CLI group):
     take_backup → on failure BackupError (abort BEFORE teardown);
     DROP manufacturer/product, clear linkage_candidate, DELETE
     identity_state, ALTER TABLE DROP COLUMN product_uuid on every raw
     table that has it, then resolve all sources. SQLite ≥ 3.35
     enforced up front (named refusal).

6. **cli.py** — `identity` group (`no_args_is_help=True`, house
   pattern): `resolve [--source ID] [--dry-run] [--batch N]`,
   `rebuild`, `status`. `--source` validates against the register (d8
   pattern → usage error on unknown). DB-init preflight (d22: pending
   migrations → "run leadhs db init", exit 2). Exit mapping per
   INTERFACES: 0 ok · 1 usage/refusal-class (SourceSchemaError,
   SourceMissingError when sole source) · 2 blocked (ManifestDriftError,
   BackupError) · 130 interrupt. `identity status`: per source —
   resolved? (identity_state row), consumed hash, back-link coverage,
   queue depth (0 at r01).

7. **doctor.py** — identity section after the data-dir check (DB opened
   read-only, never created): tables present? (info: "identity layer
   not initialized"); per raw table with product_uuid: back-linked
   count, orphan count (product_uuid not in product → warn); per
   identity_state row: consumed hash vs current raw_source_profile
   manifest_hash (drift → warn + "identity rebuild" hint); absent
   identity_state → info. No identity rows → exit stays 0 (informational).

8. **Docs duty** — build appends the run row (status/SHA/tests) to
   RUNS.md + unit MASTER at the moment of truth (1A).

## FILES TOUCHED

- `src/leadhs/migrations/0013__identity.sql` (new)
- `src/leadhs/normalize.py` (edit)
- `src/leadhs/identity/__init__.py` (new)
- `src/leadhs/identity/errors.py` (new)
- `src/leadhs/identity/spec.py` (new)
- `src/leadhs/identity/adapters.py` (new)
- `src/leadhs/identity/resolve.py` (new)
- `src/leadhs/cli.py` (edit)
- `src/leadhs/doctor.py` (edit)

Unplanned files are a run-gate violation. report.py untouched (r03 owns
identity report visibility). No tests authored (FINAL owns testing).

## USER TEST PLAN

1. `leadhs db init` — applies 0013; `leadhs db status` shows it; backup
   exists under `data/backups/`.
2. `leadhs identity resolve --dry-run` — plan lines per source (groups,
   gtin/article/name-basis counts), zero writes (row counts unchanged).
3. `leadhs identity resolve` — real DB: summary shows AS-2 ≈ 80,847
   groups / AS-33 ≈ 193,456 groups; created/linked/skipped counts;
   multi-code counts visible. Spot-SQL: `SELECT COUNT(*) FROM product`;
   a known manufacturer row; `SELECT ident_string FROM product LIMIT 5`
   shows typed composites.
4. `leadhs identity resolve` again — created=0, linked=0 (no-op).
5. `leadhs identity status` — per source: resolved, coverage ≈ 100%,
   no drift.
6. `leadhs doctor` — identity section green (or informational pre-init).
7. (Optional, destructive-safe) `leadhs identity rebuild` — backup
   first, then re-derive; counts match step 3.

## FINAL TEST-PLAN INPUTS

(risky spots / hand-expensive branches; registered in RUNS.md)

- Double-resolve hash-identity on the real DB (determinism showcase).
- SIGKILL mid-batch → re-run completes, counts reconcile (chaos).
- Real blank/odd ECAT rows (empty norms) — skipped/refused reconcile to
  raw row counts.
- norm_manufacturer/norm_name behavior change — staging/overlap norm
  recompute consistency (fu7 consumers).
- GTIN canonicalization edges: 8/12/13/14-digit inputs, non-digit
  reject, EAN13 vs GTIN14 of the same product → ONE canonical row.
- Mixed-code-type groups (851 in ECAT) — election determinism
  (gtin-wins, min-sorted fallback); multi_gtin count sane.
- Rebuild on SQLite < 3.35 → named refusal, nothing torn down.
- Dry-run zero-write invariant on a fixture DB.

## LINT SCOPE

No linter/formatter/typechecker configured (PROJECT gates table). Run
gate = the user test plan above + build's WIP-commit hygiene.

## FAILURE MODES (new codepaths)

| codepath | failure mode | rescued? | test? | user sees? | logged? |
|---|---|---|---|---|---|
| adapter column check | ECAT/BASTA layout change | Y (SourceSchemaError, refuse source) | FINAL input | named error + column | run notes |
| manifest drift | re-scrape changed the raw table | Y (refuse source, rebuild hint) | FINAL input | named error | run notes |
| blank group keys | odd ECAT rows | Y (skip + count) | FINAL input | skipped count | run details |
| bad GTIN | letters/too-short codes | Y (EmptyNormError count) | FINAL input | refused count | run details |
| UNIQUE violation | concurrent writer / logic bug | N (loud, batch rollback) | FINAL input | traceback exit 1 | run failed |
| crash mid-run | SIGKILL/power | Y (committed batches, re-run) | FINAL chaos input | re-run completes | run rows |
| rebuild backup fail | disk full pre-DROP | N (loud BackupError, abort) | FINAL input | named error exit 2 | run notes |
| SQLITE_BUSY | two identity commands | Y (named fail-fast) | FINAL input | named error | run notes |
| SQLite < 3.35 rebuild | old bundled sqlite | Y (up-front refusal) | FINAL input | named error | — |
| orphan back-links | manual DB surgery | Y (doctor warn) | FINAL input | doctor line | doctor |

No silent + untested + unhandled rows. The only swallow-and-continue
class is counted row-level skip.

## NOT IN SCOPE (deferred, one-line rationale)

- `identity enrich` — r02 (reads what r01 builds).
- matching/blocking/scoring, rapidfuzz, review queue — r03.
- `ident_prefixes.csv`, `legal_forms.csv` move from the hardcoded
  frozenset — r03 (behavior-identical config churn; rides normalization
  scrutiny). OPEN ITEM recorded.
- identity report section — r03 ("review-queue visibility").
- hs_code/city canonical fill — reserved blank (no source carries them;
  MATCHING.md scan).
- BASTA `gtin` as identity — il3: article basis; gtin stays raw-side
  evidence until r03.

## WHAT ALREADY EXISTS (reused)

`normalize.py` norms + `identity()` (fu7 — extended, not rebuilt) ·
interpreter patterns (batch=500, dry-run, ensure, quoting — mirrored) ·
`db.py` migration auto-discovery, `take_backup`, `utcnow` · `ids.py`
run_key builder + next_attempt · unified `run` table · doctor
DoctorResult surface · cli group/exit conventions (i1/i10).

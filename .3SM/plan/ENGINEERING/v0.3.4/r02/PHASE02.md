---
unit: v0.3.4
run: r02
phase: PHASE02
status: PLANNED
updated: 2026-10-10
---

# r02 / PHASE02 — HS completion (curated map + deterministic apply)

## GOAL

After this phase the tool fills `products.hs_code` (currently empty,
migration 0013) for **all** product rows from a curated, versioned
mapping of each source's product-group key to its primary HS4 code:
`leadhs hs apply` loads `src/leadhs/dict/hs_group_map.csv` (build
curates a first pass: 25 ECAT `eu_group` values + 320 BASTA `bk04_code`
values, confidence-flagged), applies it deterministically and
idempotently (ECAT via `product.eu_group`; BASTA via the raw
back-link `product_uuid` with a per-product majority vote on
`bk04_code`), and `leadhs hs status` reports coverage in three states
(hs set / reviewed-out-of-scope / pending) plus the pending-group
worklist ranked by product count — which is simultaneously the de5
BASTA paint-subset enumeration. A new informational doctor line shows
HS coverage. Conflicts and unknown groups never block the pass; they
are counted and visible. Everything is run-booked (run_kind
`hs_apply`, counters, D18 traceability).

## STEPS

1. **Migration `src/leadhs/migrations/0014__hs.sql`** — `run_kind`
   INSERT only: `('hs_apply', 'HS completion', 'Curated group→HS4 map
   applied to products.hs_code')`. No other schema change (`hs_code`
   exists; update the test_migrations expected set when tests are
   authored).
2. **Mapping CSV `src/leadhs/dict/hs_group_map.csv`** — header
   `source_id,group_code,hs_code,confidence,note`. Build curates the
   first pass (user decision Q1: build first-pass + flags):
   - ECAT: `SELECT DISTINCT eu_group FROM product WHERE eu_group IS
     NOT NULL` (25 values, readable names) → primary HS4 each.
   - BASTA: `SELECT DISTINCT bk04_code, bk04_name FROM raw_as33_basta
     WHERE bk04_code != ''` (320 codes, Swedish construction
     classification) → primary HS4 each; `confidence` ∈
     `high|medium|flag` (flag = user review wanted); multi-HS groups
     record alternatives in `note`.
   - Rows with empty `hs_code` are legal = reviewed-out-of-scope
     (product stays NULL, counted separately from pending).
   - `source_id` values match the source register (`AS-2`, `AS-33`).
3. **Module `src/leadhs/hs.py`** —
   - `load_map(path) -> dict[(source_id, group_code), MapRow]`;
     MapRow = dataclass (hs_code, confidence, note). Validation:
     duplicate (source, group) → `HsMapError` (refuse before any
     write); hs_code when present must be 4 digits.
   - `apply(conn, map_path, *, dry_run=False) -> HsResult` — one
     transaction: open run row (kind `hs_apply`, params incl. map
     hash); ECAT pass: UPDATE ... FROM map join on eu_group; BASTA
     pass: `CREATE TEMP TABLE` votes (`SELECT product_uuid, bk04_code,
     COUNT(*) ... GROUP BY 1,2`), per-product majority, conflicts
     (≥2 distinct bk04 mapping to different HS4) → skip + count;
     counters: `ecat_set, basta_set, conflicts, pending, reviewed,
     unchanged`; close run row. Re-run on unchanged data → unchanged =
     all, 0 sets (idempotent by construction). `--dry-run` computes
     and reports, writes nothing (no run row).
   - `status(conn) -> HsStatus` — coverage query: products total / hs
     set / reviewed-null / pending, per-source breakdown, pending
     worklist top-N groups by product count.
   - Order dependency to document in the module docstring (with the
     ASCII diagram below): **run after any resolve/rebuild** —
     `identity rebuild` re-creates canonical rows and back-links, so
     hs values must be re-applied (apply is re-runnable by design).
4. **CLI `src/leadhs/cli.py`** — `hs` group mirroring `identity`:
   `leadhs hs apply [--map PATH] [--dry-run]` and
   `leadhs hs status`; `_ensure_migrated()` preflight reused;
   exit codes per i1 (map/validation refuse → 2).
5. **Doctor `src/leadhs/doctor.py`** — `_hs_checks` (user decision
   Q2: include): informational line — hs coverage %, pending count,
   last `hs_apply` run freshness.
6. **README.md** — one status-line sentence in the v0.3 block (HS
   coverage state after apply; provenance = hs status output). Docs
   sync beyond this is FINAL's.

Data flow (embed in hs.py docstring):

    hs_group_map.csv ──load/validate──▶ (source,group)→HS4 map
                                              │
    product.eu_group ──ECAT join──────────────┤
                                              ▼
    raw_as33_basta.product_uuid ─▶ votes ─▶ majority ─▶ UPDATE products.hs_code
        (bk04_code)        ▲                    │
                           └── conflicts ──▶ skip+count ──▶ hs status
    shadow paths: unknown group → pending · empty hs_code row →
    reviewed-null · mapping edit → re-apply (idempotent)

## FILES TOUCHED

- `src/leadhs/migrations/0014__hs.sql` (new)
- `src/leadhs/dict/hs_group_map.csv` (new, curated content)
- `src/leadhs/hs.py` (new)
- `src/leadhs/cli.py` (hs group + registration)
- `src/leadhs/doctor.py` (_hs_checks)
- `README.md` (one line)
- tests at build's discretion per project practice (r01 precedent):
  `tests/test_hs.py`, pinned-set updates in `tests/test_migrations.py`
  (expected set {1..14}), `tests/test_raw_layer.py` — build-authored,
  suite run belongs to the build session's gate as before

## USER TEST PLAN

1. `leadhs db status` — migration 0014 listed; `leadhs hs status`
   before apply: everything pending, 0 coverage.
2. `leadhs hs apply --dry-run` — prints per-source set/conflict/
   pending counts, writes nothing (run `hs status` unchanged; no new
   run row via `leadhs db status`).
3. `leadhs hs apply` — real pass; `leadhs hs status`: coverage ≈ all
   271,005 products (three-state split; pending only where the map
   has gaps — flags list expected); spot-check 3 products:
   an ECAT "Decorative paints…" product → hs `3208`/`3209`;
   a BASTA "Plastgolv" product → 39xx floor-covering code per map;
   a BASTA "Fönsterdörrar" product → its map HS4.
4. Re-run `leadhs hs apply` — all `unchanged`, 0 sets (idempotence).
5. `leadhs doctor` — new informational line present, green.
6. Edit one CSV row's hs_code (paint product to a wrong-but-valid
   code), re-apply, confirm the product's value changed and counters
   reflect it; revert, re-apply.
7. Skim `hs_group_map.csv` rows with `confidence=flag` — confirm or
   correct each (this is the Q1 review loop).

## FINAL TEST-PLAN INPUTS

- duplicate (source,group) row in CSV → refuse, exit 2, no writes.
- hs_code not 4 digits → refuse at load.
- conflict path: product whose rows carry two bk04 codes mapping to
  different HS4 → skipped + counted, hs stays NULL.
- reviewed-NULL semantics: mapping row with empty hs_code → product
  stays NULL, counted reviewed (not pending).
- ECAT product whose eu_group has no mapping row → pending.
- BK04 code formatting variants (leading zeros/spaces: `03104`) —
  exact-match contract, no normalization beyond strip.
- `identity rebuild` then `hs apply` — coverage restored; order
  dependency holds.
- re-apply after mapping edit — only changed rows rewrite; counters
  correct.
- crash mid-apply (SIGKILL) — transaction rolls back, no run row
  residue (stuck-running cleanup pattern exists from r01).
- empty map file → apply refuses (nothing to do is an error, not a
  0-op success).

## LINT SCOPE

No linter configured (PROJECT.md); the run gate is fast static checks
where available + user review of this plan's test steps.

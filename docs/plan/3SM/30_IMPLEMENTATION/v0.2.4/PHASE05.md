---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE05 — Addendum (D37): AS-class source probe (build, offline)

## Objective

Fold the operator instruction into unit v0.2.4: a probe across **all
30 AS-class sources** that tries to obtain a product-row CSV per
register, and — where none exists — records why and what is available
instead, plus the exact-or-estimated record count. Output folder
`data/report/AS-source-probe/` (obtained CSVs + per-source summary).
ENG review 2026-09-14 (SMALL CHANGE): sideways-import the csv_sample
machinery (1A), copy-or-unavailable reuse for AS-2/AS-3 (2A),
explicit handler sets + split guard test.

## Premise correction (recorded)

AS is **not** all product registries — the class is
"Associations & registers": 9 product/label databases
(AS-2..AS-10) and **21 trade associations** (AS-1, AS-11..AS-29,
AS-30) with member lists, not product registers. The probe has two
finding kinds accordingly.

## Governing references

- `../../20_DESIGN/units/v0.2.4.md` — addendum section (method sheet)
- `../../10_STRATEGY/v0.2.4.md` — addendum note (D37)
- `src/leadhs/probe/csv_sample.py` — reused machinery (sideways import)
- `src/leadhs/xlsx.py` — `sheet_rows()` for the AS-4 path

## Design (data flow)

```
per source (30)                                → finding
──────────────────────────────────────────────────────────────────
AS-2/AS-3 ─ artifacts exist? ─ yes ─▶ copy     → as_probe_rows (exact)
                │                              → note: original run key
                └─ no ─▶ honest unavailable    → as_probe_unavailable
                  ("run download-csv-sample first")
AS-4..AS-10 ─ export attempt (≤5 GETs) ─ csv/xlsx ─▶ parse + count
                │                                  → as_probe_rows
                ├─ page ok, count visible ─▶ estimate + method + date
                │                                  → as_probe_records
                └─ neither ─▶ reason + what's-instead
                                               → as_probe_unavailable
assoc (21) ─ 1 liveness GET ─ ok ─▶ association + member-list ptr
                │                              → as_probe_assoc
                └─ down ─▶ network note        → as_probe_assoc
exit: 2 only on should-deliver fetch failure; summary ALWAYS written
```

## Steps

1. **Migration `0010__as_source_probe.sql`:** probe_mode
   `as_source_probe`; metric seeds `as_probe_rows` (exact product rows
   obtained), `as_probe_records` (exact-or-estimated record count;
   note carries basis + access date), `as_probe_unavailable` (reason +
   what is available instead), `as_probe_assoc` (association finding);
   sync the migration-count test.
2. **Module `src/leadhs/probe/as_probe.py`:**
   `REGISTRY_HANDLERS` (AS-2..AS-10, explicit) + association default;
   reuse csv_sample privates (sideways import, same package);
   bounded fetch (≤5 GETs registry, 1 GET association); summary
   `as-source-probe.summary.{md,csv}` ALWAYS written (1A pattern);
   reuse-copy for AS-2/AS-3; estimates carry method + access date;
   `unknown` is a valid recorded outcome.
3. **CLI:** `leadhs probe as-source-probe` (`--out-dir` default
   `data/report/AS-source-probe`, `--source` multi, `--dry-run`);
   default scope = all AS rows from the register.
4. **Makefile:** `as-probe: guard-as-probe` (GO=1), `## help` entry,
   `.PHONY`.
5. **Tests `tests/test_as_probe.py` (offline, fixture site):**
   - XLSX delivery (AS-4 fixture) → exact count + CSV rendering
   - discovery-fail → unavailable + what's-instead line
   - reuse-copy success; missing-copy → honest unavailable
   - association liveness ok / site down
   - estimate visible / not visible (unknown)
   - summary written even when every source fails; exit codes
   - split guard: handler sets vs DB register (9 + 21 = 30)
   - migration 0010 seeds; dry-run plans, writes nothing
   - Makefile guard blocks without GO
6. **Full suite:** `make test` green, count recorded.

## Exit criteria

- All steps done; suite green; `--dry-run` plans ~zero-network;
  version stays 0.2.4 (fold-in).

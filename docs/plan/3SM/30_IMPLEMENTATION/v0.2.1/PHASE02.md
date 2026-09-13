---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE02 — Code delta: ASAdapter, register-capability branch, 0.2.1

## Objective

Land the unit's entire code delta, offline-verified: the
register-capability adapter branch (CSV/API fetch → header/shape
inspect → row count → capability findings), the `capability` mode
surface, the operator targets, and the version bump.

## Preconditions

- PHASE01 done (0007 applied; capability metrics in the vocabulary).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.1.md` (cap2, cap4, cap5 → ASAdapter;
  register-capability machinery; ENG review C1)
- `../../20_DESIGN/MASTER/architecture.md` (a19/a23; AS adapter
  mapping)
- `../../20_DESIGN/MASTER/interfaces.md` (i17; i7 dry-run invariant;
  run semantics)
- `../../20_DESIGN/MASTER/testing.md` (t11 adapter paths)

## Steps

1. **`probe/adapters.py` — `ASAdapter`:** `matches` returns
   `source.class_code == "AS"`; `probe` dispatches on
   `ctx.mode` — for `mode != "capability"` return an empty
   `ProbeResult()` (no-op so census/recon sweeps are unchanged,
   C1); for `mode == "capability"` and `access_method_code IN
   (download, api)` run the register-capability branch:
   fetch the export (`fetcher.get`, dry-run plans zero fetches —
   i7), inspect the header/shape (manufacturer column? product-ident
   column? a nomenclature/CN8 column?), count rows, emit the six
   capability findings + `products_identifiable`; archive the raw
   export as a document. Reuse a single `_inspect_register(rows,
   header)` helper (C1) returning the capability findings.
   - Shadow paths: empty export → UnexpectedFormat → format finding,
     run done; malformed/CSV parse error → ParseError → format
     finding; auth-gated (403) → Blocked → access_blocked, run
     blocked; network error → ProbeNetworkError → run failed.
2. **CLI + engine:** `probe run --mode` choice list gains `capability`
   (no new command — V9); mode dispatch passes through to adapters
   (existing `ctx.mode`). `probe record --mode capability` labels
   manual capability records (mode parameter exists, e8).
3. **Makefile:** `probe-capability` target (one leadhs call:
   `probe run --mode capability --all`; `guard-probe-capability`
   GO=1 prerequisite) + `capability` target (setup → probe-capability
   → report → db-audit), mirroring census/recon; **the probe step
   inside the `capability` chain tolerates exactly exit 2
   (`|| test $$? -eq 2`)** — expected blocked sources no longer abort
   the chain (v0.2.0 e1 idiom); `probe-single` gains `MODE=` var
   pass-through.
4. **Version bump 0.2.1** (pyproject.toml, `__init__.py`, Makefile
   header, version assertions); wheel build check.
5. **Tests (t11, test_adapters_as.py + fixtures):** happy path
   (CSV + API fixture) — header/shape inspect, row count →
   `products_identifiable`, capability findings emitted, document
   archived; manufacturer column but no product-ident →
   cap_manufacturer=1/cap_product_ident=0; no nomenclature column →
   cap_cn8_linkage='manual', cn8_reachable=0; malformed/empty export
   → UnexpectedFormat → format finding, run done; auth-gated 403 →
   access_blocked, run blocked; zero-call dry-run (i7); non-
   `capability` mode → empty result (census/recon unchanged). Plus:
   test_makefile.py (probe-capability guarded; capability chain; exit-
   2 tolerance; MODE pass-through); test_migrations.py sync already
   extended in PHASE01.

## Deliverables

ASAdapter + register-capability branch; `capability` mode surface;
probe-capability/capability targets; 0.2.1 wheel; green suite.

## Exit gate

Full offline suite green incl. t11 adapter/makefile cases; `db audit`
exit 0 on the real DB; `leadhs --version` → 0.2.1; wheel installs in a
managed interpreter (`uv tool install`, `--data-dir` from a foreign
CWD). (Golden regeneration belongs to PHASE06, when report output
changes.)

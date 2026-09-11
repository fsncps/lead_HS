---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE03 — Operator layer (Makefile, housekeeping, report routing)

Status: planned · Depends on: PHASE01 (targets invoke the fixed
CLI) · Governs: the stable operator entrypoint.

## Objective

One canonical way to drive the tool from the repo root: `make help`
as the index, one target per `leadhs` call, `GO=1` on the costly and
destructive paths, reports routed (intermediates gitignored,
publishing deliberate). Pipeline logic stays in the CLI — make is a
thin wrapper.

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §Makefile (**the complete
  recipe text — copy verbatim**), §Report routing (od1, od5, od6).
- `../../20_DESIGN/MASTER/architecture.md` — §Operator layer
  (a12/a13).
- `../../10_STRATEGY/v0.1.2.md` — §Makefile target map (contract),
  U1–U6.

## Steps

1. **Create the repo-root `Makefile`** with the exact recipe text
   from `../../20_DESIGN/units/v0.1.2.md` §Makefile (it is
   parse-verified against GNU make). Load-bearing semantics:
   - `guard-%` is a **prerequisite**, so the GO gate fires before
     any recipe side effect; `census: guard-census setup probe
     report db-audit` lists the guard **first** — `setup` (pip
     install) never runs without `GO=1`;
   - `clobber: guard-clobber` + interactive typed `yes` confirm;
   - `.DEFAULT_GOAL := help`; `help` via the grep/sed/sort
     self-documenting pattern; `.PHONY` covers every target;
   - parameters as make variables (`PYTHON`, `DB`, `MODE`,
     `SAMPLE`, `SOURCE`, `REPORT_DIR`, `PUBLISH_DIR`;
     `export LEADHS_CONTACT LEADHS_DEBUG`); `LEADHS = leadhs --db
     $(DB)`;
   - `record` builds optional flags with `$(if …)`; values that can
     contain spaces are shell-quoted in the recipe;
   - M1–M4 stub targets (`frame sample acquire ingest parse analyze
     full`) echo the milestone pointer and exit 1;
   - recipe lines use **literal tabs**.
2. **`.gitignore`**: add `.benchmarks/` (the other design entries —
   `build/`, `.pytest_cache/`, `__pycache__/`, `data/`, `dist/` —
   are already present; verify, don't duplicate).
3. **Report routing** (a13): `make report` renders into
   `data/report/{probe-report.md,csv,json}` (gitignored, regenerated
   freely); `make report-publish WHICH=…` **copies** — never moves —
   one report into `docs/report/` (committed finals) and prints the
   commit reminder. Both directories are created on demand by the
   targets; nothing is committed by the build.

## Deliverables

Repo-root `Makefile`; `.gitignore` delta. No Python changes.

## Exit gate

- `make help` → exit 0, sorted target list; `make` (no args) shows
  it.
- `make probe` and `make census` **without** `GO` → fail with the
  guard message, **no side effects** (census: no pip run).
- `make sample` (stub) → exit 1 with the milestone pointer.
- `GO=1 make -n probe` → prints the `leadhs … probe run --all` line;
  `make -n report` → prints the three `--out` lines.
- `make report-publish` (no `WHICH`) → fails with the usage line;
  with `WHICH=` → copies into `docs/report/`, prints the reminder,
  leaves the original in place.
- `make clean` removes caches/build artifacts; `make db-audit`,
  `make db-status`, `make sources-list`, `make probe-dry`, `make
  doctor` each run their single `leadhs` call against `DB`
  (default `data/leadhs.sqlite`).
- `pytest` still green (make has no Python surface yet — PHASE04
  wires the tests).

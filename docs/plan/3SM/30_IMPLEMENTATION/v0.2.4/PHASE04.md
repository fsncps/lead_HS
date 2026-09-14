---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE04 — Makefile target, full suite, docs close-out (offline)

## Objective

Wire the `sample-csv` operator target (GO=1 guard), run the full
offline suite + audit, and bring the docs current — the unit is then
built; the first real-network run (`GO=1 make sample-csv`) is an
operator act, not a phase gate.

## Preconditions

- PHASE01–03 done.

## Governing references

- `../../20_DESIGN/units/v0.2.4.md` (Makefile section; the `sample`
  M1 stub stays untouched)
- `../v0.2.4/MASTER.md` (scope)
- Makefile (guard-% pattern, help index, `.PHONY`)

## Steps

1. **Makefile:** `.PHONY` + `sample-csv: guard-sample-csv` target
   (`$(LEADHS) probe download-csv-sample`) with the `## help` comment;
   `N`/`SEED` pass-through variables optional, defaults in the CLI.
2. **Makefile test:** `tests/test_makefile.py` v0.2.4 block —
   guard blocks without GO; `-n sample-csv` shows the command line.
3. **Full suite + audit:** `make test` green (count recorded);
   `leadhs db audit` exit 0 on the test DB; `leadhs --help` /
   `probe --help` show the new command.
4. **Docs close-out:** the design doc's test list matches what
   landed; `30_IMPLEMENTATION/v0.2.4/MASTER.md` statuses → done;
   strategy/design `updated` stamps current; README + management
   summary get their built-unit summary lines only after the first
   real run delivers management-facing artifacts (per convention:
   summaries carry real numbers, not plans).

## Deliverables

Makefile target + test; suite/audit results; updated planning docs.

## Exit gate

Full offline suite green including the makefile wiring tests; audit
clean; planning docs current.

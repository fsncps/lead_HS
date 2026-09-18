---
unit: global
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-18
---

# Topic — Architecture (strategy summary)

## Abstract

Light data-engineering for a single user on one machine: a stdlib-first
Python CLI (`leadhs`; requests/bs4/click/jinja2/pypdf only) over one
SQLite file and a hash-addressed raw-document store; a repo-root
`Makefile` is the operator entrypoint (one target = one `leadhs`
call); pipeline stages probe → acquire → ingest → frame → sample →
parse → corroborate → analyze → report, implemented progressively from
the shipped probe core; a slim generated report layer (od8 content,
md/csv/json) renders from the database only, with published finals in
`docs/report/` and run intermediates in `data/report/`. Operations
touching real sites are gated behind `GO=1`; the tool stores product
data only (no legal referencing in tool, database or reports).

## DECISIONS

- D16 — tooling: single-user, no-server pipeline, stdlib-first stack,
  SQLite + raw store.
- D21 — operator layer: repo-root Makefile; pipeline logic gravitates
  into the CLI; GO=1 gates for costly network operations and `clobber`.
- D22 — report routing: intermediates in `data/report/` (gitignored),
  publishing into `docs/report/` is an explicit act; management summary
  never overwritten by generated artifacts.
- D18 — every reported number traces to a database run (run ID + seed).
- D24/D32 — distribution: wheel via managed interpreter (`uv tool
  install`); GitHub release assets, no PyPI; vanilla-Windows install is
  a v0.3 goal (per-OS bundled artifact mechanism open, D32).
- D23 — English canonical; DE/FR siblings; planning docs EN-only.

## OPEN ITEMS

- Vanilla-Windows installer mechanism — decide in v0.3 design (bundling
  promoted from contingency to planned).
- Config file migration (one migration, not two) lands at milestone M1
  per D21.

## Detail documentation

The public architecture document (pipeline stages, CLI surface,
repository layout, distribution/portability, report concept, testing
and failure behavior) lives outside the plan tree:

- `docs/study/ARCHITECTURE.md` (EN).

The engineering authority is `20_DESIGN/MASTER/architecture.md`
(+ `20_DESIGN/units/<unit>.md` deltas); Design wins on conflict.

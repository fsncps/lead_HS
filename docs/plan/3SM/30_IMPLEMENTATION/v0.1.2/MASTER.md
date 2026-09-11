---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# Unit v0.1.2 — Implementation plan: operator layer (make, CLI operability, report routing)

## Abstract

The executable phase plan for unit v0.1.2. It formalizes the design
phases P1–P7 (`../../20_DESIGN/units/v0.1.2.md` §Implementation
phases) into seven self-contained `PHASE##.md` files — same format as
unit v0.1.1: objective, governing references, steps, deliverables,
exit gate. The design docs carry the full detail (including the
complete Makefile recipe text); phase files restate only what a
builder needs at hand and cite the governing section for the rest.
The plan was ENG-reviewed on 2026-09-11 (SMALL CHANGE mode; findings
and decisions below). With strategy **D26** the unit is the **M0
close-out**: the operator layer (PHASE01–04) is completed by the
census capability (PHASE05), docs/distribution (PHASE06) and the
census close-out execution (PHASE07) — the census runs through
`GO=1 make census` and closes the gaps of the 2026-09-11
feasibility pass.

## Scope

The operator layer **plus the census close-out (D26)**: CLI
exit-code enforcement in `main()` + DB-init preflight (`cli.py`);
`source list` / doctor / `--data-dir` fixes; repo-root `Makefile`
(thin wrapper, `GO=1` guard, report routing); `.gitignore`
housekeeping; migration 0003 per-HS count metrics (od9); structured
census report content (od8/D25); README + translations; wheel build
verification; and the census execution itself (PHASE07). M1–M4
surfaces stay stub targets.

## Phase tracking

| # | Focus | Depends on | Exit gate | Status |
|---|---|---|---|---|
| 01 | CLI operability (main() exit mapping, no_args_is_help, list fix, doctor --net, --data-dir, version 0.1.2) | — | `--help` 0; `leadhs dource` 1; bare groups help/0 on stdout; `--db`+`--data-dir` 1; `--no-net` gone; Ctrl-C 130; existing suite green | planned |
| 02 | DB-init preflight (`_ensure_initialized` + wiring into 7 commands) | 01 | guided error exit 1 on missing/empty/no-schema_version for all 7; `db init` exempt; passes after init | planned |
| 03 | operator layer (repo Makefile, .gitignore `.benchmarks/`, report routing) | 01 | `make help` 0; probe/census fail at guard before side effects; stubs exit 1; `-n report` 3 `--out` lines; `report-publish` copies | planned |
| 04 | tests (operability, preflight, make-wiring; net-marked doctor --net; smoke updates) | 01–03 | full offline suite green (net/mdbtools deselected); `pytest -m net` collects ≥ 1 | planned |
| 05 | census capability (migration 0003 per-HS metrics; structured report content per D25; tests + golden refresh) | 04 | suite green incl. sync test (0001+0003 == metrics.py); structured sections + matrix on fixture corpus; R4 holds for new metrics | planned |
| 06 | docs & distribution (README EN/DE/FR, Status, layout; wheel-build verification) | 01–05 | wheel installs into throwaway uv tool env; `--data-dir <tmp> db init` works; READMEs current | planned |
| 07 | census close-out (execution through the operator layer) | 01–06 + explicit go | every register row probed or manual; feasibility gaps closed/documented; structured report published; `db audit` exit 0 | planned |

Statuses: `planned → in-progress → done` (update this table and the
PHASE file header when a phase starts/finishes). Build executes
phases only on explicit user instruction, in order.

## Implementation decisions (ENG review of this plan, 2026-09-11)

Empirically verified against click 8.3.1 before finalization
(`standalone_mode=False` behavior):

- **B1 — exit-map contract:** `main()` hardcodes UsageError → **1**
  (click's `UsageError.exit_code` is 2 — never use `exc.exit_code`
  there). `NoArgsIsHelpError` (a UsageError subclass raised by bare
  groups) is caught **before** UsageError: help re-printed to
  **stdout** (consistent with `--help`/`--version`), exit 0.
  Interrupts surface as `click.exceptions.Abort` (click converts;
  raw `KeyboardInterrupt` caught as belt-and-braces) → 130.
  `--help`/`--version`/`ctx.exit(n)` return ints from click's
  `main()` under `standalone_mode=False` → `isinstance(result, int)`
  mapping; `main()` returns int; the `__main__` guard becomes
  `sys.exit(main())` (smoke tests run `python -m leadhs.cli`).
  Import exceptions from `click.exceptions` (`click.Exit` is not
  exported at top level in 8.3.1).
- **B2 — preflight before connect:** `_ensure_initialized(ctx, rt)`
  runs **before** `dbmod.connect()` in each of the seven commands
  (connect would create an empty file). Check: file exists and is
  non-empty, then `schema_version` present via a `mode=ro` URI
  connection (never creates the file).
- **B3 — `--data-dir` plumbing:** `--db` becomes `default=None`;
  the `cli` callback computes the final path (`--data-dir DIR` →
  `DIR/leadhs.sqlite`; neither → `data/leadhs.sqlite`); both given →
  `click.UsageError` (exit 1). `Runtime.store_root` unchanged
  (dirname(db_path)/raw). Explicit `_ensure_initialized` call at the
  top of each command — no decorator (explicit > clever; no click
  signature-introspection risk).
- **B4 — version bump in P1:** `pyproject.toml` +
  `src/leadhs/__init__.py` → `0.1.2` so the P5 wheel artifact,
  `leadhs --version` and the fetch UA are honest.
- **B5 — test-net gets a job:** zero `@pytest.mark.net` tests exist
  today, so `pytest -m net` collects nothing and exits 5 —
  `make test-net` would fail. P4 adds one net-marked `doctor --net`
  test (single RFC 2606 URL, example.com) — deterministic
  single-request, deselected from the default suite.
- **B6 — README EN/DE/FR in one change set:** PHASE06 updates
  README.md and both translations together (AGENTS.md tranche-1
  convention; no `source_updated` drift marker). The README section
  documents the **workflow**; the real census numbers live in the
  delivered report (PHASE07) — this resolves the strategy open item
  that tied the section to census numbers.
- **B7 — OD-A resolved: per-HS metrics via migration 0003, not
  deferred to M1.** D25 mandates per-HS records (3208/3209/3213) in
  this unit's census report, so the metric vocabulary must exist
  before execution (i4 extension rule: migration INSERT; codes never
  renamed). New PHASE05 delivers the migration + the od8 report
  content.
- **B8 — PHASE08 of v0.1.1 is absorbed here (D26).** The v0.1.1
  PHASE08 feasibility pass (2026-09-11) is the empirical record; its
  close-out is PHASE07 of this unit. The v0.1.1 trail is updated to
  mark the transfer (no code or history rewritten).

## Acceptance criteria (from `../../20_DESIGN/units/v0.1.2.md`)

- `leadhs dource` → exit 1; `source list` registered exactly once;
  bare groups → help, exit 0 (stdout); Ctrl-C → 130.
- Uninitialized DB → guided error on all seven schema-reading
  commands, never `bug: no such table`.
- `make help` exit 0; `make probe`/`make census` without GO fail
  with the guard message before any side effect; M1–M4 stubs exit 1
  with a pointer; `make report` writes the three formats;
  `report-publish` copies and reminds.
- `make setup` idempotent on a fresh clone.
- Full offline suite green including the three new files (net/
  mdbtools deselected).
- `--data-dir` honored; `--db`+`--data-dir` → exit 1.
- Wheel builds and installs into a throwaway uv tool env;
  `leadhs --data-dir <tmp> db init` works.
- README updated; translations updated in the same change set (B6).
- Migration 0003 applies idempotently (fresh + upgrade); vocabulary
  sync test green; structured census report renders per D25 on the
  fixture corpus.
- **Census delivered (PHASE07):** every register row probed or
  explicitly manual; feasibility gaps closed or documented-blocked;
  structured report published to `docs/report/`; `db audit` exit 0
  on the real corpus.

## Open items carried into build

- Wheel release mechanics (tag → GitHub release asset → per-OS
  smoke) — first external use; PHASE06 verifies the wheel builds
  only.
- `make -n` cannot assert the GO gate's exit code — covered by
  running the guarded targets (they fail before side effects);
  accepted in design.
- DE/FR README sync — resolved as B6 (same change set).
- OD-A (per-HS metrics) — resolved as B7 (migration 0003).
- PHASE07 census execution — requires the explicit real-network
  go-ahead (preconditions in the phase file).

## Handoff note

Writing these files implies no freeze, stage advancement, or
execution start. Build executes phases only on explicit instruction,
in order. LOG entry, root-MASTER stage pointer, and commit/push all
await explicit user instruction (3SM process).

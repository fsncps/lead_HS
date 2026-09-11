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
and decisions below) and **rescoped at implementation activation the
same day** to the second-pass design delta (od8–od10: report content
layer, census completion mechanics, migration 0003 with the
records_hs*/census_status vocabulary; the pre-od8 "hs3208_count"
naming and the report sketch are superseded — PHASE05 rewritten,
PHASE07 metric names aligned). With strategy **D26** the unit is the
**M0 close-out**: the operator layer (PHASE01–04) is completed by the
census capability (PHASE05), docs/distribution (PHASE06) and the
census close-out execution (PHASE07) — the census runs through
`GO=1 make census` and closes the gaps of the 2026-09-11
feasibility pass.

## Build record (2026-09-11)

PHASE01–06 executed in order; **155 passed** on the full offline suite
(net/mdbtools deselected; 2 deselected by markers), up from 101 before
the unit. Recorded build decisions beyond the phase text:

- **od9/R4 seam:** od9's "category path in value_text" collided with
  the binding R4 audit rule (numeric metrics carry no value_text) —
  the category path lives in the finding **notes**; interfaces.md
  vocabulary row clarified (docs-only, R4 unchanged). Details in
  PHASE05.
- **make stub exit code:** the M1–M4 stub recipe exits 1, but GNU make
  surfaces any recipe failure as exit 2 — tests assert nonzero + the
  milestone pointer (the load-bearing behavior); design recipe text
  unchanged.
- **Wheel verification:** `python -m build` → wheel 0.1.2; installs
  into a throwaway `uv tool` env; `leadhs --data-dir <tmp> db init`
  applies 0001–0003 from a foreign CWD; doctor runs. No release
  artifacts committed (dist/ gitignored).
- PHASE07 (census execution, real network) remains **planned** —
  awaits the explicit go-ahead.

## Scope

The operator layer **plus the census close-out (D26)**: CLI
exit-code enforcement in `main()` + DB-init preflight (`cli.py`);
`source list` / doctor / `--data-dir` fixes; repo-root `Makefile`
(thin wrapper, `GO=1` guard, report routing); `.gitignore`
housekeeping; migration 0003 probe-metric extension —
records_hs3208/3209/3213 + census_status, v_anchor_candidates
redefined (od10); census completion mechanics (od9: parameterized
CS-2 query, ST-2 register URL fix, PE category depth ≤ 3, manual
census_status records); structured report content layer (od8/D25);
README + translations; wheel build verification; and the census
execution itself (PHASE07). M1–M4 surfaces stay stub targets. Schema
carries product data only (Strategy MASTER D27).

## Phase tracking

| # | Focus | Depends on | Exit gate | Status |
|---|---|---|---|---|
| 01 | CLI operability (main() exit mapping, no_args_is_help, list fix, doctor --net, --data-dir, version 0.1.2) | — | `--help` 0; `leadhs dource` 1; bare groups help/0 on stdout; `--db`+`--data-dir` 1; `--no-net` gone; Ctrl-C 130; existing suite green | done 2026-09-11 |
| 02 | DB-init preflight (`_ensure_initialized` + wiring into 7 commands) | 01 | guided error exit 1 on missing/empty/no-schema_version for all 7; `db init` exempt; passes after init | done 2026-09-11 |
| 03 | operator layer (repo Makefile, .gitignore `.benchmarks/`, report routing) | 01 | `make help` 0; probe/census fail at guard before side effects; stubs exit 1; `-n report` 3 `--out` lines; `report-publish` copies | done 2026-09-11 |
| 04 | tests (operability, preflight, make-wiring; net-marked doctor --net; smoke updates) | 01–03 | full offline suite green (net/mdbtools deselected); `pytest -m net` collects ≥ 1 | done 2026-09-11 |
| 05 | census capability (migration 0003 records_hs*/census_status + v_anchor_candidates redefinition; od9 mechanics: CS-2 parameterized query, ST-2 URL fix, PE category depth; od8 report content layer; tests + golden refresh) | 04 | suite green incl. sync test (0001+0003 == metrics.py); matrix + sections + legend on fixture corpus (csv = matrix only); blocked/failed visible; R4 holds for new metrics | done 2026-09-11 |
| 06 | docs & distribution (README EN/DE/FR, Status, layout; wheel-build verification) | 01–05 | wheel installs into throwaway uv tool env; `--data-dir <tmp> db init` works; READMEs current | done 2026-09-11 |
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
  renamed). PHASE05 delivers the migration + the od8 report content.
  Second-pass naming (od10): `records_hs3208/3209/3213` +
  `census_status` (not the earlier `hs*_count` sketch);
  v_anchor_candidates redefined; design-ahead migrations renumbered
  0004–0010 (docs-only).
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
  sync test green; report renders per od8 on the fixture corpus —
  framing, summary matrix over all registered sources (incl.
  inactive), per-source sections, run status incl. blocked/failed +
  notes, "—" vs 0 legend; csv is the matrix; json the full
  structure.
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

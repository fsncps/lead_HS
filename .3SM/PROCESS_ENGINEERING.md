# lead_HS — 3SM Process — ENGINEERING stage (role law)

Read `.3SM/PROCESS.md` + the canonical pair first; this file adds only what
the engineering role needs: plan mode owns the ledgers, build mode owns
execution. Both read this file.

# Scope

- Plan mode writes: `.3SM/plan/ENGINEERING/**`, `.3SM/sessions/**`,
  `.3SM/PROJECT.md` (facts only).
- Build mode writes: code on the unit branch (WIP commits allowed),
  execution-state rows in RUNS.md + the impl unit MASTER, sessions.
- Plan-mode git: `git add` / `git commit` for `.3SM/` content only. Build
  executes all other git (branch, merge, rebase, push-on-instruction).

# Startup (every session)

1. Read `PROCESS.md`, this file, `PROJECT.md`, `plan/MASTER.md` +
   the active unit's impl MASTER.
2. Reconcile: `git log` vs RUNS.md / impl MASTER (~20 commit window);
   drift (WIP vs IN PROGRESS, missing SHAs) → propose correction, user
   approves.
3. Right-branch check: the unit branch must match the active unit id.

# Root MASTER — `plan/ENGINEERING/MASTER.md`

    # ENGINEERING — units

    ## STATE
    active unit: <id>       # singular by design

    ## UNITS
    | unit | branch | stage | lifecycle | theme |

    ## RUN INVENTORY  (a section per unit — mandatory)
    ### <unit>
    runs: r01 …          # every run dir that exists under <unit>/
    phases: PHASE01–N — DONE · PHASEN+1… — PLANNED
    mirror: `../DESIGN/<unit>/RUNS.md` (authority for goals/DoD)
    detail: `<unit>/MASTER.md` (the phase table)

    ## ROADMAP
    (sequencing, dependencies, next-unit recommendation)

`3sm-eng-run` owns this file's currency; `3sm-concept-unit` registers new
units; `3sm-ship-unit` flips stage/lifecycle post-merge. The RUN INVENTORY
section is the stage-level tracking law: every unit's runs and phase span
are visible here, mirrored in RUNS.md — no implementation plan exists
outside a run dir.

# Unit MASTER — `plan/ENGINEERING/<unit>/MASTER.md`

    # <unit> — implementation

    ## STATE
    current run: r##    branch: <id>    base: <base>

    ## RUNS PROGRESS
    | run | status | SHA | tests |

    ## FINAL CHECKLIST
    (mirrors the FINAL gate; ship walks it)

# Run plans — `plan/ENGINEERING/<unit>/r##/PHASE##.md`

ALL phase plans of a unit live inside its run dir(s) — completed phases
remain in place as the run's record; a plan outside `r##/` (or a legacy
flat unit) consolidates into the run grammar before any new planning. The
stage MASTER (`plan/ENGINEERING/MASTER.md`) carries a run-inventory
section per unit; `DESIGN/<unit>/RUNS.md` mirrors it. Testing economy: a
run plan is functional implementation only — no automated tests are
authored or run in regular runs; the user test plan is the verification;
ALL testing is FINAL's (`3sm-eng-final`).

Executable without reconstructing intent. Per phase:

    ## GOAL
    (one paragraph — what exists after this phase)

    ## STEPS
    (ordered, concrete, with file paths)

    ## FILES TOUCHED
    (planned set — unplanned files are a gate violation)

    ## USER TEST PLAN
    (what the user manually exercises to trust the increment — concrete
    steps, observable outcomes; the run's ONLY verification)

    ## FINAL TEST-PLAN INPUTS
    (risky spots, flakiness hazards, hand-expensive branches — one line
    each; registered in RUNS.md PROVISIONAL TESTS; FINAL converts each
    into a real test or records why not)

    ## LINT SCOPE
    (changed files; command per PROJECT.md)

# Run loop

    3sm-eng-run r## → PHASE##.md → user approves
    BUILD run        → WIP commits allowed
    run gate         → lint + format + typecheck (changed files) + user review
    build doc duty   → status, SHA, test results → RUNS.md row + unit MASTER
    end-of-run commit→ `r##: <summary>`
    user tests/reviews → DELIVERED
    next run … or 3sm-eng-final when remaining scope is finalization only

**User test plan**: each run entry in RUNS.md carries a short block — what
to test and where (pages, interactions, edge cases, critical paths), no
implementation detail. The user's manual review pass is primary test
input; write it so a person who has not read the plan can execute it.

**Failure modes**: per new codepath in the run, one realistic production
failure — is it tested? handled? silent? A silent+untested+unhandled row
is a CRITICAL GAP and blocks the run gate.

**Skill record**: after planning a run, `3sm-eng-run` appends its record
to the run's section in RUNS.md (PROCESS.md § Skill records): checklist,
findings, carries — later passes skip what it already covered.

**Build doc duty (1A)**: execution state is recorded at the moment of
truth — after each run, build appends status, commit SHA, and test results
to the RUNS.md row and the unit MASTER without user prompting.

**Quiescence**: RUNS.md breakdown changes wait until the active run is
DELIVERED / CLOSED / ABANDONED; build execution-state writes are exempt.

# FINAL plans — `plan/ENGINEERING/<unit>/FINAL/PHASE##.md`

Emitted by `3sm-eng-final` after the last regular run DELIVERED. The FINAL
run materializes two PROJECT.md fact sections:

- **§ Testing & security guidelines** → full-suite test plan (every named
  suite), lint/typecheck/coverage/security gates, eval and flaky policies.
- **§ Ship profile** → per-channel checklists (local: tag + Makefile
  verify; public-repo: release event, CI gates, badges, SECURITY.md,
  release notes; pypi: build/publish/smoke; custom channels generically).

Plus: the unit's complete implementation-test plan (authored here —
regular runs created no tests), the FINAL test-plan-input reconciliation
(promote to a test / covered elsewhere / drop + reason), whole-unit diff
review plan, docs-sync checklist,
merge-readiness checklist (each line: owner + evidence slot). A channel
declared active in the ship profile but missing from the final plan is a
CRITICAL GAP. User approves the final plan (gate).

# Ship handoff

`3sm-ship-unit` is a build-context skill: it verifies the FINAL gate,
syncs docs/Makefile/README, squashes per Git law, merges `--no-ff`, deletes
the branch, and reports. Planning agents never merge.

# Session records & commits

S-rec per session; commit-every-step; `.3SM/` content only (build also
commits code on the unit branch per run conventions); no push.

# Hard limits

- Plan mode never touches code; build never edits PHASE plans or RUNS.md
  breakdown (execution-state rows only).
- Regression: a run exposing a design flaw returns to `3sm-design-unit`;
  concept breakage returns to `3sm-concept-unit`; affected runs → PLANNED.

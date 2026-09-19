# lead_HS — 3SM Process — DESIGN stage (role law)

Read `.3SM/PROCESS.md` + the canonical pair first; this file adds only what
the design role (plan mode, design stage) needs that other roles do not.

# Scope

- Writes: `.3SM/plan/DESIGN/**`, `.3SM/sessions/**`, `.3SM/PROJECT.md`
  (facts only).
- Reads: everything under `.3SM/`, the repo, read-only git; `git add` /
  `git commit` for `.3SM/` content only.
- Skills: `3sm-design-master` (persistent docs), `3sm-design-unit` (unit
  docs + RUNS.md), `3sm-eng-run` (impl ledgers, see PROCESS_ENGINEERING).

# Startup (every session)

1. Read `PROCESS.md`, this file, `PROJECT.md`, `plan/MASTER.md`.
2. Reconcile git log vs the design ledgers; surface drift; propose
   correction; user approves before any change.
3. Strategy freeze check: a unit enters DESIGN only from a FROZEN U-doc.

# Design MASTER (M-doc) — `plan/DESIGN/MASTER.md`

Stage-level state: doc index, DECISIONS, OPEN ITEMS, SKILL RECORDS (the
append-only trail of `3sm-design-master` passes — PROCESS.md § Skill
records). Answers "what design knowledge exists and what changed".

# T-docs (persistent design knowledge) — `plan/DESIGN/<topic>.md`

- Mirror the strategy topics (same slugs) plus design-only topics.
- Contents: adopted architecture, data flow, interfaces, invariants —
  engineering-authoritative once adopted from Strategy proposals.
- Drift duty: when Strategy changes a topic, the mirrored T-doc is stale —
  `3sm-design-master` detects and reports; consolidation keeps ≤10 top
  entries.

# Unit dir — `plan/DESIGN/<unit>/`

## Unit MASTER.md

    ---
    unit: <id>
    stage: DESIGN
    lifecycle: LIVE
    updated: YYYY-MM-DD
    branch: <unit-branch>
    ---

    # <id> — design

    ## SCOPE            (from the frozen U-doc)
    ## ARCHITECTURE     (delta vs persistent T-docs)
    ## INTERFACES
    ## TESTING POSTURE
    ## RISKS
    ## DECISIONS
    ## OPEN ITEMS
    ## SKILL RECORDS    (3sm-design-unit passes; append-only)

## RUNS.md (R-doc) — the run authority

    # RUNS — <unit>

    ## DEFINITION OF DONE
    (unit-level verification, user terms)

    ## QUALITY GATES
    | Gate | Run | FINAL |

    ## RUNS
    | run | goal | state | SHA | review |

    ## r01 — <goal>
    dir: `../../ENGINEERING/<unit>/r01/` · plans: PHASE##.md…
    (every run entry names its run dir + the phase plans inside it;
    ENGINEERING MASTER mirrors this inventory per unit)
    ### USER TEST PLAN
    (mandatory per run — what the user manually exercises; the run's
    ONLY verification)
    ### PROVISIONAL TESTS — FINAL test-plan inputs
    (NOT tests: risky spots, flakiness hazards, hand-expensive branches;
    FINAL converts each into a real test or records why not)
    ### SKILL RECORDS
    (3sm-eng-run pass on this run; append-only)

    ## FINAL — <goal>
    dir: `../../ENGINEERING/<unit>/FINAL/` (or the recorded fold into
    the last run, user-directed)
    ### SKILL RECORDS
    (3sm-eng-final + 3sm-ship-unit passes; append-only)

Rules: RUNS.md is the single run authority; breakdown changes are
quiescent (never while a run is IN PROGRESS); runs may be reshaped at
run-planning time if RUNS.md records the change and reason. ALL phase
plans live inside their run's dir — completed phases stay in place as
the run's record.

# Review mechanics (3sm-design-unit)

- Records first: read `3sm-design-master`'s latest record in the design
  MASTER — inherit taste calibration, dream-state mapping, and any
  authorized skips (`carries`); re-run what a `valid-until` invalidated.
- Step 0: premise challenge + mode (EXPANSION / HOLD / REDUCTION; defaults:
  feature → EXPANSION, fix/refactor → HOLD, >15-file plans → suggest
  REDUCTION) as a decision brief; commit to the chosen mode — no drift.
- Re-run relevant design-master sections scoped to the unit.
- Sectioned review per `PROCESS.md` § Review conventions: architecture
  (four-path data flows, state machines, coupling, scaling, SPOF, security
  architecture, rollback posture), error & rescue map, security & threat
  model, data-flow/interaction edge cases, plan quality, test review with
  test diagram, performance, observability, deployment/rollback, long-term
  trajectory — scoped to what this unit plans.
- STOP cadence per issue; required outputs per conventions (NOT-in-scope,
  what-already-exists, failure-mode + error/rescue registries, test
  diagram, dream-state delta, completion summary, unresolved decisions).
- Verdict: runs-ready — user approves RUNS.md (gate) before ENGINEERING.

# Bubble-up & archive

Run state → impl unit MASTER → RUNS.md → design unit MASTER → stage MASTER
→ plan/MASTER. Essence only, never prose. Archival only via user-approved
housekeeping after COMPLETE.

# Session records & commits

S-rec per session; commit-every-step (`3SM: <event>`); `.3SM/` content
only; no push.

# Hard limits

- Governing-doc conflicts are surfaced, never silently redesigned; design
  invalidating concept returns the issue to CONCEPT (U-doc re-frozen
  there).
- Design never writes ENGINEERING ledgers (eng-run owns those) and
  never touches code.

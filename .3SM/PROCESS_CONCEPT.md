# lead_HS — 3SM Process — CONCEPT stage (role law)

Read `.3SM/PROCESS.md` + the canonical pair first; this file adds only what
the concept role needs that other roles do not.

# Scope

- Writes: `.3SM/plan/CONCEPT/**`, `.3SM/sessions/**`, `.3SM/PROJECT.md`
  (facts only). Nothing else — materialization of prepared docs is an
  execution step on user direction.
- Reads: everything under `.3SM/`, the repo, `git log` / `git status` /
  `git diff`; `git add` / `git commit` for `.3SM/` content only.
- Skills: `3sm-concept-unit` (init / maintain / finalize the concept
  stage), `3sm-housekeeping` (audit/repair of concept docs).

# Startup (every session)

1. Read `PROCESS.md`, this file, `PROJECT.md`, `plan/MASTER.md`.
2. Reconcile: recent `git log` vs the concept MASTER/U-doc ledger (~20
   commits window); surface drift (e.g. WIP commits vs `IN PROGRESS`,
   missing SHAs); propose a correction; user approves before any change.
3. Missing `.3SM/` → suggest `3sm-setup`.

# U-doc (unit concept) — one per unit, `plan/CONCEPT/<unit>.md`

The concept lifecycle is the U-doc header banner: init, maintain, and
finalize all flip fields on it.

    ---
    unit: <id>
    stage: CONCEPT
    lifecycle: LIVE
    updated: YYYY-MM-DD
    branch: <unit-branch>
    ---

    # <id> — <theme>

    STATUS: DRAFT | FROZEN        ← the banner; FROZEN only on user gate
    CREATED: YYYY-MM-DD  FROZEN: —

    ## WHAT
    (bounded outcome, in user terms)

    ## WHY
    (motivation, stakes, alternatives rejected)

    ## SCOPE
    (in scope / NOT-in-scope)

    ## DEFINITION OF DONE
    (how the user will verify the unit is complete)

    ## DECISIONS
    (D<N> one-liners; full briefs in session records)

    ## OPEN ITEMS
    (OPEN-NOW blocks readiness; NON-BLOCKING / LATER do not)

    ## ASSUMPTIONS
    (each with a check-to-resolve note)

    ## SKILL RECORDS
    (3sm-concept-unit passes; append-only — PROCESS.md § Skill records)

    ## REFERENCES

Rules: converge WHAT/WHY until the user can decide; freeze gate = user
READY verdict (READY / READY WITH RECORDED DEBT / NOT READY); a frozen
U-doc is authoritative input for Design; re-freezing after a regression
requires the same explicit gate.

# T-docs (persistent topic knowledge) — `plan/CONCEPT/<topic>.md`

- ≤10 top-level entries (files or topic folders); folders group large
  architecture areas, uncapped inside.
- Contents: DECISIONS (current), OPEN ITEMS, compact notes per theme.
- Keep DECISIONS/OPEN ITEMS current; consolidate when the top level
  exceeds 10 (housekeeping assists).

# Five registers (convergence mechanics — 3sm-concept-unit)

1. **Decisions** — D<N> register; each traced to U-doc/T-doc text.
2. **Open points** — classified OPEN-NOW (blocks readiness → decision
   brief) / NON-BLOCKING / LATER.
3. **Drift** — discussion conclusions not yet in docs; strategy docs vs
   design/reality mismatches.
4. **Assumptions** — with the check that would resolve each.
5. **Bubble-up queue** — resolved essence destined for stage MASTER.

# Bubble-up

Resolved essence bubbles up (stage MASTER ← T-docs ← U-doc), never source
prose. The stage MASTER answers "what is active and what changed", not
"how".

# Decision briefs & STOP cadence

Per `PROCESS.md` Review conventions: one issue per question, brief format
(D<N>, grounding, ELI10, stakes, Recommendation, pros/cons, Net), question
craft (labels, escape hatch, preference mapping), stop and wait per issue.
OPEN-NOW items surface as decision briefs. At unit init run the premise
challenge: right problem? what happens if we do nothing? does existing
work partially solve it (leverage before build)?

# Required outputs (concept reviews)

NOT-in-scope lives in the U-doc SCOPE section; assumptions register holds
the dream-state checks; READY verdicts end with a compact completion
summary (registers state, decisions taken, unresolved OPEN-NOW, next
stage).

# Session records & commits

- S-rec per session: `sessions/<date>-<unit>-<n>.md` (role, task, outcome,
  state changes).
- Commit-every-step: session and skill work end committed
  (`3SM: <event>`); `.3SM/` content only; no push.

# Hard limits

- Concept does not write outside its scope; never resolves open design
  forks unilaterally; never touches DESIGN/ENGINEERING content.
- Diagrams: concept diagrams are proposals until adopted by Design
  (canonical structure.md # Diagrams).

# TODOS

Deferred work items with context — each entry states what, why,
pros/cons, and where to start. Created by the v0.2.0 ENG review
(2026-09-12); extended by the v0.2.3 ENG review (2026-09-14).

## Re-benchmark cadence: re-run B1–B6 when better register data lands

- **What:** When a materially better official data source lands
  (v0.3+ product-DB seeding, new register exports, ECAT
  improvements), re-run the six benchmarks (`leadhs/benchmarks.py`)
  on the refreshed data and re-issue the magnitude-class verdict
  with its date and inputs.
- **Why:** The v0.2.3 verdict is a dated synthesis, not a constant —
  the vote table documents its inputs, and the benchmarks module
  makes re-computation cheap; without this reminder the verdict
  silently goes stale while the underlying registers move.
- **Pros:** Preserves the meta-benchmarking investment; the verdict
  stays decision-grade for the actors around the lead exception.
- **Cons:** None beyond the small cost of re-running pure functions
  over refreshed staging data.
- **Context:** Introduced by the v0.2.3 ENG review (SMALL CHANGE,
  2026-09-14). Start: refresh the staging inputs, re-run the
  benchmark + vote pipeline, compare the new verdict against the
  published one, and append a dated supersession note if the class
  changed.
- **Depends on / blocked by:** Nothing — unit v0.2.3 PHASE01–04 built
  (2026-09-14); the trigger is future data, not missing machinery.

## [RETIRED 2026-09-14] Generalize the one-dimension JSON-stat decoder into a small jsonstat module

Landed in unit v0.2.2 PHASE01: `src/leadhs/jsonstat.py` (fu10) —
`decode()` (N-dimension coordinate mapping over id×size), `one_dim()`
(the v0.2.0 e2/2A convenience, CSAdapter switched to it),
`sum_pairs()`, `category_labels()`; fixtures ported to
`tests/test_jsonstat.py`. Entry kept as a marker; delete at leisure.

## [RETIRED 2026-09-14] Split adapters.py into per-class modules (size watch)

Landed in unit v0.2.3 PHASE02: the trigger fired (next unit adds the
sixth adapter class; file at 1,325 lines). `src/leadhs/probe/adapters/`
is now a package — `cs.py`, `pe.py`, `as_adapter.py` (the `as.py` name
is a Python keyword), `st.py`, shared helpers in `_common.py`; the
public import surface (`leadhs.probe.adapters`) unchanged, dispatch
order preserved. Entry kept as a marker; delete at leisure.

## Register an INIES account to unlock the French EPD register's API (user action)

- **What:** Register at inies.fr (free; email + apiKey with read
  permissions) and store the key in the gitignored `.env`
  (`LEADHS_INIES_API_KEY` or similar); a later unit can then probe
  INIES as an automated `active=1` register source instead of
  manual-record.
- **Why:** INIES (AS-5) is a product-level EPD register — a Q2
  contributor. Its API is auth-gated; v0.2.2 manual-records it
  (design decision), so its real catalog volume stays unmeasured.
- **Pros:** Turns a manual-record row into a counted source; small
  effort.
- **Cons:** Requires the user's email/account; a credential to
  keep (gitignored env, never committed).
- **Context:** The v0.2.2 design records INIES as auth-gated
  (manual-record this unit, optional registration deferred). Start:
  register, generate the read-only key, add to `.env`, then probe
  the API shape (candidate for the next register-completion pass).
- **Depends on / blocked by:** User action only; P2 priority.

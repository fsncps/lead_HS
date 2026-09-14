# TODOS

Deferred work items with context — each entry states what, why,
pros/cons, and where to start. Created by the v0.2.0 ENG review
(2026-09-12).

## [RETIRED 2026-09-14] Generalize the one-dimension JSON-stat decoder into a small jsonstat module

Landed in unit v0.2.2 PHASE01: `src/leadhs/jsonstat.py` (fu10) —
`decode()` (N-dimension coordinate mapping over id×size), `one_dim()`
(the v0.2.0 e2/2A convenience, CSAdapter switched to it),
`sum_pairs()`, `category_labels()`; fixtures ported to
`tests/test_jsonstat.py`. Entry kept as a marker; delete at leisure.

## Split adapters.py into per-class modules (size watch)

- **What:** When `src/leadhs/probe/adapters.py` crosses ~1,500
  lines, split it into per-class modules (`probe/adapters/cs.py`,
  `pe.py`, `as.py`, `st.py`) with the shared helpers
  (`_sniff`, CSV-shape, `_depth_tier`) in a common module; the
  adapter registration/dispatch stays where it is.
- **Why:** The file holds all five adapters (CS/PE/AS/ST, 1,122
  lines after v0.2.1) and v0.2.2 extends the AS ingest and PE recon
  further; it is the file most likely to become hard to navigate.
- **Pros:** Keeps each adapter readable in isolation; clearer
  ownership of the shared parse helpers.
- **Cons:** Pure refactor — no behavior change; touches import
  surface and test files for a problem that is not yet real.
- **Context:** Check the line count at the start of the unit after
  v0.2.2; split only if the threshold is crossed or the next unit
  adds another adapter class. Keep the module-level helper functions
  import-stable.
- **Depends on / blocked by:** Nothing; P3 priority.

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

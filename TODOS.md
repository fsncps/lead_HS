# TODOS

Deferred work items with context — each entry states what, why,
pros/cons, and where to start. Created by the v0.2.0 ENG review
(2026-09-12).

## Generalize the one-dimension JSON-stat decoder into a small jsonstat module

- **What:** Extract the minimal flat-index → dimension-label decoder
  built for the CS-2 trade sums (v0.2.0, e2/decision 2A) into a
  reusable module (`leadhs/jsonstat.py` or similar) that decodes any
  JSON-stat payload's `value` object against `id`/`size` for
  selected dimensions.
- **Why:** PRODCOM and SBS — the remaining N1 statistics sources on
  the roadmap — are also Eurostat APIs speaking the same JSON-stat
  format. The v0.2.0 decoder deliberately handles only one free
  dimension (partner); the future callers will need product/NACE
  and period dimensions decoded too.
- **Pros:** No re-derivation of the JSON-stat indexing rules at each
  future unit; one tested implementation instead of copy-grow.
- **Cons:** ~150 lines + tests now for a single current caller;
  deferred to avoid speculative generality (engineered-enough
  preference).
- **Context:** v0.2.0 ships the decoder inline in the CS adapter
  aggregation (adapters.py) with fixtures shaped on real Eurostat
  Comext responses (value as object keyed by flat row index,
  row-major over `id`×`size`). Start: lift the decoder, add
  multi-dimension coordinate mapping, port the fixtures.
- **Depends on / blocked by:** Nothing; natural landing spot is the
  first unit that adds a PRODCOM/SBS source (N1 completion work).

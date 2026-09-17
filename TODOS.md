# TODOS

Deferred work items with context — each entry states what, why,
pros/cons, and where to start. Created by the v0.2.0 ENG review
(2026-09-12); extended by the v0.2.3 ENG review (2026-09-14), the
v0.2.4 ENG review (2026-09-14) and the v0.2.4 addendum D40 ENG review
(2026-09-17).

## RESOLVED 2026-09-17 — manual browser pass to pin the /sok search route

RESOLUTION: no browser pass was needed — the code pin found the
answer when extended past the first displacement: the /sok search
component loads `type='module'` bundles whose API paths are built
dynamically, and the site calls its OWN same-origin proxy
`<origin>/apiproxy/v3/...` anonymously (pinned verbatim from the
generated OpenAPI client `assets/ui/services.gen-onZ4SLnf.js`,
accessed 2026-09-17; module constant db8). Delivered the 100-article
sample (run_key probe-20260917-as33bastaprobe, D40 addendum). This
entry is kept as the record of the resolution, not as pending work.

## bk04Code paint-code enumeration for a server-side paint filter (open)

- **What:** pin the BK04 code values that denote paints/varnishes
  (the sample surfaced 03402 Fasadfärg utomhus and 03404 Vägg- och
  takfärg inomhus; a full enumeration of the paint-family codes in
  the register's BK04 vocabulary still has no pinned list — the
  /apiproxy search takes one bk04Code per call) so a BASTA
  paint-subset filter can run server-side. When pinned, the D40
  draw re-runs with `_PAINT_FILTER_PARAM` set and **de5 (a
  data_sources.csv row) is met** — the de5 gate still NOT met for
  BASTA.
- **Why:** the paint subset of BASTA's ~195k construction articles
  is the study's AS-33 population; the articleName search is not a
  filter (färg→106, lack→30, "lack färg"→200,769 — the D40 record).
- **Pros:** turns a source-survey answer (Q2 floor) into a real
  bulk surface; the identity tuple is already proven 100% complete.
- **Cons:** needs the BK04 master (likely behind the same-origin
  /apiproxy code lists or an SSR category page); possible manual devtools
  pin (one fetch).
- **Context:** created by the D40 execution (2026-09-17). Start: on
  the extend of the basta special probe; see
  20_DESIGN/units/v0.2.4-basta-addendum.md db5.
- **Depends on / blocked by:** nothing hard; any future paint-filter
  probe run.

- **What:** If the `basta-probe` PHASE01 bundle-chain pin ends in an
  honest "no anonymous route found" record, run one manual devtools
  session in a normal browser on bastaonline.se/sok (Network tab,
  one query), record the upstream request (URL, method, params) in
  the AS-33 strategy/design notes, and re-run the probe with the
  route added as a pinned constant (db1).
- **Why:** The D40 design rests on one unproven assumption — that an
  anonymous JSON route serves the client shell's search. Code pinning
  greps minified bundles and may come up empty even where the route
  exists; the manual pass resolves that single fact deterministically.
- **Pros:** Unlocks the 100-article BASTA sample (a second
  identity-tuple source beyond ECAT/Nordic Swan — Q2 floor grows);
  one short session, no tools to build.
- **Cons:** Requires user time + a browser; adds a hand-copied fact
  that future probes trust (needs URL + access-date provenance like
  every pinned surface).
- **Context:** Created by the v0.2.4 addendum D40 ENG review
  (2026-09-17, adopted). The auth'ed API (api.bastaonline.se, 401
  anonymous) and the agreement/Excel-excerpt contacts are NOT
  fallbacks — D4 forbids accounts; only an anonymous surface counts.
  Start: only after a delivered `basta_special_unavailable`
  pin-not-found finding; record the finding's run_key as the
  precondition.
- **Depends on / blocked by:** v0.2.4-basta-addendum PHASE01
  executed with an honest pin-not-found outcome; nothing else.

## Reconcile the v0.2.4 AS-3 discovery trial with the pilot unit's pinned mechanics

- **Status (D38, 2026-09-14): the mechanics are now known** — the
  export is a GET on the search URL with `?format=csv` (semicolon
  CSV, header `Product;License number;…;City`). The parse/filter
  defects behind the "trial-grade 14 distinct" record were fixed and
  the sample re-rendered from the archived export (structured
  product-group filter; source-parameterized dedupe triple). What
  remains of this entry: pin the real URL as the first candidate
  (or the only one) in `_NS_CANDIDATE_SUFFIXES` and drop the guess
  paths — a small refactor for the pilot unit.
- **What:** When a later unit pins the Nordic Swan (AS-3) export
  mechanics for real (the pending second-register pilot), revisit
  the bounded-discovery handler in `src/leadhs/probe/csv_sample.py`
  (`_NS_CANDIDATE_SUFFIXES` + failure text) and replace the trial
  endpoint guesses with the pinned export URL + parse path.
- **Why:** The v0.2.4 handler is a bounded best-effort attempt over
  candidate endpoints; once the real mechanics are known the trial
  code lingers as guesswork that neither fails nor succeeds
  honestly.
- **Pros:** The sample command keeps working unchanged; the pilot's
  knowledge lands in one place instead of drifting between modules.
- **Cons:** None beyond a small refactor when the pilot lands.
- **Context:** Proposed by the v0.2.4 ENG review (2026-09-14,
  approved). The trial code is offline-tested against the fixture
  site; its failure mode is an honest `csv_sample_unavailable`
  record. Start: take the pilot unit's pinned export URL, swap it
  into `_NS_CANDIDATE_SUFFIXES` as the first candidate (or drop the
  candidate list entirely), and retire this entry. (The criterion-096
  filter part of the original entry is resolved — replaced by the
  structured product-group filter, D38.)
- **Depends on / blocked by:** The second-register pilot unit
  (Strategy OPEN ITEMS); nothing in v0.2.4 blocks on it.

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
  The 2026-09-14 AS-class source probe (D37) confirms the finding:
  no bulk export endpoint exists (≤5 bounded GETs, 404s), count not
  visible on the landing page — registration stays the only path to
  a counted INIES universe.
- **Depends on / blocked by:** User action only; P2 priority.

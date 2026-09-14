---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE03 — AS-3 Nordic Swan bounded discovery (offline)

## Objective

Add the Nordic Swan (AS-3) bounded export-discovery handler to
`csv_sample.py`: up to 5 polite, robots-checked GETs across the
pinned source URL and candidate export endpoints; a CSV response
feeds the ECAT path with the criterion-096 filter; anything else
lands an honest `unavailable` record. Offline via the fixture site.

## Preconditions

- PHASE02 done (module, CLI wiring, manifest).
- Design in force: per-registry behavior row AS-3; named-exception
  amendment (no bare except).

## Governing references

- `../../20_DESIGN/units/v0.2.4.md` (per-registry behavior; review
  outcomes — named-exception amendment)
- `../v0.2.4/MASTER.md` (acceptance criteria)
- TODOS.md (the reconciliation entry — this trial code is revisited
  when the pilot unit pins the real mechanics)

## Steps

1. **Candidate list (i4 constant):** `_NS_CANDIDATE_PATHS` — the
   pinned source URL first, then plausible export endpoints
   (`?format=csv` style); ≤5 GETs total, each through
   `fetcher.get` (robots + spacing apply), stop at the first CSV.
2. **CSV branch:** reuse the ECAT ingest path with the criterion-096
   in-scope filter (`_in_scope_group` semantics over name/category
   text: paint/varnish/coating/096/färg/lack) — sampling, archive,
   provenance identical to AS-2 (de3).
3. **Failure branch:** HTML/other/4xx/5xx/network — catch the named
   taxonomy only (`FetchError` subclasses, `UnexpectedFormat`);
   after the budget → run done + `csv_sample_unavailable` finding:
   "export mechanics unpinned after ≤5 bounded GETs — browser pass
   required (TODOS reconciliation)"; the manifest shows
   `unavailable` with the reason. A should-deliver failure (register
   row misconfigured, e.g. export_url set but host dead) stays
   `failed` → exit 2 — the distinction lives in the finding text.
4. **Tests:** HTML search surface → unavailable record, GET count
   ≤5 asserted via site hits, manifest entry present; a CSV
   response on the first candidate → delivered via the 096 filter;
   a 500 on the pinned URL → unavailable (bounded, no crash).

## Deliverables

AS-3 handler in `csv_sample.py`; the three test cases.

## Exit gate

Full offline suite green; the six-source default set ends
delivered/unavailable/failed correctly on fixtures.

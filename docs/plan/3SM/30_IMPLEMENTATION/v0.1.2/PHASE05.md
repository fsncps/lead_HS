---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE05 — Census capability (migration 0003, census mechanics, report content layer)

Status: done (2026-09-11) · Depends on: PHASE04 (green suite) · Governs: the
schema extension, the census completion mechanics and the report
contract the census close-out delivers through.

## Objective

Give the census its final shape before it runs, per the second-pass
design (od8–od10): migration 0003 adds the per-HS count metrics
`records_hs3208/3209/3213` + `census_status` (od10) and redefines
`v_anchor_candidates`; the adapters gain the census completion
mechanics (od9: parameterized CS-2 query, ST-2 register URL fix, PE
category depth); `report.py` becomes the od8 content layer — one
DB-only assembly, three renderers (md narrative + matrix, csv summary
matrix only, json full structure).

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §Migration 0003 (od10),
  §Census completion mechanics (od9), §Report content layer (od8),
  §Testing additions (t8).
- `../../20_DESIGN/MASTER/interfaces.md` — probe_metric vocabulary
  (i4/i12; extension rule: migration INSERT; sync test pins
  0001 + 0003).
- `../../20_DESIGN/MASTER/data_model.md` — §Migration plan (0003 row,
  renumber note; dm11/dm16).
- `../../10_STRATEGY/DATA_SOURCE.md` — §Census metadata set (D25).
- `../v0.1.2/MASTER.md` — B7 (per-HS metrics via migration 0003).

## Steps

1. **Migration `0003__probe_metrics.sql`** (od10) — applied after
   0002 (forward-only; backup default on):
   - `probe_metric` INSERTs (codes never renamed, value_type fixed at
     insert): `records_hs3208` ("Records HS 3208", numeric — rows for
     HS 3208 in the parameterized query; 0 = queried and empty),
     `records_hs3209` (numeric), `records_hs3213` (numeric, census
     annex), `census_status` ("Census status", text — manual/deferral
     record on a source's census state; method=manual).
   - `v_anchor_candidates` redefined: metric list gains the three
     records_hs* codes; the view header comment records the
     redefinition per data_model dm11.
   - Idempotent via the schema_version machinery; applies on existing
     v0.1.1 databases (backup taken).
2. **`metrics.py`** — four new constants (`METRIC_RECORDS_HS3208`,
   `METRIC_RECORDS_HS3209`, `METRIC_RECORDS_HS3213`,
   `METRIC_CENSUS_STATUS`) + seeds; extend the vocabulary sync test to
   pin **0001 + 0003 == metrics.py** and bump the size test (17 → 21).
3. **Census mechanics (od9):**
   - **CS adapter (CS-2):** build a parameterized JSON query on the
     register's base URL — documented constants (format, frequency,
     period, flow, product list) fixed as module defaults; exact
     values land in `run.parameters_json` at execution; the response
     is archived as a document (verification artifact). Per-HS queries
     emit `records_hs3208/3209/3213` (method=api); an empty result set
     is an honest 0. The bare-URL fetch (the `export_rows=1`
     artefact of the v0.1.1 pass) is retired for API sources.
   - **ST-2 register URL fix:** `sources.csv` SPIN URL → the download
     page (`?page_id=54`, matching the ST adapter's hints);
     persistent failure stays a `failed` run with notes + a manual
     census_status record if needed (execution concern).
   - **PE adapter category depth:** after the landing page, fetch up
     to 3 category pages (from the enumerated category_list; polite
     spacing unchanged) and emit `category_count` per category;
     `catalog_count` stays landing-page-derived with a notes line;
     product-page sampling (sample_n) unchanged. A failing category
     page appends a note and continues (sample-page pattern).
     **Build seam resolved (recorded):** od9's "value_text = category
     path" collided with the binding R4 audit rule (numeric metrics
     carry no value_text); the category path lives in the finding
     **notes** instead — interfaces.md vocabulary row clarified
     accordingly (docs-only, R4 unchanged).
   - **Manual records:** `probe record` works on inactive sources
     (ST-1 already registered active=0) — verify, add a regression
     test; ST-1 PCN aggregates, PE-3 deferral note and CS-1 export
     mechanics are recorded via `make record` with metric
     `census_status` (method=manual) at execution.
4. **Report content layer (od8)** — one assembly in `report.py`,
   three renderers, same data, DB reads only (P7). Fetchers:
   `_fetch_sources` (register: id, class, name, url, access_method,
   verification_status, active, notes), `_fetch_latest_runs` (latest
   census probe run per source — GROUP BY on run.id, any status —
   with status_code, finished_at, notes, document/finding counts;
   dry-run runs excluded by parsing `parameters_json` in Python;
   malformed JSON fails open = treated as a real run), plus the
   existing views (v_probe_latest, v_anchor_candidates,
   v_source_activity — unchanged).
   - **md** — decision-maker document: title "Source feasibility
     census report" + framing paragraph (source-feasibility metrics;
     product and lead prevalence are M2+ deliverables, never implied
     here — U9; product data only, Strategy MASTER D27); summary
     matrix over **all registered sources** (all 14, active flag
     included; LG rows appear solely as inactive rows — no legal
     content, no findings); per-source sections
     (identity/access/content/counts/availability/provenance) with
     duplicate same-run metric rows (per-category category_count)
     listed in full; run status table incl. **blocked/failed with
     notes**; anchors + activity (footnote: raw counts, dry runs
     included there); legend "—" = metric absent (not queried) vs
     `0` = queried, empty; metric values cite their done run's
     run_key.
   - **csv** — the summary matrix only (spreadsheet deliverable; json
     carries the full data — no duplication).
   - **json** — the full structure (stable shape; the future M3/M4
     report build consumes the same assembly).
5. **Tests (t8)** — `test_report_content.py` (framing/title strings;
   run-status section shows a blocked and a failed source with notes;
   matrix rows for all registered sources incl. inactive;
   dry-run-only DB → "no census runs yet"; "—" vs 0 distinction;
   duplicate category_count rows listed; csv = one row per source
   with the matrix header; json section keys);
   `test_adapters_cs.py` extends (parameterized per-HS emission on
   fixture JSON; empty result → 0; UnexpectedFormat path unchanged;
   parameters surfaced for parameters_json); `test_adapters_pe.py`
   extends (category-page depth on the fixture site; category failure
   → note + continue); `test_engine.py`/`test_views.py` extend
   (census_status manual record; v_anchor_candidates includes
   records_hs*); `test_migrations.py` gains the 0003 view test.
6. **Golden regeneration (t3)** — delete `tests/golden/*`, re-run,
   review the diff — explicit step after od8 lands.

## Deliverables

`src/leadhs/migrations/0003__probe_metrics.sql`; `metrics.py`
extension; od9 adapter deltas (`probe/adapters.py`) + ST-2 URL fix in
`dict/sources.csv`; restructured `report.py` (+ template); test +
golden updates.

## Exit gate

- `pytest` green offline, including the new/extended tests and the
  regenerated golden files; sync test pins 0001 + 0003 == metrics.py.
- Migration 0003 applies clean on a fresh DB **and** upgrades an
  existing 0001/0002 database (backup taken);
  v_anchor_candidates includes the records_hs* codes.
- The report on the fixture corpus shows: framing + title, summary
  matrix over all registered sources (incl. inactive), per-source
  structured sections, run status incl. blocked/failed + notes, the
  "—" vs 0 legend — md, csv (matrix only) and json (full structure).
- CS adapter emits records_hs* findings from parameterized queries
  (empty result → 0) and records its parameters; PE adapter walks up
  to 3 category pages (category_count rows carry the category path;
  failing category → note, run continues).
- `probe record --metric census_status --value-text …` works on an
  inactive source; R4 holds (text metric rejects --value).

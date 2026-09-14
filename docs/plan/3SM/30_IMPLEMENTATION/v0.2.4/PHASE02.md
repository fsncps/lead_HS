---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE02 — csv_sample.py: ECAT sampling + ST no-fetch records + manifest (offline)

## Objective

Land `src/leadhs/probe/csv_sample.py` (the command module minus the
AS-3 discovery handler — PHASE03) and the CLI wiring
(`leadhs probe download-csv-sample`), with the full offline test set
on the fixture site. Everything in this phase runs offline.

## Preconditions

- PHASE01 done (0009 seeds; metrics validatable).
- Design in force: command surface, per-source state machine, 1A
  (manifest always written), amendments 1–7.

## Governing references

- `../../20_DESIGN/units/v0.2.4.md` (all sections; review outcomes)
- `../v0.2.4/MASTER.md` (acceptance criteria)
- `src/leadhs/probe/engine.py` (`_insert_run`/`_insert_probe_run`/
  `_finish_run`/`persist` — the single write path, i3);
  `src/leadhs/fetch.py` (error taxonomy; `plan()` = zero network);
  `src/leadhs/probe/adapters/_common.py` (`read_csv_rows`,
  `sniff_kind`, `_delimiter_of`);
  `src/leadhs/probe/adapters/as_adapter.py` (`_in_scope_group`,
  `_EXPORT_EXPECTED`)

## Steps

1. **Module constants (i4):** `_DEFAULT_SOURCES` (AS-2, AS-3, ST-1,
   ST-3, ST-6, ST-7); `_PROVENANCE_COLUMNS = ("source_id", "run_key",
   "retrieval_date", "doc_hash", "sample_seed", "sample_index")`;
   `_NO_FETCH_REASONS` — the four pinned reason strings with URL +
   access-date citations (PCN authority-only; KemI secrecy;
   DK aggregates-only Power BI; SBS enterprise-level); the
   cross-identification candidate line for the manifest.
2. **Run bookkeeping:** per source one run (kind=probe, slug =
   `slug_for_source(id)` + `csvsample`, parameters: n/seed/dry_run)
   + probe_run mode `csv_sample` + `UPDATE run SET seed=?` — via the
   engine helpers; findings via `engine.persist` with a ProbeResult
   (document draft for the archived export; findings
   `csv_sample_rows` numeric / `csv_sample_unavailable` text with
   the reason). Run status: delivered/unavailable → done,
   should-deliver failure → failed.
3. **ECAT handler:** source row must exist (caller validates) and
   carry `export_url` (else failed, loud note); `fetcher.get` →
   `sniff_kind` gate (html → failed "HTML landing page") →
   `read_csv_rows(content, separator=_delimiter_of(...), expected=`
   `_EXPORT_EXPECTED["AS-2"])` → in-scope filter (`_in_scope_group`
   on group_name) → dedupe on (product+company+group) →
   `random.Random(seed).sample(pool, min(n, len(pool)))` (clamp +
   shortfall note) → archive via store (persist does it) → write
   `csv-sample.<ts>.AS-2.csv` (verbatim columns + provenance) →
   finding `csv_sample_rows` (notes: pool pre/post dedupe, clamp,
   seed, file, header columns). 0 in-scope rows → failed
   (data-drift signal).
4. **ST no-fetch handler:** zero network; finding
   `csv_sample_unavailable` with the pinned reason + citation; run
   done; no document.
5. **Manifest renderer:** `csv-sample.manifest.<ts>.md` + `.csv` —
   per source: status, rows, fields returned (column list),
   identifier columns, cross-identification candidates, reason/file;
   header carries ts, seed, n, out-dir. ALWAYS written (1A). Plus
   the unversioned `csv-sample.manifest.md`/`.csv` latest copies.
6. **CLI wiring:** `probe download-csv-sample` with `--n`
   (IntRange(min=1), default 100), `--seed` (default 42),
   `--source` (multiple; default all six; unknown id → exit 1 with
   the load-register hint), `--out-dir` (default `data/report`),
   `--dry-run` (plan the export URL, zero network, zero files, no
   run rows). Aggregate exit code: any failed → 2 else 0. Echo one
   summary line per source.
7. **Tests** (`tests/test_csv_sample.py`, fixture site):
   happy-path determinism (same/different seed via the /ecat.csv
   fixture); column preservation + provenance; clamp (pool 2 < n
   100); dedupe + pool reporting; manifest content + latest copies;
   ST records with citations + zero network; AS-2 failure (mocked
   500 via /error500 row) → manifest exists with failed + exit 2;
   --dry-run zero network/files; exit codes; unknown source / --n 0
   → exit 1; column drift (/export-bad.csv row) → UnexpectedFormat →
   failed + exit 2. Add fixture register rows (unique hosts per
   active row, i13) + an /ecat-pool.csv fixture path (≥30 in-scope
   rows + duplicates) for the determinism-with-headroom test.

## Deliverables

`src/leadhs/probe/csv_sample.py`; CLI command; conftest fixture
paths; `tests/test_csv_sample.py`.

## Exit gate

Full offline suite green including the new tests; no network in the
phase (fixture site only); existing suite still green.

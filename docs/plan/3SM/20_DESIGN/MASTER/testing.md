---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-10
---

# Testing (Design)

## Abstract

The test strategy for the `leadhs` tool: what gets tested, how, and
the rules that keep the suite deterministic and fast. Core rules: no
network in the default suite (a local fixture site stands in for the
real web; network tests are opt-in via a marker); no real time
waiting (the fetcher's clock and sleep are injected); every database
test runs on a fresh in-memory or temp-file SQLite; every error path
in the interfaces.md mapping table has at least one test.

## Test matrix

```
NEW CLI FLOWS:
  db init/status/audit | source load/list | probe run (dry+fixture)
  probe record | probe report | doctor

NEW DATA FLOWS:
  register CSV → source rows
  fetch → document row + raw-store file
  adapter → FindingDrafts (+ documents)
  views → report output

NEW CODEPATHS:
  robots deny | 403/429 block | retry→fail | rate-limit spacing
  abort/resume | migration order | audit rules R1–R9 | dry-run plan

NEW INTEGRATIONS / EXTERNAL CALLS:
  local http.server fixture site (HTML catalog + robots.txt + PDF)
  fixture swiss-impex-style export CSV
  SPIN fixture via mdbtools (gated on binary presence)
  SQLite (migrations, views, constraints)

NEW ERROR/RESCUE PATHS:
  every row of the interfaces.md exception table
```

Each matrix item maps to: test type (unit / integration / smoke),
file, and happy + failure + edge case. Edge cases include the empty
path (no sources → "no sources", exit 0) and nil/empty inputs
(malformed CSV row, empty HTML page, 404 robots.txt = allow-all).

## Key test files

- **test_migrations.py** — fresh DB applies 0001→0002; re-run is a
  no-op (idempotency via schema_version); migration order enforced;
  CHECK constraints hold (per-source probe run; archived ⇒ hash).
- **test_store.py** — hash-only filenames; source-id allowlist
  rejects traversal attempts (`../`, `CS-1/../../`); orphan
  detection; verify(hash) round-trip.
- **test_fetch.py** — fake clock: ≥2 s spacing per domain; robots
  deny → RobotsDisallowed; 403/429 → Blocked; retry 2× then
  ProbeNetworkError; dry-run mode performs zero network calls.
- **test_adapters_pe.py** — fixture catalog HTML → catalog_count,
  category_count/category_list, languages; sample pages →
  page_sample_ok/sds_sample_ok; sample pages archived as documents.
- **test_adapters_cs.py** — fixture export CSV → format,
  granularity, export_rows; wrong-layout fixture → UnexpectedFormat
  → format finding with WARNING.
- **test_adapters_st.py** — gated on mdbtools binary (skipif):
  extraction_path ok; missing binary → BinaryMissing path (forced).
- **test_engine.py** — one run per source; `--all` continues past a
  failing source; interrupt → run aborted, findings persist; re-run
  → new run_key (-2 suffix); exit codes.
- **test_views.py** — v_probe_latest correctness under re-run (newer
  run wins); v_anchor_candidates lists count-metrics; v_source_activity
  first/last retrieval.
- **test_report_golden.py** — fixture findings → exact md/csv/json
  output (golden files; intentional changes regenerate with review).
- **test_cli_smoke.py** — end-to-end on a temp DB + fixture register
  + local fixture site: init → load → probe run → report → audit
  exit 0. The 2am-Friday confidence test.
- **test_audit.py** — R2 violation (archived document, missing file)
  detected; R4 value/type mismatch detected; `--unreferenced` lists
  a planted orphan file; clean fixture corpus exits 0.
- **test_doctor.py** — fake binaries on PATH; missing contact →
  warning; data-dir not writable → error.

## Hostile-QA cases (explicitly tested)

Traversal-style source IDs and URLs; malformed register CSV (bad
class, missing URL, duplicate ID — last errors loudly, exit 1);
empty register; huge HTML page; non-UTF-8 bytes (raw store keeps
bytes; parsing degrades to page_sample_ok=0); robots.txt 404 (treat
as allow) and empty file; duplicate findings on re-probe (dedup by
new-run semantics, not mutation).

## Chaos test

Kill a probe run mid-source (simulated interrupt): run=aborted,
findings persisted, re-run idempotent, `db audit` still clean.

## Flakiness & environment rules

- No sleeps: rate-limit tests use the injected clock.
- Network tests marked `@pytest.mark.net` — deselected by default.
- mdbtools tests marked `@pytest.mark.mdbtools` — skipped when the
  binary is absent (Slackware).
- Tests are order-independent; each builds its own temp state
  (tmp_path + in-memory SQLite).
- The fixture site runs on an ephemeral localhost port in a thread —
  no external dependencies.

## Ambition checks

- **2am-Friday test:** test_cli_smoke green + test_audit clean on the
  fixture corpus.
- **Hostile QA:** the hostile list above.
- **Chaos:** the interrupt test above.
- Load/stress: not applicable at this scale; the SPIN bulk-import
  path (M2) will get batching tests with a generated large fixture.

## DECISIONS (design-level; consolidated in 20_DESIGN/MASTER.md)

- t1: no-network default suite; markers for net/mdbtools.
- t2: injectable clock/sleeper — no time-dependent flakiness.
- t3: golden report tests with reviewed regeneration.
- t4: every interfaces.md error row has ≥1 test (mapping table is
  the coverage checklist).
- t5: fixture site via local http.server thread; fixture register +
  fixture exports in tests/fixtures/.

## OPEN ITEMS

- SPIN fixture file format for the gated tests (small .mdb via
  mdbtools or pre-extracted CSV) — resolve at implementation.
- Golden-file refresh policy: regenerate on intentional output
  change with explicit review (convention note, enforce in PRs).
- Coverage target: no fixed percentage; the matrix is the contract.

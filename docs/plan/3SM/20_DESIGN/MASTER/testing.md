---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-11
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
  exit-code mapping (usage → 1, Abort → 130) | bare-group help
  source list single registration | doctor --net | --data-dir

NEW DATA FLOWS:
  register CSV → source rows
  fetch → document row + raw-store file
  adapter → FindingDrafts (+ documents)
  views → report output
  make target wiring (make -n / guarded targets)
  report file routing data/report → docs/report

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
  uninitialized DB → guided error | make GO guard | clobber confirm
  report-publish missing WHICH
```

Each matrix item maps to: test type (unit / integration / smoke),
file, and happy + failure + edge case. Edge cases include the empty
path (no sources → "no sources", exit 0) and nil/empty inputs
(malformed CSV row, empty HTML page, 404 robots.txt = allow-all).

## Key test files

- **test_migrations.py** — fresh DB applies 0001→0002; re-run is a
  no-op (idempotency via schema_version); migration order enforced;
  CHECK constraints hold (per-source probe run; archived ⇒ hash);
  backup round-trip (seeded DB → migrate → timestamped backup
  restores a working DB); sync test (0001 probe_metric seeds ==
  metrics.py list).
- **test_store.py** — hash-only filenames; source-id allowlist
  rejects traversal attempts (`../`, `CS-1/../../`); orphan
  detection; verify(hash) round-trip.
- **test_fetch.py** — fake clock: ≥2 s spacing per domain; robots
  deny → RobotsDisallowed; 403 → Blocked; 429 → RateLimited (one
  capped backoff) → retry succeeds, persistent 429 → blocked; retry
  2× then ProbeNetworkError; dry-run mode performs zero network calls.
- **test_adapters_pe.py** — fixture catalog HTML → catalog_count,
  category_count/category_list, languages; sample pages →
  page_sample_ok/sds_sample_ok; sample pages archived as documents.
- **test_adapters_cs.py** — fixture export CSV → format,
  granularity, export_rows; wrong-layout fixture → UnexpectedFormat
  → format finding with WARNING.
- **test_adapters_st.py** — gated on mdbtools binary (skipif):
  extraction_path ok; missing binary → BinaryMissing path (forced).
- **test_adapters_contract.py** — each adapter runs against a
  `PRAGMA query_only=ON` connection and completes draft-only: pins
  i3 (adapters never write the DB; engine owns the single write
  path) and guards the adapter contract for future adapters
  (implementation-plan ENG review 2026-09-11).
- **test_engine.py** — one run per source; `--all` continues past a
  failing source; interrupt → run aborted, findings persist; re-run
  → new run_key (-2 suffix); exit codes; stale-run reclaim
  (pre-inserted stale `running` run → next command marks it failed
  with `stale run reclaimed`).
- **test_views.py** — v_probe_latest correctness under re-run (newer
  done run wins); a later aborted/blocked run does not shadow the
  last done census; v_anchor_candidates lists count-metrics;
  v_source_activity first/last retrieval.
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
- **test_cli_operability.py** — exit-code mapping (unknown command,
  missing option, bad choice → 1); bare groups print help exit 0;
  `source list` registered once (no `list-`); `--db`+`--data-dir`
  conflict → 1; `--no-net` gone from doctor help; Abort/interrupt
  → 130 (v0.1.2).
- **test_preflight.py** — uninitialized DB (missing file / empty /
  no schema_version) → guided error, exit 1, on db status|audit,
  source load|list, probe run|record|report; after `db init` the
  same commands pass; `db init` itself unaffected (v0.1.2).
- **test_makefile.py** — gated on `make` + repo root: `make help`
  exit 0; `make probe`/`make census` (no GO) fail with the guard
  message before any side effect; `make sample` fails with the
  milestone pointer; `GO=1 make -n probe` prints the leadhs line;
  `make -n report` prints the three `--out` lines;
  `make report-publish` (no WHICH) fails with the usage line
  (v0.1.2).

## Hostile-QA cases (explicitly tested)

Traversal-style source IDs and URLs; malformed register CSV (bad
class, missing URL, duplicate ID — last errors loudly, exit 1);
empty register; huge HTML page; non-UTF-8 bytes (raw store keeps
bytes; parsing degrades to page_sample_ok=0); robots.txt 404 (treat
as allow) and empty file; duplicate findings on re-probe (dedup by
new-run semantics, not mutation).

## Chaos test

Kill a probe run mid-source (simulated interrupt): run=aborted,
findings persisted, re-run idempotent, `db audit` still clean,
v_probe_latest unchanged by the aborted run.

## Flakiness & environment rules

- No sleeps: rate-limit tests use the injected clock.
- Network tests marked `@pytest.mark.net` — deselected by default.
- mdbtools tests marked `@pytest.mark.mdbtools` — skipped when the
  binary is absent (Slackware).
- Tests are order-independent; each builds its own temp state
  (tmp_path + in-memory SQLite).
- The fixture site runs on an ephemeral localhost port in a thread —
  no external dependencies.
- Makefile tests run only `make -n` (dry-run) or guarded targets
  that fail before any side effect; skipped when `make` is absent.

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
- t6: crash/backup coverage — metrics sync, backup round-trip,
  stale-run reclaim, 429-retry tests (ENG review 2026-09-11).
- t7: operability + preflight + make-wiring tests
  (test_cli_operability.py, test_preflight.py, test_makefile.py) —
  v0.1.2 (HOLD-SCOPE review 2026-09-11).

## OPEN ITEMS

- SPIN fixture file format for the gated tests (small .mdb via
  mdbtools or pre-extracted CSV) — resolve at implementation.
- Golden-file refresh policy: regenerate on intentional output
  change with explicit review (convention note, enforce in PRs).
- Coverage target: no fixed percentage; the matrix is the contract.

---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-11
---

# Architecture — modules, runtime, tooling (Design)

## Abstract

This document fixes how the `leadhs` Python package is built: which
modules exist, what each one is responsible for, how the program runs
(one command = one short-lived process, no servers, no daemons), how
the raw-document store and the database are accessed, and how the
probe engine is structured so that new source types can be added
without touching the engine. The stack and the M0–M4 rollout are
inherited unchanged from 10_STRATEGY/ARCHITECTURE.md; this is the
detailed HOW on top of it.

## Stack (inherited)

Python ≥ 3.11, stdlib-first; `requests`, `beautifulsoup4`, `click`,
`jinja2` (reports), `pypdf` (M2, backend decision open); optional
`matplotlib` (M3), mdbtools route for SPIN. No servers, no services —
every stage is a CLI step (10_STRATEGY/ARCHITECTURE.md D1/D5).

## Runtime model

- One CLI process per command; one SQLite connection; WAL mode,
  `foreign_keys=ON`, `busy_timeout=5000` set by `db.connect()`.
- `data/leadhs.sqlite` and `data/raw/` are gitignored; code,
  migrations (`src/leadhs/migrations/`), seed dictionaries
  (`src/leadhs/dict/`) and final reports are in git.
- No long-lived state anywhere; resumability comes from the `run`
  audit trail + append-only evidence, not from daemon state.

## Operator layer (v0.1.2)

The Makefile at the repo root is the stable operator entrypoint — a
thin wrapper, one target per `leadhs` call; pipeline logic lives in
the CLI (strategy D21; d21/a12). Full target contract and recipe
text: `units/v0.1.2.md`.

- Parameters are make variables with documented defaults (`DB`,
  `MODE`, `SAMPLE`, `SOURCE`, `REPORT_DIR`, `PUBLISH_DIR`) until M1,
  when a committed config file joins (one config migration).
- GO gate: costly network targets (`probe`, `census`) and the
  destructive `clobber` carry a `guard-%` **prerequisite** — the
  gate fires before any recipe side effect; `census` lists its guard
  first, so `setup` never runs without GO=1. `clobber` additionally
  prompts for a typed `yes`.
- `make help` is the self-documenting operator index; M1–M4 stages
  exist as stub targets that exit 1 with a pointer.
- Report routing: `make report` renders into `data/report/`
  (gitignored intermediates); `make report-publish WHICH=…` copies —
  never moves — one report into `docs/report/` (committed finals).
- CLI contract enforcement lives in `cli.main()`:
  `standalone_mode=False`; usage errors exit 1; `Abort`/interrupt
  exit 130; bare groups print help; `_ensure_initialized` turns an
  uninitialized DB into a guided error (never `bug:`).
- Installed (non-repo) use: `--data-dir DIR` (mutually exclusive
  with `--db`) is the explicit home for `leadhs.sqlite` + `raw/` —
  never CWD-implicit writes (strategy D24).

```
┌──────────────────────── make (operator layer) ───────────────────────────┐
│ help · install · doctor · db-init/status/audit · sources-load/list       │
│ setup · probe-dry · probe-single · record · report · report-publish      │
│ probe · census · clobber      ◀── guard-% prerequisite: GO=1 (+ typed    │
│ frame sample acquire ingest        yes on clobber)                       │
│   parse analyze full  ◀── M1–M4 stubs, exit 1                            │
└──────────────┬───────────────────────────────────────────┬───────────────┘
               │ one `leadhs` call per target              │ files
               ▼                                           ▼
┌──────────────────────────────┐        data/report/ (gitignored intermediates)
│ leadhs CLI (click)           │        docs/report/ (published finals)
│ main(): exit-code mapping    │
│ _ensure_initialized gate     │──▶ db.py · store.py · fetch.py ·
│ --db PATH | --data-dir DIR   │    probe/ · report.py · doctor.py
└──────────────────────────────┘                 │
                                                 ▼
                          data/leadhs.sqlite + data/raw/ (gitignored)
```

## Package layout (v0.1.1)

    src/leadhs/
      __init__.py        # version
      cli.py             # click groups: db, source, probe, doctor;
                         # main() exit mapping + _ensure_initialized
                         # preflight (v0.1.2)
      db.py              # connect(), migrate (forward-only + backup),
                         # status, audit (rules R1–R9)
      models.py          # dataclasses (SourceRef, Document, Run,
                         # ProbeFinding, FindingDraft …)
      store.py           # raw store: hash-only filenames, verify,
                         # orphans
      fetch.py           # THE fetch seam: robots, rate limit, UA,
                         # retry/backoff; injectable clock+sleep
      ids.py             # deterministic run_key builder
       metrics.py         # probe-metric constants + seed list
                          # (runtime source of truth; 0001 seeds
                          # pinned to it by a sync test)
      source.py          # register CSV load/list
      probe/
        __init__.py
        engine.py        # per-source run loop, run lifecycle
        adapters.py      # CS / PE / ST adapters + manual recording
      report.py          # probe report rendering (md/csv/json)
      doctor.py          # environment preflight
      dict/
        sources.csv      # source register seed (mirrors
                         # 10_STRATEGY/DATA_SOURCE.md register)
        substances.csv   # M1 dictionary seed (schema designed now)
      migrations/
        0001__probe_base.sql
        0002__probe_core.sql
    tests/
    pyproject.toml       # console script: leadhs = leadhs.cli:main

Growth notes: `cli.py` may split into a `cli/` package at M2 when the
command count grows; `adapters.py` may become a package when adapter
count grows. Split on pain, not before (minimal-diff preference).

## Module contracts (details in interfaces.md)

- **db.py** — `connect(path, readonly=False)` applies pragmas;
  `migrate(conn)` applies pending migrations in one transaction each,
  after taking a timestamped backup of an existing DB; `status(conn)`;
  `audit(conn, store)` implements rules R1–R9.
- **store.py** — `put(source_id, data: bytes, ext) -> (hash, relpath)`:
  filename is `<sha256>.<ext>` ONLY; the source directory name is the
  allowlisted source_id lowercased (`^[a-z]{2}-[0-9]+$` after
  lowering); `get(hash)`, `verify(hash)`, `orphans()` for
  `db audit --unreferenced`.
- **fetch.py** — the single network seam: `Fetcher(config)` with an
  injectable clock and sleeper (deterministic tests); robots.txt
  checked per domain (cached); ≥ 2 s between requests per domain;
  UA `leadhs/<version> (+<contact>)` (contact via `LEADHS_CONTACT`
  env or flag — doctor warns when unset); 2 retries with exponential
  backoff; `RobotsDisallowed`, `Blocked` (403/paywall) and
  `RateLimited` (429 — one capped backoff, then Blocked) raised as
  typed errors.
- **ids.py** — `run_key(kind, date, slug, attempt)`:
  `<kind>-<YYYYMMDD>-<slug>`; probe slug = source id lowercased
  without the dash (`CS-1` → `probe-20260910-cs1`); collisions append
  `-2`, `-3`.
- **metrics.py** — `METRIC_*` constants + `PROBE_METRIC_SEEDS`;
  runtime validation uses this list; a sync test asserts migration
  0001's seeds match it exactly.
- **probe/engine.py** — `run_one(source, mode, sample_n, dry_run)`:
  creates the run row, resolves the adapter, collects documents +
  finding drafts, writes them, sets run status; `--all` loops over
  active sources — **one run per source**; a per-source failure never
  aborts the loop; Ctrl-C marks the current run `aborted` (inserted
  findings persist) and stops.
- **probe/adapters.py** — adapter registry keyed by source class;
  the Python contract is in interfaces.md. The contract is considered
  defined only once all three initial adapters (CS export check, PE
  census, ST SPIN check) run against it.
- **report.py** — renders the probe report from views (md default;
  csv/json via `--format`).
- **doctor.py** — checks: Python version, sqlite3, optional binaries
  (mdbtools, pdftotext, pandoc — warnings, not errors), data dir
  writability, contact configured, optional network reachability of
  seeded sources (`--net`).

## Probe workflows per source class (v0.1.1)

- **CS-1 swiss-impex** (format_check + census): attempt a small
  export/query (HS 3208, one year, one partner); record format,
  granularity, coverage_years, export_rows, free_access; archive the
  export file as a document. Comext (CS-2) already verified — light
  re-check only.
- **PE-1..4** (census): robots/terms/rate_limit/languages findings;
  enumerate catalog categories (category_list); catalog_count and
  category_count where exposed; sample N products (default 5) →
  page_sample_ok, sds_sample_ok; sample pages raw-archived as
  documents.
- **ST-2 SPIN** (format_check): download availability, mdbtools
  presence, small extraction attempt; extraction_path finding; the
  downloaded DB file is hashed and archived as a document.
- **ST-1 PCN** (access_check): manual-web findings recorded via
  `leadhs probe record` (method=manual), like any probe finding.
- **LG**: not probed (Strategy — legal-text verification is a manual
  document workstream; register rows stay inactive and never reach
  reports — MASTER D27).

All classes: blocked/robots_denied → findings with a manual-fallback
note; never hammering (10_STRATEGY/DATA_SOURCE.md discipline).

## Failure behavior & resumability

- One run per source; interrupt → run `aborted`, findings persist;
  re-run = a NEW run (append-only); "current" census =
  v_probe_latest (latest run per source × metric).
- Per-domain backoff and retry in fetch.py; sustained failure →
  blocked finding + continue.
- Stale-run reclaim: a run left `running` by a hard crash (SIGKILL/
  power loss) is marked `failed` with note `stale run reclaimed` by
  the next `db init` / `probe run` / `db status`; the census is
  unaffected (v_probe_latest reads done runs only).
- Nothing swallowed silently: every rescue writes a finding or a
  run.notes line and a log line (CEO review rule).

## Observability (no-server translation)

- `--verbose`: structured log lines (timestamp, module, event, url,
  status, ms) on every fetch and DB write.
- The `run` table is the operation audit trail; `db status` (migrations
  applied/pending, row counts) and `db audit` (provenance health) are
  the day-1 operational surface.
- Reconstruction test: three weeks after a bug report, logs + run +
  document rows alone must explain what happened.

## Report & export tooling (design-ahead; M3/M4)

- **analyze/report (M3/M4):** jinja2 → Markdown, PDF via pandoc when
  available; every figure from the DB, cited with run ID + seed
  (Strategy D18); analytical views computed in code.
- **db export (M4, designed now):** frozen snapshot (SQLite backup
  API / VACUUM INTO), generated schema doc + data dictionary, CSV
  dumps per table, and a MANIFEST.sha256 over the snapshot + raw
  files (cross-checked against document.raw_hash). This is the
  "reusable evidence database" deliverable made concrete.
- **per-product evidence dossier (M4):** rendered from
  v_product_dossier as a report annex.
- **db query (M4):** read-only, SELECT-only, parameterized ad-hoc
  queries for downstream consumers.

## Diagrams (design-adopted from the CEO review)

### System components (v0.1.1)

```
┌──────────────────────────────────────────────────────────────────┐
│  leadhs CLI (click)                                              │
│  db init|status|audit   source load|list   probe run|record|     │
│  report   doctor         (acquire/ingest/parse/… stubbed → M1+)  │
└───────┬──────────────────────────────────────────────────────────┘
        │  one connection per command (WAL, foreign_keys=ON)
        ▼
┌───────────────┐   ┌──────────────────┐   ┌───────────────────────┐
│ db.py         │   │ fetch.py         │   │ store.py (raw store)  │
│ migrations    │   │ robots+rate-limit│   │ data/raw/<source-id>/ │
│ audit R1–R9   │   │ UA+retry/backoff │   │   <sha256>.<ext>      │
└───────┬───────┘   └───────┬──────────┘   └───────────┬───────────┘
        │                   │                          │
        ▼                   ▼                          ▼
┌──────────────────────────────────────────────────────────────────┐
│ probe/ engine.py + adapters.py                                   │
│   CS: swiss-impex export/granularity check                       │
│   PE: catalog census (counts, robots, terms, languages, SDS)     │
│   ST: SPIN mdbtools extraction check | PCN manual-web            │
└──────────────────────────────────────────────────────────────────┘
        │  emits documents (raw-archived) + probe_finding rows
        ▼
┌──────────────────────────────────────────────────────────────────┐
│ SQLite leadhs.sqlite — probe-era subset (0001–0002)              │
│ schema_version │ source │ document │ run │ probe_run │           │
│ probe_finding  │ 10 lookups          │ views: v_probe_latest,    │
│ v_anchor_candidates, v_source_activity                             │
└──────────────────────────────────────────────────────────────────┘
```

### Probe data flow — happy, empty, error paths

```
             ┌───────────────────────────┐
             │ probe run --source PE-1   │
             └────────────┬──────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │ load source + robots/terms/rate   │
         └──────┬────────────┬─────────────┘
     happy      │              │ error
       ▼        ▼              ▼
   enumerate  robots deny   fetch fail
   categories   │            (retry 2x,
       │        ▼             backoff;
       ▼     finding         429: one capped
   fetch pages (robots_     backoff first)
   ≤1 req/2s  denied,         ▼
       │      manual);      finding(access_
       │      run=blocked,  blocked, manual)
       │      exit 2          │
       │                      ▼
       │                  run=blocked,
       │                  exit 2 (findings
       │                  collected before
       │                  → run=done+notes)
       ▼
   document (raw) + findings (catalog_count,
   category_count, sds_sample_ok, languages,
   terms, rate_limit)
       ▼
   run → done
   empty path: no active sources → "no sources", exit 0
```

### Run state machine

```
planned ──► running ──► done
                │  ▲
            error │  │ re-run (NEW run id; old findings stay)
                ▼  │
             failed/blocked/aborted
   blocked: manual fallback recorded as finding
   aborted: interrupt; inserted findings persist
   stale running (SIGKILL/power loss) → failed
   ("stale run reclaimed") on next db/probe command
```

## Repository layout (target, beyond the package)

    Makefile               # operator entrypoint (v0.1.2)
    data/raw/              # gitignored raw store
    data/leadhs.sqlite     # gitignored database
    data/report/           # gitignored report intermediates
    docs/report/           # published final reports only (committed)
    tests/                 # pytest (see testing.md)
    docs/plan/3SM/         # planning (this tree)

## Testing

Test strategy, matrix and key tests: testing.md.

## DECISIONS (design-level; consolidated in 20_DESIGN/MASTER.md)

- a1: single fetch seam (fetch.py) — all network through one module
  (discipline + testability).
- a2: one probe run per source (partial-failure visibility).
- a3: adapters keyed by source class; three initial adapters define
  the contract.
- a4: injectable clock/sleeper in fetch.py (deterministic
  rate-limit tests).
- a5: hash-only raw filenames + source-id allowlist (security).
- a6: deterministic human-readable run_key IDs.
- a7: cli.py stays one module until M2 pain; adapters.py likewise.
- a8: backup-before-migration, default on for existing DBs.
- a9: report/export/query surfaces designed now, built M4 (CEO
  review).
- a10: doctor/status/audit are the operational surface — no-server
  observability.
- a11: stale-run reclaim — hard-crash `running` rows are marked
  failed with a `stale run reclaimed` note by the next db/probe
  command (ENG review 2026-09-11).
- a12: make is the operator entrypoint — thin wrapper, `guard-%`
  GO=1 prerequisite (census guard precedes setup), params as make
  vars until M1 (v0.1.2; strategy D21).
- a13: report routing implemented — `data/report/` intermediates,
  `report-publish` copies to `docs/report/` (v0.1.2; strategy D22).

## OPEN ITEMS

- swiss-impex export mechanics (URL parameters, CSV layout) — the
  probe answers this; CS adapter details follow.
- mdbtools availability/version on Slackware — doctor + probe.
- pandoc/PDF route, chart rendering — M3/M4 (inherited).
- acquire queue design (persistent per-domain queue vs in-run state)
  — M2 design.
- sample-page selection strategy (first-N vs seeded random) — decide
  at implementation; seeded random preferred for reproducibility.
- Wheel release mechanics (tag → wheel → GitHub release asset;
  install smoke on Linux/macOS/Windows) — first external use; v0.1.2
  verifies the wheel builds only (units/v0.1.2.md).

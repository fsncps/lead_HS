---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE01 — Scaffold

Status: done (implemented + gate verified 2026-09-11) · Depends on: — · Governs build order: first.

## Objective

A installable Python package skeleton with every module in place
(stubbed), the metric vocabulary, deterministic run IDs, typed
errors, the shared logging helper, and the CLI frame with global
flags and the exit-code convention. No behavior beyond `--help` and
imports.

## Governing references

- `../../20_DESIGN/MASTER/architecture.md` — §Stack, §Package layout,
  §Module contracts (entrypoint, modules, growth notes).
- `../../20_DESIGN/MASTER/interfaces.md` — §CLI surface, §Command
  contracts, §Global flags, §Exit-code convention, §probe_metric
  vocabulary (the 17 metrics — authoritative table).
- ENG review 2026-09-11 decision A2 (logutil.py).

## Steps

1. **`pyproject.toml`** — project `leadhs`; `requires-python >= 3.11`;
   dependencies: `click`, `requests`, `beautifulsoup4`, `jinja2`
   (pypdf/matplotlib are NOT dependencies — M2/M3). Console script
   `leadhs = leadhs.cli:main`. pytest config: `testpaths = tests`,
   markers `net`, `mdbtools`.
2. **Package skeleton** under `src/leadhs/` exactly per
   architecture.md §Package layout, plus `logutil.py` (A2):
   `__init__.py` (version), `cli.py`, `db.py`, `models.py`,
   `store.py`, `fetch.py`, `ids.py`, `metrics.py`, `logutil.py`,
   `source.py`, `report.py`, `doctor.py`, `probe/__init__.py`,
   `probe/engine.py`, `probe/adapters.py`; empty `dict/` (filled
   PHASE04) and `migrations/` (filled PHASE02). Stubs raise
   `NotImplementedError` — commands print "not implemented in this
   phase" and exit 1 until their phase lands.
3. **`metrics.py`** — `METRIC_*` constants + `PROBE_METRIC_SEEDS`
   for exactly the 17 codes of the interfaces.md vocabulary table
   (catalog_count … free_access), each with label and value_type
   ('numeric'|'text'). Runtime validation uses this list; migration
   0001 seeds are pinned to it by a sync test (PHASE07).
4. **`ids.py`** — `run_key(kind, date, slug, attempt)`:
   `<kind>-<YYYYMMDD>-<slug>`; probe slug = source id lowercased,
   dash stripped (`CS-1` → `probe-20260910-cs1`); same-day re-runs
   append `-2`, `-3` (caller supplies attempt or queries the DB).
5. **Typed errors** — in `fetch.py`: `RobotsDisallowed`, `Blocked`
   (403/paywall), `RateLimited` (429), `ProbeNetworkError` (wraps
   `requests.RequestException` after retries); in
   `probe/adapters.py`: `UnexpectedFormat`, `BinaryMissing`,
   `ExtractionError`, `ParseError`. No blanket excepts anywhere.
6. **`logutil.py`** — single `log_event(logger, module, event, **fields)`
   helper emitting one structured line: timestamp, module, event,
   then fields (url, status, ms, source, run …). All modules log
   through it — never bare `print`/hand-rolled formats (A2;
   architecture.md §Observability, interfaces.md §Error surfaces).
7. **`cli.py`** — click groups `db`, `source`, `probe`, `doctor`;
   global options `--verbose`, `--db PATH` (default
   `data/leadhs.sqlite`), `--contact` / env `LEADHS_CONTACT`. Wire the
   exit-code convention 0/1/2/3 (130 on KeyboardInterrupt) into the
   main entry now, so later phases only raise typed errors.

## Deliverables

Installable package; all modules present (stubs); metrics list; ids;
typed errors; logging helper; CLI frame.

## Exit gate

- `pip install -e .` succeeds; `leadhs --help`, `leadhs db --help`,
  `leadhs probe --help` exit 0.
- `python -c "from leadhs.metrics import PROBE_METRIC_SEEDS"` —
  exactly 17 codes, codes/labels/value_types match interfaces.md.
- `run_key("probe", date(2026,9,10), "cs1", 1)` ==
  `"probe-20260910-cs1"`; attempt 2 appends `-2` (quick unit test).
- `log_event` renders one line with timestamp+module+event+fields
  (quick unit test).

## Open items resolved here

None new; carries A2 (logutil.py) into the layout.

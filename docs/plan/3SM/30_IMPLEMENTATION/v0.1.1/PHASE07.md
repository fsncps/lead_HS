---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE07 — Test suite

Status: done (implemented + gate verified 2026-09-11) · Depends on: PHASE01–06 · Governs: the confidence
layer.

## Objective

The full test matrix of `../../20_DESIGN/MASTER/testing.md` — every
matrix item, every exception-table row, hostile-QA and chaos cases —
deterministic and green offline.

## Governing references

- `../../20_DESIGN/MASTER/testing.md` — the whole document is the
  contract: matrix, key test files (incl. test_adapters_contract.py
  added 2026-09-11), hostile-QA cases, chaos test, flakiness rules,
  t1–t6.
- `../../20_DESIGN/MASTER/interfaces.md` — §exception mapping table
  (the coverage checklist, t4), §db audit rules R1–R9.

## Steps

1. **Fixtures** (`tests/fixtures/`): local `http.server` fixture site
   (thread, ephemeral port): catalog HTML with categories + product
   pages + SDS links, `robots.txt` (allow), a robots-disallow
   variant, a 403 endpoint, a 429 endpoint (then success on retry —
   for the RateLimited path), a PDF; fixture register CSV; fixture
   swiss-impex-style export CSV (good + wrong-layout); SPIN fixture
   (small .mdb or pre-extracted CSV — resolve per testing.md open
   item, gated on mdbtools marker); huge-HTML and non-UTF-8 fixtures
   for hostile cases.
2. **Test files** per testing.md §Key test files — nothing skipped:
   test_migrations (idempotency, order, CHECKs, **backup round-trip,
   metrics sync 0001 == metrics.py**), test_store (hash-only,
   traversal reject, orphans, verify), test_fetch (spacing, robots,
   403/Blocked, **429/RateLimited capped backoff + persistent**,
   retry→ProbeNetworkError, **dry-run zero network**),
   test_adapters_pe / test_adapters_cs (UnexpectedFormat → format
   finding + WARNING) / test_adapters_st (mdbtools-gated),
   **test_adapters_contract (query_only connection; adapters
   draft-only — A3)**, test_engine (per-source runs, loop-survives-
   failure, abort/resume, re-run `-2`, exit codes, **stale-run
   reclaim**), test_views (**newer done run wins; aborted/blocked
   don't shadow**; anchor candidates; source activity),
   test_report_golden (md/csv/json golden files; regenerate on
   intentional change with review), test_cli_smoke (init → load →
   probe run → report → audit exit 0 — the 2am-Friday test),
   test_audit (R2/R4 violations detected; planted orphan;
   clean corpus exit 0), test_doctor (fake binaries on PATH, missing
   contact warning, unwritable data dir error).
3. **Chaos test** — kill a probe run mid-source (simulated
   interrupt): run `aborted`, findings persisted, re-run idempotent,
   `db audit` clean, **v_probe_latest unchanged by the aborted run**.
4. **Hostile QA** — traversal source IDs/URLs; malformed register
   CSV (bad class, missing URL, duplicate id — loud exit 1); empty
   register; huge HTML; non-UTF-8 bytes (raw store keeps bytes;
   parse degrades to page_sample_ok=0); robots 404/empty = allow;
   duplicate findings on re-probe (new-run semantics, no mutation).
5. **Markers & flakiness rules** — `@pytest.mark.net` /
   `@pytest.mark.mdbtools` deselected by default; no real sleeps
   (injected clock); order-independent; each test builds its own
   tmp_path / in-memory state.

## Deliverables

The complete `tests/` tree + fixtures; golden files.

## Exit gate

- `pytest` green offline (markers deselected) — full matrix, every
  exception-table row ≥ 1 test.
- `pytest -m net` optional against the fixture site is not needed
  (fixture site is local) — net marker is for real-source checks,
  kept deselected.
- 2am-Friday: test_cli_smoke green + test_audit clean on the fixture
  corpus in one command.
- Chaos + hostile lists fully covered.

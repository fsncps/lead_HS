---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE05 — Probe engine & adapters

Status: done (implemented + gate verified 2026-09-11) · Depends on: PHASE02, PHASE03, PHASE04 · Governs:
the unit's core.

> **Implementation decisions recorded (2026-09-11):**
> - **CS-1 dual mode** — resolved to a single census run that records
>   format/granularity/coverage/export_rows/free_access findings; a
>   wrong export layout degrades via `UnexpectedFormat` to a format
>   finding + WARNING note (tested against the fixture export).
> - **PE sample-page selection** — seeded random,
>   `random.Random("pe-sample-<source_id>")` shuffled then first-N;
>   reproducible per source.
> - **`sample_n`/`mode` home** — `mode` lives in the typed
>   `probe_run.mode_code` only; `parameters_json` carries
>   `{"sample_n", "dry_run", "contact_set"}` (no duplication).
>   `probe record` fixes mode_code='census' (method=manual marks the
>   observation itself).
> - **Partial-result preservation** — typed adapter errors carry a
>   `partial` ProbeResult; findings/documents collected before a block
>   persist and flip the outcome to done+notes per the rule.

## Objective

The probe engine with outcome-based run semantics and the three
class adapters, plus `probe record` for manual-web findings — the
single-write-path heart of the unit.

## Governing references

- `../../20_DESIGN/MASTER/architecture.md` — §Module contracts
  (engine, adapters), §Probe workflows per source class, §Failure
  behavior & resumability.
- `../../20_DESIGN/MASTER/interfaces.md` — §Adapter contract
  (Protocol, ProbeContext/ProbeResult, exception mapping table),
  §Run semantics (outcome rule, abort/resume, stale-run reclaim,
  pacing, parameters_json), §probe CLI contracts.
- `../../20_DESIGN/MASTER/data_model.md` — §probe-era tables/views.
- `../../20_DESIGN/units/v0.1.1.md` — §Probe workflows per source
  class, §Anchor promotion context.

## Steps

1. **`probe/engine.py`** — `run_one(source, mode, sample_n,
   dry_run)`:
   - Create the run row (status `planned` → `running`), run_key per
     ids.py (same-day re-run → `-2` suffix).
   - Resolve adapter by source class; **engine owns ALL DB writes**
     — documents and findings are inserted from adapter-returned
     drafts only (i3; enforced by test in PHASE07).
   - Final status per the **outcome rule** (i9): reachable with
     findings → `done`; wholly inaccessible (robots deny / 403 /
     persistent 429 / paywall) → `blocked`; unrecoverable network →
     `failed`; findings collected before a block → `done` + notes.
   - KeyboardInterrupt → run `aborted` (inserted findings persist),
     exit 130.
   - `--all`: loop **active AND adapter-backed** sources (A1: ST-1
     active=0 — never selected; no engine skip rule); one run per
     source; a failing source never aborts the loop; stale-run
     reclaim pass at loop start; exit 2 if any run ended
     blocked/failed; multi-minute pacing note + `--verbose` progress.
   - parameters_json: `{"mode","sample_n","dry_run","contact_set"}`.
   - Exception mapping exactly per the interfaces.md table; every
     rescue logs a context-complete line via `log_event`.
2. **`probe/adapters.py`** — registry keyed by source class
   (`supports(source)`); adapters use `ctx.fetcher` /
   `ctx.fetcher.plan` (dry-run) and never the DB:
   - **CS adapter** (CS-1 swiss-impex; CS-2 light re-check): attempt
     a small test export/query (HS 3208, one year, one partner);
     findings: format, granularity, coverage_years, export_rows,
     free_access; the export file is archived as a document (via the
     engine). Export mechanics are unknown a priori — layout surprise
     → `UnexpectedFormat` → format finding (value_text) + WARNING
     note for manual review. **Resolve here:** single census-mode run
     recording format findings (preferred — all evidence is metric
     findings) vs separate format_check run; record the decision in
     the run's parameters_json and this file's status note.
   - **PE adapter** (PE-1..4, census): robots/terms/rate_limit/
     languages findings; enumerate catalog categories → category_list
     (JSON), catalog_count, category_count where exposed; sample N=5
     products (**seeded random selection — finalize here**, open
     item) → page_sample_ok, sds_sample_ok; sample pages raw-archived
     as documents. Blocked/robots_denied → findings + manual-fallback
     note; never hammering.
   - **ST adapter** (ST-2 SPIN, format_check): download availability;
     mdbtools presence; small extraction attempt → extraction_path
     finding; the downloaded Access-DB file hashed + archived as a
     document; `BinaryMissing`/`ExtractionError` → extraction_path
     (blocked/failed) notes.
3. **`probe record`** — manual run (kind=probe, method=manual) + one
   finding: `--source ID --metric M [--value X | --value-text T]
   [--unit U] [--url URL] [--document FILE] [--note TEXT]`; validates
   metric against vocabulary + value_type (bad → exit 1); attached
   file → store.put + document row. This is ST-1 PCN's entry path
   (and any manual fallback finding).
4. **CLI wiring** — `leadhs probe run --source ID | --all [--mode
   census|format_check|access_check] [--sample N] [--dry-run]`;
   `leadhs probe record …`.

## Deliverables

engine.py, adapters.py (3 adapters), `probe run`/`probe record` live.

## Exit gate

- Fixture-site runs hit all outcome paths: happy → `done` exit 0;
  robots deny → `blocked` exit 2 (robots_denied finding); 403 →
  `blocked`; persistent 429 → `blocked`; network failure → `failed`
  exit 2; partial collection then block → `done` + notes.
- `--all` on a mixed register: one run per source; a failing source
  doesn't stop the loop; exit code aggregates (0 all done / 2 any
  blocked-failed); empty register → "no sources", exit 0.
- Interrupt mid-source → `aborted`, findings persisted, exit 130.
- Re-run same source same day → new run (`-2` key suffix); old
  findings untouched; v_probe_latest reflects the latest **done** run.
- `--dry-run` → zero network calls (socket guard), planned requests
  logged via plan().
- Adapters complete draft-only (the query_only test lands in PHASE07
  but the seam — engine-only writes — is in place here).

## Open items resolved here

- CS-1 dual-mode question (single census run vs two runs).
- PE sample-page selection strategy (seeded random).
- `sample_n`/`mode` duplicate home: parameters_json vs
  probe_run.mode_code — pick one (typed column preferred; parameters
  then hold only what has no column).

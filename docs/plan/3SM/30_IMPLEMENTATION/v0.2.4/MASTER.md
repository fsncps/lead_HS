---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# Unit v0.2.4 — Implementation plan: management CSV sample (`leadhs probe download-csv-sample`)

> **Drafted 2026-09-14.** Executable phase plan for the D36
> management-CSV-sample unit (strategy `../../10_STRATEGY/v0.2.4.md`;
> design `../../20_DESIGN/units/v0.2.4.md` — CEO + ENG review same
> day, HOLD SCOPE, decision 1A + amendments folded). Four
> self-contained PHASE files in the house format. The unit rides the
> existing probe machinery end-to-end (fetcher, raw store, run/findings
> write path, ids, logutil) — the only migration is 0009, a
> lookup-seed INSERT (no new tables); no engine or adapter changes;
> no staging writes. PHASE02/03 touch the real network only via
> `GO=1 make sample-csv` (official exports, recon-only, D31/D3);
> every phase's build is offline.

## Abstract

The executable phase plan for unit v0.2.4. One new probe command
(`leadhs probe download-csv-sample`) draws, per registry, 100 random
in-scope product items with all available data fields as CSV for
management review, plus a generated manifest (md+csv) answering per
registry: what fields are returned per product item, whether
cross-identification is possible, which identifier columns exist —
and, for the four registers that publish no product rows, an honest
reason with citation. The manifest is ALWAYS written (review 1A);
exit 0 = delivered or expected-unavailable, 2 = should-deliver
failure, 1 = usage (i1).

## Scope

`src/leadhs/probe/csv_sample.py` (per-source handlers, seeded draw,
CSV writers, manifest renderer) + CLI wiring under the probe group +
migration 0009 (probe_mode `csv_sample`, metrics `csv_sample_rows`/
`csv_sample_unavailable`) + metrics.py seeds + Makefile target
`sample-csv` (guard; the M1 `sample` stub untouched) + full offline
test set + docs (ARCHITECTURE/DATA_SOURCE lines already landed at
the strategy turn). Product data only (D27); recon-only (D31).

## Phase tracking

| # | Focus | Depends on | Exit gate (summary) | Status |
|---|---|---|---|---|
| 01 | Migration 0009 (lookup seeds) + metrics.py constants + sync updates (t6 count 41, fresh-apply {1..9}) | — | 0009 applies, idempotent; sync green | **done 2026-09-14** (backup-round-trip fake bumped to 0010) |
| 02 | `probe/csv_sample.py` (ECAT handler, ST no-fetch records, seeded draw, CSV writers, manifest renderer, exit codes) + CLI wiring + tests | 01 | sample command offline-green on fixture exports; manifest/exit-code conformance | **done 2026-09-14** (15 csv-sample tests; canonical pool order for cross-machine reproducibility) |
| 03 | AS-3 bounded discovery handler + tests | 02 | HTML surface → honest unavailable, ≤5 GETs; CSV response → ECAT path | **done 2026-09-14** (budget-spent reason carries the canonical browser-pass text + last probe context) |
| 04 | Makefile `sample-csv` + makefile test + full suite + audit + docs close-out | 02 | suite green; audit clean; docs current | **done 2026-09-14** (364 offline tests; version 0.2.4; guard/dry/exit-2-tolerance verified) |
| 05 | Addendum (D37): migration 0010 + `probe/as_probe.py` + CLI `as-source-probe` + Makefile `as-probe` + tests + split guard | 04 | offline suite green incl. 18 as-probe tests; register split guard holds | **done 2026-09-14** (ENG-review SMALL CHANGE, 1A/2A/3A folded; 385 offline tests) |
| 06 | Addendum (D37): dry-run + real run + publish + docs close-out | 05 | folder populated; summary published; docs current | **done 2026-09-14** (run 20260914-125322, all 30 AS sources, exit 0; summary published in `docs/report/`) |

Statuses: all four phases **done 2026-09-14** (364 offline tests
green, 2 net-deselected; `db audit` exit 0 on the CLI end-to-end
flow; version 0.2.4). The real-network run executed same day
(`GO=1 make sample-csv`, 11:19 UTC): AS-2 delivered 100 of 17,013
distinct (header re-pinned, matches v0.2.3 staging); **AS-3
delivered trial-grade** — the `?format=csv` discovery found a real
9.8 MB export, 14 distinct items drawn, quality caveats flagged in
the manifest; ST-1/3/6/7 honest no-fetch records; exit 0.
Report: `docs/report/report-0.2.4.md`. The addendum (D37) executed
the same day (`GO=1 make as-probe`, run 20260914-125322, exit 0):
all 30 AS-class sources carry one finding each — delivered 2
(AS-2/AS-3 reuse), estimated 2 (AS-4 ≈70k, AS-7 ≈2k), unavailable 5
(AS-5/6/8/9/10, why-not + what-is-instead), associations 18 live +
3 unreachable; summary published (`docs/report/
as-source-probe.summary.20260914-125322.{md,csv}`).

## Acceptance criteria

From `../../20_DESIGN/units/v0.2.4.md` — per-source state machine
(delivered/unavailable/failed) with the manifest always written; ECAT
CSV: all export columns verbatim + the 6 provenance columns
(source_id, run_key, retrieval_date, doc_hash, sample_seed,
sample_index); seeded reproducible draw from DISTINCT product items
with clamping + shortfall note; the four no-fetch records cite the
verified findings (URL + access date); AS-3 bounded discovery with
named-exception catches; run rows carry mode `csv_sample` and the
`run.seed` column; findings land via the engine's single write path;
exit codes 0/1/2 per i1; full offline suite green; `db audit` exit 0;
docs per convention.

## Open items carried into build

From the design doc (OPEN ITEMS) — each phase resolves or
dispositions its own:

- Nordic Swan export mechanics — PHASE03 bounds the attempt and
  records an honest failure; the browser pass stays the fallback;
  reconciliation TODO added to TODOS.md.
- Exact public ECAT export header — re-pinned by the first real
  `GO=1 make sample-csv` run; the full column list lands in the
  manifest (not a phase gate).

## Handoff note

These files were drafted 2026-09-14 and follow the CEO + ENG reviews
of the same day (both HOLD SCOPE; decision 1A + the amendment list in
the design doc's Review outcomes section). Writing these files
implies no freeze, stage advancement, or execution start. Commit/push
and any stage advancement await explicit user instruction (3SM
process).

---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE08 — Census run (execution, not code)

Status: **transferred to unit v0.1.2** (strategy D26, 2026-09-11) —
the feasibility pass below was executed 2026-09-11 and is the
empirical record; the census close-out (gap completion, structured
report, register updates) is `../v0.1.2/PHASE07.md`, executed through
the operator layer. · Original dependencies: PHASE01–07 + explicit
go-ahead.

## Objective

Run the real source census with the built tool against the register —
the Strategy deliverable of unit v0.1.1: verified access metadata,
provisional frame inputs, blocked sources documented. **No new code:
surprises are findings and notes, not patches** (a design conflict
goes back to DESIGN per 3SM regression rules).

## Preconditions

- PHASE01–07 exit gates green (suite green offline).
- `leadhs doctor --net` — mdbtools presence (ST-2), contact set,
   data dir, reachability. Fix blockers first.
- **Explicit user go-ahead** — this phase hits the real network
  (polite, multi-minute: ≥ 2 s spacing per domain; `--verbose`
  progress; re-runs incremental).

## Governing references

- `../../10_STRATEGY/v0.1.1.md` — §Scope (deliverable 3/4),
  §OPEN ITEMS (the questions this run answers).
- `../../10_STRATEGY/DATA_SOURCE.md` — §Probing pass (per-class
  plan), §Access & scraping discipline (binding).
- `../../20_DESIGN/units/v0.1.1.md` — §Probe workflows per source
  class, §Acceptance criteria.
- `../../20_DESIGN/MASTER/interfaces.md` — §Run semantics (pacing,
  outcome rule).

## Steps

1. `leadhs db init` (fresh DB or upgrade; backup default on) →
   `leadhs source load`.
2. **Dry pass first:** `leadhs probe run --all --dry-run` — planned
   requests logged, zero network; sanity-check the source selection
   (7 active adapter-backed rows; ST-1/LG/LI/ST-3 excluded per A1).
3. **Real pass:** `leadhs probe run --all` (census mode; sample N=5).
   Per-source runs; blocked/failed sources re-run individually after
   inspection if transient (new runs, append-only; v_probe_latest
   takes the latest done run). swiss-impex (CS-1) export mechanics
   answered here as format/granularity/coverage/export_rows/free_access
   findings — closes the Strategy's high-priority open item.
4. **Manual-web work (ST-1 PCN):** locate formulation-level
   aggregates on the ECHA PCN statistics pages by hand; record via
   `leadhs probe record --source ST-1 --metric … --value-text …
   --url … --note …` (method=manual; attach page as `--document`
   where useful). Blocked automated sites: document the manual
   fallback rule (DATA_SOURCE.md D4) as findings/notes.
5. **Deliver the report:** `leadhs probe report --format md --out
   docs/report/` (+ csv/json); review v_anchor_candidates output —
   the provisional frame inputs (promotion to population_anchor is a
   manual M1 method decision, not part of this unit).
6. **Update the register of record:** DATA_SOURCE.md §Source register
   Status column from the probe findings (open → verified /
   partially_verified / blocked+manual); new PE seed sites discovered
   during probing enter as CSV rows + `source load` (i2).
7. `leadhs db audit` — must exit 0 on the real corpus.

## Deliverables

- Census findings in the DB for every OPEN register row (probed or
  explicitly manual).
- Blocked sources documented with manual-fallback notes.
- `docs/report/` probe report (md + csv/json) — the unit's Strategy
  deliverable.
- Updated DATA_SOURCE.md register + sources.csv.
- swiss-impex format/granularity answer; SPIN extraction-path answer
  (or blocked note); PCN aggregates located/recorded if published.

## Exit gate (unit acceptance, from the design unit file)

- Every OPEN register row probed or explicitly manual (PCN).
- Findings recorded; blocked sources documented.
- `probe report` delivered; `db audit` exit 0.
- Unit v0.1.1's empirical questions answered or documented-blocked:
  swiss-impex export mechanics, PE candidate-site enumeration,
  SPIN mdbtools path, PCN aggregates.

## Post-run (flagged, not executed here)

Unit completion/COMPLETE marking, planning archival, LOG entry,
commit/push — all await explicit user instruction per 3SM process.

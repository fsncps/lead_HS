---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE06 — Probe reporting

Status: done (implemented + gate verified 2026-09-11) · Depends on: PHASE05 · Governs: the census readout.

## Objective

`leadhs probe report` — the census summary rendered from the
database views only, in md (default), csv and json.

## Governing references

- `../../20_DESIGN/MASTER/interfaces.md` — §Command contracts
  (`probe report`), P7 (user-facing counts from the DB only).
- `../../20_DESIGN/MASTER/data_model.md` — §Probe-era views
  (v_probe_latest done-filtered, v_anchor_candidates,
  v_source_activity).
- `../../20_DESIGN/MASTER/architecture.md` — §Module contracts
  (report.py), §Observability.

## Steps

1. **`report.py`** — render the census from `v_probe_latest` (all
   sources or `--source ID`): per source — access findings (robots,
   terms, rate_limit, languages), count findings (catalog_count,
   category_count, export_rows), sample results (page_sample_ok,
   sds_sample_ok), format/granularity/coverage findings; blocked
   notes; then the **anchor candidates** section from
   v_anchor_candidates (catalog_count, category_count, export_rows)
   flagged as provisional (promotion is a manual M1 method decision —
   never automatic).
2. **Formats** — md default (jinja2 template); `--format csv`
   (per-finding rows: source, metric, value, unit, method, run_key,
   retrieved_at); `--format json` (same fields, structured). Every
   number carries its run/provenance fields (P7: DB only).
3. **Output location** — stdout by default; `--out` writes to
   `docs/report/` (generated reports; final ones committed per the
   repo layout).
4. **CLI wiring** — `leadhs probe report [--source ID] [--format
   md|csv|json] [--out PATH]`.

## Deliverables

report.py + jinja2 template; `probe report` live.

## Exit gate

- Fixture findings render identically-stable md/csv/json (golden
  files established in PHASE07 from this output).
- A re-run scenario: report reflects the latest **done** run only
  (aborted/blocked runs' findings excluded from the census section).
- Anchor candidates listed with their metric, value, unit, run_key —
  marked provisional.
- No hard-coded numbers anywhere in the output path (P7).

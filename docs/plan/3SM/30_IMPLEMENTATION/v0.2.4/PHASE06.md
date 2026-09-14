---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE06 — Addendum (D37): AS-class source probe (real run + close-out)

## Objective

Run the AS-class source probe against the real network, populate
`data/report/AS-source-probe/`, publish the summary per the publish
policy, and bring the docs current.

## Preconditions

- PHASE05 done (build + offline tests green).

## Steps

1. **Dry-run:** `leadhs probe as-source-probe --dry-run` — request
   plan sane (≤5 GETs per registry, 1 per association), zero files.
2. **Real run:** `GO=1 make as-probe` — ~65 small sequential GETs
   across 30 hosts; obtained CSVs + XLSX renderings + summary land in
   `data/report/AS-source-probe/`; DB runs + findings recorded.
3. **Summary review:** per-source findings sane (statuses, counts
   with provenance, what's-available-instead lines); exit code
   correct; fix offline and re-run only if a should-deliver path
   misbehaves.
4. **Publish:** summary copies (timestamped + latest) into
   `docs/report/` (`data/` is gitignored — the published copies are
   canonical); sample CSVs stay working renders.
5. **Docs close-out:** `report-0.2.4.md` addendum section (per-source
   table); README EN/DE/FR current-stage note; management summary
   DE/FR short paragraph; DATA_SOURCE.md register note;
   `30_IMPLEMENTATION/v0.2.4/MASTER.md` + dashboards (D37);
   strategy/design `updated` stamps; TODOS entry only if the run
   surfaces concrete EPD-API follow-up evidence (3A: evidence first).

## Exit criteria

- Folder populated, summary published, docs current, suite green.

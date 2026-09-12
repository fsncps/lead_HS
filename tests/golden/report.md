# Source feasibility census report

This report answers two study questions: (Q1) how many paint/varnish products each registered source exposes — observed listings, a floor, never a market total — and (Q2) for how many of them SDS-type documentation is reachable. Trade-statistics rows are volume context: tariff-line flows, never products. These remain source-feasibility metrics only: product and lead prevalence are M2+ deliverables and are never implied here. The tool, the database and the reports carry product data only (Strategy MASTER D27): inactive register rows appear in the matrix without findings.

## The two numbers

Per registered source — Q1: observed product listings (a floor, never a
market total); Q2: SDS-type documentation links seen.

| source | class | active | status | products listed (Q1) | doc links seen (Q2) | sds sample | last run |
|---|---|---|---|---|---|---|---|
| CX-1 | CS | 1 | done | — | — | — | probe-20260910-cx1 |
| CX-2 | CS | 1 | — | — | — | — | — |
| CX-3 | CS | 1 | — | — | — | — | — |
| CX-4 | CS | 1 | — | — | — | — | — |
| PX-1 | PE | 1 | done | 6 count | 1 count | 1 count | probe-20260910-px1 |
| PX-2 | PE | 1 | — | — | — | — | — |
| PX-3 | PE | 1 | — | — | — | — | — |
| PX-4 | PE | 1 | — | — | — | — | — |
| PX-5 | PE | 1 | — | — | — | — | — |
| PX-6 | PE | 1 | — | — | — | — | — |
| PX-7 | PE | 1 | — | — | — | — | — |
| PX-8 | PE | 1 | — | — | — | — | — |
| PX-9 | PE | 1 | — | — | — | — | — |
| ST-1 | ST | 0 | — | — | — | — | — |
| SX-1 | ST | 1 | — | — | — | — | — |


## Summary matrix

One row per registered source (active flag included; inactive rows carry no
findings). The records_hs* columns are volume context — tariff-line flows,
not products.

| source | class | active | status | products | doc links | walk budget | catalog | category | page ok | sds ok | hs3208 | hs3209 | hs3213 | export rows | last run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CX-1 | CS | 1 | done | — | — | — | — | — | — | — | — | — | — | 3 count | probe-20260910-cx1 |
| CX-2 | CS | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CX-3 | CS | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CX-4 | CS | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-1 | PE | 1 | done | 6 count | 1 count | 0 | 500 count | 2 count | 2 count | 1 count | — | — | — | — | probe-20260910-px1 |
| PX-2 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-3 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-4 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-5 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-6 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-7 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-8 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-9 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ST-1 | ST | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| SX-1 | ST | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |


## Execution log (latest census run per source)


| source | run_key | status | started | finished | notes |
|---|---|---|---|---|---|
| CX-1 | probe-20260910-cx1 | done | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | — |
| PX-1 | probe-20260910-px1 | done | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | — |



## Sources


### CX-1 — Fixture export

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/export.csv
- access: robots — · terms — · rate limit — · free access 1
- content: format CSV; columns: hs_code, year, partner, value · granularity CN8 x partner x year (observed columns) · coverage to confirm (year column present) · languages —
- counts: export rows 3 count
- register note: good csv
- latest census run: probe-20260910-cx1 (done)

### CX-2 — Fixture bad export

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/export-bad.csv
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: bad layout

### CX-3 — Fixture api

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/api.json
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: json

### CX-4 — Fixture 500

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/error500
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: network fail

### PX-1 — Fixture catalog

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/
- access: robots allowed · terms link present: /terms · rate limit unknown — polite default <= 1 req / 2 s · free access 1
- content: format — · granularity — · coverage — · languages ["de", "fr"]
- counts: catalog 500 count · categories: /cat/wandfarben=2, /cat/grundierung=0 · walk budget: within budget
- register note: census good catalog
- latest census run: probe-20260910-px1 (done)

### PX-2 — Robots-denied

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/private/secret
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: robots deny

### PX-3 — Blocked 403

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/forbidden
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 403

### PX-4 — Persistent 429

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/ratelimited-always
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 429

### PX-5 — 429 once

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/ratelimited-once
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 429-then-ok

### PX-6 — Empty page

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/empty.html
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: parse error

### PX-7 — Huge page

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/huge.html
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: hostile

### PX-8 — Non-utf8

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/non-utf8.html
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: hostile

### PX-9 — Missing page

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/missing
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: 404

### ST-1 — PCN stats

- identity: class ST · active no · verification open · http://127.0.0.1:PORT/missing
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: manual-web via probe record

### SX-1 — Fixture spin

- identity: class ST · active yes · verification open · http://127.0.0.1:PORT/spin
- access: robots — · terms — · rate limit — · free access —
- content: format — · granularity — · coverage — · languages —
- counts:
- register note: mdbtools

## Legend

- “—” = metric absent (source not queried for it); 0 = queried, empty result.
- Metric values cite the run_key of the done run they come from.
- Status reflects the latest census run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.
- products_listed / doc_links_seen are walk floors (BFS depth ≤ 3, page budget ≤ 12 incl. homepage); walk budget: exhausted marks a budget-limited walk — the floor is then a weaker lower bound.
- records_hs* columns are volume context: tariff-line flows, not products (D28 grain rule).

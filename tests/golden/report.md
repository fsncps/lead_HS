# Source feasibility census report

This report documents what each registered source delivers for the census — access, formats, granularity, counts and availability. These are source-feasibility metrics only: product and lead prevalence are M2+ deliverables and are never implied here. The tool, the database and the reports carry product data only (Strategy MASTER D27): inactive register rows appear in the matrix without findings.

## Summary matrix

One row per registered source (active flag included; inactive rows carry no
findings).

| source | class | active | status | format | granularity | coverage | free | export rows | hs3208 | hs3209 | hs3213 | catalog | category | page ok | sds ok | last run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CX-1 | CS | 1 | done | CSV; columns: hs_code, year, partner, value | CN8 x partner x year (observed columns) | to confirm (year column present) | 1 | 3 count | — | — | — | — | — | — | — | probe-20260910-cx1 |
| CX-2 | CS | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CX-3 | CS | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| CX-4 | CS | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-1 | PE | 1 | done | — | — | — | 1 | — | — | — | — | 500 count | 2 count | 2 count | 1 count | probe-20260910-px1 |
| PX-2 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-3 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-4 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-5 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-6 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-7 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-8 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| PX-9 | PE | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| ST-1 | ST | 0 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| SX-1 | ST | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — | — |


## Run status (latest census run per source)


| source | run_key | status | started | finished | docs | findings | notes |
|---|---|---|---|---|---|---|---|
| CX-1 | probe-20260910-cx1 | done | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | 1 | 5 | — |
| PX-1 | probe-20260910-px1 | done | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | 5 | 11 | — |



## Sources


### CX-1 — Fixture export

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/export.csv
- register note: good csv
- latest census run: probe-20260910-cx1 (done)


#### availability

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| free_access | 1 | download | probe-20260910-cx1 | — |

#### content

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| format | CSV; columns: hs_code, year, partner, value | download | probe-20260910-cx1 | — |
| granularity | CN8 x partner x year (observed columns) | download | probe-20260910-cx1 | — |
| coverage_years | to confirm (year column present) | download | probe-20260910-cx1 | — |

#### counts

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| export_rows | 3 count | download | probe-20260910-cx1 | — |


### CX-2 — Fixture bad export

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/export-bad.csv
- register note: bad layout



### CX-3 — Fixture api

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/api.json
- register note: json



### CX-4 — Fixture 500

- identity: class CS · active yes · verification open · http://127.0.0.1:PORT/error500
- register note: network fail



### PX-1 — Fixture catalog

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/
- register note: census good catalog
- latest census run: probe-20260910-px1 (done)


#### access

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| robots | allowed | scrape | probe-20260910-px1 | — |
| terms | link present: /terms | scrape | probe-20260910-px1 | — |
| rate_limit | unknown — polite default <= 1 req / 2 s | scrape | probe-20260910-px1 | — |

#### availability

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| free_access | 1 | scrape | probe-20260910-px1 | — |
| page_sample_ok | 2 count | scrape | probe-20260910-px1 | 2/2 |
| sds_sample_ok | 1 count | scrape | probe-20260910-px1 | 1/2 |

#### content

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| languages | ["de", "fr"] | scrape | probe-20260910-px1 | — |
| category_list | ["http://127.0.0.1:PORT/cat/wandfarben", "http://127.0.0.1:PORT/cat/grundierung", "http://127.0.0.1:PORT/cat/broken"] | scrape | probe-20260910-px1 | — |

#### counts

| metric | value | method | run_key | notes |
|---|---|---|---|---|
| catalog_count | 500 count | scrape | probe-20260910-px1 | — |
| category_count | 2 count | scrape | probe-20260910-px1 | category path: /cat/wandfarben |
| category_count | 0 count | scrape | probe-20260910-px1 | category path: /cat/grundierung |


### PX-2 — Robots-denied

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/private/secret
- register note: robots deny



### PX-3 — Blocked 403

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/forbidden
- register note: 403



### PX-4 — Persistent 429

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/ratelimited-always
- register note: 429



### PX-5 — 429 once

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/ratelimited-once
- register note: 429-then-ok



### PX-6 — Empty page

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/empty.html
- register note: parse error



### PX-7 — Huge page

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/huge.html
- register note: hostile



### PX-8 — Non-utf8

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/non-utf8.html
- register note: hostile



### PX-9 — Missing page

- identity: class PE · active yes · verification open · http://127.0.0.1:PORT/missing
- register note: 404



### ST-1 — PCN stats

- identity: class ST · active no · verification open · http://127.0.0.1:PORT/missing
- register note: manual-web via probe record



### SX-1 — Fixture spin

- identity: class ST · active yes · verification open · http://127.0.0.1:PORT/spin
- register note: mdbtools



## Anchor candidates (provisional — manual promotion, M1 decision)


| source_id | metric | value | run_key |
|---|---|---|---|
| CX-1 | export_rows | 3.0 count | probe-20260910-cx1 |
| PX-1 | catalog_count | 500.0 count | probe-20260910-px1 |
| PX-1 | category_count | 2.0 count | probe-20260910-px1 |
| PX-1 | category_count | 0.0 count | probe-20260910-px1 |



## Source activity

| source_id | first retrieved | last retrieved | runs | findings |
|---|---|---|---|---|
| CX-1 | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | 1 | 5 |
| CX-2 | — | — | 0 | 0 |
| CX-3 | — | — | 0 | 0 |
| CX-4 | — | — | 0 | 0 |
| PX-1 | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | 1 | 11 |
| PX-2 | — | — | 0 | 0 |
| PX-3 | — | — | 0 | 0 |
| PX-4 | — | — | 0 | 0 |
| PX-5 | — | — | 0 | 0 |
| PX-6 | — | — | 0 | 0 |
| PX-7 | — | — | 0 | 0 |
| PX-8 | — | — | 0 | 0 |
| PX-9 | — | — | 0 | 0 |
| ST-1 | — | — | 0 | 0 |
| SX-1 | — | — | 0 | 0 |

> Raw counts — dry-run runs are included here (and only here).


## Legend

- “—” = metric absent (source not queried for it); 0 = queried, empty result.
- Metric values cite the run_key of the done run they come from.
- Status reflects the latest census run per source (dry-run runs excluded); blocked/failed runs are shown with their notes.

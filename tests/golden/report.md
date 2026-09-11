# Probe report — unit v0.1.1

Generated from the database views (v_probe_latest / v_anchor_candidates /
v_source_activity). Counts come from the DB only (P7).

## Census findings (latest done run per source × metric)



### CX-1

| metric | value | method | run_key | started_at |
|---|---|---|---|---|
| coverage_years | to confirm (year column present) | download | probe-20260910-cx1 | 2026-09-10T12:00:00Z |
| export_rows | 3.0 count | download | probe-20260910-cx1 | 2026-09-10T12:00:00Z |
| format | CSV; columns: hs_code, year, partner, value | download | probe-20260910-cx1 | 2026-09-10T12:00:00Z |
| free_access | 1.0 | download | probe-20260910-cx1 | 2026-09-10T12:00:00Z |
| granularity | CN8 x partner x year (observed columns) | download | probe-20260910-cx1 | 2026-09-10T12:00:00Z |


### PX-1

| metric | value | method | run_key | started_at |
|---|---|---|---|---|
| catalog_count | 500.0 count | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| category_list | ["http://127.0.0.1:PORT/cat/wandfarben", "http://127.0.0.1:PORT/cat/grundierung"] | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| free_access | 1.0 | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| languages | ["de", "fr"] | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| page_sample_ok | 2.0 count | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| rate_limit | unknown — polite default <= 1 req / 2 s | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| robots | allowed | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| sds_sample_ok | 1.0 count | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |
| terms | link present: /terms | scrape | probe-20260910-px1 | 2026-09-10T12:00:00Z |




## Anchor candidates (provisional — manual promotion, M1 decision)


| source_id | metric | value | run_key |
|---|---|---|---|
| CX-1 | export_rows | 3.0 count | probe-20260910-cx1 |
| PX-1 | catalog_count | 500.0 count | probe-20260910-px1 |

> Provisional frame inputs only. Promotion to population_anchor is a
> manual method decision (10_STRATEGY/MASTER D20), not automatic.


## Source activity

| source_id | first retrieved | last retrieved | runs | findings |
|---|---|---|---|---|
| CX-1 | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | 1 | 5 |
| CX-2 | - | - | 0 | 0 |
| CX-3 | - | - | 0 | 0 |
| CX-4 | - | - | 0 | 0 |
| PX-1 | 2026-09-10T12:00:00Z | 2026-09-10T12:00:00Z | 1 | 9 |
| PX-2 | - | - | 0 | 0 |
| PX-3 | - | - | 0 | 0 |
| PX-4 | - | - | 0 | 0 |
| PX-5 | - | - | 0 | 0 |
| PX-6 | - | - | 0 | 0 |
| PX-7 | - | - | 0 | 0 |
| PX-8 | - | - | 0 | 0 |
| PX-9 | - | - | 0 | 0 |
| ST-1 | - | - | 0 | 0 |
| SX-1 | - | - | 0 | 0 |

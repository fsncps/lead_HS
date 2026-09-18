# Probe workflow — per source class

Source of truth: 20_DESIGN/MASTER/interfaces.md (adapter contract,
exception mapping) and docs/study/DATA_SOURCE.md (probing pass).
Rendered with --type flowchart.

## Process

1. Load source row from register (class, url, status)
2. Check robots.txt + site terms + rate limit
3. Decision: robots deny our paths?
   - yes → record robots_denied finding (method=manual, fallback note); run blocked, exit 2 (findings already collected → run done + notes)
   - no → continue
4. Fetch per mode (census / format_check / access_check); ≥2 s per domain, 2 retries; 429 → one capped backoff (RateLimited), then blocked
5. Decision: HTTP 403, persistent 429, or paywall/login?
   - yes → record access_blocked finding; run blocked, exit 2 (findings already collected → run done + notes)
   - no → continue
6. Decision: export layout as expected?
   - no → record format finding (WARNING, manual review); continue
   - yes → continue
7. Enumerate categories and counts (census) or run test export (format_check)
   → catalog_count, category_count, category_list, granularity, coverage_years, export_rows, free_access
8. Sample N products (default 5) → page_sample_ok, sds_sample_ok
9. Archive sample pages + export file as raw documents (sha256-named)
10. Write findings + documents; run done (network failure → run failed, exit 2)

```
probe run --source PE-1
   │
   ▼
load source + robots/terms/rate
   │
   ├─ happy ─▶ enumerate categories ─▶ fetch pages (≤1 req/2s)
   │            └─▶ document (raw) + findings (catalog_count,
   │                category_count, sds_sample_ok, languages, terms)
    ├─ robots deny ─▶ finding(robots_denied, manual); run blocked, exit 2
    └─ fetch fail ─▶ finding(access_blocked, manual); run blocked, exit 2
                    (partial collection before → run done + notes)
```

---
unit: v0.1.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE03 — Network & environment

Status: done (implemented + gate verified 2026-09-11) · Depends on: PHASE01 (parallel to 02) · Governs:
the fetch seam + preflight.

## Objective

The single network seam (`fetch.py`) with politeness, retry and the
reviewed error taxonomy, plus `leadhs doctor` — the first-run
de-risking surface on Slackware.

## Governing references

- `../../20_DESIGN/MASTER/architecture.md` — §Module contracts
  (fetch.py, doctor.py): injectable clock/sleeper, robots cache,
  ≥ 2 s spacing, UA, retries; `RateLimited` (429 — one capped
  backoff, then Blocked), `Blocked` (403/paywall).
- `../../20_DESIGN/MASTER/interfaces.md` — §Adapter contract
  (ProbeContext.fetcher, `plan()` dry-run, zero network), §Error
  surfaces (exception mapping).
- `../../10_STRATEGY/DATA_SOURCE.md` — §Access & scraping discipline
  (binding: robots, UA+contact, ≤ 1 req / 2 s, official exports
  preferred, no accounts/paywalls).

## Steps

1. **`fetch.py`** — `Fetcher(config)` with **injectable clock and
   sleeper** (deterministic tests; no real sleeps in suite):
   - robots.txt checked per domain, cached; 404 or empty file =
     allow-all; disallow of our paths → `RobotsDisallowed`.
   - ≥ 2 s spacing between requests **per domain** (queue per host).
   - UA `leadhs/<version> (+<contact>)` — contact from
     `--contact`/`LEADHS_CONTACT`; unset contact → doctor warns (and
     fetcher logs a warning line once).
   - HTTP 403 or paywall/login wall → `Blocked`.
   - HTTP 429 → `RateLimited`: **one capped backoff** (cap e.g. 60 s
     on the injected clock), then retry; persistent 429 → raise
     `Blocked` (i8).
   - Other errors (DNS/TLS/timeout/5xx): 2 retries with exponential
     backoff, then `ProbeNetworkError`.
   - **Dry-run mode: zero network calls** — `plan(url, …)` returns
     the would-be request record instead; robots checks also skipped
     (nothing fetched). Test-enforced invariant (i7).
   - All fetches logged via `logutil.log_event` (url, status, ms).
2. **`doctor.py`** — preflight: Python version (≥ 3.11), sqlite3
   import + version; optional binaries **mdbtools, pdftotext, pandoc**
   → warnings (not errors) when absent; data dir writability
   (`data/`, `data/raw/` creatable); contact configured (warning);
   `--net`: reachability HEAD of seeded register sources (opt-in;
   default `--no-net`). Exit 0 with warnings; 1 on errors.
3. **CLI wiring** — `leadhs doctor [--net | --no-net]`.

## Deliverables

fetch.py (the one network seam), doctor.py, `doctor` command live.

## Exit gate

- Fake-clock tests: two requests to one domain ≥ 2 s apart; different
  domains interleave independently.
- robots disallow → `RobotsDisallowed`; 403 → `Blocked`;
  429 → `RateLimited` (one capped backoff, injected clock), retry
  succeeds on transient 429; persistent 429 → `Blocked`.
- 2 retries then `ProbeNetworkError` (connection error fixture).
- Dry-run: a fetcher under a socket-blocking test guard performs
  **zero** network calls including robots.
- `leadhs doctor` on this host: exits 0 or 1 with a clear report
  (mdbtools likely a warning on Slackware — expected).

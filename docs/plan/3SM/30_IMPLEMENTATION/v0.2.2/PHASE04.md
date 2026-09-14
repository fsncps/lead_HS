---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE04 — Wave harness + W1/W2 adapter extensions

## Objective

Build the four-wave harness (selection, budget, resume, disposition
invariant) at the CLI/Make layer — no engine budget concept, no new
CLI command — and the W1/W2 adapter extensions that ingest the bulk
official exports and complete the capability matrix.

## Preconditions

- PHASE03 done (census-shape register loaded; anchors populated).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (four-wave run, wave gates,
  fu5; ENG e2/e6; CEO c1/c2)
- `../../20_DESIGN/MASTER/interfaces.md` (i20 wave/landscape
  contract)
- `../../20_DESIGN/MASTER/architecture.md` (a26)
- `../../20_DESIGN/MASTER/testing.md` (t12 wave/adapter blocks)

## Steps

1. **Run filter generalization (e2):** `run_all` gains an optional
   source-selection parameter (class list / source ids); the
   capability-mode AS-filter becomes one preset of it — no `mode ==`
   chain growth. Existing callers unchanged.
2. **CLI options:** `probe run --wave {1..4}`, `--budget SECONDS`,
   `--staging-db PATH` (default `data/testdata.sqlite`). Waves expand
   to (mode, filter) presets per i20; the CLI loop checks elapsed
   budget per source and stops with a resumable state; wave progress
   lines print each source's disposition as it lands (c4).
3. **`make landscape`** guarded GO=1 with WAVES/BUDGET/STAGING
   vars (probe-capability precedent); `test_makefile.py` extends.
4. **W1 adapter extensions:**
   - **ECAT ingest:** fetch `export_url` → `_sniff` → shared CSV
     helper → full-row parse → normalize → stage rows (group 044
     filter) → run-close derivation. Column drift → `format_finding`.
   - **Nordic Swan:** pin export mechanics (GET vs form-POST) at
     execution; if POST-only → manual-record fallback built into the
     wave (c1).
   - **Blue Angel XLSX** via `leadhs/xlsx.py` (sheet layout pinned at
     execution; manual fallback built in).
   - **PRODCOM bulk TSV** (ST row): bulk download → per-NACE
     production values → `stg_trade_cn8` staging (NACE↔CN8 via the
     correspondence; NACE-proxy fallback with caveat if the official
     table is unclean — design c5).
   - **Comext per-CN8 batches:** per-CN8 × flow queries via
     `leadhs/jsonstat.py` (declarant + period dims decoded);
     per-query timeout + retry; batch shape (13 codes × flows) pinned;
     `stg_trade_cn8` staging.
5. **W2 extensions:** IBU/environdec/NF/natureplus/EPD-Norway export
   inspection (real format pinning — not landing-page-only); manual
   fallback step built into the wave definition; counted-0 semantics
   (c2) for legitimately-empty exports.
6. **W3 extension:** PEAdapter recon gains `sds_doc_urls` counting
   (SDS/TDS document URLs discovered via sitemaps/index pages —
   counts only, no URL harvesting beyond the existing rule); the
   widened caps ride the register notes from PHASE03.
7. **Tests (t12 wave/adapter blocks):** wave filter selection;
   budget expiry mid-wave (virtual clock) → resumable, no partial
   source; after-run disposition invariant; `_sniff` regression
   (HTML-as-CSV); column drift; BOM/encoding; counted-0; 403
   blocked; dry-run plans zero fetches; `make landscape` guard.

## Deliverables

Wave harness (CLI options + run filter + Make target); W1/W2/W3
adapter extensions; t12 tests.

## Exit gate

Full offline suite green incl. t12; `probe-dry` per wave plans the
expected source sets; `make landscape` requires GO=1; audit exit 0.

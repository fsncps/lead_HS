---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE02 — Unit machinery: migration 0006, recon mode, CS-2 aggregation, 0.2.0

## Objective

Land the unit's entire code delta, offline-verified: the recon
machinery (nu1/i15), the CS-2 trade aggregation (nu2), the schema
delta (migration 0006), the operator targets, and the version bump.

## Preconditions

- PHASE01 done (0005 applied; validation live; design-ahead files
  already renumbered to 0007–0013).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.0.md` (nu1/nu2/nu6/nu8)
- `../../20_DESIGN/MASTER/interfaces.md` (i15; exception table;
  i7 dry-run invariant; run semantics)
- `../../20_DESIGN/MASTER/architecture.md` (a19/a20)
- `../../20_DESIGN/MASTER/testing.md` (t10; t5 fixture site)

## Steps

1. **Migration `0006__recon_numbers.sql`:** INSERT source_class
   `AS`; INSERT probe_mode `recon`; INSERT 7 probe_metric rows
   (`sitemap_products`, `sds_library_visible`,
   `producers_registered`, `trade_kg_hs3208`, `trade_eur_hs3208`,
   `trade_kg_hs3209`, `trade_eur_hs3209`); UPDATE source CS-1 →
   active=0 + notes append "out of scope D31 (EU-only; TLS wall
   documented 2026-09-12)"; redefine v_anchor_candidates (gains
   `sitemap_products`).
2. **CLI + engine:** `probe run --mode` choice list gains `recon`
   (no new command — V9); mode dispatch passes through to adapters.
3. **PEAdapter recon branch** (dispatch on ctx.mode inside probe;
   nu1/i15): robots.txt fetch (existing robots/terms findings;
   RobotsDisallowed → blocked; 404 → allow-all; network error →
   policy "unknown" → proceed with note — e6) → sitemap discovery
   (robots `Sitemap:` lines, else `/sitemap.xml`) → structured
   fetch (per-call ~25 MB streaming cap, SizeLimit → count 0 +
   "floor partial" note — e3/3A), counts only, no URL harvesting;
   `<sitemapindex>` → child fetches up to hard cap 5 (1A), cap hit
   → note "index, K children fetched, cap 5 — floor partial";
   nested-index child → noted, not recursed (e7); count `<loc>`
   entries matching the site's product-URL pattern —
   `product_pattern=` notes token (i13 extension), generic fallback
   (`/product`, `/p/`, case-insensitive); **gzip payloads
   decompressed via magic-byte sniff before parsing (e4); tag
   matching iterates local names, namespace-agnostic (e5)**;
   pattern/fallback use in finding notes; ElementTree (stdlib)
   parsing; sitemap bytes archived as document; shadow paths — no
   sitemap → 0 + note "no sitemap"; empty/zero matches → 0;
   malformed XML → ParseError → format finding (WARNING), run done;
   ProbeNetworkError → run failed; dry-run plans robots + base
   only, zero fetches (i7).
4. **CSAdapter census branch += full-year aggregation** (nu2): per
   HS × flow=import (flow + resolved year pinned in
   parameters_json), JSON-stat decode via the minimal
   one-dimension decoder — `value` object + flat index → partner
   via id/size (e2/2A); sums → `trade_kg/eur_hs3208/3209`
   findings; partner tops + supplementary units in finding notes;
   bounded year step-back (empty → previous year, max 3 tries,
   noted; exhausted → document-blocked note — e7); latest resolved
   year noted; empty result → honest 0; UnexpectedFormat → format
   finding; raw JSON archived; dry-run plans the aggregation URLs.
5. **fetch seam:** `get(url, max_bytes=…)` streaming cap (e3/3A) —
   typed `SizeLimit` error; default uncapped (census/ST unchanged).
6. **engine:** `record_manual` gains a mode parameter (CLI
   `--mode`, default census — e8).
7. **Makefile:** `probe-recon` target (one leadhs call:
   `probe run --mode recon --all`; `guard-probe-recon` GO=1
   prerequisite) + `recon` target (setup → probe-recon → report →
   db-audit), mirroring census; **the probe step inside the
   `census` and `recon` chains tolerates exactly exit 2
   (`|| test $$? -eq 2`) — expected blocked/failed sites no longer
   abort the chain (e1/1A)**; `probe-single` gains `MODE=` var.
8. **Version bump 0.2.0** (pyproject.toml, `__init__.py`, Makefile
   header, version assertions); wheel build check.
9. **Tests** (t10): recon paths on the fixture site — happy
   (robots + sitemap fetch only; product-pattern count; document
   archived; no cap note), index + 3 children (fetched, summed, one
   note), index + 8 children (cap 5, "floor partial" note), no
   sitemap → 0 + note, robots deny → blocked exit 2, robots
   unreachable → unknown → proceeds with note (e6), malformed XML
   → format finding + done, gzip fixture (e4), namespaced fixture
   (e5), nested-index child (e7), oversized fixture → SizeLimit →
   0 + floor-partial (e3), zero-call dry-run; fetch cap tests
   (uncapped default unchanged); aggregation fixture tests (JSON-
   stat value-as-object + partner decode — sums AND tops per HS;
   import flow + resolved year in parameters_json; step-back noted;
   3 empties → blocked note; empty → 0; malformed → format finding;
   raw archived; dry-run plans aggregation URLs); record --mode
   label test (e8); test_migrations.py 0006 (lookups + 7 metrics +
   CS-1 retired with note + view gains sitemap_products) and sync
   test through 0006 (0001+0003+0004+0005+0006 == metrics.py);
   test_makefile.py (probe-recon guarded; recon chain; exit-2
   tolerance idiom in census/recon recipes; MODE pass-through).

## Deliverables

Migration 0006; recon mode + PE recon branch; CS-2 aggregation;
probe-recon/recon targets; 0.2.0 wheel; green suite.

## Exit gate

Full offline suite green incl. new t10 cases; `db audit` exit 0 on
the real DB; `leadhs --version` → 0.2.0; wheel installs in a managed
interpreter (`uv tool install`, `--data-dir` from a foreign CWD).
(Golden regeneration belongs to PHASE06, when report output
changes.)

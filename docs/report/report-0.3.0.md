---
unit: v0.3.0
stage: ENGINEERING
lifecycle: LIVE
updated: 2026-10-03
language: en
---

# Unit report v0.3.0 — the instruction-driven raw source layer

**What the unit promised:** a potential source URL goes `probe url` →
ballpark; `raw scan` turns a live delivery into a committed, reviewable
JSON sourcing instruction (with derived politeness guards); `raw run`
registers the source, creates its raw table, and bulk-loads **every
record verbatim** — upsert + change journal, checkpoints, truncation by
priority never dropping a record; `raw status` reports honest coverage.
A new same-shape source onboards with **zero code changes** (one JSON
file). AS-2 and AS-3 were to be loaded live as the proof.

**Status: built and gate-verified (2026-10-03).** AS-2 loaded live and
verified; AS-3's confirmed delivery route died between units — recorded
honestly as the reserved `html_pages` case (see below).

## What was built

- **Migration `0012__raw_layer.sql`** — `raw_export_kind` lookup
  (csv_snapshot, api_endpoint, web_query reserved, html_pages
  reserved), `raw_source_profile` (manifest contract + table registry),
  the pinned tables `raw_as2_ecat` (12 verbatim columns) and
  `raw_as3_nordic_swan` (10), and the `raw_change` journal.
- **Instruction schema v1** (`raw_sources/<source_id>.instruction.json`,
  canonical JSON) — fail-closed validation refusing unknown versions
  and unknown fields (typo protection), misdirected natural keys,
  `_`-prefixed columns, non-positive budgets, delays below the 2 s
  floor; every refusal names its JSON path. The `manifest_hash` is the
  sha256 of the canonical re-serialization, so hand-editing key order
  or whitespace never changes the contract version.
- **CLI:** `probe url` (light pre-probe, ballpark, DB only with
  `--source`), `raw scan` (live delivery → draft instruction; never
  writes DB), `raw run` (init + seed, `--cap/--dry-run/--resume/
  --workers/--batch`), `raw status` (coverage vs the instruction's
  expected count — drift printed, never silent), `raw explain`.
  Make targets `raw-scan`/`raw-run` (GO=1 gated), `raw-status`,
  `raw-explain`.
- **Seed semantics:** upsert on the declared natural key + sha256 row
  hash (new → insert, equal → skip, changed → update + one `raw_change`
  journal row); batch checkpoints every 500 records; interrupt keeps
  committed batches + checkpoint (exit 130) and `--resume` continues
  the same run; politeness starts are serialized at ≥ max(2 s, delay)
  even with concurrent page fetches. Per-record budget 1024 bytes:
  identity fields never truncated, overflow cut by declared priority,
  `_truncated` flags the row.
- **Degraded row-hash identity** (documented in the data model, used
  for AS-2): when an export carries intra-export duplicates, no column
  combination can be a key — the empty `natural_key` selects row-hash
  identity (inserts only, byte-identical rows collapse, changed content
  inserts rather than updates).

## The live proof — AS-2 (EU Ecolabel ECAT)

`GO`-gated scan + run on 2026-10-03 against the pinned export URL:

| figure | value |
|---|---|
| delivery | 17,267,207 bytes, semicolon CSV, UTF-8 (BOM stripped) |
| delivery rows | 89,867 |
| byte-identical duplicate rows | 471 (collapsed under row-hash identity) |
| **distinct records loaded** | **89,396** |
| fetches | 1 (single snapshot request) |
| truncation | 0 rows over the 1 KiB budget |
| verification | 200/200 seeded random delivery rows matched verbatim (all 12 columns, empty-string-preserving); 0 BOM/mojibake artifacts; paint-group licences well-formed (`SE/044/002` style) |
| provenance | `db audit` exit 0; one `acquire` run row per load; re-run with `--cap 5`: 0 inserted / 5 skipped (idempotent) |

For scale: the 89,396 rows cover **all ecolabel groups** (lubricants,
tissue, textiles …) — 17,843 rows sit in paint/varnish groups; the
paint filter is downstream analysis, the raw table is the unfiltered
verbatim copy. `code_value` (EAN13 et al.) is populated on 40.1% of
rows.

## AS-3 (Nordic Swan) — the route died between units

The export route pinned in v0.2.4
(`…/search-for-ecolabelled-products-and-services/?format=csv`, archived
twice 2026-09-14/15, 52,539 rows, sha256-verified) returned **HTTP 404**
at the 2026-10-03 scan: svanen.se was redesigned into a server-rendered
WordPress product search (`GET /?s=&post_type=markeds`, plugin
`nordic-swan-ecolabel` content-search). The unit's instruction file
records this with the reserved `html_pages` kind — `raw run AS-3`
refuses it (named refusal) until the HTML-walk interpreter lands
(v0.3.8 per the design's reserve list). The v0.2.4 archived snapshot
remains the newest verified full copy.

This is also a methodological datapoint: **bulk CSV exports of ecolabel
catalogues are not stable infrastructure** — AS-2's snapshot survives
via the public-storage URL, AS-3's died within three weeks. The
instruction file per source (with scan dates) is the instrument that
makes such drift visible and dated.

## Live-found defects (fixed during the unit)

1. UTF-8 deliveries without a charset decoded as ISO-8859-1 (mojibake
   + BOM artifact in the first header) — raw-layer decode is now
   UTF-8-first with BOM stripping, falling back to the declared
   encoding only on genuine non-UTF-8 content.
2. `raw scan` profiled a 404 error page as a zero-value CSV delivery —
   non-2xx responses are now a named refusal (exit 2).
3. The pinned-table lookup missed `raw_as2_ecat` (id sanitization
   `AS-2 → as_2` vs the migration's `as2`) — both spellings are tried.
4. `raw explain` crashed on `expected_count: null` — fixed.
5. Latent fixture bug (`/basta.json` double-encoding) surfaced by the
   new tests — fixed.

## Verification posture

456 → 460 offline tests green (48 new for the raw layer: refusal
matrix, canonical-hash stability, migration chain 0001→0012, upsert
triple, truncation boundaries and determinism, checkpoint resume across
a page boundary, register sync warnings, guard derivation, pacing).
`make smoke` green. `db audit --unreferenced` exit 0 after the live
loads. No legal referencing anywhere in the layer — product data only.

## Open items

- AS-3 re-acquisition needs the `html_pages` walk interpreter
  (v0.3.8); until then the archived 2026-09-14 snapshot is the newest
  Nordic Swan copy.
- The seed's per-record upsert loop takes ~12 min for 89k rows
  (one SELECT per record) — correct and durable; a batched
  (executemany) path is a performance note for a later unit, not a
  defect.
- `api_endpoint` interpretation is implemented and fixture-tested but
  has no live source yet; `offset` pagination likewise.

## Addendum (2026-10-09, at ship)

Post-FINAL live operation (run r04, booked at ship): JSON dot-path
projection for nested source fields (r04, `3c1c7c5`) — BASTA's
`flags`/`grades` containers project through dotted paths. AS-33 BASTA
whole-load executed and verified: **198,742 rows = envelope total
exactly, 0 truncated**, ~3 h walk at the 10 s robots crawl-delay,
audit clean, verbatim spot-checks vs the live API pass. First-light
defect recorded: the 1,024-byte default budget truncated every row
(the `flags` object averages ~750 B) — instruction budget set to
4,096 (`50f833c`). AS-7 environdec reserved as an `html_pages`
record. Suite at ship: **461 passed, 2 deselected**; `make smoke` 6
passed; `db-audit` exit 0. DB content inventory:
`docs/report/db-content.md`.

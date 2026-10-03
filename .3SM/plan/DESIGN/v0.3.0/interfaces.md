---
unit: v0.3.0
stage: DESIGN
lifecycle: LIVE
updated: 2026-10-03
branch: v0.3.0
---

# v0.3.0 — interfaces (instruction schema, raw CLI contracts)

Authoritative for the unit. Where this file and a module docstring
disagree, this file wins. Convention basis: exit codes 0/1/2/3/130 and
P1–P7 as in `../interfaces.md`; raw-layer tables as in
`../data_model.md` § Raw source tables.

## Instruction file — schema v1 (rs2)

One JSON file per source: `raw_sources/<source_id>.instruction.json`
(override dir: `--instructions-dir` — the drop-folder mode). Canonical
serialization: sorted keys, 2-space indent, UTF-8, trailing newline —
the file's sha256 is the `manifest_hash` recorded in
`raw_source_profile`.

```json
{
  "schema_version": 1,
  "source_id": "AS-2",
  "source_name": "EU Ecolabel catalogue",
  "source_class": "AS",
  "export_kind": "csv_snapshot",
  "delimiter": ";",
  "endpoints": { "list": "https://.../catalogue.csv", "detail": null },
  "pagination": { "kind": "single" },
  "records": {
    "expected_count": 88920,
    "count_derivation": "raw scan 2026-10-03: full download, counted"
  },
  "columns": [
    { "source_header": "licence_number", "column": "licence_number",
      "type": "text", "truncation_priority": 1,
      "description": "part of natural key" }
  ],
  "natural_key": ["licence_number", "product_or_service_name"],
  "payload_budget_bytes": 1024,
  "politeness": {
    "delay_seconds": 2.0,
    "crawl_delay_seconds": 10,
    "request_budget_per_run": 10,
    "records_per_request": 88920,
    "derivation": "single-file snapshot; 1 fetch/run, delay floor 2 s"
  },
  "notes": "verbatim full copy per D44; group_name spans all groups"
}
```

Field rules:

- `schema_version` — the CLI refuses unknown versions and **unknown
  fields** (typo protection; forward-only evolution like migrations).
- `export_kind` — one of the `raw_export_kind` codes: `csv_snapshot`,
  `api_endpoint` (JSON), `web_query` (reserved), `html_pages`
  (reserved; refused by the v0.3.0 interpreter, rs3).
- `pagination.kind` — `single` | `page_param` | `offset` (`cursor`
  reserved). `page_param` carries `page_param`, `page_size`,
  `max_pages` (null = until empty page).
- `records.expected_count` — scan-derived coverage anchor; `raw status`
  reports actual vs expected as a drift line, never silently.
- `columns[]` — `source_header` (verbatim D44), `column` (snake_case
  table column), `type` (`text` | `int` | `float` | `date_iso`),
  `truncation_priority` (1 = keep longest under budget; ties broken by
  array order), optional `description`. The column list is the table
  DDL minus bookkeeping.
- `natural_key` — non-empty subset of `column` values; seed upsert key.
  **Build amendment (live AS-2, 2026-10-03):** an EMPTY array is the
  data_model's documented degraded row-hash identity mode — row hash is
  the identity: inserts only, byte-identical duplicates collapse,
  changed content inserts rather than updates. AS-2 uses it (471 exact
  duplicate rows make every column combination non-unique). `null` is
  still refused.
- `payload_budget_bytes` — per-record inline budget, default 1024
  (rs8): identity (`natural_key`) fields never truncated; overflow
  truncates by priority; `_truncated` flag set.
- `politeness.*` — `delay_seconds` ≥ 2.0, `crawl_delay_seconds` from
  robots (larger wins), `request_budget_per_run` > 0,
  `records_per_request` (scan-measured; the flood-guard input),
  `derivation` (human-readable arithmetic of the budget). **Fail-closed:
  missing or zero/negative budget, delay < 2 s, or empty
  `natural_key` → the command refuses before any network call.**

## CLI contracts

    leadhs probe url <URL> [--source ID]          # rs5: light pre-probe
    leadhs raw scan <SOURCE_ID> --url <URL>
                  [--instructions-dir DIR]        # profile → draft
    leadhs raw run <SOURCE_ID> | --all
                  [--instructions-dir DIR] [--cap N] [--dry-run]
                  [--resume]                      # init + seed
    leadhs raw status [SOURCE_ID]                 # counts, runs, journal
    leadhs raw explain <SOURCE_ID>                # render instruction view

- **probe url** — unregistered URL: access, robots (crawl-delay),
  content-type, rough size/shape, sample-first-bytes. Ballpark only, no
  DB writes unless `--source ID` (then one finding inside a probe run).
- **raw scan** — profiles the live delivery for the declared
  `export_kind`: exact record count, column list + types + emptiness,
  records-per-request, robots; derives guards (rs4); writes the draft
  instruction (canonical form) and prints the path + drift vs pinned
  keyfigures if any. Never writes DB rows. Exit 2 if the source is
  unreachable/unsupported — with findings where `--source` known.
- **raw run** — per instruction, two phases: *init* (upsert `source`
  row from instruction metadata + register-CSV sync warning for new
  sources rs6; upsert `raw_source_profile` with manifest_hash;
  create-if-not-exists the raw table from the column list) then *seed*
  (generic interpreter: fetch pages honoring `politeness`, extract
  records, upsert on natural key + sha256 payload hash, journal
  changes in `raw_change`, commit per batch with checkpoint). `--cap N`
  limits records (tests), `--dry-run` fetches nothing, `--resume`
  continues from the checkpoint (default: refuse to start when an
  unfinished checkpoint exists for the source — honest state, no silent
  restart).
- **raw status** — per source (or all): table, row count, first/last
  run, changed rows, truncated rows, checkpoint state, coverage vs
  `records.expected_count`.
- **raw explain** — instruction rendered readably; never a second
  contract file.

Exit codes (convention unchanged): 0 success; 1 usage/data error
(incl. refused instruction, unknown field); 2 ran but failed/blocked
(partial seed: committed batches kept, checkpoint kept, findings
recorded); 3 audit violations; 130 interrupt (checkpoint kept).

## Make targets (GO=1 pattern)

    make raw-scan SOURCE=AS-2      # GO=1 — live profile → draft
    make raw-run SOURCE=AS-2|all   # GO=1 — live init + seed
    make raw-status                # offline
    make raw-explain SOURCE=AS-2   # offline

Network targets sit behind `guard-%` GO=1 like all others (d21).

## Seed semantics (binding)

1. Upsert on `natural_key` + sha256 over the normalized payload
   (canonical JSON of the record's field values): missing → insert,
   equal → skip, different → update + `raw_change` row (old_hash,
   new_hash, run_id, note).
2. Every seed run = one `run` row, `run_kind='acquire'`, staging
   run_key pattern (rs9).
3. Batches commit every N records (default 500) with the checkpoint
   cursor (rs7): `csv_snapshot` → none (single pass, idempotent rerun);
   `page_param` → next page number; `offset` → offset. Interrupt keeps
   committed batches + checkpoint.
4. Completeness: every record captured — stubs, nulls, duplicates
   included (D44); truncation per rs8; a record is never dropped for
   size.

## Build record (r01–r03 + live, 2026-10-03)

Deviations and additions discovered while building and running — the
authoritative deltas over the sketch above:

- `table_name` — optional schema-v1 field (the one addition to the
  field list). Emitted by scan via the pinned-table lookup (existing
  `raw_<id>%` table from a migration wins, e.g. `raw_as2_ecat`);
  otherwise derived `raw_<source_id no-dash>` (`raw_as33…` for a
  future BASTA). Hand-written instructions may omit it.
- Scan derivation depth: the natural-key search is a lattice over ALL
  columns (singles → pairs → triples → quads, ≤ 14 columns; first
  unique wins). Sparse columns participate — AS-2 proved a fully-
  populated bound would miss the truth (its keylessness comes from
  exact duplicate rows, not sparse columns). No key found → draft
  written anyway with `natural_key: []` + loud incomplete warning;
  the run refuses nothing in that case (degraded mode is valid).
- Scan refuses non-2xx deliveries with a named error and exit 2 (a
  404 error page must never be profiled as a zero-record delivery —
  live-found on AS-3).
- Raw-layer delivery decode is UTF-8-first with BOM stripping
  (`raw.delivery_text`); single-byte fallbacks (ISO-8859-1/ascii) only
  on genuine non-UTF-8 content (live-found on AS-2: text/csv ships
  without charset).
- `raw run` extras: `--workers N` (page fetches may overlap; request
  STARTS stay ≥ max(delay, 2 s) apart via a pacer — the politeness law
  holds under any worker count), `--batch N` (checkpoint every N
  records, default 500). `--all` runs every instruction file in the
  directory (exit 1 if any is refused). Interrupt → run `aborted`,
  checkpoint kept, exit 130; budget exhausted → `blocked`, exit 2.
- `raw run --dry-run` plans with zero network AND zero DB writes
  (house dry-run discipline); the run-plan init phase (source upsert
  + register sync warning, profile row, create-if-not-exists) happens
  only on a real run.
- `probe url` caps its ballpark fetch at 64 KiB (report says "> cap"
  when the delivery streams past it); `--cap N` overrides.
- Reserved kinds (`web_query`, `html_pages`): valid instructions,
  rendered by `raw explain`, refused by scan/run with a named message
  — AS-3 uses this deliberately for its dead CSV route (2026-10-03).

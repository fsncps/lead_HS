---
unit: v0.1.1
stage: DESIGN
lifecycle: LIVE
updated: 2026-09-11
---

# Interfaces & contracts (Design)

## Abstract

This document is the binding contract set for the `leadhs` tool: the
CLI commands of unit v0.1.1 with their arguments, effects and exit
codes; the provenance rules every database write must obey; the
Python contract that probe adapters implement; the authoritative
census-metric vocabulary; the run lifecycle semantics; the database
audit rule set; and the design-ahead contracts for the query/export
surface that lands at M4. Where this document and a module docstring
disagree, this document wins.

## CLI surface — implemented in v0.1.1

    leadhs db init [--no-backup]
    leadhs db status
    leadhs db audit [--unreferenced]
    leadhs source load [--file CSV]
    leadhs source list [--class CS|PE|LG|ST|LI]
    leadhs probe run --source ID | --all
                     [--mode census|format_check|access_check]
                     [--sample N] [--dry-run]
    leadhs probe record --source ID --metric M
                        [--value X | --value-text T] [--unit U]
                        [--url URL] [--document FILE] [--note TEXT]
    leadhs probe report [--source ID] [--format md|csv|json]
    leadhs doctor [--net]

Design-ahead surface (milestones per 10_STRATEGY/ARCHITECTURE.md):
`acquire run`, `ingest sightings`, `parse sds`, `review next|decide`,
`frame set`, `frame promote`, `sample plan`, `sample draw`,
`corroborate`, `analyze prevalence`, `report build`, `dict load`,
`db query`, `db export`.

All groups print help on bare invocation (`no_args_is_help`; exit 0).
`source list` is registered under exactly one name — the derived
`list-` artifact is removed (v0.1.2).

## Command contracts

| Command | Effect | Exit codes |
|---|---|---|
| `db init` | apply pending migrations (0001–0003 in this unit); backup existing DB first unless `--no-backup` | 0 ok; 1 no/invalid DB path |
| `db status` | applied/pending migrations, table row counts, file path+size | 0 |
| `db audit` | run rules R1–R9, print report; `--unreferenced` also lists raw-store orphans | 0 clean; 3 violations |
| `source load` | upsert register from `src/leadhs/dict/sources.csv` (or `--file`); register of record is the CSV in git | 0; 1 malformed CSV / bad row |
| `source list` | table of sources with class, status, active | 0 |
| `probe run` | one run per source (see run semantics); findings + documents written; per-source summary line | 0 all done; 2 any run failed/blocked (findings still recorded) |
| `probe record` | create a manual run (kind=probe, method=manual) + one finding; optionally attach a raw file as document | 0; 1 bad metric/value |
| `probe report` | render the source-feasibility census (od8 content layer): md (framing, summary matrix, per-source sections, run status incl. blocked/failed, anchors, activity), csv (summary matrix, all registered sources), json (full structure); md default | 0 |
| `doctor` | environment preflight (python, sqlite, binaries as warnings, data dir, contact, optional reachability) | 0 (warnings allowed); 1 errors |

Global flags: `--verbose` (structured logging); `--db PATH`
(default `data/leadhs.sqlite`) **or** `--data-dir DIR` (base
directory for `leadhs.sqlite` + `raw/`; installed non-repo use —
mutually exclusive with `--db`, conflict is a usage error, exit 1);
`--contact` / `LEADHS_CONTACT` (user-agent contact; doctor warns
when unset).

Exit-code convention (all commands): **0** success; **1**
usage/data error — including click usage errors (unknown command,
missing required option, bad choice), enforced in `main()`;
**2** an operation ran but ended failed/blocked (findings
recorded); **3** audit found violations; **130** on interrupt
(`KeyboardInterrupt` → `Abort` → 130 in `main()`).

## DB initialization contract (v0.1.2)

Every command that reads the schema requires an initialized
database: `db status`, `db audit`, `source load`, `source list`,
`probe run`, `probe record`, `probe report`. If the DB file is
missing/empty or `schema_version` is absent, the command prints a
guided error and exits 1:

    error: database not initialized — run `make setup` (repo) or
    `leadhs db init` then `leadhs source load` first

Never a `bug:` label (strategy D21; operability requirement 2).
`db init` is the only command that initializes. The check lives once
in `cli.py` (`_ensure_initialized`), shared by all seven commands.

## Provenance contract (binding — every write path)

- **P1** every evidence insert happens inside a run
  (probe/acquire/import/sampling) and carries run_id.
- **P2** every document insert carries source_id, url, retrieved_at;
  status `archived` ⇒ raw_hash set AND the raw file exists in the
  store.
- **P3** every probe_finding carries a per-source probe run, a metric
  from the vocabulary, a value (numeric or text per metric
  value_type), and a method.
- **P4** all SQL is parameterized — no string interpolation of values
  into statements, ever.
- **P5** raw store: filenames are `<sha256>.<ext>` only; the source
  directory is the source_id lowercased and must match
  `^[a-z]{2}-[0-9]+$` (path-traversal guard; enforced in store.py).
- **P6** append-only evidence (documents, findings, runs, sightings):
  no value updates, no deletes; corrections are new rows or
  review-status transitions. Reference data (source, lookups,
  dictionary, study) is updatable in place, never deleted.
- **P7** user-facing counts in reports come from the DB only
  (Strategy D18 restated as an interface rule).

## Adapter contract (Python)

    class ProbeAdapter(Protocol):
        key: str                       # source class: 'CS' | 'PE' | 'ST'
        def supports(self, source: SourceRef) -> bool: ...
        def probe(self, source: SourceRef, ctx: ProbeContext) -> ProbeResult: ...

- `ProbeContext`: fetcher, store, db connection, mode, sample_n,
  dry_run, clock, logger. In dry_run the fetcher performs **zero**
  network calls (adapters must use `ctx.fetcher.plan(...)` for
  would-be requests).
- `ProbeResult`: `documents` (raw bytes + metadata drafts), `findings`
  (typed FindingDraft: metric, value/unit, method, document link,
  note), `blocked`/`failed` notes.
- Adapters **never** write the DB directly — the engine owns all
  writes (single write path; audit rules hold by construction).
- Adapters raise typed errors; the engine maps them:

| Exception (defined in fetch.py / adapters.py) | Trigger | Engine maps to |
|---|---|---|
| `RobotsDisallowed` | robots.txt disallows our paths | finding robots_denied (method=manual) + run blocked (exit 2); findings already collected → run done + notes |
| `Blocked` | HTTP 403 or paywall/login wall | finding access_blocked + run blocked (exit 2); findings already collected → run done + notes |
| `RateLimited` | HTTP 429 | one capped backoff then retry; persistent 429 → finding access_blocked + run blocked (exit 2) |
| `ProbeNetworkError` (wraps `requests.RequestException` after 2 retries) | DNS/TLS/timeout/5xx | run failed; exit 2 |
| `UnexpectedFormat` | export layout not as expected | finding format (value_text) — WARNING, manual review |
| `BinaryMissing` / `ExtractionError` | mdbtools absent / SPIN extraction fails | finding extraction_path (blocked/failed) |
| `ParseError` | unparseable/empty HTML | finding page_sample_ok=0 |
| `KeyboardInterrupt` | user interrupt | run aborted; findings persist; exit 130 |

Anything else propagates as a bug (fail loudly — no blanket excepts;
no `rescue StandardError` equivalent).

## probe_metric vocabulary (authoritative)

| code | label | value_type | meaning |
|---|---|---|---|
| catalog_count | Catalog product count | numeric | total products listed site-wide |
| category_count | Category product count | numeric | products in one category (category path in the finding notes — R4 stays strict: numeric metrics carry no value_text) |
| category_list | Categories exposed | text | JSON list of category names/paths |
| format | Export/download format | text | observed layout of official exports |
| granularity | Statistics granularity | text | dimensions available (e.g. CN8 × partner × year) |
| coverage_years | Coverage years | text | year range available (e.g. 2019–2025) |
| export_rows | Export rows | numeric | rows returned by a test export/query |
| robots | Robots policy | text | robots.txt summary for our paths |
| terms | Site terms | text | terms relevant to access/scraping |
| rate_limit | Rate limit | text | observed or documented limit |
| languages | Languages | text | languages offered (JSON list) |
| page_sample_ok | Sample pages retrievable | numeric | n_ok/n_sample |
| sds_sample_ok | SDS on sample pages | numeric | n_with_sds/n_sample |
| extraction_path | Extraction path | text | result of an extraction-tooling check (e.g. mdbtools/SPIN) |
| access_blocked | Access blocked | text | detail when blocked (403/429/paywall/login) |
| robots_denied | Robots denial | text | detail when robots.txt disallows |
| free_access | Free access confirmed | numeric | 0/1 — no account/paywall needed |
| records_hs3208 | Records HS 3208 | numeric | rows for HS 3208 in the parameterized query (absent = not queried; 0 = queried, empty) |
| records_hs3209 | Records HS 3209 | numeric | same, for HS 3209 |
| records_hs3213 | Records HS 3213 | numeric | same, for HS 3213 (census annex) |
| census_status | Census status | text | manual/deferral record on a source's census state (PCN aggregates, deferral notes, manual export mechanics; method=manual) |

Extension rule: new metrics are added by a migration INSERT (code
never renamed; value_type fixed at insert). `metrics.py` is the
runtime source of truth; a sync test pins the migration seeds
(0001 + 0003) to it (migrations are static SQL and cannot call
Python).

## Run semantics

- **Per-source runs:** `probe run --all` loops active sources, one
  run each (`run.source_id` NOT NULL for kind='probe' — schema
  CHECK); a failing source never aborts the loop.
- **run_key:** `<kind>-<YYYYMMDD>-<slug>`; probe slug = source id
  lowercased dash-stripped (`CS-1` → `probe-20260910-cs1`);
  same-day re-runs append `-2`, `-3` (deterministic, unique).
- **Abort/resume:** interrupt → current run `aborted` (findings
  persist); re-run creates a new run; the "current" census is
  v_probe_latest (latest done run per source × metric) — never a
  mutation of old findings.
- **Outcome rule:** run status reflects the whole source — reachable
  with findings collected → `done`; wholly inaccessible (robots deny,
  403, persistent 429, paywall) → `blocked`; unrecoverable network
  error → `failed`. `probe run` exits 2 when any run ended blocked or
  failed; findings collected before a block keep the run `done` with
  a notes line.
- **Stale-run reclaim:** a run left `running` by a hard crash
  (SIGKILL/power loss) is marked `failed` with note
  `stale run reclaimed` by the next `db init` / `probe run` /
  `db status` (threshold: started_at older than the current process,
  or 1 h); the census is unaffected — v_probe_latest reads `done`
  runs only.
- **Pacing:** `probe run --all` on the full register is a multi-minute
  operation (≥ 2 s spacing per domain); progress via `--verbose`;
  re-runs are incremental (per-source new runs).
- **parameters_json (probe):**
  `{"mode": "...", "sample_n": 5, "dry_run": false, "contact_set": true}`
  — other kinds define their schema at their milestone.
- **Sampling runs** additionally carry seed + computed n
  (data_model.md, sampling group).

## db audit rules (authoritative R1–R9)

- **R1** every probe_finding joins a probe_run whose run.source_id is
  set (per-source rule).
- **R2** every document has source_id + retrieved_at; status
  'archived' ⇒ raw_hash present AND file exists in store.
- **R3** every finding document_id resolves (FK) and the referenced
  file exists.
- **R4** value presence matches probe_metric.value_type (numeric →
  value_numeric; text → value_text).
- **R5** finished runs have finished_at; failed/blocked/aborted runs
  carry notes.
- **R6** run_key present, unique, well-formed.
- **R7** `PRAGMA foreign_key_check` empty.
- **R8** (`--unreferenced`) raw-store files without a document row
  are listed as orphans.
- **R9** no evidence rows exist outside a run of the right kind.

Exit 3 on any violation; a human-readable report is printed (the
"git status for the database" surface).

## Query & export surface (design-ahead — M4 contract, fixed now)

- **`leadhs db query --sql "SELECT …" [--param k=v …]`** — read-only
  connection; statement must be a single SELECT (parse-checked);
  parameterized values only; output table/CSV.
- **`leadhs db export --out DIR/`** produces the frozen, hash-
  verifiable "reusable evidence database" artifact:
  1. snapshot of the SQLite DB (backup API / VACUUM INTO);
  2. generated `SCHEMA.md` + `DATA_DICTIONARY.md` (from migrations +
     lookup contents);
  3. CSV dump per table (stdlib csv; Parquet only if a consumer
     requires a dependency — M4 decision);
  4. `MANIFEST.sha256` over the snapshot and every raw file,
     cross-checked against document.raw_hash;
  5. freeze note: run IDs, seeds, row counts, applied migrations.
- **Per-product evidence dossier** — rendered from v_product_dossier
  as a report annex (M4).

## Error surfaces

The exception→finding/run/exit mapping table above is the complete
error surface for v0.1.1; each row has at least one test
(testing.md). Log lines accompany every rescue (source, URL,
attempted action — full context, never message-only).

## DECISIONS (design-level; consolidated in 20_DESIGN/MASTER.md)

- i1: exit-code convention 0/1/2/3 as defined above.
- i2: register of record = repo CSV; `source add` from the Strategy
  CLI sketch is deferred — new PE sites enter as CSV rows + reload
  (single source of truth).
- i3: adapters never write the DB; engine owns the single write path.
- i4: metric vocabulary fixed now, migration-extended, codes never
  renamed.
- i5: audit rules R1–R9 as the binding provenance contract.
- i6: export/query contracts fixed now, built M4 (CEO review).
- i7: dry_run performs zero network calls (enforced via
  ctx.fetcher.plan).
- i8: `RateLimited` (429) split from `Blocked` (403/paywall): one
  capped backoff, then blocked (ENG review 2026-09-11).
- i9: outcome-based run status — done / blocked / failed per source;
  exit 2 on any blocked or failed run (ENG review 2026-09-11).
- i10: exit-code enforcement in `main()` — click runs with
  `standalone_mode=False`; UsageError → 1, other ClickException →
  its code, Abort/KeyboardInterrupt → 130, Exit → its code; bare
  groups print help (`no_args_is_help`) (v0.1.2; HOLD-SCOPE review).
- i11: DB-initialization preflight contract — guided error, exit 1,
  never `bug:`, for all schema-reading commands (v0.1.2).
- i12: report content contract (od8) — one DB-only assembly, three
  renderers from the same data; run status and notes visible incl.
  blocked/failed; dry-run runs excluded from census sections
  (malformed parameters_json fails open); matrix covers all
  registered sources; legend distinguishes "—" (not queried) from
  0 (queried, empty); framing states source-feasibility ≠
  product/lead (M2+) (v0.1.2; HOLD-SCOPE review).

## OPEN ITEMS

- swiss-impex query/export mechanics (URL parameters, CSV dialect) —
  CS adapter detail; probe answers.
- CS-2 exact Comext query parameters (reporter/product/period/flow)
  — pinned at census execution; the archived response verifies
  (od9).
- Sample-page selection: seeded random preferred (reproducible);
  finalize at implementation.
- `db query` output formats (table vs csv flag) — trivial, at M4.
- parameters_json schemas for acquire/import/sampling kinds — at
  their milestones.
- `probe record` = one run per finding — revisit batching (one manual
  run, multiple findings) at M1 if PCN passes produce run churn.
- `sample_n`/`mode` stored in both `parameters_json` and typed columns
  (`probe_run.mode_code`) — pick one home at implementation.

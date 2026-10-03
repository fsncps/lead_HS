---
unit: v0.3.0
stage: DESIGN
lifecycle: LIVE
updated: 2026-10-03
branch: v0.3.0
---

# v0.3.0 — design (instruction-driven raw source layer)

## SCOPE

From the frozen concept (PIPELINE v0.3.0 entry; `../../CONCEPT/RAW_SOURCING.md`;
CONCEPT MASTER D42–D44) plus the user's pipeline correction of 2026-10-03.

**The unit's product is the generic acquisition pipeline**, not a feed of
historical exports: discover a source and read it into the raw DB without
ever touching code. The user's three-step flow, mapped:

1. **probe light** — cheap ballpark of a potential source URL (unregistered;
   new `probe url`, rs5).
2. **probe detail → sourcing instruction** — `raw scan` profiles the delivery
   (endpoints, pagination, exact record count, columns, types,
   records-per-request) and emits one schema-versioned JSON instruction
   (rs2); guards are derived at scan time and written into the instruction
   (rs4).
3. **process instruction** — `raw run` registers the source, creates the raw
   table from the instruction, and bulk-downloads every record verbatim into
   it (upsert + change journal).

IN: migration 0012 (raw layer), instruction schema v1 + fail-closed loader,
`probe url`, `raw scan/init/run/status/explain`, seed interpreter for
`csv_snapshot` and JSON-API pagination (single/page_param), checkpoints +
resume, deterministic truncation, Makefile targets (GO=1), committed
instructions for AS-2 + AS-3, live bulk load of both.

OUT (recorded): `html_pages` interpreter (reserved in schema; built with the
first real HTML source, v0.3.8); BASTA/AS-33 onboarding (de5 gate open —
paint filter; becomes the first zero-code onboarding *test* later, not here);
`raw export` (feeds MATCHING at v0.3.4); normalization/matching (v0.3.4);
per-article detail walks.

## ARCHITECTURE

Delta vs the persistent T-docs (`../architecture.md`, `../data_model.md`);
the raw-layer schema is specified in `../data_model.md` § Raw source tables
(tables, conventions, pipeline) — not duplicated here.

- New module cluster alongside `adapters/` (which stays probe-only):
  `raw/instructions.py` (schema v1 model, canonical serialization,
  fail-closed validation), `raw/scanner.py` (profile → draft instruction),
  `raw/interpreter.py` (fetch/extract/upsert per instruction), wired into
  `cli.py` as a `raw` command group + a `probe url` one-shot.
- Seed runs reuse the unified `run` table with `run_kind='acquire'` (P1:
  every insert inside a run; rs9). Fetches go through the existing single
  fetch seam (injected clock, honest UA, robots honored).
- Instructions live repo-committed at `raw_sources/` (top level, reviewable
  contract); `--instructions-dir` overrides — that override is the
  drop-folder mode (drop a file, the CLI processes it; the applied
  `manifest_hash` lands in `raw_source_profile`).
- `raw run` init upserts the DB `source` row from the instruction but the
  register of record stays the repo CSV (d19): init prints a register-CSV
  sync warning for new sources (rs6). AS-2/AS-3 rows already exist.
- Rollback posture: migration 0012 is forward-only like all others; a failed
  seed leaves committed batches + checkpoint (resume), never a half-batch;
  `clobber` remains the operator reset.

## INTERFACES

Authoritative unit contract: `interfaces.md` in this directory (instruction
JSON schema v1, CLI contracts, guard enforcement, exit codes, checkpoint
representations). The persistent `../interfaces.md` CLI surface syncs at
finalize (house pattern), not before.

## TESTING POSTURE

Offline-first per house rules (PROJECT § Testing): fixture CSV/JSON files
and the local fixture site, injected clock, no sleeps, error-mapping rows
tested. The seed interpreter is exercised offline against fixtures
end-to-end; live fetches only in user-run GO=1 make targets. Net-marked
tests stay opt-in. The two historical samples (ECAT/Nordic Swan, v0.2.4)
become validation fixtures for the generated instructions (column maps,
natural keys, truncation priorities) — never the data feed.

## RISKS

- **Endpoint drift** since the v0.2.4 sampling — scan re-derives counts and
  column lists live; drift vs pinned keyfigures is reported, never silently
  absorbed (status shows expected vs actual).
- **AS-3 identity quirks** (multi-licence strings, "." null token) — pinned
  in the instruction's notes/natural-key; validation against the sample.
- **Interpreter overreach** — generality capped at the two shipped shapes
  (rs3); every speculative extension is a rejection, not a TODO.
- **Politeness failures** — budgets fail-closed (missing/zero → refuse);
  ≥ 2 s floor + crawl-delay; low-records-per-request sources get small
  budgets + longer delays (rs4).
- **Truncation correctness** — deterministic per-field priority order under
  the per-record budget; `_truncated` flag visible; identity fields never
  truncated (rs8, D44).

## DECISIONS

*(unit-local codes rs1…; concept basis: R1–R3 confirmed, R4–R8 adopted here,
R9 pinned here.)*

- **rs1** instruction-driven pipeline posture — scan is the instruction
  generator, `raw run` is a generic interpreter, zero per-source code; the
  historical CSV exports are validation fixtures only (user correction,
  2026-10-03).
- **rs2** instruction format — one JSON file per source at `raw_sources/
  <source_id>.instruction.json`; `schema_version`-tagged; canonical
  serialization (sorted keys, 2-space indent) for stable `manifest_hash`;
  documentation as structured fields, not comments; fail-closed validation
  before any network call (user decision).
- **rs3** interpreter depth = `csv_snapshot` + JSON-API pagination
  (`single`, `page_param`) — the two confirmed shapes; `html_pages` reserved
  in the schema, built with the first real HTML source (v0.3.8).
- **rs4** guard derivation at scan time, written into the instruction
  (delay, per-run request budget, records-per-request context); flood-guard:
  low records-per-request → small budget + longer delay; seed enforces
  fail-closed on top of the ≥ 2 s / crawl-delay floor.
- **rs5** `probe url <url>` — light pre-probe of an unregistered URL
  (access, robots, content-type, rough shape); findings recorded only with
  an explicit `--source ID`.
- **rs6** register integration — `raw run` init upserts the DB source row
  from the instruction; register of record stays the repo CSV (d19); init
  prints a named sync warning for sources missing from the CSV.
- **rs7** R9 pins — `raw_change` granularity is row-level (old_hash,
  new_hash, note; no field-level delta in 0.3.0); checkpoint cursors:
  `csv_snapshot` → none (single idempotent pass), `page_param` → next page
  number, offset-shape → offset.
- **rs8** truncation contract — per-field priority list from the instruction,
  per-record budget default 1024 bytes, identity fields never truncated,
  `_truncated` flag on the row (D44 determinism).
- **rs9** seed runs are `run` rows with `run_kind='acquire'`, keyed by the
  staging run_key pattern (P1).
- **rs10** FINAL folds into r03 as `PHASE_FINAL.md` (canonical default;
  no dedicated FINAL run).

## OPEN ITEMS

- Live endpoint drift check (AS-2/AS-3 counts + columns vs pinned
  keyfigures) — lands with r02 scan execution; drift is reported, adoption
  is a user decision.
- Exact guard-derivation formula (delay/budget from records-per-request and
  crawl-delay) — pinned at r02 planning; the instruction carries the
  derivation text either way.
- `raw export` shape feeding MATCHING — v0.3.4, not here.

## SKILL RECORDS

- 2026-10-03 `3sm-design-unit` — unit package authored (MASTER,
  interfaces.md, RUNS.md) from the settled concept (D42–D44, RAW_SOURCING
  R1–R9) and the session forks (pipeline correction, JSON format). Mode
  HOLD SCOPE per review preferences. Full ten-section review not re-run:
  carried from the concept adoption review; the deltas this pass settled
  are rs1–rs10. RUNS.md authored for user approval — runs-ready pending
  that approval.

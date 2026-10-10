# v0.3.4 — design unit MASTER

---
unit: v0.3.4
stage: DSG
lifecycle: LIVE
updated: 2026-10-10
branch: v0.3.4
---

Created by `/init-unit` from the unit's INIT-READY pipeline entry. Design
converges here (unit T-docs, RUNS.md) until the runs-ready gate.

## SCOPE

Identity layer first, then cross-source matching — exactly the frozen
pipeline entry (see Starting context):

- **Stage 0 (identity layer):** canonical `manufacturer` + `product`
  tables built from the raw source tables by deterministic
  extract → normalize → match-or-create over UNIQUE normalized strings;
  `raw.<table>.product_uuid` back-link; enrichment pass completing
  canonical fields by majority (MA13 rules).
- **Matching (Stages 2–5 of MATCHING.md):** exact keys → blocking →
  scored tiers → `linkage_candidate` verdicts + review queue. No LLM/
  embedding matching (MA1).
- **In scope:** migration 0013 (canonical tables + linkage_candidate +
  design-ahead renumber), `identity/` package (resolve, enrich, match),
  CLI subcommands, normalize.py extension, MA9 seed CSVs, tests.
- **Out of scope (NOT-in-scope list):** Nordic Swan identity adapters
  (CSV route dead 2026-10-03; joins via v0.3.8 re-acquisition) · UFI
  join key (DATA_MODEL pilot item) · MSE/capture-recapture outputs ·
  M1–M4 catalog/SDS integration (design-ahead blocks reconcile at their
  milestones) · raw acquisition changes (v0.3.0 owns raw/).
- **Non-goals** (pipeline): raw acquisition, source expansion.

Mode: HOLD SCOPE (user, 2026-10-10). The scope is frozen by the
2026-10-09 directive + pipeline entry; the review maximizes rigor on
determinism, failure modes and calibration, and neither adds nor cuts.

## ARCHITECTURE

Delta vs persistent T-docs (drift rule): this unit's ARCHITECTURE wins
for unit scope. The persistent `data_model.md` design-ahead block is
superseded-in-advance on naming (decision il1) — see DECISIONS.

### Dependency graph

```
raw/instructions ──> raw/interpreter ──creates──> raw_<source_id>  (built, v0.3.0)
                         │                          (instruction-dynamic schema,
                         │                           row_key + sha256, runtime)
                         │                                 │  read-only
     cli.py ─────────────┼──────────────> identity/resolve (NEW: 0013 tables)
                         │                   ├─ normalize.py (EXTEND: token-set order-
                         │                   │   insensitive; MA9 seed CSVs)
                         │                   ├─ per-source adapters (NEW: ecat, basta)
                         │                   ├─ ensure link schema (product_uuid FK+idx)
                         │                   └─ match-or-create → manufacturer / product
     cli.py ─────────────────────────────> identity/enrich (NEW: majority fill/replace)
                                         identity/match   (NEW: block → score → verdict)
                                              └─→ linkage_candidate + review queue
```

Coupling: one-directional, read-only — identity reads raw; raw never
learns about identity (back-link ensured by identity, `raw/` untouched).
`match` reads only canonical tables, never raw. No daemons.

### Data flows (four paths each)

| Flow | happy | nil | empty | error |
|---|---|---|---|---|
| resolve: raw row → adapter → normalize → match-or-create → back-link | linked | optional fields blank | raw table 0 rows → no-op summary line | missing expected column → named refusal (adapter validates at start) |
| enrich: canonical field → scan occurrences → majority | fill-if-empty; strict-majority replace | no occurrences → keep value | tie → never wins (MA13) | raw table dropped since resolve → named failure, not silent 0-count |
| match: canonical pairs → block → score → verdict row | verdict stored | no candidate in block → no row | whole run 0 pairs → explicit zero-state report | scoring lib absent → named import error (MA8 decides which lib) |
| uuid derivation: norm string → uuid5 | stable forever | — | empty norm string → guard refusal (never mint) | — |

### State machine — linkage_candidate (the unit's one stateful object)

```
created ──score band──> auto_match | review | no_match
                review ──human──> confirmed | rejected
```

Invalid transitions prevented by construction: verdict flips happen only
as NEW candidate rows (append-only corrections, MA5/D5); `auto_match`
never enters review (already exact-key linked). verdict NOT NULL;
corrections never DELETE. Canonical records: uuid + normalized key
immutable at creation; only enrichment fields mutate (MA13 rules).

### Error model (Section 2 registries — failure classes + rescues)

| codepath | failure class | rescued? | rescue action | user sees |
|---|---|---|---|---|
| resolve adapter | SourceMissingError (raw table absent) | Y | skip source, continue | named line + count in summary |
| resolve adapter | SourceSchemaError (expected column absent/renamed) | Y | refuse that source | named error + offending column |
| resolve adapter | ManifestDriftError (manifest_hash ≠ recorded, il2) | Y | refuse source, offer rebuild | "run identity rebuild" |
| resolve normalize | NormalizeError (blank manufacturer / blank ident+name) | Y | skip row + count | skipped-row total per source |
| resolve normalize | EmptyNormError (norm collapses to empty) | Y | refuse row + count | refused-row total |
| resolve match-or-create | IntegrityError (UNIQUE violation) | N (loud) | run failed, batch rolled back | traceback, exit 1 — a bug by construction |
| resolve | crash mid-run | Y | committed batches stay; re-run idempotent (il5) | re-run completes, no dupes |
| enrich | SourceMissingError (raw dropped since resolve) | Y | refuse source | named error |
| enrich | majority tie | — | rule: tie never wins (MA13) | n/a |
| match | MissingDependencyError (scoring lib absent) | N (loud) | refuse at command start | install hint / stdlib fallback line |
| match | zero canonical rows / zero pairs | — | explicit zero-state report | zero-state line |
| match | BlockTooLarge (> 500k pairs, il6) | Y | split + count | warning + block stats |
| rebuild | BackupError (pre-DROP backup fails, d20) | N (loud) | abort before any teardown | named error, exit 2 |
| migration 0013 | any step fails | N (loud) | backup-first abort (d20) | named error |

The only swallow-and-continue class is row-level skip — never silent
(counted per source, in the run summary). Constraint violations are
impossible by construction (single writer, first-claim MA16): when one
fires it is a bug and stays loud. No silent + untested + unhandled rows.

### Posture

- **Scaling:** resolve over 198k rows = batched transactions (500/batch,
  raw-run precedent), minutes. Matching's primary block
  (`manufacturer_norm`) has a blow-up tail (a 10k-article manufacturer →
  5×10⁷ within-block pairs) → secondary blocking (ident prefix 4–6
  chars) is part of the design (perf detail in RUNS.md planning).
- **SPOF:** normalization rules mint uuids (MA15) — rule change ⇒ full
  re-derivation (user-accepted doctrine; rules + namespace live under
  version control).
- **Rollback:** the identity layer is 100% derived from raw state —
  recovery = DROP + re-run resolve (minutes); migration backup default
  (d20); as of il2 the recovery path is a named CLI verb
  (`identity rebuild`) offered by the manifest-mismatch refusal.
- **Security:** local CLI; public register data; no secrets; no new
  network surface; dynamic table names quoted (interpreter precedent).

## Starting context (from the PIPELINE entry, verbatim 2026-10-09)

intent: Identity layer first (user-directed 2026-10-09): canonical
manufacturer + product tables built from the raw source tables —
extract → normalize → match-or-create over UNIQUE normalized strings →
link (raw→product back-link FK, product→manufacturer FK); then an
enrichment pass completing canonical fields with the most-common raw
values. Cross-source collapse (exact keys, blocking, scored tiers — no
LLM matching) rides on top of these tables.

decisions carried: MA10–MA14 (MATCHING.md Stage 0 — column contracts,
typed composite ident_string, group-level identity, two-pass CLI,
coverage-scan extension columns); MA1–MA7/MA9 proposed — pin at this
unit's Design; MA13 (enrichment tie rules), MA15 (deterministic uuid5)
and MA16 (GTIN collision → review queue) user-confirmed 2026-10-09.

constraints: deterministic + idempotent (re-run = no-op); product data
only (D27); MA8 dependency call open (rapidfuzz vs stdlib).

non-goals: raw acquisition (v0.3.0, built), source expansion (v0.3.8).

concept source: `../../CONCEPT/MATCHING.md` (Stage 0 + MA register);
`../../CONCEPT/PIPELINE.md` (the v0.3.4 entry — verbatim source of the
context above).

## INTERFACES

### CLI surface (`leadhs identity …`)

| verb | purpose | exit codes |
|---|---|---|
| `identity resolve [--source ID] [--dry-run] [--batch N]` | pass 1: extract → normalize → match-or-create → back-link (per source or all) | 0 ok · 1 usage · 2 refused source / budget-class · 130 interrupt |
| `identity enrich [--dry-run]` | pass 2: majority fill/replace of canonical fields | same |
| `identity match [--dry-run]` | blocking → scoring → linkage_candidate verdicts | same; MissingDependencyError → 2 |
| `identity rebuild` | teardown + full re-resolve (il2 recovery verb) | BackupError aborts before drop → 2 |
| `identity status` | per-source identity state: manifest_hash consumed, back-link coverage, queue depth | 0 |

`--source` validates against the register (d8 id pattern). DB-init
preflight (d22) applies to all verbs.

### Run kinds (unified `run` table, d3)

`identity_resolve` · `identity_enrich` · `identity_match` — status,
per-source count details (rows, groups, created, linked, skipped,
refused), dry-runs excluded from report floors (d25 convention).

### Named error classes (the Section 2 registry is the contract)

SourceMissingError · SourceSchemaError · ManifestDriftError ·
NormalizeError · EmptyNormError · MissingDependencyError ·
BlockTooLargeError · BackupError (all carry one-line remedies).

### Migration 0013 content inventory

`manufacturer` (uuid PK; name_norm UNIQUE NOT NULL; name NOT NULL;
country; city; vat_id) · `product` (uuid PK; ident_string UNIQUE NOT
NULL; ident_nr NOT NULL; manufacturer_uuid FK; hs_code; eu_group; name;
brand; url — the MA10/MA14 contracts) · `identity_state` (per source:
consumed manifest_hash) · `linkage_candidate` (pair + method + scores +
evidence tier + verdict + review status; UNIQUE (row_a, row_b, method))
· lookups as needed (code constants for block caps live in code, il6).
Additive only; design-ahead block renumbers 0014–0020 (il1).

### Seed CSV contracts (dict/, il11)

`legal_forms.csv` (form,note) · `ident_prefixes.csv` (prefix,source_id)
— loaded by normalize; versioned in git; reviewed like the substance
dictionary.

## TESTING POSTURE

Offline, deterministic, no network in tests (PROJECT guidelines; this
unit is pure derivation over fixture DBs). Pyramid: many unit
(normalize, uuid, adapters, blocking caps), fewer integration (resolve
end-to-end, enrich, match bands, run rows), few system (CLI + rebuild
via CliRunner). No e2e — real-data verification is the live-op pass on
the 288k-row DB, user-tested (r03/r04 pattern), not automated. No
wall-clock assertions — perf is guarded structurally by the il6 caps.

Test diagram (codepath → type → happy/failure/edge):

    normalize            unit            order-insensitive ≙; NUL stripped; empty
                                         guard; NFKD
    uuid derivation      unit            stable; domain-separated; empty refuse
    ecat adapter         unit+int        group extraction; il3 map; SourceSchemaError
    basta adapter        unit+int        company-scoped article group key
    match-or-create      int             new vs existing; GTIN collision → review (MA16);
                                         back-link ensure fresh+existing
    resolve end-to-end   int             fixture → canonical; RE-RUN = NO-OP
                                         (hash-compare) ← determinism showcase
    enrich               int             fill-if-empty; strict majority; tie never;
                                         dropped raw table → named error
    blocking             unit+int        same-product pairs co-block; secondary auto (il6)
    scoring + bands      int             band edges; il9 human-row protection
    BlockTooLarge        unit            split + count at synthetic cap
    run rows / dry-run   int             run row + per-source details; dry-run zero-write
    CLI + rebuild        system          exit 0/1/2/130; rebuild = backup→drop→resolve;
                                         BackupError aborts BEFORE drop
    migration 0013       int             backup default; schema; no 0014+ collision

FINAL-test inputs (provisional, recorded in RUNS.md): double-resolve
hash-identity on the real DB; SIGKILL-mid-batch chaos re-run.

Calibration plan (procedure now, thresholds at first real run):
(1) fixture samples from the on-disk 100-row ECAT/BASTA CSVs;
(2) hand-label ~50 cross-source same-product pairs + ~50 non-pairs,
committed to the repo; (3) sweep rapidfuzz scorers (JW, token_set, DL),
record distributions; (4) pin bands: auto_match ≥ T_high with zero
labelled false-positives, review ∈ [T_low, T_high) capturing ≥80% of
true pairs; (5) sweep script + labelled set + thresholds committed —
recalibration = re-run the sweep, never a hand-edit.

## RISKS

| risk | mitigation | owner |
|---|---|---|
| score bands mis-calibrate → wrong auto-matches | calibration plan (labelled set + sweep); review queue; no silent merges | operator, first real run |
| normalization rule change → uuid churn | MA15 doctrine; versioned rules; `identity rebuild` (il2) | design, rules review |
| real-data field surprises (collisions within one manufacturer at scale) | live-op first pass user-tested; skipped/refused counts visible | build + user |
| review-queue volume unknown | bands tuned for low false-positive rate; queue report-rendered, queryable | operator |

## DECISIONS

*(local numbering il1…; concept MA register stays authoritative in
MATCHING.md — this section records unit-level design decisions only.)*

- **il1 (2026-10-10, Section 1 Issue 1, user A):** the identity layer
  owns the table names `manufacturer` + `product` (MA10 verbatim). The
  persistent data_model.md design-ahead block (org / product, labeled
  0013–0019) is superseded-in-advance on naming; the identity migration
  takes `0013` and the design-ahead block renumbers 0014–0020 (d36
  pattern). M1 reconciles (org → view/subordinate of manufacturer;
  formulation-product against the canonical spine) — OPEN ITEM.
- **il2 (2026-10-10, Section 1 Issue 2, user B):** manifest-change
  semantics — resolve records the `manifest_hash` it consumed per
  source (small state table in migration 0013); on mismatch it refuses
  that source with a named error and offers `identity rebuild`
  (teardown of canonical tables + back-links, then re-resolve over all
  sources). No mixed state, ever.
- **il3 (2026-10-10, Section 1 close):** ECAT code_type mapping pinned:
  EAN13/GTIN14 → `gtin:` (global); Internal Producer ID/Other →
  `article:` (manufacturer-scoped); no code → `name:` basis. BASTA is
  always `article:` (company-scoped article numbers; GTIN only lands
  via enrichment/coverage).
- **il5 (2026-10-10, Section 2, user ok):** identity operations are
  runs — recorded in the unified `run` table (d3) with kind codes
  (`identity_resolve`, `identity_enrich`, `identity_match`), status and
  per-source count details; batch commits every 500 rows (raw-run
  precedent); crash recovery = idempotent re-run, NO checkpoint
  machinery (a resolve pass is minutes — resume-by-re-run beats
  resume-by-checkpoint on simplicity and auditability). Dry-run support
  rides the house dry-run discipline.
- **il6 (2026-10-10, Section 2, user ok):** block-size caps exist from
  day one — secondary blocking (ident prefix 4–6) auto-applies above
  50,000 pairs in a primary block; hard cap 500,000 pairs per
  block-group, beyond which the group is split and counted
  (BlockTooLarge path), never scored silently. Numbers recalibrate at
  the pilot with the score bands.
- **il7 (2026-10-10, Section 3):** MA8 decided — **rapidfuzz**, exact
  version pinned in pyproject (D16's one-package extension slot, BSD,
  vanilla-Windows wheels, 50–100× pure Python at block scale; it IS the
  reference implementation the hand-rolled path would have to be
  verified against).
- **il8 (2026-10-10, Section 4):** normalization strips control
  characters before folding (NUL bytes survive SQLite TEXT; never enter
  a normalized key). Identity commands take BEGIN IMMEDIATE per batch —
  a concurrent writer fails fast with a named SQLITE_BUSY error; serial
  operator discipline stays the house rule (raw-run pattern); il2
  manifest check covers post-hoc drift.
- **il10 (2026-10-10, Section 5):** `normalize.py` stays the single
  shared module — identity imports it; token-set order-insensitivity and
  control-char strip land there (fu7 staging consumers benefit; staging
  is rebuildable from archive, so changed norms are safe). Two
  normalizers would be the DRY violation.
- **il11 (2026-10-10, Section 5):** seed CSVs live in
  `src/leadhs/dict/` (`legal_forms.csv`, `ident_prefixes.csv`) — the D6
  pattern; versioned, reviewed, loadable.
- **il12 (2026-10-10, Section 5):** per-source adapters are plain
  functions + a registry dict (no framework), each defining its group
  key — ECAT `(licence_number, product_or_service_name)`, BASTA
  `(company_id, article_number)`; resolve iterates GROUPS, not rows
  (MA12).
- **il9 (2026-10-10, Section 4):** match re-run semantics — candidate
  pairs UNIQUE (row_a, row_b, method); a re-run updates only
  machine-owned rows (auto_match/no_match/pending review); human-decided
  rows (confirmed/rejected) are never touched and the protected count is
  reported. Human corrections remain append-only new rows (MA5/D5).
- **il13 (2026-10-10, Section 7):** resolve keeps an in-memory
  normalized-key index (bulk-loaded per run, write-through; ~300k keys ≈
  tens of MB); inserts via executemany batches. No per-row SELECT loops.
- **il14 (2026-10-10, Section 7):** enrich is set-based SQL — one
  GROUP BY aggregation per canonical field over the raw tables, majority
  by count ordering, ties detected in SQL and never applied (MA13).
  Never a per-record Python scan.
- **il15 (2026-10-10, Section 8):** `leadhs doctor` gains an identity
  section: back-link coverage (back-links = raw rows − skipped),
  orphaned-back-link detection, per-source manifest drift (il2's check,
  queryable without running resolve).
- **il4 (2026-10-10, Section 1 close):** uuid namespace pinned:
  `uuid5(uuid.NAMESPACE_URL, "https://github.com/fsncps/lead_HS#identity-v1")`;
  domain prefixes `manufacturer:<name_norm>`, `product:<ident_string>`.
  The URL is a project identifier, never fetched.

## OPEN ITEMS

- M1 reconciliation of the design-ahead catalog block against the
  canonical spine (il1) — at M1's design, not this unit. (Bubble-up to
  data_model.md OPEN ITEMS at record time.)
- ECAT code_type → ident-type mapping (OPEN-NOW): EAN13/GTIN14 → gtin;
  Internal Producer ID/Other → article; else name-basis — pin in
  Section 1 (pending Issue 2+).
- uuid5 namespace constant: pin exact value at Design (prototype
  candidate `uuid5(NAMESPACE_URL, "https://github.com/fsncps/lead_HS#identity-v1")`
  + `manufacturer:`/`product:` domain prefixes).
- Score-band calibration plan: thresholds unpinned until the labelled
  pilot; the calibration PROCEDURE must be designed (Section 6/7).
  Related pins landed: block caps il6, dependency il7.
- Bubble-ups to drain at record time: data_model.md "name_base dedup
  rules — Phase-1 pilot" OPEN item → resolved-by-reference to
  MATCHING.md; DESIGN/MASTER.md State stale (v0.3.0 shipped, v0.3.4
  active).

## SKILL RECORDS

(3sm-design-unit / 3sm-design-master passes; append-only)

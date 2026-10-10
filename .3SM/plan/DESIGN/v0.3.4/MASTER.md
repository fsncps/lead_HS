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
  (d20).
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

(authored as sections decide them)

## TESTING POSTURE

(authored at Section 6)

## RISKS

(authored as sections decide them)

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
- MA8 dependency call: rapidfuzz vs stdlib-only (pin at Section 3/6).
- Manifest-change semantics (Section 1 Issue 2 — pending).
- Bubble-ups to drain at record time: data_model.md "name_base dedup
  rules — Phase-1 pilot" OPEN item → resolved-by-reference to
  MATCHING.md; DESIGN/MASTER.md State stale (v0.3.0 shipped, v0.3.4
  active).

## SKILL RECORDS

(3sm-design-unit / 3sm-design-master passes; append-only)

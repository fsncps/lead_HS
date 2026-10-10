# lead_HS — CONCEPT PIPELINE

The unit queue. Concept plans no units: entries capture intent, mature to
INIT-READY, and the user's `/init-unit` command does the rest. Law:
capture-not-placement (no code recon — orientation comes from the DESIGN
M-docs); ≤12 visible entries, overflow archives to
`CONCEPT/_archive/PIPELINE/`; entries stay lean (~15 lines).

Sections: **ACTIVE** (unit dir exists), **NEXT-UP** (maturing or
init-ready), **PARKED** (deliberately shelved). Shipped/abandoned entries
move to the archive with their end-date.

# ACTIVE

(none — v0.3.4 shipped 2026-10-10)

# NEXT-UP

### v0.3.5 — enrichment pass (ex-v0.3.4 r02)
status: INIT-READY (spawned 2026-10-10 at v0.3.4 early close; branch
  id free)
intent: complete canonical manufacturer/product rows from their
  per-source observations — majority fill/replace per MA13 over the
  r01 back-links (288,138 rows → 271,005 products / 2,857
  manufacturers already resolved, 100% linked)
carries: archived RUNS.md r02 entry (`DESIGN/_archive/v0.3.4/`) as
  the plan payload; deferred FINAL inputs (SIGKILL chaos, full
  `identity rebuild` round, SQLite<3.35 pin, staging-norm recompute)
constraints: deterministic + idempotent; product data only (D27)
updated: 2026-10-10

### v0.3.6 — matching layer (ex-v0.3.4 r03)
status: MATURING (pends v0.3.5 DELIVERED — match reads enriched
  fields)
intent: cross-source collapse on the canonical tables — blocking +
  scored tiers (exact keys first, then Jaro-Winkler / token-set with
  small candidate blocks), verdicts auto_match/review/no_match in
  linkage_candidate, review-queue visibility in reports
carries: archived RUNS.md r03 entry; il6 block caps; `ident_prefixes`
  / `legal_forms.csv` repo move (open item)
constraints: no LLM matching; score-band calibration pins at its
  planning; MA8 dependency call (rapidfuzz vs stdlib) open
updated: 2026-10-10


### v0.3.8 — source expansion via generic bulk import
status: MATURING
intent: Streamlined scraping/import pipeline so additional sources
  become raw tables without bespoke code (same-shape sources: manifest
  + seed CSV + raw init/seed); entry gate de5. **Candidate order
  refreshed 2026-10-04 (DATA_SOURCE.md research round):** BASTA
  whole-load via the pinned anonymous API (no filter needed for raw
  load — closest to ECAT-class, 195k) → INIES Export API → Blue Angel
  (Drupal search walk, "70,000 products") → KemiDigi open data →
  retail batch (OBI/toom/hagebau/ManoMano/K-Rauta-class; Hornbach
  template proven). **Round-2 outcome (same day): BASTA whole-load
  DONE — 198,742 rows in `raw_as33_basta`, 0 truncated, audit clean;
  INIES refused (subscription-gated API), Blue Angel unwalkable now
  (token POST search), KemiDigi blocked (CKAN 403), environdec pinned
  as reserved html_pages record — the next real candidates are the
  retail batch and the html_pages walker (AS-3 re-acquisition).
  D45 scope addition: instruction = table shape ×
  ACCESS MODE (open enum, `SOURCE_ACCESS_MODES.md`) — probe ladder
  L0–L7 (`probe source` deep-probe) classifies each source;
  interpreters phase in file → API → walk/form (html_pages walker =
  first walk mode; AS-3 re-acquisition is the reference case after
  the 2026-10-03 route death).
decisions:
  - R8 proposed (RAW_SOURCING.md) — onboarding without pipeline-code
    changes for same-shape sources
  - D45 (SOURCE_ACCESS_MODES.md, 2026-10-04) — access-mode enum +
    probe ladder; run refuses unknown/unimplemented modes by name
  - 2026-10-04 user direction — corpora need: EU market, paint-rich,
    manufacturer + unique id, HS-linkable field; retailers approved;
    ≥10k records per corpus; ≥1–2 more ECAT-class sources
constraints: de5 gate applies to SAMPLES, not to raw loads (load
  whole, filter downstream); politeness budget per source;
  facet_enumeration politeness rule must exist before any facet loop
  runs
non-goals: MSE/capture-recapture methodology turn (separate decision,
  INPUT digest)
readiness: candidate order + gate mechanics at unit start (OPEN-NOW);
  mode enum naming + per-mode fields pin at unit design
updated: 2026-10-04

# PARKED

### v0.4 — vanilla-Windows installer + deferred preliminaries
status: PARKED
parked because: user decision 2026-10-03 (D42) — everything deferred
  from earlier preliminary planning lands here, after the v0.3 data
  program; D32 (self-contained Windows artifact, mechanism open) is
  the anchor decision
updated: 2026-10-03

# DECISIONS

Authoritative register: `MASTER.md` (this directory). Latest:
- **D42** — unit numbering resolved: v0.3 = product-DB turn; Windows
  installer + deferred preliminaries → v0.4; analysis after v0.3.x.
- **D43** — v0.3 sub-roadmap: v0.3.0 db + bulk download → v0.3.4
  normalization/matching (manufacturer × unique id) → v0.3.8 generic
  bulk-import source expansion.
- **D44** — raw-layer completeness mandate: every record (stubs/nulls/
  dupes); verbatim source headers; 1 KB default per-record budget;
  deterministic truncation, never drop (amends R3 spill).

# OPEN ITEMS

- OPEN-NOW (v0.3.4): MA adoption pinning (MA1–MA16); MA8 dependency
  call; ECAT code_type mapping; score-band calibration plan.
- OPEN-NOW (v0.3.8): candidate source order; gate mechanics.
- NON-BLOCKING: BASTA paint-subset filter (de5; TODOS.md), ECAT
  17,838-vs-38,233 reconciliation — standing threads, CONCEPT MASTER
  OPEN ITEMS authoritative.
- PENDING (not this stage's write scope): `plan/MASTER.md` STATE +
  ROADMAP still say "next-unit decision OPEN" — sync by a permitted
  pass (housekeeping/build context) from the text in this pipeline's
  DECISIONS + CONCEPT MASTER ROADMAP.

# SKILL RECORDS

### 3sm-concept-pipeline CAPTURE+PREPARE — 2026-10-09
scope: open-item confirmations (MA13 ties, MA16 GTIN collisions,
MA15 uuid decision prior); v0.3.4 matured to INIT-READY; v0.3.0
entry reconciled to built state
checklist:
- [x] capture — user confirmed both remaining proposals as proposed
  (enrichment strict-majority/ties; GTIN first-claim-wins + review
  queue) — MA13/MA16 updated — OK
- [x] prepare v0.3.4 — id free (no unit dir/branch); theme
  user-confirmed (identity-layer directive, "proceed to design");
  no parallel-unit conflict (v0.3.0 build complete, finalize
  pending — user's sequencing call); OPEN-NOW items are Design
  deferrals → INIT-READY — OK
- [x] audit — drift found and recorded in-entry: v0.3.0 built but
  entry said INIT-READY/NEXT-UP; unit MASTER still stage: DESIGN —
  housekeeping/ship-gate territory, flagged — OK
findings: CRITICAL GAP 0 · WARNING 1 (v0.3.0 lifecycle bookkeeping
lag; finalized via user's ship gate) · unresolved 0
carries: design may take MA10–MA16 + Stage 0 contracts as decided
(no re-derivation); MA1–MA9 pin at Design as planned
valid-until: user revisits the Stage 0 contracts or the v0.3.4 scope
commit: <lands in this pass's commits>

### 3sm-concept-pipeline CAPTURE+PREPARE — 2026-10-03
scope: PIPELINE.md created (was absent); v0.3 program adoption captured;
v0.3.0 matured to INIT-READY
checklist:
- [x] startup — PROCESS* + PROJECT + plan/MASTER + CONCEPT MASTER read;
  PIPELINE absent → created from 3sm-setup template — OK
- [x] mode — CAPTURE (user decisions) rolling into PREPARE (v0.3.0) — OK
- [x] capture — D42 (numbering), D43 (sub-roadmap), D44 (completeness +
  truncation, amends R3) landed in CONCEPT MASTER + RAW_SOURCING.md;
  MATCHING.md repointed to v0.3.4 (MA8 typo fixed) — OK
- [x] prepare v0.3.0 — id free (no unit dirs/branches/registry entries);
  theme user-confirmed; no parallel unit; no OPEN-NOW (manifest field
  lists + R9 are Design-stage deferrals) → INIT-READY — OK
- [x] audit — git log vs docs consistent (today's reconciliation
  commits); no drift beyond the plan/MASTER sync noted above — OK
findings: CRITICAL GAP 0 · WARNING 0 · unresolved 0
carries: design may take the v0.3 numbering + D44 truncation rules as
  decided (no re-derivation); RAW_SOURCING R4–R8 + R9 and MA1–MA9 pin
  at the consuming units' Design
valid-until: canonical/template change, or the user revisits the v0.3/v0.4
split
commit: <lands in this pass's commits>

# REFERENCES

Archive: `CONCEPT/_archive/PIPELINE/` holds shipped + abandoned entries
verbatim (empty — no unit has run under the v2 pipeline yet).

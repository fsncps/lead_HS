---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-09
---

# MATCHING — product identity, string matching and cross-source dedup

## Abstract

How the study will build the product evidence database from multiple
sources (ECAT, Nordic Swan, BASTA, retail/manufacturer catalogues —
the de5-confirmed bulk sources and future ones) and match records for
the **same product across sources**: normalize manufacturer names and
product identifiers into comparable keys, join on exact keys first,
then score near-matches with classic record-linkage algorithms —
**without LLM/embedding support**. This operationalizes the identity
tuple of D33 (CN8 code, manufacturer, manufacturer product-ident), the
v0.2.2 overlap-matching key ("normalized manufacturer + product
ident"), and the D2 formulation + sighting dedup layer. The immediate
driver: the v0.3-era product-DB seeding, where ~200k-row sources
(BASTA 195,391 articles pinned 2026-09-17) must be matched against
17,013 ECAT and 2,322 Nordic Swan distinct products. Status: method
proposal converged in the 2026-09-17 concept session; the product-DB
program is adopted (MASTER D42/D43, 2026-10-03) and this topic rides
unit **v0.3.4** — MA pinning and the dependency call (MA8) at that
unit's Design. Stage 0 (the canonical identity layer: manufacturer +
product tables built deterministically from the raw tables) is
**user-directed 2026-10-09** — column contracts, identity scheme and
the two-pass CLI flow recorded below.

## Problem statement

One product appears in several sources with variant spellings:
manufacturers differ in legal form and punctuation ("Foo-Bar Ltd." vs
"Foo Bar Limited."), identifiers differ in prefix, separators and
zero-padding ("ABC-123/B" vs "abc00123b"). The database must (a) keep
every source observation as its own verbatim record (provenance-first,
D17), (b) collapse them onto one formulation-level `product` (D2) with
the match evidence auditable, and (c) count cross-source overlap
correctly — which feeds the capture-recapture/MSE denominator question
filed in `INPUT-source-expansion-MSE.md`.

## Why not embeddings / LLM matching

- **Reproducibility (D4):** a model version change silently changes
  matches; this project's runs are seeded and audited. Rule-based
  normalization + edit-distance scores are deterministic and re-runnable.
- **Auditability (D17):** "Jaro-Winkler 0.94 on normalized names, legal
  form stripped" is explainable to a reviewer; "0.87 cosine similarity"
  is not.
- **No gain:** the noise is orthographic/structural (legal forms,
  prefixes, dashes, padding, diacritics) — *rule-shaped*, not
  meaning-shaped. Embeddings pay off when semantics vary ("Blau" ≙
  "Bleu"); here a diacritic-strip rule handles that deterministically.
- **Constraint fit (D16, D32):** no new heavyweight dependency, no
  vector store, vanilla-Windows portability preserved.

## Method — stages 0–5

### Stage 0 — canonical identity layer (user-directed 2026-10-09)

Before any cross-source scoring, build the canonical **manufacturer**
and **product** tables from the raw source tables, deterministically:
extract → normalize → match-or-create over **UNIQUE normalized
strings** → link. All later matching (Stages 1–5) operates on these
tables, never re-normalizes raw rows.

**Column contracts** (concept altitude; DDL is Design's):

    manufacturer — uuid PK; name_norm UNIQUE NOT NULL; name NOT NULL;
      country; city; vat_id.
    product — uuid PK; ident_string UNIQUE NOT NULL; ident_nr NOT NULL;
      manufacturer_uuid FK → manufacturer; hs_code; eu_group;
      name; brand; url (the last three per coverage scan, below).
    every raw source table — one added column product_uuid FK →
      product (back-link; sighting rows stay raw and verbatim, MA6).

**Identity scheme:**

- Uniqueness binds the *normalized string*. `ident_string` is a typed
  composite: `gtin:<norm>` is globally unique, while
  `article:<manufacturer_norm>:<norm>` and
  `name:<manufacturer_norm>:<name_norm>` are **manufacturer-scoped** —
  article numbers and product names collide across manufacturers, so
  the uniqueness constraint must carry the manufacturer key for
  anything that is not a global identifier.
- **Group-level identity:** one canonical product per natural product
  group, sighting rows collapse onto it. ECAT group =
  (licence_number, product_or_service_name) — of 80,847 groups, 3,925
  carry multiple codes (2,226 multi-EAN variants; 851 mixed code
  types), so row-level identity would split one product into variants.
  BASTA group = (company_id, article_number) — article_number alone is
  NOT unique (193,456 distinct over 198,742 rows) but company-scoped
  it is.
- **Deterministic and idempotent:** a re-run over the same raw state
  must be a no-op (match-or-create on normalized keys). UUIDs are
  **deterministic (MA15, user decision 2026-10-09):**
  `uuid5(project namespace, normalized key)`. Two key regimes: the
  normalized string is the *ingress* key — how new raw entries match
  into the canonical tables; within and after the canonical tables the
  **uuid is always the key** (raw back-links, enrichment, every later
  layer reference by uuid). Known consequence: a normalization-rule
  change can mint a new string (→ new uuid) for an unchanged real
  product; the documented recovery path is a full re-derivation of the
  layer (re-links every back-link consistently — the "re-run when
  rules improve" doctrine).

**Coverage scan** — extension columns warrant a canonical column only
when "common to a large enough number of records" (user rule). Scan of
the loaded raw tables (recorded numbers, 2026-10-04 loads):

| candidate | coverage | verdict |
|---|---|---|
| manufacturer country | ECAT 100% | include |
| manufacturer VAT-ID | ECAT 93.2% | include |
| manufacturer city | none loaded (Nordic Swan carries it) | reserved, blank |
| product name | ECAT + BASTA 100% | include |
| eu_group | ECAT group_name 100% | include (the EU product-group identifier the directive asks for) |
| brand | BASTA 76.4% | include |
| url | BASTA article_url 100% | include |
| hs_code | no source carries it | reserved, blank |

BASTA BK04/BSAB are national classifications — stay raw-side, not
canonical columns.

**Two CLI passes** (user-directed flow):

1. **Resolve pass** — loop the raw source tables; per record:
   normalize manufacturer + product ident; match-or-create both
   (fill mandatory fields from the creating raw record; add whatever
   optional fields that record carries; leave the rest blank); link
   product → manufacturer; back-link raw row → product.
2. **Enrichment pass** — loop the canonical records; scan all
   occurrences of company name, country, VAT-ID, identifiers etc.
   across the source tables; complete the canonical fields with the
   most common value. Refinements user-confirmed 2026-10-09 (MA13):
   fill-if-empty always takes the majority value; an existing value is
   replaced only on a strict majority; ties never win — deterministic
   and self-healing.

### Stage 1 — Deterministic normalization (the workhorse)

Normalization solves most matches before any scoring. Originals stay
untouched; normalized forms are derived columns, always re-derivable
(re-run when rules improve — nothing corrupts).

**Manufacturer normalization** (target: `manufacturer_norm`):
1. Unicode NFKD, strip diacritics;
2. casefold;
3. strip punctuation to spaces;
4. remove legal-form tokens **as whole tokens** (table below, repo
   seed CSV like the compound dictionary, D6 pattern);
5. collapse whitespace; order-insensitive token set (handles
   "Foo Bar" ≙ "Bar Foo").

"Foo-Bar Ltd." and "Foo Bar Limited." both → `foo bar` — exact join,
no fuzzy step needed.

**Identifier normalization** (target: `ident_norm`):
1. uppercase; strip everything non-alphanumeric; strip leading zeros
   **except on GTIN/EAN** (fixed-width, check-digit position — zeros
   are significant);
2. strip known manufacturer prefixes (prefix table built empirically
   from the staged data, updated as sources join).

"ABC-123/B" and "abc00123b" → `ABC123B`.

**Name normalization** (target: `name_base`, closes the DATA_MODEL
OPEN item): brand + core name minus colour/size/pack tokens — the D2
variant-collapse rule made concrete; keep language as-is (D17
multilingual-by-default; colour-word stripping must be language-aware —
pilot calibration).

Legal-form token seed list (to be completed per source country before
each source joins): Ltd, Limited, GmbH, AG, SA, SAS, SARL, NV, BV, AB,
AS, A/S, ApS, Oy, Oy Ab, SpA, SRL, Srl, KG, OHG, Inc, LLC, LLC-style
variants, AS/ASA (NO), OÜ, s.r.o., d.o.o., z.o.o., Kft, AB-LU variants.
Country coverage grows with the source register.

### Stage 2 — Exact keys first (strongest evidence, zero false positives)

- GTIN/EAN exact (ECAT EAN: licence coverage 100% per v0.2.4 sample;
  BASTA carries GTIN on article pages);
- normalized identifier exact (`ident_norm`) within same
  `manufacturer_norm`;
- normalized manufacturer exact (`manufacturer_norm`) as the blocking
  backbone (Stage 3).

### Stage 3 — Blocking (makes 200k+ rows tractable)

Never score all pairs (~2×10¹⁰ for BASTA alone). Candidate pairs come
from blocks only:

- `manufacturer_norm` exact (primary block);
- identifier prefix (first 4–6 chars of `ident_norm`);
- GTIN;
- Double Metaphone key on manufacturer name (catches spelling variants
  across the manufacturer block; pure-Python implementation exists).

With ~215k rows total this is seconds-to-minutes territory in SQLite +
Python.

### Stage 4 — Similarity scoring within blocks

- **Jaro-Winkler** — identifiers and short names (prefix weighting
  suits "Dulux" ≙ "DuluxPro");
- **token-set similarity** — multi-word product names (reordering and
  extra colour/size tokens; extra variant tokens are wanted collapses
  per D2 anyway);
- **Damerau-Levenshtein** — tiebreaker, catches transpositions.

### Stage 5 — Tiered verdicts, never auto-merge

Score bands → three states, stored per candidate pair (mirrors the
`sds_finding.review_status` pattern; append-only corrections per D5):

- `auto_match` — high score, ideally exact-key backed;
- `review` — middle band, human queue;
- `no_match`.

Every candidate pair is a row: both record refs, match method,
per-component scores, normalized keys, verdict, review status. Manual
corrections are new rows / status changes, never deletes.

## Evidence tiers

Name similarity alone is **low-confidence evidence** (the consultant
handover's linkage-quality table agrees: fuzzy-name-only = low). The
match table records *which* tier produced each link so downstream
lead-prevalence analysis can weight accordingly:

1. GTIN/EAN exact — highest;
2. `ident_norm` + `manufacturer_norm` both exact;
3. identifier + manufacturer high-similarity (scored);
4. name_base + manufacturer_norm (scored) — review band by default;
5. name-only — never auto-matched.

**Source-dependency caveat (handover §17, verified in our register):**
ECAT + Nordic Swan are one family; BASTA ↔ eBVD exchange data. Matches
*within* a dependency family must not count as cross-source
corroboration or as independent capture-recapture lists — the
`independence_group` column of `data_sources.csv` (D38) is the carrier.

## Storage placement

Not in the raw source tables. Raw tables stay verbatim (they are the
evidence). Additions:

- derived normalized columns (or parallel `*_norm` table keyed to the
  raw row) — re-derivable;
- a `linkage_candidate` table (pairs + method + scores + verdict +
  review status) — the auditable dedup layer feeding `sighting` →
  `product` collapse (D2) and the cross-source overlap counts
  (v0.2.2-style Q2 union, future MSE inputs).

Schema sketch (concept altitude, Design normalizes):

    linkage_candidate — id, source_row_a, source_row_b (refs into
    per-source staging tables), manufacturer_score, ident_score,
    name_score, evidence_tier, verdict (auto_match/review/no_match),
    review_status, review_note, decided_by, created_at.
    Both refs carry full provenance through their source rows (D17).

## Library decision

| Option | Verdict |
|---|---|
| `difflib` (stdlib) | SequenceMatcher slow, weak ratio for this task; pilot-only at 17k rows |
| **`rapidfuzz`** (proposed) | C++ wheels incl. vanilla Windows (D32-compatible), Jaro-Winkler/token ratios/Damerau in one API, BSD; one small well-justified dependency on top of requests/bs4/click/jinja2/pypdf |
| hand-rolled Jaro-Winkler + Double Metaphone | viable, keeps dependency set at zero, ~200 lines pure Python; adequate with blocking at this scale |

Recommendation: **rapidfuzz for scoring, hand-rolled pure-Python for
normalization + blocking** (trivial string ops). If the dependency
line is held absolutely, hand-rolled everything works — tradeoff to
pin at adoption (M8).

## DECISIONS

*(local numbering MA1…; promotion to MASTER decisions at the next
concept turn / unit Design — nothing frozen.)*

- **MA1 (proposed):** algorithmic record linkage only — no LLM or
  embedding-based matching in the pipeline. Rationale: reproducibility
  (D4), auditability (D17), rule-shaped noise, constraint fit (D16/D32).
- **MA2 (proposed):** normalization-first — deterministic
  normalization rules (Stage 1) are the primary matcher; fuzzy scoring
  only within blocks, only for what normalization missed.
- **MA3 (proposed):** exact keys outrank scores — GTIN/EAN and
  normalized identity-tuple joins are `auto_match` evidence; scores
  never override an exact key, and a low score never splits one.
- **MA4 (proposed):** blocking mandatory at scale — no O(n²) pairwise
  scoring against ≥100k-row sources.
- **MA5 (proposed):** tiered verdicts, no silent auto-merge —
  `auto_match` / `review` / `no_match` bands; `review` band requires
  human confirmation; every pair stored with method + scores.
- **MA6 (proposed):** verbatim raw rows; normalized forms and match
  verdicts live in derived tables/columns only.
- **MA7 (proposed):** evidence tier recorded per link; name-only links
  never auto-match; dependency families (ECAT+Nordic Swan; BASTA+eBVD)
  never count as independent cross-source evidence.
- **MA8 (OPEN, dependency call):** rapidfuzz (recommended) vs
  hand-rolled pure-Python — decide at the product-DB unit's Design,
  together with the wheel-dependency budget (extends D16's list by at
  most one package).
- **MA9 (proposed):** normalization token tables (legal forms,
  identifier prefixes, colour/size words) are repo seed CSVs like the
  lead-compound dictionary (D6 pattern) — versioned, reviewed, source
  of truth for `name_base` rules.
- **MA10 (user-directed 2026-10-09):** canonical identity tables
  precede all matching — one `manufacturer` and one `product` table
  built from the raw tables by deterministic extract → normalize →
  match-or-create; normalized strings are UNIQUE and are the only
  match keys; raw tables gain a `product_uuid` back-link column.
- **MA11 (proposed, from the directive):** typed composite
  `ident_string` — `gtin:` globally unique; `article:` and `name:`
  manufacturer-scoped (non-global identifiers collide across
  manufacturers; uniqueness must include the manufacturer key).
- **MA12 (proposed, scan-driven):** group-level identity — ECAT
  (licence, product name), BASTA (company, article number); multi-code
  sighting rows collapse onto one canonical product; raw rows keep
  provenance.
- **MA13 (user-directed, refinements confirmed 2026-10-09):** two CLI
  passes — resolve (match-or-create, fill-at-creation from the
  creating raw record, missing → blank) and enrichment (re-scan
  occurrences, complete with most-common value; confirmed rules:
  fill-if-empty by majority, replace only on strict majority, ties
  never win).
- **MA14 (proposed, from the directive):** canonical extension columns
  only per coverage scan ("common to a large enough number of
  records") — included: country, vat_id, name, eu_group, brand, url;
  reserved: city, hs_code.
- **MA16 (user-confirmed 2026-10-09):** cross-manufacturer GTIN
  collisions (the same global ident claimed by two manufacturers):
  first claim wins and keeps the row; every collision is counted and
  the list feeds the review queue (MA5 verdict pattern) — never
  silently resolved.
- **MA15 (user decision 2026-10-09):** deterministic UUID derivation —
  `uuid5(project namespace, normalized key)` (name_norm for
  manufacturer, ident_string for product); namespace constant pinned
  in the repo at Design. The normalized string is the ingress match
  key; after creation the uuid is the key everywhere (back-links,
  enrichment, downstream layers). Rule changes that alter normalized
  strings require a full layer re-derivation to stay consistent.

## OPEN ITEMS

- ECAT code_type → ident-type mapping (EAN13/GTIN14 → gtin; Internal
  Producer ID/Other → article; else name-basis) — pin at Design.
- Stage-0 prototype note: an out-of-stage prototype (migration +
  resolve module + tests, 672 lines, drafted 2026-10-09, reverted
  same day) is kept non-authoritative at `/tmp/opencode/`
  (matching-prototype/) — Design may mine it, nothing in it is
  decided.
- Legal-form + identifier-prefix seed tables: populate per source
  country as sources join; validate against the staged ECAT/Nordic
  Swan/BASTA samples (100-row CSVs already on disk).
- `name_base` colour/size token stripping: language-aware rules —
  calibrate in the Phase-1 pilot (this closes the standing DATA_MODEL
  OPEN item; that item should be marked resolved-by-reference when
  this file is adopted).
- Threshold values for the score bands (MA5): calibrate on the staged
  samples + a manually labelled review batch before the first real
  cross-source run.
- UFI as join key (DATA_MODEL OPEN item): format validation and
  collision handling — ride the same pilot.
- `linkage_candidate` exact DDL + per-source staging-table shape:
  Design-level, next product-DB unit.
- BASTA↔eBVD and ECAT+Nordic-Swan dependency groups: confirm the
  `independence_group` values in `data_sources.csv` cover the matching
  use case (D38 column exists; values to review at adoption).
- MA8 dependency call (rapidfuzz vs stdlib-only).

## REFERENCES

- RAW_SOURCING.md — the upstream layer this method consumes: per-source
  raw record tables, natural keys + content hashes, `raw export` into
  the matching pipeline; raw layer precedes matching in the product-DB
  unit's phases.
- DATA_MODEL.md — D2 (formulation + sighting dedup layer), D17
  (provenance), OPEN item "Exact dedup/normalization rules for
  `name_base`"; `sds_finding.review_status` pattern.
- MASTER.md (this directory) — D16 (tooling/dependencies), D33 (product
  identity tuple), D38 (data_sources.csv + de5/de6 gates), D32
  (vanilla-Windows goal).
- legacy U-docs `docs/plan/3SM/10_STRATEGY/v0.2.2.md` (overlap-matching key
  "normalized manufacturer + product-ident") and `v0.2.4.md` — ECAT EAN
  coverage, BASTA keyfigures
  (195,391 articles / 1,925 companies, 2026-09-17) and article-page
  identity fields (article number, GTIN, RSK, E-number, BASTA ID,
  BK04/BSAB).
- INPUT-source-expansion-MSE.md — linkage-quality tiers, dependency
  groups (§17), capture-recapture context; `inputs/
  consultant-handover-2026-09-14.md` (verbatim, not adopted policy).
- Algorithms (public record): Jaro-Winkler, Damerau-Levenshtein,
  Double Metaphone, token-set ratio; rapidfuzz (BSD) as the proposed
  implementation.

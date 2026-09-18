---
unit: global
stage: STRATEGY
lifecycle: LIVE
updated: 2026-09-17
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
(BASTA 195,390 articles pinned 2026-09-17) must be matched against
17,013 ECAT and 2,322 Nordic Swan distinct products. Status: method
proposal converged in the 2026-09-17 strategy session; adoption as
numbered MASTER decisions and the dependency call (M8) await the next
strategy turn / the product-DB unit's Design.

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

## Method — five stages

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
1. uppercase; strip everything non-alphanumeric; strip leading zeros;
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

Schema sketch (strategy altitude, Design normalizes):

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
strategy turn / unit Design — nothing frozen.)*

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

## OPEN ITEMS

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
- 10_STRATEGY/MASTER.md — D16 (tooling/dependencies), D33 (product
  identity tuple), D38 (data_sources.csv + de5/de6 gates), D32
  (vanilla-Windows goal).
- v0.2.2.md — overlap-matching key ("normalized manufacturer +
  product-ident"); v0.2.4.md — ECAT EAN coverage, BASTA keyfigures
  (195,390 articles / 1,925 companies, 2026-09-17) and article-page
  identity fields (article number, GTIN, RSK, E-number, BASTA ID,
  BK04/BSAB).
- INPUT-source-expansion-MSE.md — linkage-quality tiers, dependency
  groups (§17), capture-recapture context; `_inputs/
  consultant-handover-2026-09-14.md` (verbatim, not adopted policy).
- Algorithms (public record): Jaro-Winkler, Damerau-Levenshtein,
  Double Metaphone, token-set ratio; rapidfuzz (BSD) as the proposed
  implementation.

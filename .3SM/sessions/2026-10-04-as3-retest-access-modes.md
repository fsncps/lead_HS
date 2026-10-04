---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-04
type: investigation
---

# S-rec — AS-3 re-test + access-mode taxonomy (2026-10-04)

## Trigger

User questions on v0.3.0 live results: (1) ECAT "193k?" conflation,
completeness/counting units; (2) Nordic Swan — re-test the csv
download, find the error if it succeeds, else it is the
reconstruction; (3) the pipeline must handle ALL kinds of source
access modes, not assume ECAT-style snapshots — "what possible kinds
of data sources requiring different access modes can you conceive?"

## ECAT answers (DB-verified)

- 89,396 distinct rows = the COMPLETE official export
  (`most-recent-export.csv`, extract_date 2026-10-03), ALL 25
  ecolabel groups — paint is 17,843 rows (~20%); tissue 17,097;
  furniture 11,680; textiles 11,512; PRODUCT 88,384 / SERVICE 1,012.
- All rows fetched (one snapshot request, 0 truncations, coverage
  anchor exact). 3,375 licences; 80,847 distinct licence×product
  pairs; 76,922 products carry exactly 1 row; code rows (EAN13 26,225
  / Internal Producer ID 5,220 / Other 4,084 / GTIN14 260; empty
  53,590) multiply the rest.
- "193k" = BASTA's 195,391 articles (D40, Sweden) — a different
  register, often co-cited. The old ECAT catalogue keyfigure
  (17,013, pinned 2026-09-14) vs the export's 80,847 licence×name
  pairs: counting-unit reconciliation flagged OPEN (downstream
  analysis question; the verbatim raw rows are ground truth either
  way).

## Nordic Swan re-test (all live, budgeted)

1. `?format=csv`: 404 twice (study UA + browser UA) — genuine death,
   not UA gating.
2. Redirect target `/en/content-search/` is a DECOY: site-content
   search (All/Articles/News/Criteria/Other); `type=markeds`
   silently ignored; plugin view.js = scroll handling only; no
   export endpoint in the front end.
3. `/en/products-and-services/` + category pages: editorial trees,
   no register search on svanen.se at all anymore.
4. Wayback CDX (L5): the true historical mode was
   `/ExportToCsv/?st=0&brand=X&p=N` — form-download + facet
   enumeration, alive ≥ 2025-10. All variants 404 live.
5. `format=csv` was NEVER archived by Wayback → our raw-store
   snapshot is the only existing copy. Verified offline:
   `data/raw/as-3/` holds 2 retrieval copies + 3 HTML blobs, both
   CSVs sha256-matched, 52,544 lines (header + 52,543 rows) × 10
   cols, exact header preserved.
6. ecolabel.dk sister-register check (ladder L6): NOT probed — user
   rejected the request; pending user decision.

Conclusion: no error in our scan/run — the reconstruction (snapshot)
is what exists, and it is verified loadable.

## The taxonomy (main deliverable)

New Concept topic `SOURCE_ACCESS_MODES.md`: instruction = table
shape (RAW_SOURCING) × access mode (this doc). 22 modes in 5 classes
(bulk file / APIs / form-query surfaces / HTML walks / indirect),
each with its required instruction fields; probe ladder L0–L7
(robots+sitemap → format params → API discovery → form inventory →
JS-bundle scan → CDX → cross-source → manual) classifies any source;
ladder evidence recorded in instruction notes. **D45**: access-mode
enum is open; run refuses unknown/unimplemented modes by name;
interpreter phasing (file → API → walk/form) is the v0.3.8 cost
decision. Wired into: RAW_SOURCING REFERENCES, MASTER topic index +
ROADMAP, PIPELINE v0.3.8 entry.

## Writes & permission note

Allowed-path writes only: SOURCE_ACCESS_MODES.md (new),
RAW_SOURCING.md cross-ref, MASTER index+roadmap, PIPELINE v0.3.8,
this S-rec; `raw_sources/AS-3.instruction.json` notes appended via
python3 (bash-allowed). Blocked by the tightened edit rules (left
undone, flagged): TODOS.md AS-3 entry addendum,
docs/study/DATA_SOURCE.md AS-3 addendum — user/build context can
apply them from the instruction notes + SOURCE_ACCESS_MODES.md
worked example.

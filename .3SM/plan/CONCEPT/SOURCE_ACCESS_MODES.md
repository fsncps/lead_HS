---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-04
---

# Source access modes — taxonomy + probe ladder (Concept)

> A source instruction is a **two-part contract: table shape × access
> mode**. RAW_SOURCING.md owns the table-shape part (columns, keys,
> guards, seed semantics). This document owns the access-mode part:
> the distinct ways a register can deliver data, the instruction
> fields each mode requires, and the systematic probe ladder that
> classifies an unknown source into one of them.
>
> Motivating failure (2026-10-03/04): AS-3 (Nordic Swan) was pinned
> and instructed as a static CSV snapshot because ECAT (AS-2) is one.
> Re-test showed AS-3 was never that — it was a **form-download +
> facet-enumeration** source (`/ExportToCsv/?st=0&brand=X&p=N`),
> whose app the 2026 site redesign retired entirely. The route died,
> the instruction assumption with it. See the worked example below.

## Abstract

Every acquisition target in this study — official product registers,
ecolabel databases, SDS aggregators — can be classified by **how data
is delivered**. The delivery mode, not the table shape, decides what
the instruction file must contain and what the interpreter must do.
The taxonomy below enumerates the modes we can conceive for the data
we seek; the probe ladder turns an arbitrary URL into a classified
mode + the evidence to author its instruction; the schema note says
how this reshapes the instruction contract (D45).

## Mode taxonomy

Grouped by delivery class. Cost axis: file modes are cheapest (one
polite fetch), APIs middle (query loops), form/facet/HTML walks the
most expensive (request multiplicity). Onboard a source on the
cheapest mode that yields *complete* data.

### A. Bulk file delivery (static — pull, then parse locally)

1. **file_snapshot** — single stable URL delivering the full
   dataset: CSV/TSV, Excel (XLSX/XLS), XML, JSON, SQL dump, even
   Access MDB or SQLite (the SPIN extraction already consumes MDB via
   mdbtools). Fields: url, format, encoding, delimiter/header
   semantics, optional sha256 pin, extract-date source. *ECAT/AS-2 is
   the reference case (`most-recent-export.csv`).*
2. **file_bundle** — one URL, container file (ZIP/7z/GZ/tar) holding
   several inner files (per-country, per-year, data+metadata); an
   Excel workbook's sheets are the same problem in miniature. Fields:
   url + inner-file selection rule + per-inner-file format.
3. **file_index** — no stable filename: a listing surface (HTML
   directory index, S3/bucket listing, a dated landing page) where
   the current file's URL changes. Fields: index url + selection rule
   (e.g. latest `YYYY-MM-DD` pattern) → then mode 1.
4. **ftp_sync** — FTP/FTPS/SFTP/rsync endpoints; legacy but real at
   statistics agencies and register operators. Fields: host, port,
   path, credential scheme (usually anonymous), single file vs walk.
5. **external_deposit** — curated deposit with stable identity
   (Zenodo/Dataverse DOI, open-data-portal resource, HuggingFace
   dataset). Fields: deposit id + resource + version pin. Bonus:
   citable and versioned by the operator.

### B. Structured APIs (live query)

6. **api_rest_anon** — public JSON API (BASTA `/apiproxy/v3`, the old
   ECAT catalogue). Fields: endpoint, query template, envelope
   unwrap path, pagination kind (none | page | offset | cursor |
   next-link), rate limits.
7. **api_rest_key** — same shape + free registration: auth placement
   (header/query), **env-var NAME reference (never the key value in
   the instruction or the repo)**, ToS note.
8. **api_oauth** — client-credential flows; heavier; rare for public
   registers. Record token endpoint + scopes; still no secrets in
   planning docs.
9. **api_odata** — `$filter`/`$top`/`$skip` + `@odata.nextLink`;
   common wherever agencies run Microsoft stacks. Typed query
   template + paging mode.
10. **api_graphql** — one endpoint, query document, cursor paging.
11. **api_sparql** — linked-data endpoint (ECHA operates one); query
    template + LIMIT/OFFSET keyset walk.
12. **api_jsonstat / statistical dialects** — dataset URL + dimension
    enumeration; a decoder already exists in the project
    (Eurostat-style JSON-stat).

### C. Server-rendered form/query surfaces

13. **form_download_get** — search form whose results can be
    downloaded (CSV link generated from the current query); GET
    therefore bookmarkable. Two shapes seen in the wild: a format
    parameter on the search page itself (`?format=csv`) and a
    dedicated export endpoint taking the query as parameters. Fields:
    form action, parameter map, download-link extraction, export
    paging. *Old svanen.se was both shapes at once.*
14. **form_download_post** — same, but POST: not bookmarkable, not
    archivable, invisible to Wayback; fields = action + body encoding.
15. **session_gated** — consent/session cookie bootstrap chain before
    any data flows; instruction = ordered request chain + cookie jar
    semantics.
16. **facet_enumeration** — server-side filter that must be queried
    once per value (BASTA `bk04Code`; old svanen `brand=X` with `p=`
    result paging). Fields: facet value enumeration source + loop +
    merge plan; politeness budget scales with facet cardinality —
    the de5 feasibility question in this mode's clothes (R5).

### D. HTML walks

17. **html_list** — server-rendered list pages with `?page=` /
    `?more=` / offset; fields: list-url pattern, item selector,
    field selectors.
18. **html_list_detail** — two-level walk: list → per-item detail
    pages. Request count = O(items); budget + resume cursor
    mandatory.
19. **html_sitemap** — sitemap.xml enumerates item URLs directly;
    often the best walk (no list scraping at all); URL-pattern
    filter + detail selectors.
20. **spa_js** — JS-only surface: (a) internal API discovered →
    *degrade to mode 6/7* (preferred — the BASTA precedent);
    (b) genuinely headless-browser-only (last resort; fragile,
    heavyweight; record as such, don't fake it).

### E. Indirect channels

21. **archive_snapshot** — web-archive copy (Wayback/CDX); carries a
    **provenance flag + capture timestamp** and is never treated as
    "current" — anchor keyfigures govern drift detection. Note the
    double role: CDX is also the best *discovery* instrument for dead
    route vocabularies (it revealed `ExportToCsv/?brand=&p=` to us).
22. **manual_request** — formal request procedure (agency emails a
    dump; the Swiss BBL requester pattern on the regulatory side is
    the same shape). Not automatable: instruction = procedure
    description + status record.

## Instruction contract impact (D45)

- The instruction `kind` is an **access-mode enum over an open set**:
  file_snapshot, file_bundle, file_index, ftp, deposit, rest, odata,
  graphql, sparql, jsonstat, form_download, html_walk (list /
  list_detail / sitemap), archive, manual. Schema v1's
  `csv_snapshot`/`api_endpoint` refine into `file_snapshot`/`rest`;
  the reserved `html_pages`/`web_query` are the first placeholders of
  `html_walk`/`form_download`.
- Table schema (columns, core-field triple R6, guards, journal R2/R7)
  is **orthogonal**: every mode shares it; only the delivery section
  + interpreter differ.
- The enum is open: an unknown mode is *recorded and refused by
  name* (exactly what `raw run AS-3` does today), never guessed.
  Probing may classify and instruct modes whose interpreter does not
  exist yet — the instruction file is the honest record of reality.
- Interpreter phasing is a cost decision for v0.3.8 design: file
  modes first (2–3 exist in embryo), API paging modes next
  (page/offset exist), walks/forms last, headless never unless a
  source forces it.

## Probe ladder (L0–L7) — classify any new source

Run cheapest-first against any candidate source; **stop at the first
mode that yields complete data**; record ladder evidence in the
instruction notes (mode + which step classified it). This becomes the
future `probe source` deep-probe (`probe url` stays the light probe).

- **L0** `robots.txt` + `sitemap.xml` (+ sub-sitemaps): allowed
  paths, Crawl-delay, and a free URL inventory (mode-19 check).
- **L1** format-parameter probes on the register surface:
  `?format=csv|json|xml`, `?export`, `?download`, `/export`,
  `/download` path shapes; a handful of requests, budgeted.
- **L2** API discovery: `/api`, `/api/v1`, `/wp-json/`, `/rest`,
  `/graphql`, `/sparql`, `/odata`, `openapi.json`, `swagger.json`,
  `/.well-known/`.
- **L3** form inventory: parse search/list pages for `<form>`
  (action, method, hidden fields, facet `<select>`s) and any
  download/export controls — the mode-13/14/16 classifier.
- **L4** JS-bundle scan: module URLs → `fetch()` targets and route
  strings (the BASTA method, proven on AS-33) — separates mode 20a
  from 20b.
- **L5** archive CDX: wildcard queries over the domain/path; reveals
  dead endpoints, parameter vocabularies, and historical modes
  (proven today on AS-3). Also the mode-21 fallback source.
- **L6** cross-source: open-data portals (data.europa.eu, national),
  sister-country registers, aggregators — the same data elsewhere
  under a better mode.
- **L7** manual channel: request procedure record (mode 22).

Ladder output = (mode, fields needed, politeness budget class,
implemented-y/n). Unimplemented mode → instruction records it, run
refuses named; that is success of the probe, not of the load.

## Worked example — AS-3 (Nordic Swan), 2026-10-04 re-test

| date | mode classification | evidence |
|---|---|---|
| 2026-09-14 | file_snapshot (`?format=csv`, full register) | live GET, 9.8 MB, archived twice |
| 2026-10-03 | route dead; instructed as reserved html_pages | raw scan: HTTP 404; site redesigned |
| 2026-10-04 | true historical mode = **form_download_get + facet_enumeration** (`/ExportToCsv/?st=0&brand=X&p=N`, alive ≥ 2025-10) | Wayback CDX (L5) |
| 2026-10-04 | all export variants 404 live; `content-search` is a site-content decoy (no product register on svanen.se at all) | live probes (L1/L3) |
| 2026-10-04 | mode today = **archive_snapshot**: our raw-store copy is the only existing snapshot (2 retrieval copies, sha256-verified, 52,543 rows × 10 cols) | offline verification |

Lessons encoded: (1) a route that worked twice is still one
observation, not a mode guarantee; (2) redirect targets lie — the
old page now redirects to a *content* search that is not the
register; (3) CDX is the highest-value step when a route dies; (4)
the snapshot on disk outranks every dead route — verify it, pin it,
provenance-flag it.

## DECISIONS

*(local numbering A…; A1 = D45 in MASTER.)*

- **A1 (D45, 2026-10-04):** instruction `kind` = open access-mode
  enum per the taxonomy; table schema orthogonal; run refuses
  unknown/unimplemented modes by name. Classifying and instructing
  ahead of the interpreter is legitimate and expected.
- **A2 (2026-10-04):** the L0–L7 ladder is the standard onboarding
  protocol for every new source; light probe ≠ classification;
  ladder evidence recorded in the instruction notes.
- **A3 (2026-10-04):** archive-sourced loads carry a provenance flag
  + capture timestamp and are never treated as current; drift is
  judged against pinned anchor keyfigures.

## OPEN ITEMS

- Mode enum final naming + per-mode required fields → pin at v0.3.8
  design (schema v2 of the instruction contract).
- `probe source` deep-probe CLI shape: one staged command emitting
  the ladder report (mode candidates + evidence) vs per-step flags —
  decide at v0.3.8.
- facet_enumeration politeness rule (facet cardinality × delay ×
  budget) — needed before any facet loop runs (BASTA BK04, svanen
  brand-style sources).
- Sister-register cross-check for Nordic Swan (ecolabel.dk /
  Nordic-level sites) — L6 step, user-gated 2026-10-04, pending
  decision.
- Which file sub-formats the file_snapshot interpreter learns next
  (xlsx? zip bundles? mdb re-use) — pull demand-driven from the
  candidate queue (KemiDigi, WINGIS, INIES…).

## REFERENCES

- RAW_SOURCING.md — the table-shape contract this doc is orthogonal
  to (R1–R9; D42–D44 context); R8 onboarding = mode enum + manifest.
- PIPELINE.md — v0.3.8 entry (generic bulk import; ladder + enum
  land there); v0.3.0 entry (built: file_snapshot + rest/page/offset).
- MASTER.md — D38 (data_sources.csv registry), D40 (BASTA keyfigures
  + robots delay), D42–D44 (product-DB turn, sub-roadmap, truncation).
- `raw_sources/AS-3.instruction.json` — the worked example's
  instruction record; `raw_sources/AS-2.instruction.json` — the
  file_snapshot reference case.
- TODOS.md — AS-3 re-acquisition entry (html_pages walker, v0.3.8
  candidate) with the 2026-10-04 re-test facts.

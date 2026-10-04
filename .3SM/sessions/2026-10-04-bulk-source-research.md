---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-04
type: research
---

# S-rec — bulk-source research round (2026-10-04)

## Question

User: we need ≥1–2 more ECAT-class sources (≥10k records) beyond
AS-2. Corpus criteria: EU market, likely paint-rich, manufacturer +
unique id per record, HS-linkable field, more info preferred;
retailers explicitly approved as a class. "Search and research, what
else is there?"

## Method

DB inventory of the 36 registered AS-class candidates first (8
already ACTIVE: AS-2/3/6/7/31/32/33/34/35/36), then a budgeted live
research round following the research skill (acquire → evaluate;
study UA; ~25 requests across 12 hosts over 3 rounds, ≥2.5 s
spacing; DDG HTML search for dead-name discovery). All observations
carry URL + access date (2026-10-04).

## Findings (evidence table in DATA_SOURCE.md § Next bulk candidates)

1. **BASTA (AS-33)** — closest to ECAT-class: 195,391 articles,
   anonymous API pinned (D40). No probe needed. Key insight recorded:
   raw loads need NO in-scope filter — de5 applies to samples only;
   BASTA can load whole (mode: rest anon, paged).
2. **INIES (AS-5)** — Public API documentation site live
   (`base-inies.fr/docs/`) with a dedicated **Export API** — mode:
   rest; auth + volume to pin.
3. **Blue Angel (AS-4)** — site claims 70,000 products; Drupal
   search-api + autocomplete visible; /jsonapi 404. Mode:
   html_walk/form_download.
4. **KemiDigi (AS-31)** — portal live; CKAN mirror 403 to study UA;
   API route to discover properly.
5. **Retail batch (new, PE-class)** — OBI/toom/hagebau/ManoMano/
   K-Rauta/Byggmax/Biltema; Hornbach template proven (brand+SKU+EAN);
   Bauhaus 403 bot-wall noted.
6. **environdec (AS-7)** — `api.prod.environdec.com/api/v1/EPDLibrary/`
   REST pattern live; list endpoint needs JS-bundle discovery.
7. New unregistered: **dop-find.eu** (European DoP aggregator,
   construction coatings), **ÖKOBAUDAT** (file_bundle downloads).
8. Deprioritized: **NOBB** (login wall now), **eBVD (AS-34)** —
   ebvd.se PARKED (registry row needs investigation), **EPD-Global/
   EPD-Norway (AS-10)** — below the 10k bar.

## Recordings

- DATA_SOURCE.md: new "Next bulk candidates" section (ranked evidence
  table + provenance).
- PIPELINE.md v0.3.8: candidate order refreshed + the
  filter-not-needed-for-loads constraint reworded + user direction
  recorded as a decision line.
- Commit: `3SM: research round …` (this file + the two edits).

## Open

- INIES Export API endpoint/auth pin + volume count.
- Blue Angel volume pin + Drupal search endpoint naming.
- KemiDigi proper API route (CKAN 403 with study UA).
- Retail batch per-shop probes (at onboarding).
- eBVD registry row: where did the service go?

## Build turn (same day, user-approved live work)

User directive: probe the candidates for data headers/shapes, write
sourcing instructions for all that can be pinned, feed to CLI,
download data, commit.

- **r04 committed (`3c1c7c5`)**: interpreter dot-path projection
  (`_project`, `extract_json` uses `col.source_header` as dot-path;
  plain keys unchanged; missing link → None) + fixture route
  `/basta-nested.json` + test `test_json_dotpath_projection_is_verbatim`.
  Suite: 461 passed, 2 deselected.
- **AS-33 BASTA instruction written** (`raw_sources/AS-33.instruction.json`):
  api_endpoint, `?pageSize=1000` + `page` param (max_pages=250 guard),
  22 columns (dot-paths `company.name`, `bk04Code.code`, …; containers
  `grades`/`flags` JSON-encoded verbatim), natural_key
  `source_article_id`, delay 10 s = robots Crawl-delay, budget 220.
  `expected_count=198742` (live total; register drifts).
- **AS-33 load executed** (background, resumable; checkpointed pages;
  first launch killed by a tool-session timeout, relaunched detached
  with `setsid`, checkpoint `next` honored — resume verified working).
- **AS-7 environdec reserved-kind record written**
  (`raw_sources/AS-7.instruction.json`): html_pages (run refuses by
  name until a walk interpreter exists); SSR pagination
  `?page=N` (~10 EPD uuids/page, disjoint pages verified), doc route
  uuid-keyed live, robots `/library` allowed for `*`, client search API
  not extractable from inspected chunk, `/EPD` singular 500 on guessed
  params, `/EPDs` 404.
- **Refusals recorded** (no instruction — nothing loadable to pin):
  INIES AS-5 gated API (login email+apiKey, read permissions by
  subscription; root site a JS shell, no open downloads); Blue Angel
  AS-4 token-POST Drupal search, `produkte.` subdomain DNS-dead;
  KemiDigi AS-31 CKAN mirror 403 (bot-wall, retried).
- DATA_SOURCE.md research table updated with round-2 outcomes.

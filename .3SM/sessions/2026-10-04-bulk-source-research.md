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

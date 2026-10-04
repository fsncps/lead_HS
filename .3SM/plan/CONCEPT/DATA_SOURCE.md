---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-04
---

# Topic — Data sources (concept summary)

## Abstract

The source register (108 rows, classes CS/PE/ST/AS/DS) enumerates
every candidate source of paint product data on the EU market; each
source is characterized by probing (robots/terms, access, counts,
counts provenance) before any collection. Discipline: record source
URL and retrieval date per record, respect site terms, no bulk
hammering, polite crawl-delay, GO=1 gates for costly operations.
Current state of the numbers game: census headline N2 = 331,644 /
floor 17,838 (v0.2.0 rounds); exactly two sources meet the
confirmed-bulk + identity-tuple gate (`data_sources.csv`: AS-2 ECAT,
AS-3 Nordic Swan); the BASTA special probe (D40) pinned the register's
public counts (195,391 articles / 1,925 companies) via its anonymous
same-origin proxy and delivered a seeded 100-article sample — the
paint-subset filter stays open, so no third `data_sources.csv` row.

## DECISIONS

- D9 — cost constraint: publicly retrievable documents only, minimal
  cost.
- D20 probe discipline — probing obeys the register's access rules;
  census counts provisional; promotion to anchors manual (bridge).
- D25/D28 — probe-first source reports; per-source two questions:
  products identifiable, documentation reachable; product data only.
- D31 — no-scrape reconnaissance, EU-only; channels characterized, not
  walked.
- D33 — source-level sounding-out; product identity key (manufacturer,
  manufacturer product-ident) with UFI/GTIN cross-references.
- D36/D38 de5 gate — `data_sources.csv` grows only via confirmed bulk
  + identity tuple (+ in-scope filter) sources.
- D40 (2026-09-17) — BASTA addendum: same-origin anonymous
  `/apiproxy/v3` routes pinned; exact counts; sample delivered; de5
  not met.

## OPEN ITEMS

- BASTA paint-subset filter: enumerate the server-side
  `bk04Code` paint groups (TODOS item) before any third
  `data_sources.csv` row.
- ECAT reconciliation (group-044 17,838 vs Commission 38,233;
  awarded-vs-registered) — v0.2.3 residual.
- Deep per-source pinning of the six probe-queue candidates
  (AS-31..36) stays next-unit work (D39/D40 groundwork in place).

## Next bulk candidates — research round 2026-10-04 (user goal: ≥2 more ECAT-class corpora, ≥10k records)

Corpus criteria (user, 2026-10-04): sells in the EU; likely
paint-rich; manufacturer + unique id per record; HS-linkable field;
more info preferred. Retailers explicitly approved as a class
(manufacturer + id suffice). Access modes per `SOURCE_ACCESS_MODES.md`
(D45); a raw load does NOT need the in-scope filter — the filter is a
de5/sample question, never a load blocker (BASTA loads whole).

Evidence table (all URLs accessed 2026-10-04, study UA):

| rank | source (registry) | scale evidence | mode | gap to load |
|---|---|---|---|---|
| 1 | **BASTA (AS-33, ACTIVE)** — construction chemicals SE | 198,742 articles live (envelope `pagination.total`, 2026-10-04; was 195,391/200,769 at earlier pins); anonymous same-origin `/apiproxy/v3/search/articles` re-verified: envelope `{searchTime, pagination, items[]}`, 22 fields, nested `company`/`bk04Code`/`bsabCode`/`flags`, `pageSize=1000` accepted (199 pages), robots `Crawl-delay: 10` | rest (api_rest_anon, paged) | **none — instruction written, load executed 2026-10-04** (`raw_sources/AS-33.instruction.json`, 22 dot-path columns; interpreter dot-path projection added r04) |
| 2 | **INIES (AS-5)** — French EPD/FDES register | Public API documented: `base-inies.fr/docs/` (docfx) — **gated**: bearer token via `POST /ws/Login` (email+apiKey), read permissions require subscription/onboarding, whole-DB pulls throttled | rest (gated API) | **refused for now — not publicly retrievable** (hard constraint: no paid/registered sources); open exports not offered (root is a JS shell, no download links) |
| 3 | **Blue Angel (AS-4)** — German ecolabel | landing copy "70,000 products" (marketing, unpinned); `produkte.blauer-engel.de` DNS-dead (2026-10-04); search folded into `www.blauer-engel.de/de/produkte/produktsuche` — Drupal search-api **form POST** with tokens; autocomplete route `/de/search_api_autocomplete/default`; no JSON API, no plain-GET result list | form_query → html_walk | route pin for a walkable list (search is token-gated POST); mode not implementable in v0.3.x interpreters |
| 4 | **KemiDigi (AS-31, ACTIVE)** — FI chemical products register | portal `kemidigi.fi` live; CKAN mirror API `avoindata.suomi.fi/api/3/action/package_search` → **403 to study UA** (retried 2026-10-04, bot-wall) | rest/CKAN (blocked) | alternate route (portal's own API or browser-consent flow); refusal recorded, not pursued today |
| 5 | **Retail batch (PE-class, new)** — OBI, toom, hagebau, ManoMano, K-Rauta/Byggmaklar/Byggmax, Biltema | Hornbach template proven (PE-20; brand+SKU+EAN via storefront API); Bauhaus.de 403 bot-wall (needs alternate route); others unprobed | spa→api_rest_anon (BASTA method) or html_walk | per-shop probe at onboarding; thousands of paints each, EU-sold, GTIN-keyed |
| 6 | **environdec (AS-7, ACTIVE)** — International EPD System | SSR library paginates: `environdec.com/library?page=N` serves disjoint EPD uuids per page (~10 each, verified pages 1–2); doc route `api.prod.environdec.com/api/v1/EPDLibrary/Files/EPDs/<uuid>/Documents` live; client search API not in inspected bundles; `/EPD` (singular) 500s on guessed list params, `/EPDs` 404; robots: `/library` allowed for `*` | html_pages (SSR walk) — **reserved-kind instruction written** (`raw_sources/AS-7.instruction.json`; run refuses html_pages by name until a walk interpreter exists) | walk interpreter implementation; verify pages carry the full list (not a newest-strip); volume unknown |
| 7 | **dop-find.eu (unregistered)** — European DoP aggregator (construction products incl. coatings EN 1062) | site live (DE-first); /en/ 404 | html_walk | scope/volume pin; DoP no. = unique id, manufacturer named |
| 8 | **ÖKOBAUDAT (unregistered)** — German EPD/generic datasets | downloads exist behind /no_cache paths; 403 on guessed path | file_bundle (zip/xml/csv) | bundle pin; paint subset small (generic LCA data) |

Deprioritized this round: **NOBB (NO)** — moved behind a login wall
("Verifiser bruker", live 2026-10-04); **eBVD (AS-34)** — `ebvd.se`
parked at Loopia (service moved; registry row needs investigation);
**EPD-Global/EPD-Norway (AS-10)** — platform live but small (thousands
of EPDs, below the 10k bar). Round-2 outcomes (same day, build turn):
INIES refused (gated API), KemiDigi blocked (CKAN 403), Blue Angel
unwalkable for now (token POST search), environdec pinned as a reserved
html_pages record, BASTA instructed + loaded (see table).

Provenance: all live observations this round carry URL + access date
in the probe transcript; register-state facts (BASTA counts, ECAT
export) carry their pinned D-references (D40, D38).

## Detail documentation

The public register document (plain language, glossary, DE/FR
translations — source-by-source access rules and history) lives
outside the plan tree:

- `docs/study/DATA_SOURCE.md` (EN; siblings `DATA_SOURCE.de.md`,
  `DATA_SOURCE.fr.md`).

Raw cross-unit concept material: `inputs/INPUT-source-expansion-MSE.md`,
`MATCHING.md`, `RAW_SOURCING.md` (this directory).

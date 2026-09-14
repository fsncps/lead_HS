---
unit: v0.2.1
built: 2026-09-14
type: unit report (detailed, human-readable)
language: en
---

# Unit v0.2.1 — source-level capability sounding-out

The data-landscape map (v0.2.0) counted the sources; v0.2.1 goes one
level deeper on the **official registers** — the ecolabel and EPD
registries that publish product-level paint data — and characterises
each against the study's product model: CN8 code, manufacturer,
manufacturer product-ident, at what volume and data depth.
Reconnaissance-only (official exports/APIs, no scraping, no
laboratory).

> Provenance note: the machine report of this era was overwritten by
> the v0.2.2 republish — before the publish-history policy (v0.2.2
> PHASE07 addendum) existed. This file is the durable record,
> reconstructed from the planning documents
> (`docs/plan/3SM/30_IMPLEMENTATION/v0.2.1/`), the source register and
> the evidence database.

## Findings

- The register now holds **7 official registers** (AS-1–AS-7): the EU
  Ecolabel catalogue (ECAT), Nordic Swan, Blue Angel, INIES, IBU and
  environdec, plus AS-1 (EU Open Data portal entry). Four are active;
  **Blue Angel and INIES are inactive** (XLSX-only or auth-gated
  exports).
- At first contact each active register's landing page is HTML — the
  exports are documented as **export URL to anchor** at the next pass,
  recorded honestly rather than mis-read as an export.
- **One register is confirmed a real-product source:** the **EU
  Ecolabel catalogue (ECAT)** — it exposes a manufacturer field, a
  product-ident field (GTIN/EAN), a CN8-linkage mechanism (product
  group category) and data depth 2; its CSV export is downloadable.
- **Preliminary N2 numerator (official registers, floor): 17,838**
  certified products relevant to the study — paints & varnishes +
  performance coatings (16,001 + 1,817 products under the 2014 and
  2025 criteria, plus 20 performance coatings). This is a
  **certified/declared subset** of the market — a floor, never a
  market total; product-level data still awaited the collection
  go-ahead (v0.2.2 staged the full export).
- The other active registers are not yet real-product sources:
  **environdec** exposes a manufacturer but no product-ident;
  **Nordic Swan** and **IBU** are export-to-anchor.

## Obstacles and incidents

- **HTML-as-CSV defect (recorded in LOG, repaired 2026-09-14):** the
  first probe round accepted seven bogus AS-7 (environdec) findings —
  an HTML surface mis-read by the CSV parser as tabular data. The
  seven findings were deleted; a content-sniffing gate (`_sniff`) was
  introduced and regression-tested in v0.2.2.
- **IBU / environdec export shapes** could not be pinned at landing
  page level; deferred to real-format checks at the next pass.
- **INIES** API is auth-gated (email + apiKey); account registration
  remains a user action (TODOS.md).
- **Nordic Swan** export mechanics (GET vs form-POST) needed pinning
  at a real pass; v0.2.2 recorded a deferral (JS-bound search
  surface).

## Provenance

- EU Ecolabel Product Catalogue (ECAT):
  <https://data.europa.eu/data/datasets/eu-ecolabel-products> (accessed
  2026-09-12/14); CSV export at the public EU storage endpoint.
- Nordic Swan Ecolabel product database:
  <https://www.svanen.se/en/search-for-ecolabelled-products-and-services/>
- INIES: <https://www.inies.fr/>; IBU: <https://ibu-epd.com/en/>;
  environdec: <https://environdec.com/library>
- Capability profiles per register: source register
  (`src/leadhs/dict/sources.csv`) and the evidence database
  (`--db` audit clean).

## Links

- Strategy turn: `docs/plan/3SM/10_STRATEGY/v0.2.1.md`
- Build phases: `docs/plan/3SM/30_IMPLEMENTATION/v0.2.1/`
- Predecessor: v0.2.0 ([report-0.2.0.md](report-0.2.0.md));
  successor: v0.2.2 ([report-0.2.2.md](report-0.2.2.md)) — the ECAT
  numbers feed directly into the funnel's Q2 floor and the
  products-per-producer factor.

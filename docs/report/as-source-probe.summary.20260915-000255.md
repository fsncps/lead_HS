# AS-class source probe — summary

Run: `20260915-000255` · all 36 AS rows · one finding per source (D37).

Registries (15 explicit ids, first AS-2, last AS-36): product-row CSV where obtainable,
else exact-or-estimated record count with provenance, else why
not + what is available instead. Associations: no product
register by design — member-list pointer, liveness recorded.

## AS-1 — CEPE (European paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://www.cepe.org
- GETs spent: 1

## AS-2 — EU Ecolabel Product Catalogue (ECAT) — delivered

- records: **100 rows (sample of 17,013 distinct register products)**
- basis: reused csv-sample.20260915-000230.AS-2.csv
- artifact: `csv-sample.20260915-000230.AS-2.csv`
- GETs spent: 0

## AS-3 — Nordic Swan Ecolabel product database — delivered

- records: **100 rows (sample of 2,322 distinct register products)**
- basis: reused csv-sample.20260915-000230.AS-3.csv
- artifact: `csv-sample.20260915-000230.AS-3.csv`
- GETs spent: 0

## AS-4 — Blue Angel (Blauer Engel) — records

- records: **≈70000 (estimated)**
- basis: estimate from visible page text (products) on https://www.blauer-engel.de/en/products, accessed 2026-09-15
- available instead: the register's web interface
- GETs spent: 5

## AS-5 — INIES (French EPD register) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://www.inies.fr/export); count not visible on the landing page
- available instead: per-product FDES declarations behind registration (auth-gated API; TODOS.md user action)
- GETs spent: 5

## AS-6 — IBU (Institut Bauen und Umwelt EPD) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://ibu-epd.com/en/export); count not visible on the landing page
- available instead: per-product EPD downloads via the library search
- GETs spent: 5

## AS-7 — environdec (International EPD System) — records

- records: **≈2025 (estimated)**
- basis: estimate from visible page text (EPD) on https://environdec.com/library, accessed 2026-09-15
- available instead: per-product EPD downloads via the library search
- GETs spent: 5

## AS-8 — NF Environnement (AFNOR Certification) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): html at https://certification.afnor.org/marque/nf-environnement/export); count not visible on the landing page
- available instead: certified-product PDF lists (NF 130 peintures/vernis section)
- GETs spent: 5

## AS-9 — natureplus quality label — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://www.natureplus.org/export); count not visible on the landing page
- available instead: a web product database (natureplus.org) without a bulk export
- GETs spent: 5

## AS-10 — EPD Norway (EPD-Norge / EPD-Global) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://digi.epd-norge.no/export); count not visible on the landing page
- available instead: per-product EPD downloads via the digi portal
- GETs spent: 5

## AS-11 — FCiO (Austrian paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://fcio.at
- GETs spent: 1

## AS-12 — IVP Coatings (Belgian paints association) — assoc

- basis: site unreachable at probe time
- available instead: https://ivp-coatings.be
- GETs spent: 1

## AS-13 — Dansk Industri — paint section (DK) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://danskindustri.dk
- GETs spent: 1

## AS-14 — Varieteollisuus (Finnish paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://variteollisuus.fi
- GETs spent: 1

## AS-15 — FIPEC (French paints federation) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live; members visible
- available instead: member list https://fipec.org
- GETs spent: 1

## AS-16 — VdL (German paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live; members visible
- available instead: member list https://wirsindfarbe.de
- GETs spent: 1

## AS-17 — VdMI (German printing-ink association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://vdmi.de
- GETs spent: 1

## AS-18 — Hellenic Coatings (GR) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://hellenicoatings.gr
- GETs spent: 1

## AS-19 — MAFEOSZ (Hungarian paints association) — assoc

- basis: site unreachable at probe time
- available instead: https://mafeosz.hu
- GETs spent: 1

## AS-20 — IDSCA (Irish decorative paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://idsca.ie
- GETs spent: 1

## AS-21 — AVISA (Italian paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://avisa.federchimica.it
- GETs spent: 1

## AS-22 — Assovernici (Italian varnish makers) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://assovernici.it
- GETs spent: 1

## AS-23 — VVVF (Dutch paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://vvvf.nl
- GETs spent: 1

## AS-24 — MALINGOGLAKK (Norwegian paints association) — assoc

- basis: site unreachable at probe time
- available instead: https://malingoglakk.no
- GETs spent: 1

## AS-25 — PZPFiK (Polish paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://pzpfik.pl
- GETs spent: 1

## AS-26 — APINTAS (Portuguese paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://aptintas.pt
- GETs spent: 1

## AS-27 — AIVR (Romanian paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://aivr.ro
- GETs spent: 1

## AS-28 — ASEFAPI (Spanish paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://asefapi.es
- GETs spent: 1

## AS-29 — SVFF (Swedish paints association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://sveff.se
- GETs spent: 1

## AS-30 — EuACA (European artists' colours association) — assoc

- records: **0 product records (not a register)**
- basis: association landing page live
- available instead: member list https://artists-colours.org
- GETs spent: 1

## AS-31 — KemiDigi (Finnish Chemical Products Register) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): html at https://www.kemidigi.fi/export); count not visible on the landing page
- available instead: the public register search + per-product record pages (enumerability unproven)
- GETs spent: 5

## AS-32 — WINGIS Online (BG BAU / GISBAU GefKomm-Bau) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://www.wingisonline.de/export); count not visible on the landing page
- available instead: the online search per manufacturer/GISCODE product group (no documented bulk export)
- GETs spent: 5

## AS-33 — BASTA online (construction products SE) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://www.bastaonline.se/export); count not visible on the landing page
- available instead: an article-level database behind web search (API under agreement)
- GETs spent: 5

## AS-34 — eBVD (building-product declarations SE) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): HTTP 404 at https://www.ebvd.org/export); count not visible on the landing page
- available instead: a structured-declaration API (free after agreement — no unpaid bulk route)
- GETs spent: 5

## AS-35 — Quick-FDS (SDS discovery FR/EU) — unavailable

- records: **unknown**
- basis: no export endpoint found after <=5 bounded GETs (last: 5 GET(s): html at https://www.quickfds.com/export); count not visible on the landing page
- available instead: a supplier SDS discovery catalogue (crawl/export terms pending)
- GETs spent: 5

## AS-36 — ECHA Biocidal Products — PT21 antifouling (marine coatings) — failed

- note: network failure on the pinned URL: https://echa.europa.eu/robots.txt: HTTP 403

---

Generated by `leadhs probe as-source-probe` — constants in
`src/leadhs/probe/as_probe.py` + the design method sheet (D37).

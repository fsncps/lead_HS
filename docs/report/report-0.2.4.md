---
unit: v0.2.4
built: 2026-09-14
updated: 2026-09-14
type: unit report (detailed, human-readable)
language: en
---

# Unit v0.2.4 — the management CSV sample (per-registry product-row evidence)v0.2.3 answered the pool question with a benchmark vote. v0.2.4 turns
to the management question behind the sample: **what does a product
row actually look like in each of the large registers** — which data
fields come back per product item, which identifier columns exist, and
is cross-identification of individual products possible — answered
with **real downloaded rows** where a register publishes them, and
with an honest, cited reason where it does not.

The command `leadhs probe download-csv-sample` runs against the six
registries of the v0.2.3 benchmark set (AS-2 EU Ecolabel, AS-3 Nordic
Swan, ST-1 ECHA PCN, ST-3 Eurostat SBS, ST-6 Danish AT register, ST-7
Swedish KemI Products Register) and produces, per registry, either a
**seeded, reproducible CSV sample** (n=100, seed=42 — same seed and
same document hash reproduce the same rows) or a **no-product-rows
record** that cites the verified finding, plus a **manifest** that
always states the outcome of every registry (decision 1A: the
manifest is never silent about a failure).

## The real run (2026-09-14, 11:19 UTC)

`GO=1 make sample-csv` · n=100 · seed=42 · artifacts (published
copies; working renders per run live in `data/report/`, gitignored):
[csv-sample.manifest.md](csv-sample.manifest.md)
(timestamped copies `csv-sample.manifest.20260914-111921.*`, samples
`csv-sample.20260914-111921.AS-2.csv` / `.AS-3.csv`).

| Registry | Outcome | Rows | Identifier columns observed |
|---|---|---|---|
| AS-2 — EU Ecolabel (ECAT) | **delivered** | 100 of 17,013 distinct (17,838 in-scope rows) | `licence_number` (100%), `vat_number` (86%), `code_value` EAN13 (17%), plus company + country |
| AS-3 — Nordic Swan | **delivered** (trial-grade) | 14 distinct (2,283 filter hits) | none in the header beyond the ecolabel licence number |
| ST-1 — ECHA PCN | unavailable | 0 | — restricted to member-state appointed bodies (login/eDelivery) |
| ST-3 — Eurostat SBS | unavailable | 0 | — enterprise statistics (NACE 20.30), not a product registry |
| ST-6 — Danish AT register | unavailable | 0 | — aggregates only, embedded Power BI, no download URL |
| ST-7 — KemI Products Register | unavailable | 0 | — product-level secrecy; public access aggregates only |

Exit code 0 (delivered + expected-unavailable only). Six runs in the
evidence DB (`run.mode = csv_sample`, seed 42 recorded per run); the
two fetched exports are archived in the raw store with document
hashes, so every sampled row carries full provenance (source, run
key, retrieval date, hash, seed, draw index).

## What a product row looks like

**AS-2 / ECAT** — 12 fields per product item: product type,
licence number, product group, code type + code value, product name,
certification decision, expiration date, company name, country, VAT
number, extract date. The sample (all rows in group 044 "Decorative
paints, varnishes, and related products (2014 criteria)") re-pinned
the public export header exactly as staged in v0.2.3 (17,838 rows
reconciled). Identity carriers: the **licence number** (always
present, one licence can cover many products), the **EAN13/GTIN** in
`code_value` (17 of 100 sampled rows), and **company + VAT** (86%).
Cross-identification candidates, concretely: EAN13 ↔ retail or
manufacturer catalogues (the v0.3 seeding path); name + licence
holder ↔ other certified-product registers.

**AS-3 / Nordic Swan** — the bounded discovery (≤5 polite GETs on the
pinned search surface) **found a real export**: the search URL itself
serves a CSV at `?format=csv` (9.8 MB, text/csv). The paint filter
(group 096 / EU44 text) matched 2,283 rows; deduplication collapsed
them to **14 distinct product items** — drawn in full (shortfall
flagged in the manifest). The quality is **trial-grade** and the
manifest says so: several rows suffer field misalignment from
unquoted commas inside product names, the export mixes ecolabel
schemes (EU Ecolabel DK/044 licences alongside Nordic Swan ones), and
the header carries no dedicated identifier column beyond the ecolabel
licence number. Reconciliation (pin the real export mechanics, repair
the parsing) stays in TODOS.md — the discovery answer to the pilot
question (EU Ecolabel ∩ Nordic Swan overlap) is now concrete: the
overlap is joinable at least by **name + licence holder**.

**ST-1 / ST-3 / ST-6 / ST-7** — no fetch at all (zero network, method
`manual`): each record cites the verified structural reason with URL
and access date. This is the honest half of the answer to the
management question: **of the six large registers, exactly two publish
product rows at all**, and only one of them (ECAT) with per-item
identifier columns.

## Cross-identification — the manifest's verdict

- **Possible today (AS-2):** EAN13 (sparse but real), licence number,
  holder + VAT. The v0.3 seeding path (ECAT EAN ↔ retail catalogues)
  stands on real columns.
- **Pilot-feasible (AS-2 ↔ AS-3):** name + licence holder; the AS-3
  export even carries EU Ecolabel licence numbers directly.
- **Impossible today (ST-1/3/6/7):** no product rows are published —
  no join key exists.

Machine-readable side: the findings
(`csv_sample_rows`, `csv_sample_unavailable`) live in the evidence DB
and flow into the next probe-report republish; the samples and the
manifest are the review artifacts.

## Method notes

- One polite fetcher (rate limit, documented UA, robots respected);
  AS-2 one GET, AS-3 five GETs (the discovery budget), ST-* zero.
- Dedupe on the identity triple (product, company, group) before the
  draw; the pool is sorted canonically so the seeded draw is
  reproducible across machines, not only across runs.
- Exit-code contract: 0 delivered/expected-unavailable, 2 a
  should-deliver failure, 1 usage error (i1).

## Open items carried

- AS-3 reconciliation (TODOS.md): pin the `?format=csv` mechanics,
  repair the ragged-comma parsing, split the mixed-scheme export.
- The AS-2 sample's EAN coverage (17%) is a sample statistic, not the
  register's rate — the staged full register (17,838 rows) is the
  right base for the v0.3 seeding-path estimate.

## Addendum — the AS-class source probe (D37, 2026-09-14)

The unit's scope folded in one more probe (ENG-review SMALL CHANGE):
**all 30 AS-class sources** ("Associations & registers") get exactly
one finding each — product-row CSV where obtainable, else an
exact-or-estimated record count with provenance (method + access
date; `unknown` is a valid outcome), else why-not + what is available
instead. The 9 registries/databases (AS-2..AS-10) get bounded export
discovery (≤5 polite GETs each); the 21 trade associations get one
liveness GET (member list noted when visible). Same-day csv-sample
artifacts for AS-2/AS-3 are reused, not refetched.

`GO=1 make as-probe` · run `20260914-125322` · exit 0 · summary
(published copies; working renders in `data/report/AS-source-probe/`,
gitignored): [as-source-probe.summary.20260914-125322.md](as-source-probe.summary.20260914-125322.md)
/ `.csv`.

| Outcome | Sources | Detail |
|---|---|---|
| **delivered** (product-row CSV) | 2 | AS-2 ECAT (100 rows, reuse), AS-3 Nordic Swan (14 rows, reuse) |
| **record count, estimated** | 2 | AS-4 Blue Angel ≈70,000 products (page text); AS-7 environdec ≈2,025 EPDs (page text) — basis + access date recorded |
| **unavailable, why-not recorded** | 5 | AS-5 INIES (auth-gated), AS-6 IBU, AS-8 NF Env (PDF lists instead), AS-9 natureplus, AS-10 EPD Norway — no export endpoint after ≤5 bounded GETs, count not visible |
| **association, live** | 18 | no product register by design; member-list pointer recorded (members visible on AS-15 FIPEC, AS-16 VdL) |
| **association, unreachable** | 3 | AS-12 IVP, AS-19 MAFEOSZ, AS-24 MALINGOGLAKK — down at probe time, URL recorded |

Reading: the AS class holds **2 of 9 registries** publishing
product rows (both ecolabel catalogues; same two as the csv-sample
run), 2 more with estimable register sizes, and 5 without any bulk
surface — the EPD registers (AS-5/6/7/10) expose their documents
per-product behind search UIs, not as data. The 21 associations are
member directories, not product registers — recorded as such, one
liveness GET each. Evidence DB: 30 runs (mode `as_source_probe`),
60 findings across `as_probe_rows` / `as_probe_records` /
`as_probe_unavailable` / `as_probe_assoc` (migration 0010).

Open item: the per-product EPD-API follow-up (AS-5 INIES
registration, AS-6/AS-7/AS-10 library APIs) stays in TODOS.md —
 pursued only if the census pass surfaces evidence it is needed
(D37, evidence-first).

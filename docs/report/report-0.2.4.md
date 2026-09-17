---
unit: v0.2.4
built: 2026-09-14
updated: 2026-09-15
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
`csv-sample.20260914-111921.AS-2.csv` / `.AS-3.csv`; **D38 re-render**
from the archived export, run `20260914-164304`: samples
`csv-sample.20260914-164304.AS-2.csv` / `.AS-3.csv`, regenerated
manifest).

| Registry | Outcome | Rows | Identifier columns observed |
|---|---|---|---|
| AS-2 — EU Ecolabel (ECAT) | **delivered** | 100 of 17,013 distinct (17,838 in-scope rows) | `licence_number` (100%), `vat_number` (86%), `code_value` EAN13 (17%), plus company + country |
| AS-3 — Nordic Swan | **delivered** (D38-corrected: 100 of 2,322 distinct; the "14 distinct" first record was a tool defect) | 100 (re-rendered sample) | `license number` (100%), name + licensee; no EAN column |
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
serves a CSV at `?format=csv` (9.8 MB, text/csv). **Corrected
2026-09-14 (D38):** the first run's "trial-grade, 14 distinct" record
was a **tool defect, not a data defect** — the export (semicolon-
delimited, 52,539 rows) parsed correctly; a loose substring scope
filter ("lack" inside "Black") and an ECAT-shaped dedupe key (which
collapsed the pool to 14 distinct Category values) produced the wrong
figures. After the fix, the paint pool (groups 096 + EU44) is
**2,424 rows / 2,322 distinct product items across 53 licences from
20 licensees** (Nordic Swan 41 licences incl. 4 dual-listed, EU
Ecolabel 16 incl. 4 dual); the re-rendered sample (n=100, seed=42,
same archived document) is fully in-scope. The export mixes EU
Ecolabel and Nordic Swan licences — the source's data model, joinable
by **licence number** + name/licensee. The discovery answer to the
pilot question (EU Ecolabel ∩ Nordic Swan overlap) stands, now on
clean numbers: the overlap is joinable at least by **name + licence
holder**, and the export carries EU Ecolabel licence numbers directly.

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
  export even carries EU Ecolabel licence numbers directly (and vice
  versa — the mixed-scheme export is joinable by licence number).
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

- ~~AS-3 reconciliation (TODOS.md): pin the `?format=csv` mechanics,
  repair the ragged-comma parsing, split the mixed-scheme export.~~
  **Closed (D38):** the mechanics are pinned (GET `?format=csv`,
  semicolon CSV); the "ragged commas" were a tool defect (scope
  filter + dedupe keys), fixed and re-rendered. The mixed-scheme
  export stays a documented data-model fact (licence-number join).
- The AS-2 sample's EAN coverage (17%) is a sample statistic, not the
  register's rate — the staged full register (17,838 rows) is the
  right base for the v0.3 seeding-path estimate.

## Addendum — D38 (2026-09-14): corrections, evidence archiving, data_sources.csv

A review of the raw store + the AS-probe report surfaced three
defects, all fixed offline (zero network):

1. **AS-3 numbers corrected** (see the AS-3 section above): the paint
   pool is 2,424 rows / 2,322 distinct items / 53 licences / 20
   licensees; the sample was re-rendered from the archived export
   (n=100, seed=42, same `raw_hash`). `--from-store` re-renders
   samples from the raw store without refetching.
2. **Estimates carry archived evidence:** the AS-probe now stores the
   landing page (ext `html`) and cites its `doc_hash` whenever an
   estimate is derived from page text (the AS-4 ≈70,000 number —
   register-claimed, all ~170 categories, not paints — previously had
   a URL + date only). AS-probe summaries re-render offline via
   `--rebuild-summary`; reuse entries now read "100 rows (sample of
   17,013 distinct register products)" so the sample size never reads
   as the register size.
3. **data_sources.csv** (`src/leadhs/dict/data_sources.csv`, review
   artifact — never loaded by `source load`): lists only sources
   where a probe **confirmed bulk data + manufacturer + product
   ident-nr** (identity tuple) with in-scope membership derivable from
   the category filter. Initial content: **DS-1 (AS-2)** and **DS-2
   (AS-3)** — the only two sources on record meeting the gate
   (selection-bias caveat recorded: ecolabel-certified stratum,
   identity source, not a lead-prevalence frame). The file grows only
   as future probes confirm the gate; gated registers (KemI, Danish
   AT, PCN, KemiDigi, Norwegian P-no) and unprobed candidates stay
   out — they remain in DATA_SOURCE.md / strategy documentation.
4. **AS-2 size reconciliation (provenance note):** the JRC final
   Ecolabel report (2026) counts **36,960 certified products**
   (03/2025, **all** product groups); the staged ECAT export carries
   only the **in-scope** group-044 paint rows (17,838 rows / 17,013
   distinct). The two numbers differ by scope, not by error — the
   export publishes no group-independent total, so the JRC figure
   stays the citation for the register total, and 17,013 is the
   in-scope pool the sample draws from. The summary's reuse line
   reads accordingly: "100 rows (sample of 17,013 distinct register
   products)".

Also filed: the consultant source-expansion + capture-recapture
handover (2026-09-14) as next-unit strategy input
(`10_STRATEGY/INPUT-source-expansion-MSE.md`; verbatim copy under
`10_STRATEGY/_inputs/`) — not adopted policy in v0.2.4.

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
/ `.csv` — **superseded for AS-2/AS-3 by the D38-corrected rebuild**
[as-source-probe.summary.20260914-165555.md](as-source-probe.summary.20260914-165555.md)
/ `.csv` (re-rendered offline from the evidence DB; the D37 snapshot
stays for the publish history).

| Outcome | Sources | Detail |
|---|---|---|
| **delivered** (product-row CSV) | 2 | AS-2 ECAT (100 rows, reuse), AS-3 Nordic Swan (100 rows, reuse; D38-corrected sample) |
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

## Addendum — D39 (2026-09-15): full-probe round + source-expansion reconnaissance

On explicit instruction (2026-09-15) the whole probe suite ran again,
same day, in one pass — census over all 108 registered sources,
fresh CSV sample, AS-source probe — **with six new candidate
sources** from the consultant source-expansion handover (strategy
INPUT, 2026-09-14) joining the register: **AS-31 KemiDigi** (Finnish
chemical products register, Tukes), **AS-32 WINGIS/GefKomm-Bau** (BG
BAU/GISBAU), **AS-33 BASTA** (Swedish construction catalogue),
**AS-34 eBVD** (Nordic declarations), **AS-35 Quick-FDS** (SDS
discovery), **AS-36 ECHA PT21 antifouling**. All six are probe rows
(`open`, active, provenance-cited to the handover); the AS class is
now 36 rows (15 registries + 21 associations).

Runs (all rendered 20260915-000613, published as timestamp-hash
snapshots; `db audit` clean):

- **Census sweep** (`GO=1 make census`): all 108 sources; the six
  new rows classify tier (c) — visible, uncounted without scraping —
  alongside AS-2/AS-3/AS-6/AS-7/CS-2. The blocked/failed site sets
  are unchanged (PE hosts + ST-2, as documented since v0.2.2).
  Headline N2 (Σ tier a+b) stays **331,644**; the official-register
  N2 numerator floor stays **17,838** (ECAT in-scope).
- **CSV sample** (`GO=1 make sample-csv`, fresh network run
  `20260915-000230`, n=100, seed=42): AS-2/AS-3 delivered; the
  corrected D38 pools reproduce exactly — **17,013 / 2,322 distinct**
  — confirming the deterministic-draw claim on a second live
  download. ST-1/3/6/7 unavailable, per the same verified reasons.
- **AS-source probe** (`GO=1 make as-probe`, run `20260915-000255`):
  5 delivered-unavailable-free rows unchanged (AS-2/AS-3 reuse,
  AS-4 ≈70k / AS-7 ≈2k estimates, 18 associations live, 3
  unreachable); **NEW — the six candidates**: AS-31..AS-35
  **unavailable · unknown** — bounded export discovery (≤5 polite
  GETs) found no bulk surface (KemiDigi/Quick-FDS `/export` return
  HTML soft-landings; WINGIS/BASTA/eBVD 404; counts not visible on
  the landing pages) — each with an honest what's-instead note;
  AS-36 **failed** (ECHA `robots.txt` 403 — hardened host; the
  failed-registry exit 2 is the contractual contribution).

**Data-pool finding (D39): no third bulk source today.** The
confirmed-bulk list (`data_sources.csv`) stays DS-1 (AS-2) + DS-2
(AS-3) — the gate (confirmed bulk + identity tuple) was met by
nothing new. The hazard-tail candidates expose their content
per-product behind search UIs, APIs under agreement (eBVD, BASTA),
or unproven enumerability (KemiDigi, WINGIS) — pinning those
per source (category explorations, API terms) is the next unit's
probe deliverable (INPUT-source-expansion-MSE.md, handover §19), not
more URL guessing. Published artifacts: summary
[as-source-probe.summary.20260915-000255.md](as-source-probe.summary.20260915-000255.md)
/ `.csv`, fresh samples `csv-sample.20260915-000230.AS-2.csv` /
`.AS-3.csv` + regenerated [manifest](csv-sample.manifest.md),
full-coverage report snapshot
[probe-report.20260915-000619.3a5fc07d.md](probe-report.20260915-000619.3a5fc07d.md).

## Addendum — D40 (2026-09-17): the BASTA special probe

User-directed deeper probe of AS-33 BASTA online (the relaxed HS-code
requirement: a category proxy is acceptable). Recon-only discipline
(D31/D4) throughout; no accounts, no agreements.

**Route pin (the D39 "API under agreement" answer is NO):** the
recorded "auth-gated API" is bypassed by the site's own web client —
it calls a **same-origin anonymous proxy**,
`https://www.bastaonline.se/apiproxy/v3/...` (verified: 200 JSON,
anonymous). Pinned verbatim from the site's generated OpenAPI client
bundle `assets/ui/services.gen-onZ4SLnf.js` (accessed 2026-09-17):
`/apiproxy/v3/search/articles` (GET; `articleNumber, articleName,
companyId, orgNo, bk04Code, bsabCode, ebvdId, gtin, rsk, eNumber,
page, pageSize`), `/apiproxy/v3/articles/minimal`, and the detail
route `/apiproxy/v3/articles/{articleId}` (which returns the full
field schema: article number, **GTIN**, RSK, E-number, eBVD ID,
grade, company, **BK04**, **BSAB**). The api.bastaonline.se direct
route stays 401 (agreement route documented, never acted on).

**Exact public counts:** `/api/keyfigures/1` = **195,391 articles**
(195,390 the day before — live register moving), `/api/keyfigures/2`
with 1,925 companies per the recon pass. Discrepancy finding: the search route's
unfiltered total advertises **200,769** — 5,378 more than the
keyfigure; the search hits articles the public keyfigure does not
(not de-composed here).

**Sample (run_key
`probe-20260917-as33bastaprobe`, seed 42, n=100):**
`basta-probe.20260917-183244.AS-33.csv`
(both runs published: the corrected sample and the single-page first
run `.181500.` as the structure finding's evidence).
Method: random-page draws above the pinned pool threshold (2C) — the
unfiltered search advertises 100,385 pages at pageSize=250; the
pool is 80 random pages (20,000 rows, the pinned threshold) → seeded
draw of 100. First result (`.181500`) exposed the structure finding
below; the corrected second run pools across positions.

**Sample finding:** 100 rows, 41 manufacturers, 45 distinct BK04
groups, 95 distinct article names. Identity completeness: company +
article number + internal id = **100%**, GTIN 69.8%, eBVD ID 41%,
RSK ~1% (construction index, not retail). Grade: 99 BASTA ALFA,
1 DEKLARERAD. The paint share of the register is small —
in-scope BK04 groups are **03402 Fasadfärg utomhus** and
**03404 Vägg- och takfärg inomhus**: 2 of 100 sampled articles carry
them (both with full identity incl. GTIN — e.g. Flügger/a paint 07
Wood Tex Matt, Akzo Nobel ORIGINAL VÄGG HALVMATT 20).

**Structure finding:** the search pagination is **clustered per
manufacturer block** (a single page is ~one company's article run)
— seeded single-page samples are not representative; the run pools
across 80 random page positions instead (run notes record the
method). The server-side `articleName` search is unreliable for a
paint-subset filter (färg→106, lack→30, multi-token queries behave
inconsistently (200,769 for "lack färg")) — **the paint BK04 code
enumeration (03402/03404) came out of the sample data itself**, and
a server-side paint-filter plan stays an OPEN item (TODOS.md).

**de5 gate NOT met** for `data_sources.csv`: the draw delivered
(bulk surface + identity tuple) but the in-scope paint filter is not
derivable from pinned parameters alone — the 2/100 paint-slice
came from post-hoc BK04 inspection. BASTA remains out of the
bulk-list (pending the paintfilter pin), while its article
enumerability + identity tuple are fact-complete in this record.

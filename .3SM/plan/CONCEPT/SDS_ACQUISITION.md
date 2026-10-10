---
unit: global
stage: CONCEPT
lifecycle: LIVE
updated: 2026-10-10
---

# Topic — SDS document acquisition (concept)

## Abstract

v0.3.5 goal: for the canonical product basis (271,005 products /
2,857 manufacturers, identity layer v0.3.4-r01), obtain the
**manufacturer-authored safety data sheet (SDS/MSDS) as a whole PDF**
and keep it on file, linked per product. No public EU SDS repository
exists (LEAD_SDS feasibility: manufacturer/brand sites + B2B portals
are the availability reality; PCN submissions not public; UFI in Sec.
1.1 as join key). Discovery therefore runs staged, cheapest channel
first: register-carried document links → producer-site SDS libraries
→ per-product web search as the budgeted fallback. Storage follows
the established raw-store pattern (hash-addressed files + `document`
provenance rows) — no PDF bytes in SQLite. Every stored sheet is
quality-gated at fetch time: text-embedded preferred, scanned-only
accepted but flagged for later OCR (D9 cost frame; product data only,
D27; robots/crawl-delay/GO=1 discipline, D20/D21).

## DECISIONS

- **D46 — storage: files in the raw store, not DB blobs.** PDFs land
  in `data/raw/<source-id>/<sha256>.<ext>` (existing store, 427 files
  of probe evidence; d2 `document` backbone, d8 hash-only filenames +
  source allowlist, d16 architecture). The DB gains no payload:
  `document` carries url/source/retrieved_at/raw_hash once; a new
  `sds_document` link row ties product → document. Rationale: tens of
  GB of PDFs would bloat SQLite backups and the port claim; identical
  brand-family PDFs dedup by hash; the audit chain (hash → file) is
  already the design contract.
- **D47 — staged discovery A→B→C.**
  - **A. Register-carried links** (cheapest): raw tables carry per
    -article URLs (BASTA `url` exact on 198,353 rows; ECAT coverage
    to probe). Probe question first: does the register URL serve the
    PDF or an article page that links it? Also harvest candidate
    doc links met during A.
  - **B. Producer-site SDS libraries**: 2,857 manufacturer domains;
    reuse the probe walk machinery (d32 recon, bounded sitemap
    expansion, robots-aware, per-domain crawl-delay;
    `sds_library_visible` metric exists from 0006). Join candidates
    to products via the MATCHING.md stage-1 norms (manufacturer +
    normalized name / GTIN).
  - **C. Web-search fallback** (budget-gated, resumable, cached):
    per-product query = manufacturer + product name + SDS synonyms
    (safety data sheet / SDB / sikkerhedsdatablas / fiche de données
    de sécurité / scheda di sicurezza …). Backend posture open (see
    OPEN ITEMS); paid APIs excluded (D9).
- **D48 — text-layer gate at fetch.** pypdf (already in the approved
  stack) extracts at download: `text_ok` ≥ threshold (pin at Design,
  indicative ≥ 500 chars minus garbage-ratio); scanned-only PDFs are
  kept but flagged `ocr_needed` — OCR execution is out of v0.3.5
  scope. Non-PDF or undownloadable → recorded, not stored.
- **D49 — producer-authorship verdict.** The user requirement
  "authored by the manufacturer" becomes a per-document verdict
  `producer_match` (match / likely / unverified / mismatch) from
  host-vs-manufacturer-domain, PDF metadata, filename patterns.
  Distributor-hosted but manufacturer-branded sheets = likely.
- **D50 — two-pass CLI, run-booked.** `leadhs sds discover --scope
  …` (candidate URLs, no download) and `leadhs sds fetch --scope …
  --budget N` (download + hash + rows; GO=1; idempotent by URL hash;
  resumable) + `leadhs sds status` (coverage: products with ≥1 sheet,
  by source/method/text_ok/producer_match). Scope granularities:
  all | source S | manufacturer N | product N. New run kinds
  `sds_discover` / `sds_fetch` (run/run_kind pattern, counters +
  params_json) keep D18 traceability.

## Table sketch (concept altitude — Design reconciles)

`sds_document` link table: product_id → product; document_id →
document; discovery_method_code → lookup (register_link,
producer_site, web_search, manual); producer_match_code → lookup;
text_ok INTEGER; ocr_needed INTEGER; language; revision_date; active
INTEGER (revisions all kept, active flag); first_seen; run_id.
Design-ahead block `0017__sds` (old sds_document shape) predates the
identity layer and renumbers against 0013 — reconciliation + the
concrete migration number (proposal: 0014) is Design work.

## Scale honesty

Tier A is URL checks over ~200–290k rows (cheap, polite). Tier B is
2,857 site walks (days at Crawl-delay 10, resumable). Tier C is one
web query per uncovered product — the expensive tail; budgets +
checkpoints + `sds status` make coverage visible and pausable.
Exhaustive vs stratified-first posture for tier C: OPEN (user).

## OPEN ITEMS

- Register URL semantics probe (ECAT + BASTA): URL → PDF directly or
  article page? Coverage of ECAT `url` column? (first v0.3.5 probe)
- Search backend posture for tier C: DuckDuckGo HTML endpoint (bot-
  tolerant, ToS-gray at scale) vs self-hosted SearXNG (no third-party
  ToS, more infra) — decide at Design; conservative rate + cache
  either way.
- Tier-C posture: exhaustive-all vs stratified-first (tool supports
  both via budget + resume; user decides per run).
- sds_document migration number + design-ahead 0017 reconciliation.
- Multi-revision policy default (keep all + active flag — confirm).
- Language priorities for search-synonym sets (DE/FR/IT/EN/SE/NL …).
- OCR engine posture (tesseract) — later unit, flag-only here.

## Detail documentation

Nothing public yet — this topic matures at v0.3.5 design; LEAD_SDS.md
and METHODOLOGY.md carry the why (detection, feasibility), RAW_SOURCING.md
and SOURCE_ACCESS_MODES.md the instruction/mode vocabulary this topic
reuses.

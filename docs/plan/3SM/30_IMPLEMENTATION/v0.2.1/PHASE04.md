---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE04 — Capability execution (GO=1)

## Objective

Run the capability sounding-out: automate the official CSV/API
register exports and characterize the XLSX/auth-gated registers and
the enumerated PE universe by manual record — per source, the six
capability metrics with provenance (URL + access date + run_key).

## Preconditions

- PHASE03 done (register loaded, active flags correct).
- Real-network go-ahead (`GO=1`) — official exports/APIs and
  manual-web recon only (D3, D31; no scraping).

## Governing references

- `../../20_DESIGN/units/v0.2.1.md` (cap2/cap4; XLSX/auth-gated +
  PE-universe manual record)
- `../../10_STRATEGY/v0.2.1.md` (U3 official exports = recon; U6
  provenance)
- `../../20_DESIGN/MASTER/interfaces.md` (i17; run semantics; manual
  record)

## Steps

1. **Automated capability runs** on the active `access_method_code IN
   (download, api)` AS rows: `leadhs probe run --mode capability
   --all` (GO=1). Confirm per-register export shapes during the run:
   ECAT CSV column layout, Nordic Swan CSV, environdec/IBU, PRODCOM/
   stat APIs. Record `products_identifiable` + the five capability
   metrics per source; the raw export archived as a document. Any
   source whose shape is not automatable → document-blocked note,
   then fall to manual record.
2. **Manual capability records** for the auth-gated / XLSX-only
   registers (Blue Angel, INIES) and the enumerated PE universe:
   `leadhs probe record --mode capability` per source — download +
   human review, record the six metrics (volume via `sitemap_products`
   recon where available, else manual `products_identifiable`).
   Each record carries the source URL + access date + run_key.
3. **Open-item resolution during the run:** INIES API auth (email +
   apiKey + read permissions) — confirm whether the web search
   suffices for recon or document-blocked; per-register paint counts
   recorded in the notes; register export shapes confirmed.
4. **Tests (t11, integration):** end-to-end on the fixture register
   source (if available) or via the adapter fixtures; manual-record
   capability path; interrupt mid-capability-run → per-source runs
   persist (existing semantics, exercised for capability).

## Deliverables

Per-source capability findings (six metrics) for every capability
source, automated or manual, each provenance-cited; document-blocked
sources honestly noted; `db audit` exit 0.

## Exit gate

Every capability source (active AS rows + auth-gated + PE universe)
recorded with a capability profile or documented-blocked; every
number carries a URL + access date + run_key; `db audit` exit 0.

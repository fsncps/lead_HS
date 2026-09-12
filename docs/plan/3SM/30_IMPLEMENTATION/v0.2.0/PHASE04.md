---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE04 — Statistics execution (N1 backbone; GO=1; no scraping)

## Objective

Record the count-bearing sources or document them blocked: CS-2
full-year import aggregation, PRODCOM/SBS, PCN verification, SPIN,
and AS counts — the DB inputs for N1 and the register side of N2.

## Preconditions

- PHASE03 done (enumerated register loaded).
- Explicit real-network go (`GO=1`) — APIs, downloads and manual-web
  only; no scraping (D31).

## Governing references

- `../../20_DESIGN/units/v0.2.0.md` (nu2/nu3/nu5)
- `../../10_STRATEGY/DATA_SOURCE.md` (discipline; D3 — APIs/downloads
  preferred)
- `../../10_STRATEGY/v0.2.md` (scope items 1–2; V2/V8)

## Steps

1. **CS-2 aggregation (phased GO runs):** verify on one HS first,
   then the full sweep — `GO=1 make census`. The adapter lands
   records_hs3208/3209/3213 + the four sum codes
   (trade_kg/eur_hs3208/3209, import flow, latest year) + partner
   tops and supplementary units in finding notes + archived raw
   JSON. Re-query failure → documented-blocked census_status record.
2. **ST-3 PRODCOM/SBS (manual records):** `make record` —
   producers_registered (SBS NACE 20.30 number of enterprises,
   persons employed as notes) + PRODCOM production context in
   notes; URL + access date per P3.
3. **ST-1 PCN (manual-web):** verify whether ECHA publishes
   formulation-count aggregates — recorded via products_registered
   or census_status document-blocked (acceptable outcome; MASTER
   OPEN carries).
4. **ST-2 SPIN (download, best-effort):** fetch attempt
   (spin2000.net — baseline timeout known); on success,
   extraction_path check (mdbtools; BinaryMissing → documented)
   and coarse products_registered via `make record`;
   documented-blocked acceptable.
5. **AS counts (manual records, nu3 split):** producers_registered
   for CEPE/association member counts; products_registered for
   national register product counts — never mixed.
6. `make db-audit` exit 0.

## Deliverables

N1 DB inputs complete per source (counts or documented-blocked);
every record with URL + access date (P3/R4).

## Exit gate

Every count-bearing source (CS-2, ST-1, ST-2, ST-3, AS rows) has
recorded counts or an explicit census_status blocked/deferral
record; audit exit 0; exit-code discipline held (exit 2 sweeps
documented).

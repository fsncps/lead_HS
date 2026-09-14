---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE03 — Register expansion to census shape

## Objective

Grow the source register from 40 rows to its census shape
(~150–250 rows): the CS/ST/AS/LI additions the v0.2.1 PHASE03 scope
defined but never executed, the PE universe enumerated, and the
`export_url`/`export_format` anchors populated for every known
export — including the confirmed ECAT CSV URL.

## Preconditions

- PHASE02 done (export columns + staging machinery live).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (source expansion, fu6, i20)
- `../../10_STRATEGY/v0.2.2.md` (source expansion table, U8)
- `../../10_STRATEGY/DATA_SOURCE.md` (six source classes, register
  scope D31, D3)
- `../../20_DESIGN/MASTER/interfaces.md` (i13 enumeration register
  model; `source load` validation)

## Steps

1. **CS additions:** 2–3 national trade-DB cross-check rows
   (Destatis, Datacomex, Coeweb — `active=0`, manual-web
   characterization). Intra-EU flows ride the existing DS-045409
   dataset (no new row).
2. **ST additions:** PRODCOM production dataset row (distinct from
   SBS ST-3; bulk TSV access method); KEMI products-register
   statistics row (`active=0`, verify-first note).
3. **AS additions:** NF Environnement, natureplus, EPD Norway
   (product-level register rows; active per known export availability,
   `active=0` where format unconfirmed); national associations VdL /
   FIPEC / BCF (member counts, `active=0`, manual).
4. **LI additions (D27 framing — product counts only, no legal
   content):** IPEN lead-paint reports, UNEP/SAICM status, EEA,
   ILZSG supply stats — context + prevalence-prior rows,
   `active=0`, manual-record class.
5. **PE universe enumeration (fu6):** CEPE member sites → per-site
   PE rows (`active=0`, `channel=mfr`); DIY EU-wide (~20–40),
   marine, art expansions; structured notes convention
   (channel/listed_by/listed_date/inclusion); the ~75-site active
   recon subset per the widened caps (MFR≤40, DIY≤10, MARINE≤10,
   ART≤15) marked in notes.
6. **Export anchors:** populate `export_url`/`export_format` for
   every known export — ECAT CSV (the confirmed publicstorage URL,
   csv format), PRODCOM bulk TSV, others as verified during the
   phase; unknown stay NULL until W1/W2 pin them.
7. **Version 0.2.2** (pyproject + `--version`).
8. **Load validation:** `source load` green on the expanded CSV;
   `probe-dry` plans every active row; duplicate-active-host check
   respected (distinct-host rule as in AS-2).

## Deliverables

Expanded `sources.csv` (~150–250 rows); export anchors populated;
version 0.2.2; load-validation run log.

## Exit gate

`make sources-load` clean; `probe-dry` plans every active row with
zero network; register counts recorded in the phase notes; audit
exit 0.

## Execution notes (2026-09-14)

- Register: 40 → **100 rows** loaded (CS 2→5, ST 3→5, AS 7→30, LI
  0→4, PE 25→56... exact per-class counts in the DB). Version 0.2.2.
- Export anchors: ECAT CSV pinned structurally (the confirmed
  publicstorage URL, format csv); ST-4 PRODCOM carries format tsv
  with the exact bulk URL pinned at W1; others stay NULL until
  W1/W2 pin them.
- **Breadth note (scope honesty):** the desk-enumerable census shape
  is 100 rows, below the strategy's ~150–250 estimate. The remaining
  breadth is the CEPE member-manufacturer enumeration (~800 via the
  20 EU/EEA national associations) — that crawl IS the W3 wave
  content (strategy four-wave table: "full enumeration (CEPE ~800 →
  rows, active=0)" at execution), not a desk task. The full PE
  universe enumeration lands during PHASE05 W3.
- i13 refinement (needed to load the official rows): the
  duplicate-active-host rule keys on the bare host within PE (one
  site = one floor contribution) and on host+path outside PE (one
  host legitimately carries distinct datasets — Eurostat Comext CS-2
  vs PRODCOM ST-4). Tested.
- Desk URL verification (single HEAD per new host, 2026-09-14):
  ~50 reachable; 8 hosts unreachable from the desk environment
  (egress) — marked in notes with "verify at W3/W1"; 403/429/503
  walls noted (access characterization belongs to the wave).
  CEPE national-association rows are CEPE-page-pinned
  (listed_by=cepe.org/list-of-national-associations).

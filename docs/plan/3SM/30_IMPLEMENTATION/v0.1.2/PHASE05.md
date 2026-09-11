---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE05 — Census capability (per-HS metrics, structured report)

Status: planned · Depends on: PHASE04 (green suite) · Governs: the
report contract the census close-out delivers through.

## Objective

Give the census its final shape before it runs: the per-HS count
metrics the report must present (od9 — the OD-A decision: migration
INSERT, not M1 deferral) and the structured per-source report content
(od8/D25 — identification, access, content, counts, availability,
provenance, plus a cross-source summary matrix, "source feasibility"
framing).

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §Census close-out (od8–od9).
- `../../20_DESIGN/MASTER/interfaces.md` — probe_metric vocabulary
  (i4 extension rule: new metrics by migration INSERT).
- `../../10_STRATEGY/DATA_SOURCE.md` — §Census metadata set
  (complete source record, D25).
- `../v0.1.2/MASTER.md` — B7 (OD-A resolution).

## Steps

1. **Migration `0003__per_hs_metrics.sql`** — INSERT into
   `probe_metric`: `hs3208_count` ("HS 3208 records"), `hs3209_count`
   ("HS 3209 records"), `hs3213_count` ("HS 3213 records") — value
   type numeric; codes never renamed. Idempotent application via the
   schema_version machinery; applies on existing v0.1.1 databases
   (backup default on).
2. **`metrics.py`** — extend the constants + seed list; extend the
   vocabulary sync test to pin **0001 + 0003 == metrics.py**.
3. **`report.py`** — restructure the census report to the D25
   metadata set: one structured section per source
   (identification; access incl. blocked/robots status + notes;
   content; counts incl. per-HS where exposed; availability;
   provenance — run keys, timestamps, archived-document links) and a
   cross-source summary matrix; run status and notes visible in all
   formats; section titles state "source feasibility" — never
   product or lead counts. md/csv/json outputs updated accordingly.
4. **Tests** — migration 0003 idempotency + order; sync test
   extension; report golden files regenerated **with explicit
   review** (t3 policy); R4 value/type rule holds for the new
   metrics (`probe record --metric hs3208_count` accepts numeric
   only).

## Deliverables

`src/leadhs/migrations/0003__per_hs_metrics.sql`; `metrics.py`
extension; restructured `report.py`; test + golden updates.

## Exit gate

- `pytest` green offline, including the extended sync test and the
  regenerated golden files.
- Migration 0003 applies clean on a fresh DB **and** upgrades an
  existing 0001/0002 database (backup taken).
- The report on the fixture corpus shows: per-source structured
  sections, the summary matrix, feasibility framing, visible run
  status/notes — in md, csv and json.
- Per-HS metrics usable via `probe record`; text values rejected
  (R4).

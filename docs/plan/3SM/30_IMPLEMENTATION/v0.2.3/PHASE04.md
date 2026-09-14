---
unit: v0.2.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE04 — Benchmarks on real data + the report section

## Objective

Run B1–B6 on the real staging data and extractions, synthesize the
class-vote table and the dual-level verdict, and extend the compiled
report with the "pool estimate v2" section — vote table (vintage
column, indeterminate rows visible), verdict or its refusal, and the
supersession note (v2 headline replaces Q1 v0; v0.2.2 numbers marked
superseded, snapshot references).

## Preconditions

- PHASE01–03 done (verdict engine green on synthetic data; DK rows
  staged or fallback recorded; extractions dispositioned).

## Governing references

- `../../20_DESIGN/units/v0.2.3.md` (X5/X6/X7-report, vote rule,
  c1–c7, tr8; report extension)
- `../../20_DESIGN/MASTER/interfaces.md` (i12 report contract, i16
  numbers contract, i20 wave contract)
- `../../30_IMPLEMENTATION/v0.2.2/PHASE06.md` (report assembly + goldens
  precedent; publish-history snapshots in PHASE07)

## Steps

1. **Execute:** run the benchmarks module against the real staging
   DB + extraction records — `compute_b1()…b6()` with the pinned
   scenario assumptions; every number is a staging query result or a
   dated extraction (never a typed literal).
2. **Synthesize:** `vote_table()` + `verdict()` on the real
   benchmark results; render per c1 (indeterminate rows visible;
   <3 available → "insufficient basis"), c3 (tie → span + flip
   assumptions, no confidence claim), c4 (vintage column;
   cross-vintage deltas flagged); each benchmark incompatible with
   the verdict becomes an explicit open item in the section text.
3. **Report section:** extend the od8 report layer with "pool
   estimate v2: magnitude-class verdict" — class taxonomy, vote
   table, dual-level verdict (SKU/registration and formulation via
   the c2 compression-range), confidence statement or refusal, and
   the supersession note (tr8); csv/json carry the full structure
   (i12).
4. **Goldens:** regenerate the report goldens with review (c7 —
   vote-table rendering is pinned); supersession rendering tested
   (v1 marked superseded with snapshot references, v2 headline).
5. **Audit + suite:** `db audit` exit 0; full offline suite green
   incl. all t13 items on real-shaped data.

## Deliverables

Real-data benchmark results; vote table + verdict; report section +
goldens; updated open items (divergent benchmarks).

## Exit gate

Report renders on real data per the pinned rule including its
refusal paths; goldens reviewed; supersession visible; audit clean;
suite green.

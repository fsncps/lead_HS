---
unit: v0.2.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE01 — benchmarks.py: the verdict engine (synthetic data only)

## Objective

Land `src/leadhs/benchmarks.py` — the pure-function verdict engine:
named staging-query functions (ENG 2A), the six benchmark
computations B1–B6 with low/base/high scenario propagation, the
class-vote table and the verdict under the pinned confidence rule —
plus the shared synthetic-staging fixture builder and the full
verdict-path test set (t13). Everything in this phase runs offline on
synthetic data; no network, no real staging changes.

## Preconditions

- v0.2.2 PHASE01–07 done (staging DB + ingest path, report layer,
  155+ offline tests green).
- Design decisions in force: tr1–tr10; ENG 1A (benchmarks module)
  and 2A (named queries + shared fixture builder).

## Governing references

- `../../20_DESIGN/units/v0.2.3.md` (B1–B6 table, vote rule, c1–c7,
  tr1–tr10, t13)
- `../../10_STRATEGY/v0.2.3.md` (design-turn reframe; T4 amended —
  no gate)
- `../../20_DESIGN/MASTER/data_model.md` (staging schema)
- `../../20_DESIGN/MASTER/interfaces.md` (i12/i16 — report/numbers
  contracts)
- TODOS.md (PE channel mapping context — pinned in this phase)

## Steps

1. **Module skeleton:** create `src/leadhs/benchmarks.py` with the
   benchmark-result structure (name, quantity, vintage/reference
   period, low/base/high band, implicated classes, assumption notes)
   — the reusable shape per design c7 and the trajectory point.
2. **Named query functions (2A):** one function per staging question
   — ECAT category breakdown + variant structure per key tier
   (EAN → name-dedup → licence; compression factor as a **range**,
   c2), PE `products_listed` distribution by channel, staged DK
   counts by function/year (empty until PHASE02), staged Comext CN8
   tonnage. Each returns plain dicts; zero report-layer knowledge.
3. **Compute functions:** `compute_b1()`…`compute_b6()` as pure
   functions — inputs passed in, explicit scenario assumptions as
   parameters, `indeterminate` as a first-class outcome (c1: no
   penetration denominator, missing document). B4 uses the
   manufacturer-channel subset (tr7); B5 carries the ECAT∩DK
   calibration hook (populated in PHASE02).
4. **Synthesis:** `vote_table()` (rows = benchmarks with vintage +
   notes, columns = classes a–e; indeterminate rows visible, c4
   vintage deltas flagged) and `verdict()` implementing the pinned
   rule: ≥3 *available* benchmarks converge at base AND no benchmark
   exclusively compatible with a non-adjacent class; tie → span +
   flip assumptions, no confidence claim (c3); <3 available →
   "insufficient basis" (c1).
5. **Fixture builder (2A):** one `make_synthetic_staging()` test
   fixture constructing a small synthetic staging DB (ECAT-shaped
   rows with known category/EAN sparsity, PE channels, Comext
   tonnage) — shared by all refinement/benchmark/vote tests.
6. **Tests (t13 core):** verdict-path unit tests — ≥3-converge →
   class; tie → span, no claim; <3 available → "insufficient basis";
   exclusive non-adjacent conflict → flagged; scenario propagation
   arithmetic; indeterminate rendering; hostile case: synthetic
   distributions chosen to flip the compression factor — the outputs
   must flip honestly. Pin the PE channel-mapping assumption
   (manufacturer-assortment sites) as a documented constant with a
   comment linking the design decision.

## Deliverables

`src/leadhs/benchmarks.py` (result structure, query functions,
compute_b1–b6, vote_table, verdict); fixture builder in the test
suite; verdict-path tests.

## Exit gate

Module imports clean; full verdict-path test set green offline
(synthetic data only); no network access anywhere in the phase;
existing suite still green.

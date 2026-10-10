# ENGINEERING — units

## STATE
active unit: v0.3.4

## UNITS

| unit | branch | stage | lifecycle | theme |
|---|---|---|---|---|
| v0.3.0 | main (unit-branch init waived by user, 2026-10-03) | ENGINEERING | SHIPPED 2026-10-09 (archived; tag v0.3.0) | instruction-driven raw source layer (generic acquisition pipeline) |
| v0.3.4 | v0.3.4 | ENGINEERING | LIVE | deterministic normalization + matching (identity layer) |

## RUN INVENTORY  (a section per unit — mandatory)

### v0.3.0
runs: r01, r02, r03 — all DELIVERED; unit shipped 2026-10-09 (dir
archived to `_archive/v0.3.0/`; this section is the historical mirror).
mirror: `../DESIGN/_archive/v0.3.0/RUNS.md`
detail: `_archive/v0.3.0/MASTER.md`

### v0.3.4
runs: r01, r02, r03
phases: r01/PHASE01 — PLANNED · (r02, r03 phase plans land at their run planning)
mirror: `../DESIGN/v0.3.4/RUNS.md` (authority for goals/DoD)
detail: `v0.3.4/MASTER.md` (the phase table)

## ROADMAP

r01 (canonical identity layer: migration 0013, resolve, rebuild, doctor
checks) → r02 (enrichment pass, MA13 majority rules) → r03 (matching:
blocking + scoring + linkage_candidate + review queue; FINAL folded per
the RUNS.md gates unless the user directs a FINAL dir). Sequencing is
strict: r02 planning pends r01 DELIVERED (enrich reads the canonical
tables + identity_state r01 writes); r03 planning pends r02 DELIVERED
(match reads enriched canonical fields). Design OPEN ITEMS pin at their
run planning: score bands + calibration at r03; block caps already
pinned (il6). Next-unit recommendation after v0.3.4: v0.3.8 (source
expansion, per the D43 roadmap) — MSE inputs ride the spine.

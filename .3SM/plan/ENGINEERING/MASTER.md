# ENGINEERING — units

## STATE
active unit: v0.3.0

## UNITS

| unit | branch | stage | lifecycle | theme |
|---|---|---|---|---|
| v0.3.0 | main (unit-branch init waived by user, 2026-10-03) | ENGINEERING | LIVE | instruction-driven raw source layer (generic acquisition pipeline) |

## RUN INVENTORY  (a section per unit — mandatory)

### v0.3.0
runs: r01, r02, r03
phases: r01/PHASE01 — PLANNED · (r02, r03 phase plans land at their run planning)
mirror: `../DESIGN/v0.3.0/RUNS.md` (authority for goals/DoD)
detail: `v0.3.0/MASTER.md` (the phase table)

## ROADMAP

r01 (raw schema + instruction foundation, offline) → r02 (scan + guards →
committed instructions AS-2/AS-3) → r03 (seed interpreter + live bulk load;
FINAL folded per rs10). Sequencing is strict: r02 planning pends r01
DELIVERED (the scan works on the schema + validator from r01); r03 planning
pends r02 DELIVERED (the interpreter consumes the committed instructions).
Design OPEN ITEMS pin at their run planning: guard-derivation formula at
r02; nothing deferrable blocks r01. Next-unit recommendation after v0.3.0:
v0.3.4 (matching layer, concept MATCHING.md) per the D43 roadmap.

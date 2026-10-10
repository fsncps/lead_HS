# ENGINEERING — units

## STATE
active unit: (none — v0.3.4 shipped 2026-10-10; next: v0.3.5 at /init-unit)

## UNITS

| unit | branch | stage | lifecycle | theme |
|---|---|---|---|---|
| v0.3.0 | main (unit-branch init waived by user, 2026-10-03) | ENGINEERING | SHIPPED 2026-10-09 (archived; tag v0.3.0) | instruction-driven raw source layer (generic acquisition pipeline) |
| v0.3.4 | v0.3.4 | ENGINEERING | SHIPPED 2026-10-10 (early close, r01 of 3 runs; r02/r03 → v0.3.5/v0.3.6; archived; tag v0.3.4) | canonical identity layer (resolve/rebuild/status) |

## RUN INVENTORY  (a section per unit — mandatory)

### v0.3.0
runs: r01, r02, r03 — all DELIVERED; unit shipped 2026-10-09 (dir
archived to `_archive/v0.3.0/`; this section is the historical mirror).
mirror: `../DESIGN/_archive/v0.3.0/RUNS.md`
detail: `_archive/v0.3.0/MASTER.md`

### v0.3.4
runs: r01 DELIVERED (executed 2026-10-10) · r02, r03 DEFERRED →
follow-up units v0.3.5/v0.3.6 · FINAL folded into ship (early close,
user decision; gate evidence in the mirror § CLOSURE)
mirror: `../DESIGN/_archive/v0.3.4/RUNS.md` (authority for goals/DoD)
detail: `_archive/v0.3.4/MASTER.md`

## ROADMAP

**v0.3.5 — enrichment pass** (ex-v0.3.4 r02; NEXT-UP in the PIPELINE):
canonical rows completed from their per-source observations — majority
fill/replace per MA13 over the r01 back-links; plans carried verbatim
from the archived RUNS.md r02 entry.
**v0.3.6 — matching layer** (ex-v0.3.4 r03; NEXT-UP): blocking +
scoring + linkage_candidate + review-queue visibility; score-band
calibration pins at its planning (il6 caps already pinned).
**v0.3.8 — source expansion** (PARKED ordering unchanged, per the D43
roadmap) — MSE inputs ride the spine.

Sequencing: v0.3.5 pends nothing (canonical tables + identity_state
exist); v0.3.6 pends v0.3.5 DELIVERED (match reads enriched fields).
Deferred FINAL inputs (chaos, rebuild round, SQLite pin, staging-norm
recompute) ride the inheriting units' FINAL gates.

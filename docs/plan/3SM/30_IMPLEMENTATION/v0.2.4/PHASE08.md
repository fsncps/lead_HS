---
unit: v0.2.4
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-15
---

# PHASE08 — Addendum (D39): full-probe round + source-expansion reconnaissance

## Objective

On explicit user instruction (2026-09-15), run the full probe suite
over all registered sources WITH the consultant probe queue
(strategy INPUT, 2026-09-14), render a new report covering
everything, and report the new data-pool findings. The INPUT digest's
deferral (de7) was about formal unit adoption — this phase is the
reconnaissance pass itself (allowed under the numbers-first,
reconnaissance-only frame).

## Steps

1. **Register grew from 30 to 36 AS rows:** the six new candidates
   AS-31..AS-36 (KemiDigi, WINGIS/GefKomm-Bau, BASTA, eBVD,
   Quick-FDS, ECHA PT21) enter `sources.csv` as probe-queue rows
   (priority + provenance cited to the handover; all `open`, 1).
   `as_probe.REGISTRY_IDS` extends to 15 ids; the split-guard test
   asserts 15 + 21 = 36 (a register change fails loudly).
2. **Census sweep:** `GO=1 make census` (probe run --all, 108
   sources) → report render → audit.
3. **CSV sample:** fresh real-network `GO=1 make sample-csv` (n=100,
   seed=42).
4. **AS-source probe:** `GO=1 make as-probe` over all 36 AS rows.
5. **Render + publish:** probe-report set (stable + timestamp-hash
   snapshots), corrected-registry summary + manifest + per-source
   samples published in `docs/report/`.
6. **Docs:** design + strategy addenda (D39), report section,
   README EN/DE/FR, management summary, DATA_SOURCE note,
   dashboards; commit + push on explicit instruction.

## Exit criteria

- All three run families executed same-day with exit-0 (or exit-2
  tolerated for expected blocked/failed sites); audit clean; the
  published set is self-describing (run timestamps + hashes).

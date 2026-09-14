---
unit: v0.2.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE05 — Close-out: publish, docs, wheel, TODOS

## Objective

Close unit v0.2.3: publish the report with snapshots, update all
public and planning documentation, cut the wheel at 0.2.3, write the
LOG entry, and update TODOS.md (retire nothing further; add the
re-benchmark cadence item per the ENG review).

## Preconditions

- PHASE04 done (report renders the verdict on real data; audit
  clean; suite green).

## Governing references

- `../../20_DESIGN/units/v0.2.3.md` (X7; acceptance criteria)
- `../../30_IMPLEMENTATION/v0.2.2/PHASE07.md` (close-out precedent;
  publish-history snapshot policy + addendum)
- AGENTS.md (docs conventions — READMEs EN/DE/FR, management summary
  DE/FR, provenance, translations-in-the-same-changeset)

## Steps

1. **Publish:** `make report` + `make report-publish` — the new
   timestamp-hash snapshot appends per the publish-history policy
   (v0.2.2 PHASE07 addendum); the live report carries the v2
   headline with the supersession note.
2. **Unit report:** write `docs/report/report-0.2.3.md` (EN-only,
   per convention) — method (six benchmarks, vote rule), the real
   numbers with provenance, the verdict and its confidence statement
   (or refusal), divergences as open items, and what the v0.2.2
   refinement analyses contributed as supporting evidence.
3. **Public docs:** README (EN, then DE/FR translations in the same
   changeset) gains the v0.2.3 summary section; management summary
   (DE/FR) updated with the magnitude-class verdict in plain
   language; keep provenance (source, year, URL, access date) on
   every load-bearing number.
4. **Planning docs:** strategy (`10_STRATEGY/v0.2.3.md` —
   built/completed status), design unit, strategy MASTER + root
   dashboard (v0.2.3 done; next unit per the dashboard), 3SM LOG
   entry.
5. **TODOS.md:** add the **re-benchmark cadence** entry (ENG review
   TODO — see format requirements): re-run B1–B6 and re-issue the
   verdict when materially better register data lands (v0.3+);
   what/why/pros/cons/context per house format.
6. **Wheel:** version 0.2.3; build + install-verify.

## Deliverables

Published report + snapshots; report-0.2.3.md; README EN/DE/FR +
management summary updates; planning-doc statuses; LOG entry;
TODOS.md re-benchmark entry; wheel 0.2.3.

## Exit gate

Wheel 0.2.3 install-verified; docs current with the real verdict
numbers (EN/DE/FR consistent); snapshots present; LOG written;
TODOS.md updated; no commit/push without explicit user instruction.

## Addendum (2026-09-14): render history policy

**Finding (user report):** working renders in `data/report/` used
unversioned names — every `make report` overwrote the previous
report, so the render history was invisible (only `docs/report/`
snapshots preserved history, and only on explicit publish).

**Decision (user, 2026-09-14):** all saved report files get
timestamps; no new unit — small addition folded into v0.2.3 as an
addendum, mirroring the v0.2.2 PHASE07 publish-history precedent.

**Executed:**
- Makefile `report`: renders `probe-report.<UTC ts>.{md,csv,json}`
  (one shared `TS` per run) and refreshes the unversioned names as
  "latest" copies; echo of the set name. Every network chain that
  calls `make report` (census/recon/capability/landscape) inherits
  the policy.
- Makefile `report-publish`: stem normalization strips a render
  timestamp from the stable copy name (`WHICH` with a timestamped
  render still publishes as `probe-report.md` + `<pub-ts>.<sha256-8>`
  snapshot — no double timestamps); policy otherwise unchanged.
- Dry-run test extended (timestamped renders + 3 latest copies).
- AGENTS.md conventions bullet + ARCHITECTURE.md repository layout
  and routing note updated.

**Verification:** two consecutive `make report` runs leave two
timestamped triples (nothing overwritten); publish dry-check with a
timestamped `WHICH` stages stable + snapshot names correctly.

## Addendum 2 (2026-09-14): full probe re-run — trade double-count defect fixed

**Trigger:** user-requested full probe run with the new (timestamped)
report. Waves 1–3 re-ran clean; W3's incident set identical to the
morning run (4 blocked / 6 failed, deterministic); only live drift:
PE-20 SDS doc links 659→652.

**Defect:** re-runs append new run_keys (citable staging history by
design), but the report's trade queries (`_cn8_trade`, `_funnel`
shares, `_reconcile` trade flags) and register helpers (`_q2_union`,
`_ppp`, `_overlap_pilot`) read **across** runs — CN8 trade values
doubled after the second W1 staging (register sections already used
`MAX(run_key)`, so ECAT figures stayed stable; headline verdicts were
never affected — per-CN8 *shares* are doubling-invariant and B1 rides
method-sheet constants).

**Fix:** shared `_latest()` JOIN fragment scoping every staging read
to the latest run per source; reconciliation flags now cite the run;
regression test `test_trade_reads_scope_to_latest_run` (two trade
runs + two register runs → single-run totals). Suite **342 passed,
2 deselected**.

**Findings restoration:** W2's re-probe appended generic
format-finding notes that shadowed the curated IBU/environdec/NF/
natureplus/EPD-Norway/PRODCOM notes; re-recorded via the manual
fallback (`probe record`, runs `*manual-2`), as the invariant demands.

**Companion document:** `docs/report/benchmarking-0.2.3.md` (results,
benchmarking/comparison considerations, gaps, paths) — linked from
the unit report + READMEs (EN/DE/FR).

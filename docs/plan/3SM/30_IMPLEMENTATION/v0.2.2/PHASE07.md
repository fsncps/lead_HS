---
unit: v0.2.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE07 — Docs & close-out

## Objective

Close the unit: public docs carry the real landscape numbers at the
achieved granularity; the v0.2.1 governance repairs land; translations
current or drift-marked; wheel verified.

## Preconditions

- PHASE06 done (report published; audit clean).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.2.md` (deliverables & acceptance)
- AGENTS.md documentation conventions (bilingual summary, drift
  markers, provenance)
- v0.2.1 review findings (provenance repairs — PHASE05 executed the
  data side; this phase the docs side)

## Steps

1. **README EN/DE/FR:** current-stage heading → the landscape
   unit; the compiled numbers (funnel Q1 range / Q2 floor / Q3
   reach, census, register size) reported at the achieved
   granularity; Status line (tests, versions); roadmap +
   implementation-table rows. DE/FR translations updated in the same
   change set or `source_updated` left as a visible drift marker.
2. **`docs/management_summary.md` (DE/FR):** project status to
   v0.2.2 with the funnel numbers and their epistemic labels —
   always current per AGENTS.md.
3. **LOG entry:** the unit's build trail — including the defect note
   for the v0.2.1 HTML-as-CSV incident (seven bogus AS-7 findings,
   deleted 2026-09-14, `_sniff` gate introduced).
4. **Planning docs:** strategy `v0.2.2.md` freeze remains an explicit
   user action; MASTER dashboards updated (unit tables, readiness).
5. **Wheel:** `leadhs-0.2.2-py3-none-any.whl` builds; install-check
   into a throwaway env; dist/build stay gitignored.
6. **Final sweep:** full offline suite; `db audit`; register/status
   tables in the docs match the real DB.

## Deliverables

README EN/DE/FR + management summary DE/FR updates; LOG entry; unit
MASTER phase table → done; wheel verification.

## Exit gate

Docs carry the real landscape numbers (no placeholder or stale
counts); translations current or drift-marked; LOG entry written;
suite green; audit exit 0; wheel 0.2.2 verified.

## Execution results (2026-09-14)

- **LOG** (`docs/plan/3SM/LOG.md`): v0.2.2 build-trail entry written —
  landscape run + funnel numbers + engine repairs, including the
  **defect note for the v0.2.1 HTML-as-CSV incident** (seven bogus
  AS-7 environdec findings accepted by the CSV parser, deleted
  2026-09-14, `_sniff` gate introduced and regression-tested).
- **README EN**: new current-stage block "the three-question funnel
  (v0.2.2)" with the real numbers (Q1 [85,840–343,360] / Q2 17,170 /
  Q3 3,590 / ratio 0.05–0.2; dispositions 36/48/4/13; all 13 CN8
  codes staged); Status line → 299 tests, v0.1.1–v0.2.2 built;
  implementation-table row updated; "Norde registers" typo fixed.
- **README DE/FR**: current-stage blocks translated in the same
  change set (Trichter/entonnoir), Status lines updated;
  `source_updated: 2026-09-14` (current).
- **`docs/management_summary.md`**: new DE/FR funnel sections with
  the epistemic labels; Stand/État → 14.09.2026; next-steps sections
  reflect the v0.2.2 completion (second register staging → overlap
  pilot, then the pilot collection).
- **Planning docs:** unit MASTER phase table complete (01–07 done);
  strategy `10_STRATEGY/v0.2.2.md` freeze remains an explicit user
  action (still DRAFT).
- **Wheel:** `dist/leadhs-0.2.2-py3-none-any.whl` built; install
  check into a throwaway venv — import + `--help` clean; dist/build
  stay gitignored.
- **Final sweep:** full offline suite **299 passed, 2 deselected**;
  `db audit` clean; the numbers in the docs match the published
  report and the DB.

## Addendum (2026-09-14): publish history policy

**Finding:** `report-publish` copied each report to a fixed name
(`docs/report/probe-report.{md,csv,json}`); every unit republish
overwrote the previous unit's snapshot — the v0.2.0 and v0.2.1 report
states were already lost. A same-file publish (WHICH already inside
`PUBLISH_DIR`) also failed with a plain `cp`.

**Decision:** every publish stages the stable "latest" name (doc
links stay valid) **and** an immutable snapshot
`<stem>.<UTC ts>.<sha256-8>.<ext>` in `PUBLISH_DIR`; same-file
publishes are tolerated (stable copy skipped). This supersedes the
fixed-name-only copy contract in `v0.1.2/PHASE03.md` (closed unit,
docs left untouched).

**Executed:** Makefile `report-publish` extended; the currently
published v0.2.2 report backfilled as
`probe-report.20260914-032427.{12c9bf25.md,02c971d2.csv,f2bb4152.json}`;
verified in a throwaway `PUBLISH_DIR` (stable copy + snapshot; second
run idempotent on the stable name, snapshot name unchanged for
identical content within the same second).

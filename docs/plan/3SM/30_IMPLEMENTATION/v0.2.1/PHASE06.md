---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE06 — Docs & close-out

## Objective

Bring the documentation current with the real capability data and
close the unit: management summary (DE/FR), register tables, drift
markers, LOG, and golden regeneration with review.

## Preconditions

- PHASE05 done (capability report published; real data in hand).

## Governing references

- `../../20_DESIGN/units/v0.2.1.md` (acceptance criteria; references)
- `../../10_STRATEGY/v0.2.1.md` (deliverables & acceptance)
- `../../20_DESIGN/MASTER/testing.md` (goldens)

## Steps

1. **Management summary** `docs/management_summary.md` (DE/FR):
   reflect the source-level capability findings — the per-source
   capability profile summary, the preliminary N2 numerator (a floor,
   official-register subset), and the honest scope (no market total).
   Keep it current whenever the substance changes; translation
   discipline (tranche 1: README, METHODOLOGY, DATA_SOURCE DE/FR).
2. **Register tables:** update the source-register tables in the
   Strategy/Design docs to reflect the expanded AS/CS/ST/PE set and
   the active flags.
3. **Drift markers:** `source_updated` / drift markers where a
   substantive English change lacks a translation; leave visible.
4. **LOG:** add the v0.2.1 unit entry (executed phases, date, the
   capability numbers, any document-blocked sources).
5. **Goldens:** regenerate the report goldens (output changed in
   PHASE05) and review the diff; `db audit` exit 0.
6. **Version/readiness:** confirm `leadhs --version` → 0.2.1; update
   the unit status in the implementation MASTER phase table to `done`.

## Deliverables

Current management summary (DE/FR); register tables; drift markers;
LOG entry; regenerated + reviewed goldens; MASTER phase table marked
done.

## Exit gate

Docs current with the real capability data; translations
drift-marked or updated; goldens regenerated with review; `db audit`
exit 0; MASTER phase table all `done`.

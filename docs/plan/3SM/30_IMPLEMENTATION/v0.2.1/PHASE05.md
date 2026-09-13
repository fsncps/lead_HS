---
unit: v0.2.1
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-14
---

# PHASE05 — Capability report: matrix + N2 numerator

## Objective

Extend the od8 report layer (i12 unchanged — one DB-only assembly,
three renderers) with the capability matrix and the preliminary N2
numerator, then publish and audit.

## Preconditions

- PHASE04 done (capability findings in the DB).
- Clean working tree.

## Governing references

- `../../20_DESIGN/units/v0.2.1.md` (report extension cap3; ENG
  review A1/A2, C2/C3)
- `../../20_DESIGN/MASTER/interfaces.md` (i16 numbers contract, i18
  capability-report contract)
- `../../20_DESIGN/MASTER/data_model.md` (dm12; v_probe_latest)

## Steps

1. **report.py — capability metrics tuple (C2):** a single
   `CAPABILITY_METRICS` tuple of the six capability codes, used for
   both the capability-matrix columns and the predicate derivation.
2. **predicate helper (C3):** `_is_real_product_source(by_metric)` —
   `cap_manufacturer == 1 AND cap_product_ident == 1 AND
   cap_cn8_linkage != 'none' AND cap_depth_tier >= 2`, reading from
   the `by_metric` dict (already populated from v_probe_latest).
3. **capability run fetch (A1):** a separate
   `_fetch_latest_capability_runs(conn)` filtering `mode_code =
   'capability'`, giving the capability matrix its own run_key/status
   per source; leave `_fetch_latest_runs` (census/recon) untouched so
   the existing tiers are unaffected.
4. **od8 assembly:** add a capability-matrix section — per registered
   source, the six capability metrics + the derived
   real-product-source flag (md explains the predicate in prose).
   Add the preliminary N2-numerator line: Σ `products_identifiable`
   over sources passing the predicate — labeled "N2 numerator
   (official registers, floor)" with the certified/declared-subset
   caveat (A2); never feeds `_counted_value`/tiers or the existing
   N2 sum.
5. **Renderers:** md — the capability matrix section + numerator line
   (prose predicate); csv — widen the existing per-source matrix rows
   with the six capability columns + derived predicate flag (one csv
   artifact; numerator stays md+json); json — full structure incl.
   the derived predicate and the N2-numerator components.
6. **Tests (t11, test_report_content.py + goldens):** predicate
   derivation (pass/fail per source); predicate false on each axis
   (manufacturer=0, product_ident=0, linkage='none', depth<2); N2
   numerator sums real-product sources only; inactive rows out of the
   sum; the certified-subset caveat line; csv widening; a capability
   run does NOT surface in the existing matrix's `last_run_key`/tier
   (A1).
7. **Publish:** render md/csv/json to `docs/report/`; `db audit` exit
   0.

## Deliverables

Capability report (md/csv/json) with matrix + predicate + N2-numerator
line; published under `docs/report/`; audit clean.

## Exit gate

Report per i18 on real data; capability matrix + derived predicate +
preliminary N2-numerator line with the certified-subset caveat;
every number provenance-cited; published; `db audit` exit 0.

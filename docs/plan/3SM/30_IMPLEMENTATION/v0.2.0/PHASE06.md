---
unit: v0.2.0
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE06 — Numbers report: render, assembly, publish, audit

## Objective

Build and publish the unit's deliverable: the numbers-first report
(N1 range + method, N2/N3 totals with access tiers, per-source
matrix, trade/priors lines, access-decision bridge) via the od8
content layer.

## Preconditions

- PHASE04–05 done (real data in the DB).

## Governing references

- `../../20_DESIGN/units/v0.2.0.md` (nu4/nu5; acceptance criteria)
- `../../20_DESIGN/MASTER/interfaces.md` (i16, i12, P7)
- `../../20_DESIGN/MASTER/testing.md` (t3 goldens with review, t10)

## Steps

1. **report.py numbers-first layout** (i16): N1 headline (anchor
   values from the DB: trade sums, producers_registered,
   products_registered); N2/N3 headline (totals + tier composition
   (a)–(d); excluded-and-counted line; explicit zero-states — "no
   counted sources yet", never a bare 0); per-source matrix (all
   registered sources; inactive visible, never in sums; new columns
   tier / sitemap_products / sds_library_visible /
   products_registered / producers_registered / trade sums /
   census_status — plain, no walk column (V4 idle; ENG review)); trade-context lines; priors lines;
   access-decision bridge (md, qualitative, evidence-cited);
   execution log + legend. One DB-only assembly, three renderers
   (i12); csv/json carry the full structure incl. tier dicts,
   excluded-source lists, anchor values (json has NO computed N1
   range — nu5).
2. **N1 method sheet content** (hand-maintained md framing block,
   nu5): per anchor — source, coverage, formula, caveats, assumption
   bounds with provenance (URL + access date); labeled as an
   estimate (V2).
3. **Tests** (t10) on fixtures: tier derivation; excluded-and-
   counted; inactive rows out of sums; zero-states; N1 anchor
   block; bridge present/deferred; csv/json column gains; "—" vs 0
   legend; goldens regenerated with review.
4. **Publish:** `make report` → review md/csv/json → `make
   report-publish WHICH=…` → `make db-audit` exit 0.

## Deliverables

Published numbers report (md/csv/json) in `docs/report/`; reviewed
goldens; green suite.

## Exit gate

Report per i16 on real data; every number cites run_key/record;
zero-states explicit; published finals routed per D22; audit
exit 0.

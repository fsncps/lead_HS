# LOG

Major lifecycle events only (format and policy:
`~/.config/opencode/3SM_process.md`). Routine document edits are not logged.

## 2026-08-31 — v0.1 — 3SM initialized; Strategy materialized

3SM structure created under `docs/plan/3SM/` (README, MASTER, LOG,
`10_STRATEGY/{MASTER, methodology, lead_sds}`) from the completed initial
research pass (population triangulation, SDS-based lead identification,
precision-based stratified sampling design). Committed `4216d6f` and pushed
to `origin/main`. Unit v0.1 remains LIVE in STRATEGY — nothing frozen, no
stage advancement.

## 2026-08-31 — v0.1 — Scope correction: document-only, Swiss trade/bilateral lens

Laboratory validation abandoned (no lab available; physical sampling out).
Methods restricted to publicly retrievable documents at minimal cost.
Deliverable reframed as a discussion basis for decision makers on Swiss
external trade in HS 3208/3209 paints and the bilateral EU framework; Swiss
trade statistics (EZV) and an EU-vs-CH legal dossier added as first-class
Phase-0 workstreams; corroboration now cross-document only, blind spots
stated as limitations. README, AGENTS and Strategy docs corrected
(corresponding to commit pending at time of writing).

## 2026-08-31 — v0.1 — Strategy review after SECO input: regulatory frame integrated

Cassis-de-Dijon/VIPaV/ChemRRV legal frame researched and integrated
(neutral framing: study documents the field of application of the VIPaV
Art. 2 Bst. a Ziff. 1 exception; no deletion/exception outcome presumed).
Scope additions: EU-market leg as first-class study object; HS 3213
artists' colours census annex; legal-category dimension in the database.
New hard findings recorded (lead chromates: no lawful EU supply since
17 Mar 2022; red-lead primers: documented EU niche; artists' lead colours:
documented NL/IT; lead driers: unknown). The 100 ppm (CH ban) vs 0.1%
(EU SDS floor) visibility gap promoted to headline limitation. Management
summary (DE/FR), README, AGENTS and Strategy docs updated (commit pending
at time of writing). Unit remains LIVE in STRATEGY.

## 2026-09-10 — v0.1 — Background/purpose correction: autonomous CdD frame, not EU-bilateral

Framing error corrected after reading the SECO Cassis-de-Dijon/THG/MRA
pages and the THG full text (Lexaris, SR 946.51): the study is anchored in
the autonomously adopted Cassis-de-Dijon principle (THG Art. 16a — one of
three THG instruments), not in EU-bilateral compliance; MRA (THG Art. 14)
scoped out. Political protocol recorded in 10_STRATEGY decision 11:
exceptions defined at the principle's 2010 inception, each protecting a
deviating Swiss technical regulation (THG Art. 4 Abs. 3–4) with a
requesting/owning federal office responsible for implementation,
monitoring, revision; lead entry: requester/owner BBL (commissioning
context — verify before naming in deliverables), enforcement BAFU, SECO
conducts the five-yearly review of the entire catalogue (2023: keep; next
~2028); deliverable = outcome-neutral decision basis for the owner within
that cycle. THG Art. 31 Abs. 2 (list-keeping basis) verified via Lexaris.
README, management summary (DE/FR), strategy docs and AGENTS reworded.
Unit remains LIVE in STRATEGY.

## 2026-09-10 — v0.1 — Strategy topics: data source / data model / architecture

Expanded 10_STRATEGY: DATA_SOURCE.md (source register, provenance &
scraping discipline), DATA_MODEL.md (evidence-database schema:
formulation-level products, SDS findings, seeded sampling runs),
ARCHITECTURE.md (no-server CLI pipeline `leadhs`, generated reporting).
methodology.md → METHODOLOGY.md and lead_sds.md → LEAD_SDS.md (CAPS
standardization); DECISIONS/OPEN ITEMS sections added to both. MASTER
gains decisions 16–18 (tooling stack, database principles, reporting).
Unit remains LIVE in STRATEGY.

## 2026-09-10 — v0.1.1 — First unit opened: probe-first rollout (slim CLI)

Unit v0.1.1 (source probing) defined as the first bounded work unit:
slim `leadhs` slice — db init/status, source load/list, probe
run/report — nothing else; full command surface stays design-ahead
(M0–M4 rollout, ARCHITECTURE.md). Probe entities added to the schema
(probe_run, probe_finding; provisional counts, manual anchor
promotion — D20). Strategy readiness split: Design may proceed for
the slim probe CLI; full-pipeline freeze awaits probe results. v0.1
remains the foundational strategy pass. Unit v0.1.1 LIVE in STRATEGY.

## 2026-09-11 — v0.1.1 built; v0.1.2 opened as operator layer + census close-out

Unit v0.1.1 PHASE01–07 built and gate-verified (101 passed offline);
the PHASE08 census feasibility pass was executed the same day and its
recorded gaps (CS-1 fetch, CS-2 query parameters, ST-2 fetch, PE
catalog level, manual sources) move forward. Strategy decisions
D21–D26 added (operator layer, report routing, i18n, distribution,
structured source reports, M0 close-out in v0.1.2); unit v0.1.2
re-scoped accordingly (U1–U10): the census close-out is delivered by
v0.1.2 and executed through the operator layer (`GO=1 make census`),
superseding the census-first sequencing discussion. Design converged
(od1–od9; CEO review 2026-09-11 HOLD SCOPE; OD-A resolved — per-HS
count metrics via migration 0003, not deferred to M1); implementation
phase plans PHASE01–07 written and ENG-reviewed (SMALL CHANGE;
exit-map hardening from empirical click verification; test-net job;
README EN/DE/FR same change set). v0.1.1 PHASE08 marked transferred;
READMEs (EN/DE/FR), management summary, AGENTS and dashboards
updated. Nothing frozen; build and census execution await explicit
instruction (commits pending at time of writing).

## 2026-09-11 — v0.1.2 — Scope correction: product data only (D27)

User direction: no legal referencing at all in the tool, database or
reports — legal texts are framing background only. Strategy decision
D27 added (supersedes D14): the schema drops the legal-category
dimension and the ban-engagement flag from `product`, the
legal-status/Swiss-relevance fields from the compound dictionary, the
legal-coded sds_signal lookup and the legal_text document kind;
origin reworded to plain market provenance. METHODOLOGY (EN/DE/FR)
regulatory-frame section retitled background; the design-consequence
bullet now carries HS/CN + origin only. Design data_model.md aligned
(d27); LG register rows stay inactive and carry no findings (matrix
shows them only as inactive register rows). Public-facing docs
(READMEs, management summary, AGENTS) completed and committed the
same day (aaef1f3).

## 2026-09-11 — v0.1.2 — Rescope to second-pass design; PHASE01–06 built

Implementation trail rescoped to the second-pass design delta
(od8–od10) at activation: PHASE05 rewritten (migration 0003 with
records_hs3208/3209/3213 + census_status, v_anchor_candidates
redefinition, od9 census mechanics, od8 report content layer),
PHASE07 metric names aligned, data_model.md §Migration plan renumbered
0004–0010. Then PHASE01–06 executed: CLI exit-code enforcement in
main() (standalone_mode=False), DB-init preflight on all seven
schema-reading commands, repo Makefile with GO=1 guards and report
routing, operability/preflight/makefile tests plus a net-marked doctor
test, census capability (0003 applied on upgrade with backup; CS-2
parameterized per-HS queries with archived responses; PE category
depth ≤ 3; census_status manual records), od8 report content layer
(md narrative + matrix over all registered sources incl. inactive,
run status incl. blocked/failed, "—" vs 0 legend; csv = matrix only;
json full structure; goldens regenerated with review), README
EN/DE/FR "Using the tool" sections + Status + layout, wheel verified
(0.1.2, uv tool env, --data-dir from foreign CWD). Build seam
recorded: od9 category path moved to finding notes (R4 strict;
interfaces.md row clarified). 155 tests pass offline (up from 101).
PHASE07 (real-network census via GO=1 make census) planned — awaits
explicit go. Commits pending at time of writing.

## 2026-09-11 — v0.1.3 — Strategy unit drafted; D28 strategy deltas applied

Unit v0.1.3 (population sizing & sampling frame, M1 entry) drafted at
strategy DRAFT stage (`10_STRATEGY/v0.1.3.md`): Q1 product-population
estimate + Q2 documentation coverage, trade imports, register priors,
frame + seeded draw, config file. MASTER D28 decision recorded
(product-first census; register product-only); v0.1.2 unit doc
amended (U11–U13, scope items 6–7, resolved open items, rework
note); DATA_SOURCE and METHODOLOGY gained the D28 framing blocks.
DE/FR translations intentionally left with `source_updated` drift
markers (D23). No implementation trail yet — unit converges after
the v0.1.2 census execution.

## 2026-09-12 — v0.1.3 — Refocus: data-landscape map (D29)

User direction: before sizing or sampling, the study needs a general
map of the data landscape — what is available from which source, at
what scale, with what access to specifications; deliberately coarse;
legal content of no concern in this unit. Unit v0.1.3 rewritten as
the data-landscape mapping unit (`10_STRATEGY/v0.1.3.md`): channel
enumeration, census-walk extension (products_listed/doc_links_seen),
coarse SPIN/PCN/PRODCOM priors, latest-year trade context, one
cross-source availability map answering Q1/Q2 as measured floors,
and a frame-decision bridge. The sampling-frame apparatus, the
config-file migration and the full 2019–2025 trade import defer to a
later unit. Related docs aligned: MASTER (D29, ROADMAP, active-unit,
readiness), METHODOLOGY (census-to-landscape handoff; stratification
marked as deferred-unit draft material), ARCHITECTURE (rollout:
v0.1.3 inserted, M1 deferred behind the bridge), DATA_SOURCE
(landscape-map extension note). DATA_MODEL needs no change at
strategy level (frame tables stay milestone-gated at M1). DE/FR
translations intentionally left with `source_updated` drift markers
(D23). Unit stays strategy DRAFT; converges after the v0.1.2 census
execution.

## 2026-09-12 — v0.1.3 — Design converged; implementation plans written (ENG review)

Design for the refocused unit converged
(`20_DESIGN/units/v0.1.3.md`, pe1–pe7; CEO review HOLD SCOPE
2026-09-12): enumeration register model (per-site PE rows PE-10+,
PE-1..4 retired inactive, structured notes convention, `source
load` validation), priors metric `products_registered` (migration
0005), landscape-map report extensions (aggregate floors,
trade/priors lines, frame-decision bridge), budget marker. ENG
review 2026-09-12 (SMALL CHANGE): C1 — aggregate floors sum active
sources only (retired PE-1..4 would double-count; decision 1A);
C2 — budget marker as numeric metric `walk_budget_exhausted` (0004
INSERT), not a note substring (decision 2A); C3 — hostile
double-count test folded into t9. Persistent topics updated
(data_model migration plan 0004/0005 + renumber 0006–0012,
interfaces i13/i14 + vocabulary, architecture a16–a18, testing t9,
Design MASTER d28–d31). Implementation plans written:
`30_IMPLEMENTATION/v0.1.3/PHASE01–07` + unit MASTER; PHASE01–02
absorb the outstanding v0.1.2 D28 rework + PHASE07 census execution
(B8 precedent; v0.1.2 trail marked). Build awaits explicit go;
PHASE02/PHASE06 additionally require the real-network go-ahead. No
code executed; nothing committed.

## 2026-09-12 — v0.1.3 — Implementation-plan completion pass (pending additions)

Review of `30_IMPLEMENTATION/v0.1.3/` against the design contracts
surfaced five gaps, now folded in: (1) PHASE01 gains the **D28
register slim in `sources.csv`** (nine product rows) — the upsert
loader would otherwise resurrect the LG/LI rows migration 0004
prunes, on the very next `make census` (spec: v0.1.2.md step 6,
DATA_SOURCE.md register slim); (2) PHASE03 gains the t9
**test_engine.py** extension (per-site PE runs, `--all` sweep,
second-site fixture) plus the wheel-build check after the version
bump, and the loader-validation tests are pinned to the existing
`test_source.py` module; (3) row-count facts corrected everywhere:
the current register is **14 rows** (not 15), slimming to nine
product rows with **seven active** (PHASE02 census target) —
verified against `sources.csv`; (4) PHASE05 aggregate section
placement pinned (directly after the summary matrix, per pe3);
(5) v0.1.3 MASTER handoff note de-staled (LOG entry for the
planning pass exists; commit/push remain user-gated). Design unit
doc kept consistent (pe5 spec carries the CSV slim; 14-row fixes).
Still: no code executed, nothing committed.

Also 2026-09-12 (user request): **version bumped early to 0.1.3**
(`pyproject.toml`, `__init__.py`, Makefile header, test_cli_*
version assertions) — PHASE03 step 1 becomes verification; and the
run-key date literals in test_engine/test_chaos were de-hardcoded
(they asserted `probe-20260911-*` and broke on any later day);
offline suite re-verified green (155 passed, 2 net deselected).

## 2026-09-12 — v0.1.3 — Strategy converged on D30; unit kept whole (v0.1.4 split declined)

User asked whether the D30 three-number deliverable warrants a new
unit v0.1.4 or an easy fix to v0.1.3; decided: keep v0.1.3 whole —
D30 added no scope (the triad is already phase-mapped: N1 →
PHASE04+06 priors, N2/N3 → PHASE01/03/05/06 walks + aggregates), and
the strategy's own convergence condition (census floors + pinned
caps) is met by the 2026-09-12 baseline census (3 done / 1 blocked /
3 failed; audit clean). Strategy unit doc set FROZEN on D30 (caps
MFR ≤12, CH-DIY ≤4, EU-DIY ≤5, MARINE ≤5, ART ≤6; B2B OPEN);
three-numbers wording aligned across strategy, design (D30 alignment
note), implementation MASTER, PHASE05 (E1 aggregate note), PHASE06
(E2 unit codes), PHASE07, root MASTER. The deferred sampling-frame
unit stays behind the bridge — not planned ahead. Build awaits
explicit go.

## 2026-09-12 — v0.2.0 — Strategy turn: market scale & data availability (D31)

User clarification recorded as MASTER D31 and materialized as new
minor-version unit `v0.2.md` (v0.2.0, STRATEGY DRAFT): numbers-first
— N1 market-size estimate (magnitudes from official statistics) and
N2/N3 data-availability counts; no scraping (reconnaissance only;
walks defer to an explicit go); EU-only register (CS-1, CH-DIY seeds
out); new AS class (CEPE/national associations, national product
registers); 3213 demoted to low-priority annex. v0.1.3 stays FROZEN
with a supersession note (walk machinery idles); METHODOLOGY
(population, handoff, stratification) and DATA_SOURCE (six classes,
register scope, EU-only table rows) updated. DE/FR translations keep
`source_updated` drift markers (D23); management summary updates
when v0.2 numbers land.

## 2026-09-12 — project-wide — Framing and tone correction (user direction)

User review of the public README framing: the study researches the
**EU market** — Switzerland is not a studied market, it enters only as
the regulatory frame (consistent with D31, now applied everywhere); and
the study takes no position on the regulation — "does the exception
still have a factual field of application" phrasing is out of depth and
removed (D11 reworded: documented EU-market numbers within the review
cycle, no position). Study arc as stated by the user: count products,
establish for how many detailed specifications (MSDS) are obtainable,
analyse — currently at the probing stage (data landscape). Applied to:
README trio (rewritten — slimmer, professional tone, detail moved to
the linked docs), management summary (rewritten in both languages,
status brought up to v0.2.0 — superseding the D31 entry's "summary
updates when v0.2 numbers land" deferral), strategy MASTER (abstract,
D1/D3/D10 supersession markers, D11 wording), project MASTER dashboard
(abstract, current stage), AGENTS.md project paragraph.

## 2026-09-12 — v0.2.0 — Design converged; implementation plans drafted (CEO review HOLD SCOPE)

Planning pass over the D31 numbers-first unit: design converged
(`20_DESIGN/units/v0.2.0.md`, nu1–nu8; CEO review HOLD SCOPE; user
decision 1A — bounded sitemap-index expansion ≤ 5 children within
the no-scrape recon bound). Key decisions: recon as new probe_mode
(no new commands, V9); CS-2 full-year import sums as four per-HS
metric codes; AS candidate rows (active=0 manual-web, URL-pinned)
with the producers_registered vs products_registered split;
numbers-first od8 layout with access tiers and a md N1 method sheet
(json anchors only); CS-1 retires inactive (dm12 — differs from the
D27-driven LG/LI prune); migration 0005 absorbed with the corrected
view (promoted-exclusion moves to 0008), the unit delta takes 0006,
design-ahead block renumbered 0007–0013; v0.1.3 pe1/pe2/pe6
groundwork absorbed, walk execution + i14 render superseded/
deferred (machinery idles). Persistent topics updated: interfaces
(i15/i16 + 7 vocabulary rows + recon mode), data_model (migration
plan + corrected 0005 + renumbered headers), architecture (a19–
a21), testing (t10), Design MASTER (d32–d38, state, readiness).
Implementation plans drafted: `30_IMPLEMENTATION/v0.2.0/` MASTER +
PHASE01–07; **ENG review pending** before build. v0.1.3 trail
carries the supersession/transfer note. Strategy `v0.2.md` stays
DRAFT — freeze untouched. No code executed; nothing committed.

## 2026-09-12 — v0.2.0 — ENG review done (BIG CHANGE); findings e1–e8 folded

ENG review of the phase plans (skill plan-eng-review, mode BIG
CHANGE chosen at the scope challenge; Step 0 confirmed the plan
reuses existing machinery, introduces no new classes). Architecture
decisions by the user: **1A** make chains (census/recon) tolerate
exactly the expected sweep exit 2 (`|| test $$? -eq 2` — blocked
sites no longer abort report/audit); **2A** CS-2 JSON-stat responses
decoded by a minimal one-dimension decoder (value object + flat
index → partner via id/size; sums + partner tops from one archived
payload — the old list heuristic would have silently counted 0);
**3A** per-call `max_bytes` streaming cap at the fetch seam (typed
SizeLimit; recon ~25 MB; census/ST uncapped — SPIN .mdb is
legitimately ~100 MB). Stated fixes folded without questions: gzip
magic-byte sniff before sitemap parsing; namespace-local tag
matching (silent-0 trap); `record_manual` mode parameter (CLI
--mode, default census); bounded year step-back (max 3 tries →
document-blocked); CS-2 dry-run plans aggregation URLs; nested-index
children noted, not recursed; robots-unknown proceeds with note;
plain census_status matrix column (no walk column, V4). Tests: new
fixtures added to t10 (gzip, namespaced XML, oversized, robots-
unreachable, nested index, JSON-stat shape, step-back, cap, record
--mode, chain idiom); no test gaps; no critical failure-mode gaps;
test-plan artifact written. TODOS.md created with one item
(generalize the JSON-stat decoder — PRODCOM/SBS future callers);
conditional-GET caching skipped (one-shot sweeps). Docs updated:
design doc ENG review section + nu9, PHASE02/05/06 step texts,
interfaces i15/i16, architecture a19–a22, testing t10, Design
MASTER d39, tracking MASTERs. Still no code executed; nothing
committed; build awaits explicit go.

## 2026-09-12 — v0.3 (goal noted) — Vanilla-Windows install as distribution goal (D32)

User direction: PyPI publication is not needed, but the tool must
become easily installable on vanilla Windows — no make, no preinstalled
Python — via a self-contained artifact. Recorded as strategy decision
**D32** (amends D24: per-OS bundling/PyInstaller promoted from
contingency to planned v0.3 scope; GitHub release assets stay the
channel, bundled Windows artifact alongside the wheel; mechanism choice
deferred to v0.3 design). Strategy MASTER (D24 marker, D32, Active-unit
v0.3 bullet) and ARCHITECTURE.md distribution section updated; READMEs
state the current install truth (repo `make setup`; wheel+uv
build-verified, release assets pending; Windows installer = v0.3 goal)
in EN/DE/FR. No code executed.

## 2026-09-12 — v0.2.0 built (market scale & data availability — the numbers unit)

Explicit user go to implement 0.2.0, upgrade leadhs, run the probe and
report, summarize, update docs, commit and push. All seven phases
executed; offline suite green (205 passed, 2 deselected); leadhs
upgraded to 0.2.0.

- **PHASE01/02 (unit machinery):** migration 0005 (products_registered
  priors metric) and 0006 (recon numbers: AS class, recon mode,
  sitemap_products, CS-2 aggregation + JSON-stat one-dimension decoder,
  CS-1 retirement); fetch SizeLimit streaming cap; PE recon branch
  (declared sitemap discovery, gzip sniff, bounded index, nested-index
  depth, size cap, robots-unknown → proceed); record --mode; make
  probe-recon/recon targets with expected-exit-2 tolerance; version
  0.2.0.
- **PHASE03 (register rework):** sources.csv → per-site rows PE-10..34
  (MFR≤12, EU-DIY≤5, MARINE≤5, ART≤6), PE-1..4 retired, AS-1 (CEPE)
  + ST-3 (Eurostat SBS) added/verified, EU-only slim. 34 rows loaded;
  probe-dry plans every active row; audit clean. PE-22 URL corrected
  (bauhaus.de is the museum; DIY retailer is bauhaus.info).
- **PHASE04 (statistics execution, GO=1):** CS-2 aggregation landed
  real anchors — 2024 EU extra-EU imports: HS 3208 ≈2.47 Mt / ≈€12.21 bn;
  HS 3209 ≈2.10 Mt / ≈€6.22 bn (query pinned to the live DS-045409
  schema: time dimension `time`, import flow `1`, indicators pinned so
  partner is the single free dimension; QUANTITY_IN_100KG ×100 → kg).
  ST-3 producers_registered=3,200 (SBS NACE 20.30, 2020); AS-1
  producers_registered=800 (CEPE member companies). ST-2 (SPIN)
  unreachable (network); ST-1 PCN inactive in register.
- **PHASE05 (recon execution, GO=1):** 25 PE sites swept (22 done,
  PE-31 blocked, PE-24 failed); sds_library_visible assessed and
  recorded for all 25 (9 visible). N2 = 204,693 sitemap-visible URLs
  across 23 counted sources; N3 = 9 sites with a visible SDS library.
- **PHASE06 (report):** numbers-first report rework (tiers a–d, N1
  method sheet + anchors, N2/N3, trade/priors lines, access-decision
  bridge, 26-column matrix, census_status); published
  `docs/report/probe-report.{md,csv,json}`; audit exit 0.
- **PHASE07 (docs & close-out):** management summary DE/FR (results
  filled), READMEs EN/DE/FR current-stage + status updated,
  DATA_SOURCE.md register table (PE-1..4 retired, AS-1/ST-3 verified,
  caps note), unit MASTER phase table → done, root MASTER dashboard,
  this LOG entry. N1 range stays an estimate (method sheet, nu5); the
  report carries anchor values, never a computed range.

Docs and report are committed and pushed with the tool changes; the
strategy `v0.2.md` stays DRAFT (freeze untouched).

## 2026-09-14 — v0.2.1 built (source-level capability sounding-out)

Explicit user go to implement 0.2.1 (the D33 source-level expansion) and
run the live sweep. All six phases executed; offline suite green (231
passed, 2 deselected, up from 205); wheel builds at 0.2.1; leadhs
upgraded to 0.2.1.

- **PHASE01 (migration):** `0007__capability.sql` — probe_mode
  `capability` + six capability probe_metrics
  (products_identifiable, cap_manufacturer, cap_product_ident,
  cap_cn8_linkage, cap_depth_tier, cn8_reachable); metrics.py seeds;
  sync test 0001+0003+0004+0005+0006+0007.
- **PHASE02 (code delta):** `ASAdapter` (matches class_code 'AS',
  no-ops for non-`capability` modes — C1; CSV/JSON shape-inspect via a
  reused `_inspect_register`; HTML landing pages are recorded as a
  format finding, never mis-parsed as an export); capability mode on
  the CLI choice list; `make probe-capability`/`capability` (GO=1
  guards, expected-exit-2 tolerance, MODE pass-through); `run_all`
  sweeps AS sources only in capability mode; version 0.2.1; t11
  adapter/makefile tests.
- **PHASE03 (register expansion):** sources.csv gains AS-2..AS-7
  (EU Ecolabel ECAT on data.europa.eu — the duplicate-active-host
  constraint resolved by the distinct host; Nordic Swan; Blue Angel
  active=0 XLSX; INIES active=0 auth-gated; IBU; environdec). 40
  rows loaded; probe-dry plans every active row; audit clean.
- **PHASE04 (capability execution, GO=1):** automated sweep of the
  four active AS registers — each honestly recorded "HTML landing
  page — not a machine-readable export; export URL to anchor". The
  EU Ecolabel ECAT CSV export (88.920 products, semicolon dialect) is
  a manual case (cap2): a manual capability record documented the
  real profile — manufacturer + GTIN/EAN product-ident, depth tier 2,
  category CN8-linkage, **17.838 paints & varnishes + performance
  coatings** → ECAT is a real-product source. environdec exposes
  manufacturer but no product-ident (not a real-product source).
- **PHASE05 (report):** od8 extension — capability matrix section
  (six metrics + derived real-product-source flag per source), the
  preliminary N2-numerator line ("official registers, floor",
  certified-subset caveat — a separate derived line, never folded
  into the existing N2 tiers, A2); the capability matrix fetches its
  own latest-`capability` run (A1); one `CAPABILITY_METRICS` tuple
  (C2) and one `_is_real_product_source` predicate (C3); csv widens
  the per-source matrix with the six columns + predicate flag; json
  carries the full structure. Published
  `docs/report/probe-report.{md,csv,json}`; audit exit 0. Goldens
  regenerated with review.
- **PHASE06 (docs & close-out):** management summary DE/FR (capability
  findings — ECAT 17.838 real-product source, preliminary N2
  numerator; other registers export-to-anchor), project status
  brought to v0.2.1 (231 tests, five build stages), unit MASTER phase
  table → done, this LOG entry.

Real-data outcome: the preliminary N2 numerator (official registers,
floor) = **17.838** (EU Ecolabel ECAT, certified subset — a floor,
never a market total). The other registers' CSV/API endpoints remain
to be anchored at the next pass (documented, not asserted). Nothing
frozen; the strategy `v0.2.1.md` stays DRAFT. Commits pending at time
of writing.

## 2026-09-14 — v0.2.2 — Strategy drafted; design converged; implementation plans written (CEO HOLD SCOPE, ENG BIG CHANGE)

Planning pass for unit v0.2.2 (D34, the three-question funnel —
product-identity and granularity sounding-out). The v0.2.1 review
(2026-09-14) found the headline number unreproducible from DB state,
6 of ~10 capability sources unmeasured, and the PHASE04 exit gate
marked done unmet; v0.2.2 answers with a design built on two
principles: **completeness is a testable invariant, not operator
discipline** and **every number is a query result, never a typed
literal**.

- **Strategy** (`10_STRATEGY/v0.2.2.md`, DRAFT): funnel Q1 pool per
  CN8 (modeled) / Q2 definitively identifiable (counted floor) / Q3
  SDS reachable (modeled reach) under Product = manufacturer +
  identnr; test-data staging DB allowed (U4); 30–60 min runtime
  budget (U5); CN8 verification a metric, not a gate (U6); source
  expansion to census shape (U8). User decisions on the four design
  forks: export-anchor columns, staging-side CN8 dictionary, ~75-site
  W3 recon, minimal metric extension.
- **Design** (`20_DESIGN/units/v0.2.2.md`, fu1–fu10): three
  measurement layers (evidence facts / staging observations /
  derived analyses) with reconciliation by construction; staging DB
  `data/testdata.sqlite` fed only from archived documents, idempotent
  per (source_id, run_key), rebuildable from the archive; four-wave
  run under a 60-min default budget with a test-backed disposition
  invariant; migration 0008 (source export anchors + `sds_doc_urls`)
  + third design-ahead renumber 0009–0015; jsonstat module lift (the
  TODOS item — retired in build); CEO review HOLD SCOPE (c1–c6) and
  ENG review BIG CHANGE (e1–e8) folded.
- **Implementation plans** (`30_IMPLEMENTATION/v0.2.2/`,
  PHASE01–07): migration+jsonstat → staging/normalize/xlsx + engine
  ingest path → register census shape → wave harness + adapter
  extensions → landscape execution (GO=1) → report extension → docs
  & close-out. New module contracts i19 (staging) / i20
  (wave/landscape); architecture decisions a25–a28; design decision
  d41.

Nothing built, nothing frozen; the strategy stays DRAFT. Commit/push
and any stage advancement await explicit user instruction.

## 2026-09-14 — v0.2.2 built — the three-question funnel (product-identity and granularity sounding-out)

Unit v0.2.2 built and executed end to end (PHASE01–07): staging DB
(`data/testdata.sqlite`), engine ingest path, register at census shape
(101 rows), wave harness, the real-network landscape run (GO=1,
2026-09-14), and the od8 report extension — all numbers now query
results.

- **Real-network landscape run (PHASE05):** 101 register rows
  dispositioned — 36 counted / 48 manual-recorded / 4 blocked / 13
  inactive-by-design; W1 staged **ECAT 17,838 rows** (exact
  reconciliation with the v0.2.1 manual record: 16,001 + 1,817 + 20)
  and **Comext 6,316 trade rows** (all 13 CN8 codes, dictionary
  verified). JS-gated registers (Nordic Swan, IBU, environdec, NF,
  natureplus, EPD Norway) and the preset-gap sources (Destatis,
  Coeweb, Datacomex, SPIN) carry honest documented deferrals.
- **Funnel (PHASE06, report published):** Q1 pool **[85,840–343,360]
  products** (modeled: M 800–3,200 producers × ppp 107.3 × staged CN8
  kg shares) · Q2 floor **17,170** distinct (manufacturer, ident)
  pairs · Q3 SDS reach **3,590** (upper bound, match-rate pending) ·
  v0.5 ratio **0.05–0.2**. Reconciliation flags visible, zero
  mismatches; overlap pilot (ECAT ∩ Nordic Swan) explicitly not
  computable this unit.
- **Defect note (v0.2.1 HTML-as-CSV incident):** during the v0.2.1
  probe round the environdec source (AS-7) returned an HTML page that
  the CSV parser silently accepted, producing **seven bogus
  findings**; the rows were deleted 2026-09-14 (evidence-DB repair in
  the v0.2.2 build) and the `_sniff` gate (content-type + first-bytes
  check before parse) introduced and regression-tested (t12) so the
  class cannot recur silently. The v0.2.1 environdec capability claim
  was softened in the v0.2.2 records ("export not obtained").
- **Engine repairs during execution:** automated failure findings no
  longer labelled method="manual" (reserved for `probe record`
  operator entries; 19 existing findings relabelled);
  staging-aware dispositions; W4 checklist predicate = the real c1
  invariant; disposition order (all-manual is terminal); U6
  dictionary verification wired into the CN8 batch.
- **Tests:** 299 passed, 2 deselected (offline suite); `db audit`
  clean; wheel `leadhs-0.2.2` builds and installs.

Strategy `10_STRATEGY/v0.2.2.md` remains DRAFT (freeze is an explicit
user action); nothing committed, nothing advanced without instruction.

## 2026-09-14 — v0.2.3 built — pool estimate v2 (meta-benchmarking, dual-level magnitude verdict)

Unit v0.2.3 built end to end (PHASE01–05, one session): the
single-model funnel headline (Q1) replaced by a **meta-benchmarking
vote** — seven independent benchmark quantities vote into five
contiguous magnitude classes (a 20k–50k … e >300k); a pinned rule
converts the vote into a **dual-level verdict** with a pinned
confidence rule (≥3 converge, no exclusive non-adjacent conflict ⇒
"reasonable-high"; tie ⇒ span + flip assumptions; <3 ⇒ visible
refusal).

- **Verdict on real data:** SKU level **class e (>300k)**,
  formulation level **class c (100k–200k)** — both confidence-
  withheld, divergences recorded (SKU: B1→b, B4→c, B6→a;
  formulation: B1→<a, B2-SE→e, B6→a). The formulation conversion
  rides a pinned 1–10 shade-collapse band (flagged assumption —
  the measurable ECAT key-tier dedup is small: name ×1.049,
  EAN ×1.266 over 17,838 rows, 199 licences).
- **Code:** `src/leadhs/benchmarks.py` (pure verdict engine —
  taxonomy, result constructors, named DB queries, compute_b1–b6,
  vote table, verdict, md renderers, assemble()); the 1,325-line
  `adapters.py` split into the `probe/adapters/` package (import
  surface unchanged); report content layer extended (pool estimate
  v2 section in md/csv/json, funnel supersession banner); goldens
  regenerated and reviewed.
- **Extractions (all primary-source verified, GO=1-gated):**
  BfR-Akademie SE deck — pc-pnt-* counts are poison-centre
  submissions, not register products (71,231 paints/coatings,
  Echo DB 2022-09-15); SWD(2022) 435 Annex 16 — 1,444,290 PCN
  dossiers 2021, no paint-share/non-hazardous constant; JRC final
  Ecolabel report (DOI 10.2760/4572222, supersedes JRC145238) —
  no market-share data exist (official), 217 licences/36,960
  products 03/2025; DK Produktregistret ≈40,000 hazardous products
  (aggregates-only via Power BI — no adapter, PHASE02 shape gate);
  Eurostat SBS verify — 3,300 enterprises (C2030, 2020).
- **Evidence DB:** four new records (ST-1 1,444,290; ST-3 3,300;
  ST-6 40,000; ST-7 71,231 — ST-6/ST-7 newly registered); no
  metric-vocabulary migration (estimate constants live in the
  module + method sheet); `db audit --unreferenced` clean.
- **Contract fixes caught by the golden/content layer:**
  compute_b5 ignored its base-penetration scenario (span midpoint
  ≠ base scenario — fixed + asserted); the formulation vote was
  initially built from unconverted rows (fixed); B6 band now
  carries landscape-scale anchors only.
- **Tests:** 341 passed, 2 deselected (38 benchmark tests on
  synthetic staging; 4 new report-layer tests); wheel
  `leadhs-0.2.3` builds and installs (0.2.3 imports verified);
  published report re-staged with timestamp-hash snapshots.

Strategy `10_STRATEGY/v0.2.3.md` remains DRAFT (freeze is an
explicit user action); nothing committed, nothing advanced without
instruction.

## 2026-09-14 — render history policy (v0.2.3 addendum, user-reported)

`data/report/` renders were unversioned — every `make report`
overwrote the previous report, hiding the render history (only
`docs/report/` publish snapshots preserved it). User decision:
timestamp all saved report files, folded into v0.2.3 as an addendum,
no new unit.

- Makefile `report` now renders `probe-report.<UTC ts>.{md,csv,json}`
  (one shared ts per run, nothing overwritten) and refreshes the
  unversioned names as "latest" copies; every network chain that
  calls `make report` inherits the policy.
- Makefile `report-publish` normalizes the stem, so publishing a
  timestamped render still stages the stable `probe-report.md` name
  plus its `<pub-ts>.<sha256-8>` snapshot (no double timestamps).
- Dry-run test extended; AGENTS.md conventions bullet and
  ARCHITECTURE.md routing note updated; verified with two
  consecutive renders + a publish dry-check.

## 2026-09-14 — full probe re-run; trade double-count defect fixed (v0.2.3 PHASE05 addendum 2)

User-requested full probe run with the timestamped report
(`probe-report.20260914-083931`, published snapshots
`probe-report.20260914-084007.*`). Waves 1–3 reproduced every
headline (ECAT 17,838 exact; Comext 6,316; verdicts e/c unchanged);
W3's blocked/failed sets identical to the morning run; only live
drift: PE-20 SDS links 659→652.

The re-run caught a report-layer defect: staging history is
append-per-run_key by design, but the report's trade/register-helper
queries read across runs — CN8 trade values doubled. Fixed with a
uniform latest-run-per-source scope (`_latest()` JOIN) + regression
test; 342 tests. W2's generic format-findings were re-recorded over
via the manual fallback (curated IBU/environdec/NF/natureplus/
EPD-Norway/PRODCOM notes restored).

New companion document
`docs/report/benchmarking-0.2.3.md`: run record, per-benchmark
comparison considerations, cross-benchmark/method considerations,
gaps, paths — linked from the unit report and all three READMEs.

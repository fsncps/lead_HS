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

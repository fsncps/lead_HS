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

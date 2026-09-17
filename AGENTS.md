# AGENTS.md — lead_HS (robin_HS)

Project-specific instructions for all agents in this repository.

## Project

Documentation-only study of the **EU market** for lead in paints under
HS/CN 3208 + 3209 (artists' colours under 3213 as a low-priority
annex): how many products the market holds, for how many of them
detailed documentation (SDS) is obtainable, and what that documentation
shows about lead — situated in the context of the autonomous Swiss
Cassis-de-Dijon regulatory frame (THG Art. 16a, VIPaV exceptions
catalogue, ChemRRV lead ban — not an EU-bilateral matter; MRA out of
scope). Switzerland is the regulatory frame only, never a studied
market (D31); the study documents market facts and takes no position
on the regulation itself. Deliverable: documented market numbers for
the actors around the lead-paint exception (regulation owner, review
lead; commissioning context stays implicit in public documents) plus a
reusable product/SDS evidence database. Research study + light
data-engineering hybrid (document scraping, database). Currently in
3SM stage IMPLEMENTATION: unit v0.1.1 (source probing — slim CLI) is
built and gate-verified (PHASE01–07; the PHASE08 census feasibility
pass ran 2026-09-11, its close-out transferred to v0.1.2 per D26);
unit v0.1.2 (operator layer + census close-out) is built (PHASE01–06
done 2026-09-11, 155 offline tests; migration 0003 per-HS metrics +
census_status, od8 report content layer, repo Makefile with GO=1
guards); unit v0.1.3 (data-landscape map) is built (walk counters,
migration 0004, 165 offline tests; baseline probe round 2026-09-12) —
its walk-based execution superseded by the v0.2.0 strategy turn (D31,
`v0.2.md`: numbers-first N1/N2/N3, reconnaissance-only, EU-only) —
on top of the v0.1 foundational strategy pass. The v0.2.4 addendum
D40 (BASTA special probe) is built and executed 2026-09-17: the
register's exact public counts are pinned (195,391 articles /
1,925 companies), the anonymous same-origin `/apiproxy/v3` search
route is pinned (the "auth-gated API" answer reversed), and a seeded
100-article sample CSV with the identity tuple (100% complete) and
the BK04/BSAB category proxy is delivered — the paint-subset filter
stays open (de5 not met, no data_sources.csv row).

**Hard constraints:** no laboratory work, no physical samples, no paid data
sources — publicly retrievable documents only, minimal cost.

The directory has appeared as `robin_HS` and `lead_HS`; the GitHub remote is
`lead_HS`. Treat them as the same project.

## Session startup

In planning work, read first:

    docs/plan/3SM/MASTER.md
    docs/plan/3SM/10_STRATEGY/MASTER.md

then the relevant topic files (`10_STRATEGY/METHODOLOGY.md`,
`10_STRATEGY/LEAD_SDS.md`, `10_STRATEGY/DATA_SOURCE.md`,
`10_STRATEGY/DATA_MODEL.md`, `10_STRATEGY/ARCHITECTURE.md`). Treat existing
Strategy as accumulated knowledge;
do not re-research settled questions.

## 3SM

Canonical structure and lifecycle rules live in
`~/.config/opencode/3SM_structure.md` and `~/.config/opencode/3SM_process.md`.
Do not duplicate them here; follow them, including: writing planning files
never implies freeze/stage advancement/archival; commit and push only on
explicit user instruction.

## Documentation conventions

- README and document abstracts: plain or semi-technical language; define
  specialist terms at first use. Deep-dive documents may be fully technical.
- Every load-bearing number carries provenance: source name, year, URL
  (access date for web sources). Keep REFERENCES sections current.
- Distinguish sourced facts from inference; mark unverified items explicitly
  (the Strategy docs already do — keep it that way).
- Frontmatter metadata (`unit`, `stage`, `lifecycle`, `updated`) on all 3SM
  documents; bump `updated` when editing.
- Per-unit public summaries: every built unit gets a summary section in
  the READMEs — the current/recent unit in some detail, older units as
  short summaries — each linking a detailed unit report
  `docs/report/report-<unit>.md` (e.g. `report-0.2.2.md`, EN-only).
  The machine-readable probe report (`probe-report.*`) lives alongside;
  republishes append timestamp-hash snapshots (publish history policy,
  v0.2.2 PHASE07 addendum). Working renders in `data/report/` are
  timestamped per run (`probe-report.<UTC ts>.{md,csv,json}`, nothing
  overwritten) with unversioned "latest" copies kept for stable
  references (render history policy, v0.2.3 addendum).
- `docs/management_summary.md` — bilingual (DE/FR) management summary for
  decision makers: always keep it current whenever the project's substance
  changes; it is linked early in the README.
- Multilingual documentation: English is canonical. Translations live in
  sibling files with a language suffix (`README.de.md`, `README.fr.md`,
  `METHODOLOGY.de.md`, …) next to the English original. Each translation
  carries frontmatter `language`, `translation_of`, `source_updated` plus
  a language-switcher line at the top. The binding term map is
  `docs/terminology.md`; official act/institution names are never
  re-translated. Tranche 1 covers README, METHODOLOGY, DATA_SOURCE (DE/FR);
  planning, design and implementation documents remain EN-only. When the
  English original changes substantively, update translations in the same
  change set or leave `source_updated` behind as a visible drift marker.

## Research/data discipline

- Lead-compound identifiers (CAS/EC) that are still unverified must stay
  flagged until checked against the ECHA EC inventory.
- Swiss regulatory specifics (ChemO/REACH alignment, current ChemRRV
  Anhang 2.8 wording, consolidated VIPaV text, BBL
  requester/owner role for the lead exception) remain OPEN until verified
  against primary sources — see 10_STRATEGY open items; do not assert them
  as fact.
- Web-scraped SDS/product data: record source URL and retrieval date per
  record; respect site terms; no bulk hammering.
- No legal referencing in the tool, database or reports — product data
  only (Strategy MASTER D27, supersedes D14). Legal context lives in the
  10_STRATEGY documentation (LEAD_SDS.md, METHODOLOGY regulatory frame)
  as framing background, never as DB fields or report sections.

## Git

- Subject line: short, imperative, present tense; body for anything
  non-trivial (match existing history style).
- Never commit secrets or credentials; `.env` and common junk are gitignored.

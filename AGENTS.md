# AGENTS.md — lead_HS (robin_HS)

Project-specific instructions for all agents in this repository.

## Project

Documentation-only study of lead in paints under HS/CN 3208 + 3209 (plus a
census annex for artists' colours under 3213) on the **Swiss and EU
markets**, framed by Swiss external trade and the bilateral/regulatory
frame (Cassis-de-Dijon principle, VIPaV exceptions catalogue, ChemRRV lead
ban). Deliverable: a discussion basis for decision makers plus a reusable
product/SDS evidence database. Research study + light data-engineering
hybrid (document scraping, database). Currently in 3SM stage STRATEGY,
unit v0.1.

**Hard constraints:** no laboratory work, no physical samples, no paid data
sources — publicly retrievable documents only, minimal cost.

The directory has appeared as `robin_HS` and `lead_HS`; the GitHub remote is
`lead_HS`. Treat them as the same project.

## Session startup

In planning work, read first:

    docs/plan/3SM/MASTER.md
    docs/plan/3SM/10_STRATEGY/MASTER.md

then the relevant topic files (`10_STRATEGY/methodology.md`,
`10_STRATEGY/lead_sds.md`). Treat existing Strategy as accumulated knowledge;
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
- `docs/management_summary.md` — bilingual (DE/FR) management summary for
  decision makers: always keep it current whenever the project's substance
  changes; it is linked early in the README.

## Research/data discipline

- Lead-compound identifiers (CAS/EC) that are still unverified must stay
  flagged until checked against the ECHA EC inventory.
- Swiss regulatory specifics (ChemO/REACH alignment, MRA coverage, EZV data
  granularity, current ChemRRV Anhang 2.8 wording, consolidated VIPaV text)
  remain OPEN until verified against primary sources — see 10_STRATEGY open
  items; do not assert them as fact.
- Web-scraped SDS/product data: record source URL and retrieval date per
  record; respect site terms; no bulk hammering.

## Git

- Subject line: short, imperative, present tense; body for anything
  non-trivial (match existing history style).
- Never commit secrets or credentials; `.env` and common junk are gitignored.

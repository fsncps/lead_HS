# AGENTS.md — lead_HS (robin_HS)

Project-specific instructions for all agents in this repository.

## Project

Lead-in-paint prevalence study for the EEA market under HS/CN 3208 + 3209,
built on a reusable product/SDS evidence database. Research study +
data-engineering hybrid. Currently in 3SM stage STRATEGY, unit v0.1.

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

## Research/data discipline

- Lead-compound identifiers (CAS/EC) that are still unverified must stay
  flagged until checked against the ECHA EC inventory.
- Web-scraped SDS/product data: record source URL and retrieval date per
  record; respect site terms; no bulk hammering.

## Git

- Subject line: short, imperative, present tense; body for anything
  non-trivial (match existing history style).
- Never commit secrets or credentials; `.env` and common junk are gitignored.

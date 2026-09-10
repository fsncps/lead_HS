# lead_HS — Project Planning (3SM)

This folder holds the planning notes for the lead-in-paint study described in
the [project README](../../../README.md). It uses a simple three-stage
notebook system called **3SM**:

    STRATEGY → DESIGN → IMPLEMENTATION

- **Strategy** answers *what* and *why*: research findings and decisions.
- **Design** answers *how exactly*: the technical shape of the database and
  the data collection.
- **Implementation** (later) contains the finished step-by-step work plans.

These are working documents: they are meant to be corrected and refined, and
ordinary edits never silently advance the project to the next stage. The
strategy stage is filled; the design stage holds the technical design for
the first build unit (v0.1.1 — source probing). Implementation plans will
be written when the project is ready to build.

## What is where

| File | What it contains |
|---|---|
| [`MASTER.md`](MASTER.md) | Project dashboard: current stage, key numbers, document index |
| [`LOG.md`](LOG.md) | Lifecycle log (major events only) |
| [`10_STRATEGY/MASTER.md`](10_STRATEGY/MASTER.md) | The decisions taken so far, open questions, and the roadmap |
| [`10_STRATEGY/METHODOLOGY.md`](10_STRATEGY/METHODOLOGY.md) | How the market is measured — written for non-technical readers, with a glossary |
| [`10_STRATEGY/LEAD_SDS.md`](10_STRATEGY/LEAD_SDS.md) | Background: which lead compounds occur in paints, what EU law allows, and what safety data sheets can and cannot reveal |
| [`10_STRATEGY/DATA_SOURCE.md`](10_STRATEGY/DATA_SOURCE.md) | The register of every data source and the access rules — written for non-technical readers, with a glossary |
| [`10_STRATEGY/DATA_MODEL.md`](10_STRATEGY/DATA_MODEL.md) | The planned shape of the evidence database (technical) |
| [`10_STRATEGY/ARCHITECTURE.md`](10_STRATEGY/ARCHITECTURE.md) | How collection and analysis work as a small command-line tool (semi-technical) |
| [`10_STRATEGY/charts/`](10_STRATEGY/charts/) | Rendered diagrams (three in active use), with their markdown sources |
| [`20_DESIGN/MASTER.md`](20_DESIGN/MASTER.md) | Consolidated design decisions for the collection tool and the evidence database |
| [`20_DESIGN/MASTER/`](20_DESIGN/MASTER/) | The four design documents: data model, architecture, interfaces, testing (technical) |
| [`20_DESIGN/units/v0.1.1.md`](20_DESIGN/units/v0.1.1.md) | The design delta for the first build unit (source probing) |
| [`20_DESIGN/FIXPLAN_2026-09-11.md`](20_DESIGN/FIXPLAN_2026-09-11.md) | Pending work order from the design reviews (critical + engineering, 2026-09-11) |
| [`_archive/`](_archive/) | Superseded material (kept for the record) |

A `30_IMPLEMENTATION/` folder will be created when the project moves to
building.

Structure and process conventions live in the global configuration
(`~/.config/opencode/3SM_structure.md`, `~/.config/opencode/3SM_process.md`);
they are deliberately not duplicated here.

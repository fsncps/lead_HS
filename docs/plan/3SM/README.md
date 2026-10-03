# lead_HS — Project Planning (3SM)

> **Read-only since 2026-09-18.** This v1 planning tree is kept as a
> historical reference and is no longer edited. The live planning tree
> is [`.3SM/`](../../../.3SM/) (3SM v2: CONCEPT → DESIGN →
> ENGINEERING); the distilled unit history (v0.1 … v0.2.4) is
> [`../CONCEPT/DEV_HISTORY.md` in the live tree](../../../.3SM/plan/CONCEPT/DEV_HISTORY.md).

This folder holds the planning notes for the lead-in-paint study described in
the [project README](../../../README.md). It uses a simple three-stage
notebook system called **3SM**:

    STRATEGY → DESIGN → IMPLEMENTATION

- **Strategy** answers *what* and *why*: research findings and decisions.
- **Design** answers *how exactly*: the technical shape of the database and
  the data collection.
- **Implementation** (later) contains the finished step-by-step work plans.

During the v1 era (2026-08-31 → 2026-09-18) these were working
documents: they were corrected and refined, and ordinary edits never
silently advanced the project to the next stage. The strategy stage
was filled; the design stage held the technical design for the build
units (v0.1.1 through v0.2.4 — all built and merged; see the
DEV_HISTORY link above).

## What is where

| File | What it contains |
|---|---|
| [`MASTER.md`](MASTER.md) | Project dashboard: current stage, key numbers, document index |
| [`LOG.md`](LOG.md) | Lifecycle log (major events only) |
| [`10_STRATEGY/MASTER.md`](10_STRATEGY/MASTER.md) | The decisions taken so far, open questions, and the roadmap |
| [`10_STRATEGY/` topic files](10_STRATEGY/MASTER.md) | Slim strategy summaries per topic (methodology, lead in-paints background, data sources, data model, architecture) |
| [`docs/study/METHODOLOGY.md`](../../study/METHODOLOGY.md) | How the market is measured — written for non-technical readers, with a glossary |
| [`docs/study/LEAD_SDS.md`](../../study/LEAD_SDS.md) | Background: which lead compounds occur in paints, what EU law allows, and what safety data sheets can and cannot reveal |
| [`docs/study/DATA_SOURCE.md`](../../study/DATA_SOURCE.md) | The register of every data source and the access rules — written for non-technical readers, with a glossary |
| [`docs/study/DATA_MODEL.md`](../../study/DATA_MODEL.md) | The planned shape of the evidence database (technical) |
| [`docs/study/ARCHITECTURE.md`](../../study/ARCHITECTURE.md) | How collection and analysis work as a small command-line tool (semi-technical) |
| [`docs/study/charts/`](../../study/charts/) | Rendered diagrams (three in active use), with their markdown sources |
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

---
updated: 2026-09-18
---

# Strategy charts — rendered diagrams

## Abstract

Rendered diagrams in active use, generated with the canonical
`flowchart` skill from the written Strategy and Design documents.
Per the 3SM canon these are **Strategy proposals**: a diagram is
engineering-authoritative only when adopted into current Design, and
where a rendering disagrees with the written documents, the written
documents win. Each chart keeps its source markdown (the semantic
record) beside the PNG/SVG/DOT renders in this folder. Three further
charts were rendered on 2026-09-11 and archived the same day (user
decision — superseded); see the archive note below.

## Chart index (active)

| Chart | Type | Shows | Source of truth | Used in |
|---|---|---|---|---|
| architecture-components | component | `leadhs` system: CLI, modules, raw store, SQLite | [20_DESIGN/MASTER/architecture.md](../../plan/3SM/20_DESIGN/MASTER/architecture.md) | project README, docs/study/ARCHITECTURE.md |
| lead-decision-tree | decision_tree | lead determination & blind-spot logic: SDS Sec. 3 → declared ≥0.1% → Swiss ban → corroboration | docs/study/METHODOLOGY.md + LEAD_SDS.md | project README, docs/study/METHODOLOGY.md |
| probe-process | flowchart | probe workflow per source class: robots/terms check → polite fetch → blocked/format decisions → sampling → raw archive | [20_DESIGN/MASTER/interfaces.md](../../plan/3SM/20_DESIGN/MASTER/interfaces.md) + [docs/study/DATA_SOURCE.md](../DATA_SOURCE.md) | project README, docs/study/ARCHITECTURE.md |

`probe-process` was re-rendered 2026-09-11 to match the reviewed
design semantics (blocked runs end `run blocked, exit 2`; 429 gets
one capped backoff) — see [20_DESIGN/FIXPLAN_2026-09-11.md](../../plan/3SM/20_DESIGN/FIXPLAN_2026-09-11.md) (C-1).

## Archive note

Three further charts (pipeline-data-flow, run-state-machine,
data-model-er) were superseded on 2026-09-11 and moved — with their
sources and renders — to:

    ../../plan/3SM/_archive/10_STRATEGY/charts/

The written Strategy/Design documents remain authoritative for those
subjects (pipeline stages and run states: docs/study/ARCHITECTURE.md
and 20_DESIGN/MASTER/architecture.md; data model:
docs/study/DATA_MODEL.md and 20_DESIGN/MASTER/data_model.md).

## Regeneration

From the skill directory, per chart:

    python -m flowchart <chart>.md --type <type>

(Z.ai provider; with a coding-plan key the provider's default
endpoint 404s — patch `API_BASE` to `https://api.z.ai/api/coding/paas/v4`
at runtime, as done 2026-09-11; the wrapper source is embedded in
[20_DESIGN/FIXPLAN_2026-09-11.md](../../plan/3SM/20_DESIGN/FIXPLAN_2026-09-11.md).)

## DECISIONS

- c1 (amended 2026-09-18, documentation-tree split): active charts live in
  `docs/study/charts/` beside the public detail documents as Strategy
  proposals;
  written Strategy/Design documents win on any ambiguity.
- c2: one chart type per subject; the source markdown files are the
  semantic record and stay beside the renders.
- c3 (2026-09-11): active set reduced to the three charts in active
  use (user decision); the rest archived under `_archive/`.

## OPEN ITEMS

- Adopting selected diagrams into 20_DESIGN (engineering authority)
  awaits explicit instruction.

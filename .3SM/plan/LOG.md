---
unit: global
stage: GLOBAL
lifecycle: LIVE
updated: 2026-09-19
---

# LOG

Major lifecycle events only (format and policy: `PROCESS.md`; canonical:
`~/.config/opencode/3SM_process.md`). Routine document edits are not
logged. Pre-migration history (2026-08-31 → 2026-09-17): legacy
`docs/plan/3SM/LOG.md` and git.

## 2026-09-18 — project — MIGRATION: v1 planning tree → v2 .3SM/ structure

User-ordered migration from the v1 layout (`docs/plan/3SM/`) to the
canonical v2 `.3SM/` tree. Law and facts scaffolded from the canonical
templates (PROCESS.md + three stage PROCESS files + PROJECT.md);
M-docs and T-docs migrated from `10_STRATEGY/` and `20_DESIGN/`
(adapted, frontmatter normalized); unit records distilled into
`plan/CONCEPT/DEV_HISTORY.md` instead of being copied; the legacy tree
stays as a read-only historical reference. All pre-migration units
recorded COMPLETE (v0.1.1 … v0.2.4). No lifecycle transition of any
live document is implied by the migration itself.


## 2026-09-19 — project — MIGRATION: v2-legacy stage names → v2.1 canonical (STRATEGY→CONCEPT, IMPLEMENTATION→ENGINEERING)

User-ordered housekeeping rename (3sm-housekeeping REPAIR pass) to the
canonical v2.1 vocabulary: `plan/STRATEGY/` → `plan/CONCEPT/` (11
files), `PROCESS_STRATEGY.md` → `PROCESS_CONCEPT.md`,
`PROCESS_IMPLEMENTATION.md` → `PROCESS_ENGINEERING.md`, empty
`plan/IMPLEMENTATION/` removed; stage tokens in frontmatter, skill
names (`3sm-strategy-unit` → `3sm-concept-unit`, `3sm-plan-run` →
`3sm-eng-run`, `3sm-plan-final` → `3sm-eng-final`) and live-path
references updated across law, facts, plan and pointer docs.
Legacy-tree paths (`docs/plan/3SM/10_STRATEGY/`, `30_IMPLEMENTATION/`)
and skill records stay untouched (historical record, append-only). No
lifecycle transition of any live document is implied.

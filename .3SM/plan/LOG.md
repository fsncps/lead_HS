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


## 2026-10-09 — v0.3.0 — SHIP: unit completed and archived

`/finalize-and-merge v0.3.0` executed (branch waiver held: unit ran on
main, so ship = verification + sync + archive + pipeline flip + local
tag; no merge, no branch delete). Gate evidence fresh at ship: 461
passed / smoke 6 passed / db-audit clean incl. --unreferenced / doctor
ok (informational warns: pandoc M3/M4-deferred, contact is per-session
env, network skipped offline). Pass 1 booked the post-FINAL r04
(dot-path `3c1c7c5` + AS-33 budget `50f833c`) and backfilled
`r03/PHASE_FINAL.md`; whole-unit diff reviewed (18 non-planning files,
none unplanned). Pass 2 synced interfaces.md § Build record (+r04),
PROJECT facts (461, raw-load state, AS-3 route death), pyproject
0.2.3 → 0.3.0, report-0.3.0.md addendum, management summary (DE/FR)
Stand + addenda. Unit dirs archived, PIPELINE entry → SHIPPED. Tag
`v0.3.0` (local, annotated) at the archive commit. **Push + GitHub
release deferred — explicit user instruction pending.**

## 2026-10-10 — v0.3.4 — UNIT REGISTERED (/init-unit)

Gates: clean tree (after the AGENTS.md permission-header housekeeping
commit 6e17158 the user ordered first), id free (branch + archives),
unregistered. Branch `v0.3.4` created off `main` (f039b26). Scaffolded:
`DESIGN/v0.3.4/{MASTER,RUNS}.md`, `ENGINEERING/v0.3.4/MASTER.md`;
pipeline intent carried verbatim into the design MASTER as starting
context. Registries: plan/MASTER UNITS row (DSG/LIVE) + State flip;
PIPELINE entry ACTIVE. Next: the user's move — design discussions /
3sm-design-unit.

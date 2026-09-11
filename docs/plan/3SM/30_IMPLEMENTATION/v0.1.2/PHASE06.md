---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE06 — Docs & distribution readiness

Status: done (2026-09-11) · Depends on: PHASE01–05 · Governs: the
user-facing surface and the portability check.

## Objective

The tool is discoverable and installable outside the repo: README
gains the plain-language "Using the tool" section (both install
paths), current Status, and the updated repo layout — with the DE/FR
translations updated in the same change set (B6). The wheel builds
and installs into a throwaway managed environment (D24 verification
only — no release mechanics).

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §README "Using the tool",
  §Distribution readiness (D24).
- `../../10_STRATEGY/v0.1.2.md` — §Operator workflow (target),
  U7 (install paths).
- AGENTS.md — documentation conventions (plain language for README;
  translations in the same change set; specialist terms defined at
  first use).

## Steps

1. **README.md**:
   - **"Using the tool"** section (plain language, after "The
     evidence engine"): repo developers — `make install` /
     `make setup` (idempotent first run); peers — `uv tool install`
     from the release wheel + `leadhs --data-dir DIR` (never
     CWD-implicit writes). Day-to-day: `make probe-dry` (plan),
     `GO=1 make probe` (real census — the go-ahead discipline),
     `make record SOURCE=… METRIC=…`, `make report`,
     `make report-publish WHICH=…`, `make db-audit`,
     `make clobber` (guarded wipe). `LEADHS_CONTACT` via environment
     (`.envrc` works); doctor warns when unset. Exit codes in one
     sentence (0 ok · 1 usage/data · 2 blocked · 3 audit · 130
     interrupt).
   - **Status** section: reflect the built state — probe tool +
     operator layer built and reviewed; census run (roadmap Phase 0)
     next via `GO=1 make probe`.
   - **Repository layout**: add `Makefile`, `data/report/`
     (gitignored intermediates), `docs/report/` (committed finals).
2. **README.de.md / README.fr.md** (B6): translate the same three
   changes in the same change set; frontmatter `source_updated`
   current; language-switcher lines untouched; official act/
   institution names never re-translated (terminology map binding).
3. **Wheel verification** (in-unit only):
   - `python -m build` (or `uv build`) → wheel in `dist/`
     (gitignored); version `0.1.2`;
   - install into a throwaway managed env (`uv tool install
     dist/leadhs-0.1.2-py3-none-any.whl --force` or an equivalent
     venv);
   - `leadhs --version` → `0.1.2`; `leadhs doctor` runs;
   - `cd /tmp && leadhs --data-dir <tmpdir> db init` initializes
     there (no CWD-implicit writes; raw store at `<tmpdir>/raw`);
   - clean the throwaway env afterwards.
4. **Not built** (recorded, not executed): tag → GitHub release
   asset → per-OS smoke — first external use (strategy
   ARCHITECTURE open item).

## Deliverables

README.md + README.de.md + README.fr.md; wheel-build verification
(no release artifacts committed; `dist/` stays gitignored).

## Exit gate

- README "Using the tool" present, plain language, both install
  paths, real command examples that match the Makefile targets.
- DE/FR translations current (same change set; `source_updated`
  current; no drift marker).
- Wheel builds at version 0.1.2 and installs into a throwaway env;
  `leadhs --data-dir <tmp> db init` works from a foreign CWD.
- Full offline suite still green; no committed build artifacts.

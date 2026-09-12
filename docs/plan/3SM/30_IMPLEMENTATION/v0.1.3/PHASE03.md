---
unit: v0.1.3
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-12
---

# PHASE03 — Enumeration register (load validation, per-site rows)

Status: planned · Depends on: PHASE02 (baseline census done — the
batch sizes are pinned against real floors) · Governs: pe1/pe6,
d28, i13.

## Objective

Grow the register the only sanctioned way (W6): one reviewed CSV
batch of per-site PE rows with full enumeration provenance, guarded
by new `source load` validation. Version bumps to 0.1.3.

## Steps

1. **Version bump** — **already applied 2026-09-12 at user request,
   ahead of PHASE01** (`pyproject.toml` + `src/leadhs/__init__.py`
   → 0.1.3, Makefile header, version assertions in test_cli_*;
   run-key date literals in test_engine/test_chaos de-hardcoded
   same pass). This step verifies: `leadhs --version` reports
   0.1.3, wheel still builds (design acceptance criterion).
2. **`source load` validation (pe6):** per row — id matches
   `^[A-Z]{2}-[0-9]+$`; url non-empty and http(s); no duplicate host
   among **active** rows (netloc lowercased, `www.` stripped);
   failing rows named in the error, exit 1; inactive rows exempt
   (the retired echa.europa.eu pair must keep loading).
3. **Enumeration CSV batch (the research step):** per channel
   family — MFR (tier A/B manufacturers), CH-DIY, EU-DIY, MARINE,
   ART (3213 annex), B2B portals (resolves the PE-3 placeholder) —
   add rows `PE-10`… with real URL, class PE, scrape, and the
   structured notes convention (`channel=…; listed_by=…;
   listed_url=…; listed_date=…; inclusion=…`). Cap per channel
   recorded in the batch note (design OPEN item — pin here).
   Every site: robots/terms spot-check before inclusion (discipline
   D4 — no login-walled sites).
4. **PE-1..4 retirement:** flip `active=0` in the CSV; after
   reload, record `census_status` notes "superseded by per-site
   enumeration (see PE-10..)" via `make record` (reference rows
   updatable, never deleted — P6).
5. **Reload + check:** `make sources-load`; `make sources-list`
   shows the grown register; `make probe-dry` plans every active
   per-site row, zero network.
6. **Tests** — test_source.py extends (the design's
   `test_source_load.py` folds into the existing loader module):
   bad id / empty url / non-http scheme / duplicate active host
   (both ids named) → exit 1; dup host with one row inactive →
   loads; the pre-slim 14-row register still loads via `--file`
   (inactive LG/LI exemption case). test_engine.py extends (t9):
   per-site PE rows run individually (`--source PE-10`); `--all`
   sweeps the enumerated register; the PE fixture gains a second
   site so the sweep covers more than one walk.

## Deliverables

- Validated loader; enumerated sources.csv (per-site rows,
  PE-1..4 retired); probe-dry plan covering every active row;
  validation + engine tests; version 0.1.3 wheel.

## Exit gate

- Validation exits 1 with the row named for each malformed case;
  enumerated register loads; PE-1..4 inactive with supersession
  notes; probe-dry lists every active per-site row; per-site runs
  and the `--all` sweep behave in test_engine; suite green; wheel
  builds at 0.1.3.

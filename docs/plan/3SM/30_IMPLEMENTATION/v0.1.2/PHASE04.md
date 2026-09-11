---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE04 — Tests (operability, preflight, make wiring)

Status: done (2026-09-11) · Depends on: PHASE01–03 · Governs: the confidence
layer for the operator layer.

## Objective

Every new codepath of PHASE01–03 pinned by a test: the exit-code
mapping (including the click-behavior subtleties), the preflight
contract on all seven commands, and the Makefile wiring — run only
in ways that cannot cause side effects.

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §Testing additions (od7).
- `../../20_DESIGN/MASTER/testing.md` — key test files
  (test_cli_operability / test_preflight / test_makefile), t7,
  flakiness rules (make tests `-n`/guarded only; skipped when make
  absent).
- `../v0.1.2/MASTER.md` — B1/B5 (mapping subtleties; the net-marked
  doctor test).

## Steps

1. **`tests/test_cli_operability.py`** — subprocess pattern from
   `test_cli_smoke.py` (`python -m leadhs.cli`):
   - unknown command → 1; missing required option → 1; bad
     `--format` choice → 1;
   - `--help` and `--version` → 0, output on stdout (`--version`
     prints `0.1.2`);
   - bare `leadhs` / `db` / `source` / `probe` → 0, help on
     **stdout**;
   - `source list` works; `source list-` → usage error (registered
     once);
   - `--db X --data-dir Y` → 1;
   - `leadhs doctor --help` contains `--net`, not `--no-net`;
   - `Abort` → 130 and generic `Exception` → 1 via **monkeypatched
     `main()`** (deterministic — no real signals, no debuggers):
     monkeypatch `leadhs.cli.cli` to raise, assert `main()` return;
   - `ctx.exit(2)` path preserved (`probe run` blocked still exits 2
     — existing smoke already covers; keep).
2. **`tests/test_preflight.py`** — for each of the seven commands
   (`db status`, `db audit`, `source load`, `source list`,
   `probe run --all`, `probe record …`, `probe report`):
   - DB file **missing** → guided error, exit 1;
   - DB file **empty** (created with `touch`) → same;
   - DB **without `schema_version`** (a plain table created via
     sqlite3) → same;
   - stderr contains the guided message; never `bug:`;
   - after `leadhs db init`, the same commands proceed (exit 0 or
     their normal codes);
   - `db init` itself on all three states → initializes fine;
   - a **directory** at the DB path → guided error, no traceback.
3. **`tests/test_makefile.py`** — `skipif` when `make` is absent;
   repo root = `Path(__file__).resolve().parents[1]`; `-n` and
   guarded targets only (flakiness rule):
   - `make help` → exit 0, output contains e.g. `probe-dry`;
   - `make probe` / `make census` (no `GO`) → nonzero exit, stderr
     contains "set GO=1", **no side effects** (guard is a
     prerequisite; assert no `data/leadhs.sqlite` created);
   - `make sample` → exit 1 with the milestone pointer;
   - `GO=1 make -n probe` → stdout contains
     `probe run --all --mode`;
   - `make -n report` → stdout contains the three `--out`
     `$(REPORT_DIR)` lines;
   - `make report-publish` (no `WHICH`) → fails with the usage
     line.
4. **Net-marked doctor test** (B5) — extend `tests/test_doctor.py`
   (or a small `test_doctor_net.py`): `doctor.run(rt, net=True)`
   against a temp register pointing at `https://example.com`,
   marked `@pytest.mark.net` — makes `pytest -m net` (and
   `make test-net`) collect ≥ 1 test instead of exiting 5;
   deselected from the default suite by the existing addopts.
5. **Smoke updates** — `test_cli_smoke.py`: bare-group help
   assertion (exit 0, stdout) and `--version` → `0.1.2`; existing
   flows unchanged.

## Deliverables

`tests/test_cli_operability.py`, `tests/test_preflight.py`,
`tests/test_makefile.py`, the net-marked doctor test, smoke deltas.

## Exit gate

- `pytest` green offline — markers deselected — including the three
  new files (~104–110 tests total).
- `pytest -m net` collects and passes the doctor test (needs
  network; run explicitly, not in CI).
- No sleeps, no order dependence; make tests create no DB, no
  installs, no network.

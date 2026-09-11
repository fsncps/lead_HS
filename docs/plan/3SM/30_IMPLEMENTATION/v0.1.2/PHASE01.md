---
unit: v0.1.2
stage: IMPLEMENTATION
lifecycle: LIVE
updated: 2026-09-11
---

# PHASE01 — CLI operability

Status: done (2026-09-11) · Depends on: — · Governs: the CLI contract
enforcement everything else sits on.

## Objective

`cli.py` delivers the binding exit-code contract: every failure path
exits with the convention's code, never a raw traceback, never a
silent wrong code. Plus the contained operability fixes from first
real use: `source list` registered once, bare groups print help,
doctor loses the no-op `--no-net`, `--data-dir` for installed use,
version bumped to 0.1.2.

## Governing references

- `../../20_DESIGN/units/v0.1.2.md` — §CLI contract deltas
  (od2–od4).
- `../../20_DESIGN/MASTER/interfaces.md` — exit-code convention (i1)
  and i10.
- `../v0.1.2/MASTER.md` — B1/B3/B4 (empirical click contract,
  `--data-dir` plumbing, version bump).

## Steps

1. **`main()` rewrite** (B1): `cli(standalone_mode=False)`; import
   exceptions from `click.exceptions`; mapping, in order:
   - return value `int` → that code (covers `ctx.exit(n)`,
     `--help`, `--version` — click returns the code itself under
     `standalone_mode=False`); `None` → 0;
   - `NoArgsIsHelpError` (bare groups; UsageError subclass) →
     `click.echo(exc.format_message())` to **stdout**, return 0 —
     caught **before** UsageError;
   - `Exit` → `exc.exit_code` (defensive; normally already returned
     by click);
   - `Abort` → "interrupted" to stderr, return 130;
   - `KeyboardInterrupt` → same (belt-and-braces; click normally
     converts to Abort);
   - `UsageError` → `exc.show()`, return **1** (hardcoded — click
     default is 2; convention i1);
   - other `ClickException` → `exc.show()`, return
     `exc.exit_code`;
   - `Exception` → `bug: {exc}` + return 1; `LEADHS_DEBUG` set →
     re-raise.
   `if __name__ == "__main__": sys.exit(main())` (console script
   wrapper already does `sys.exit(main())`).
2. **`no_args_is_help=True`** on all four groups (`cli`, `db`,
   `source`, `probe`).
3. **`source list` single registration:** decorate `list_` with
   `@source.command("list")`; delete the trailing
   `source.add_command(list_, name="list")` line (the derived
   `list-` artifact disappears).
4. **doctor:** drop the `--no-net` option (was a no-op
   `default=True`); callback →
   `ctx.exit(doctormod.main(rt, net=net))`.
5. **`--data-dir`** (B3): `--db` → `default=None` (keep
   `show_default` honest via help text); add `--data-dir DIR`; in
   the callback: both given → `raise click.UsageError("--db and
   --data-dir are mutually exclusive")`; `--data-dir` →
   `db_path = os.path.join(data_dir, "leadhs.sqlite")`; neither →
   `data/leadhs.sqlite`. `Runtime.store_root()` untouched — the raw
   store follows `dirname(db_path)/raw` (also correct for
   `--data-dir`).
6. **Drop the unused `field` import** (`dataclasses`).
7. **Version 0.1.2** (B4): `pyproject.toml` `version` and
   `src/leadhs/__init__.py` `__version__`.

## Deliverables

`src/leadhs/cli.py` deltas; `pyproject.toml` + `__init__.py` version
bump. No other module changes.

## Exit gate

- `python -m leadhs.cli --help` → exit 0, help on stdout.
- `leadhs dource` (unknown command) → exit 1 with click's error +
  "Try 'leadhs --help' for help."
- Bare `leadhs` / `leadhs db` / `leadhs source` / `leadhs probe` →
  help on stdout, exit 0.
- `leadhs --db X --data-dir Y db status` → exit 1.
- `--no-net` absent from `leadhs doctor --help`; `--net` works.
- `source list` resolves; `source list-` is gone (404 → usage error).
- Ctrl-C during a command → 130, "interrupted".
- Existing suite green (`pytest`): only legitimate expectation
  updates allowed, no skips.

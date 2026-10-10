"""click entrypoint: db, source, probe, doctor groups.

Exit-code convention (i1): 0 success; 1 usage/data error; 2 an
operation ran but ended failed/blocked (findings recorded);
3 audit found violations; 130 on KeyboardInterrupt.

`main()` enforces the mapping itself (standalone_mode=False; i10):
UsageError → 1 (hardcoded — click's default is 2), bare groups print
help on stdout with exit 0, Abort/KeyboardInterrupt → 130, Exit → its
code, anything else → `bug:` + 1 (LEADHS_DEBUG re-raises).
"""

from __future__ import annotations

import os
import sys
import time as _timemod
from dataclasses import dataclass
from typing import Optional

import click
from click.exceptions import Abort, Exit, NoArgsIsHelpError, UsageError

from . import __version__
from .logutil import configure_logging


@dataclass
class Runtime:
    db_path: str = "data/leadhs.sqlite"
    contact: Optional[str] = None
    verbose: bool = False
    logger: object = None

    def store_root(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(self.db_path)), "raw")


def _runtime(ctx: click.Context) -> Runtime:
    return ctx.obj


@click.group(no_args_is_help=True)
@click.version_option(__version__)
@click.option("--verbose", is_flag=True, help="structured log lines")
@click.option("--db", "db_path", default=None, help="SQLite database path (default: data/leadhs.sqlite)")
@click.option("--data-dir", "data_dir", default=None, help="base directory for leadhs.sqlite + raw/ (exclusive with --db)")
@click.option("--contact", envvar="LEADHS_CONTACT", default=None, help="user-agent contact (doctor warns when unset)")
@click.pass_context
def cli(ctx, verbose, db_path, data_dir, contact):
    """leadhs — lead-in-paints evidence tool (HS 3208/3209/3213)."""
    if db_path and data_dir:
        raise UsageError("--db and --data-dir are mutually exclusive")
    if data_dir:
        db_path = os.path.join(data_dir, "leadhs.sqlite")
    ctx.obj = Runtime(
        db_path=db_path or "data/leadhs.sqlite",
        contact=contact, verbose=verbose, logger=configure_logging(verbose),
    )


@click.group(name="db", no_args_is_help=True)
def db():
    """Database: migrate, status, audit."""


@click.group(name="source", no_args_is_help=True)
def source():
    """Source register."""


@click.group(no_args_is_help=True)
def probe():
    """Probe runs and reports."""


@click.group(name="raw", no_args_is_help=True)
def raw():
    """Raw source layer: scan, run, status, explain (v0.3.0)."""


@click.group(name="identity", no_args_is_help=True)
def identity():
    """Canonical identity layer: resolve, rebuild, status (v0.3.4)."""


@click.group(name="hs", no_args_is_help=True)
def hs():
    """HS-code completion: apply, status (v0.3.4 r02)."""


def _hs_map_path(map_path: str | None) -> str:
    return map_path or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dict", "hs_group_map.csv"
    )


@hs.command("apply")
@click.option("--map", "map_path", default=None, help="hs_group_map.csv path (default: bundled dict)")
@click.option("--dry-run", is_flag=True, help="identical read path; zero writes, no run rows")
@click.pass_context
def hs_apply(ctx, map_path, dry_run):
    """Apply the curated group-to-HS4 map to products.hs_code."""
    import json

    from . import db as dbmod
    from .hs import HsMapError, apply as hs_apply_mod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    _ensure_migrated(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        try:
            counts = hs_apply_mod(conn, _hs_map_path(map_path), dry_run=dry_run)
        except HsMapError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(2)
        except FileNotFoundError as exc:
            click.echo(f"error: map file not found: {exc}", err=True)
            ctx.exit(2)
        prefix = "dry-run planned: " if dry_run else ""
        click.echo(prefix + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    finally:
        conn.close()


@hs.command("status")
@click.option("--map", "map_path", default=None, help="hs_group_map.csv path (default: bundled dict)")
@click.pass_context
def hs_status(ctx, map_path):
    """Three-state HS coverage per source + pending-group worklist."""
    from . import db as dbmod
    from .hs import HsMapError, render_status, status as hs_status_mod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    _ensure_migrated(ctx, rt)
    conn = dbmod.connect(rt.db_path, readonly=True)
    try:
        try:
            out = hs_status_mod(conn, _hs_map_path(map_path))
        except HsMapError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(2)
        except FileNotFoundError as exc:
            click.echo(f"error: map file not found: {exc}", err=True)
            ctx.exit(2)
        render_status(out)
    finally:
        conn.close()


def _ensure_migrated(ctx: click.Context, rt: Runtime) -> None:
    """d22 preflight: pending migrations are a blocked state, not a
    usage error — the identity tables may not exist yet."""
    import sqlite3

    from . import db as dbmod

    if not (os.path.isfile(rt.db_path) and os.path.getsize(rt.db_path) > 0):
        click.echo("error: database not initialized — run `leadhs db init` first", err=True)
        ctx.exit(2)
    try:
        conn = sqlite3.connect(f"file:{os.path.abspath(rt.db_path)}?mode=ro", uri=True)
        try:
            applied = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        click.echo("error: database not initialized — run `leadhs db init` first", err=True)
        ctx.exit(2)
    pending = [name for number, name, _ in dbmod.migration_files() if applied is None or number > applied]
    if pending:
        click.echo(
            f"error: pending migrations ({', '.join(pending)}) — run `leadhs db init` first",
            err=True,
        )
        ctx.exit(2)


def _wanted_identity_sources(ctx, rt, source_id):
    """--source validation (d8 pattern) against the register + the
    adapter registry; default = every acquired adapter-backed source."""
    from . import db as dbmod, source as sourcemod
    from .identity.adapters import ADAPTERS

    conn = dbmod.connect(rt.db_path, readonly=True)
    try:
        if source_id:
            if sourcemod.get_source(conn, source_id) is None:
                click.echo(f"error: unknown source {source_id!r} (run `leadhs source load` first)", err=True)
                ctx.exit(1)
            if source_id not in ADAPTERS:
                click.echo(
                    f"error: no identity adapter for {source_id} (known: {', '.join(sorted(ADAPTERS))})",
                    err=True,
                )
                ctx.exit(1)
            return [source_id]
        acquired = [
            r[0]
            for r in conn.execute(
                "SELECT source_id FROM raw_source_profile WHERE source_id IN "
                f"({', '.join('?' for _ in ADAPTERS)}) ORDER BY source_id",
                tuple(sorted(ADAPTERS)),
            )
        ]
        if not acquired:
            click.echo("error: no acquired adapter-backed sources (run `raw run` first)", err=True)
            ctx.exit(1)
        return acquired
    finally:
        conn.close()


@identity.command()
@click.option("--source", "source_id", default=None, help="source ID (default: every acquired adapter-backed source)")
@click.option("--dry-run", is_flag=True, help="identical read path; zero writes (its own run row only)")
@click.option("--batch", "batch", type=click.IntRange(min=1), default=500, show_default=True,
              help="rows per BEGIN IMMEDIATE commit")
@click.pass_context
def resolve(ctx, source_id, dry_run, batch):
    """Derive canonical manufacturer/product rows from the raw tables."""
    from . import db as dbmod
    from .identity import resolve as resolvemod
    from .identity.errors import IdentityError, SourceMissingError, SourceSchemaError

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    _ensure_migrated(ctx, rt)
    wanted = _wanted_identity_sources(ctx, rt, source_id)
    conn = dbmod.connect(rt.db_path)
    try:
        try:
            summaries = resolvemod.resolve(conn, wanted, dry_run=dry_run, batch=batch, logger=rt.logger)
        except (SourceMissingError, SourceSchemaError) as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(1)
        except IdentityError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(2)
        for s in summaries:
            counts = ", ".join(f"{k}={v}" for k, v in sorted(s.items()) if k not in ("source", "run_key", "dry_run"))
            state = "dry-run" if s["dry_run"] else "done"
            click.echo(f"{s['source']:<6} {s['run_key']:<34} {state:<8} {counts}")
    finally:
        conn.close()


@identity.command()
@click.option("--batch", "batch", type=click.IntRange(min=1), default=500, show_default=True,
              help="rows per BEGIN IMMEDIATE commit")
@click.pass_context
def rebuild(ctx, batch):
    """Backup → tear down → re-derive ALL sources (il2). Aborts before
    any teardown when the backup fails; keeps a timestamped snapshot."""
    from . import db as dbmod
    from .identity import resolve as resolvemod
    from .identity.errors import IdentityError

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    _ensure_migrated(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        try:
            summaries = resolvemod.rebuild(conn, rt.db_path, batch=batch, logger=rt.logger)
        except IdentityError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(2)
        for s in summaries:
            counts = ", ".join(f"{k}={v}" for k, v in sorted(s.items()) if k not in ("source", "run_key", "dry_run", "backup"))
            click.echo(f"{s['source']:<6} {s['run_key']:<34} done   {counts}")
        click.echo(f"backup: {summaries[0]['backup']}" if summaries else "backup: (no sources)")
    finally:
        conn.close()


@identity.command("status")
@click.pass_context
def identity_status(ctx):
    """Per-source resolution state, back-link coverage, drift, queue."""
    from . import db as dbmod
    from .identity import resolve as resolvemod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    _ensure_migrated(ctx, rt)
    conn = dbmod.connect(rt.db_path, readonly=True)
    try:
        resolvemod.status(conn)
    finally:
        conn.close()


def _instruction_path(source_id: str, instructions_dir: str | None) -> str:
    import os as _os

    directory = instructions_dir or "raw_sources"
    return _os.path.join(directory, f"{source_id}.instruction.json")


@click.command()
@click.option("--net", is_flag=True, help="check reachability of seeded sources")
@click.pass_context
def doctor(ctx, net):
    """Environment preflight (python, sqlite, binaries, data dir, contact)."""
    from . import doctor as doctormod

    rt = _runtime(ctx)
    ctx.exit(doctormod.main(rt, net=net))


# --- db -------------------------------------------------------------


@db.command()
@click.option("--no-backup", is_flag=True, help="skip the timestamped backup of an existing DB")
@click.pass_context
def init(ctx, no_backup):
    """Apply pending migrations (0001–0002 in this unit)."""
    from . import db as dbmod

    rt = _runtime(ctx)
    os_parent = os.path.dirname(rt.db_path)
    os.makedirs(os_parent, exist_ok=True) if os_parent else None
    conn = dbmod.connect(rt.db_path)
    try:
        applied, pending = dbmod.migrate(conn, backup=not no_backup, db_path=rt.db_path)
        dbmod.stale_run_reclaim(conn)
        click.echo(f"applied: {', '.join(applied) if applied else '(none)'}")
        click.echo(f"pending: {', '.join(pending) if pending else '(none)'}")
    finally:
        conn.close()


@db.command()
@click.pass_context
def status(ctx):
    """Applied/pending migrations, row counts, file size."""
    from . import db as dbmod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        dbmod.stale_run_reclaim(conn)
        dbmod.status(conn)
    finally:
        conn.close()


@db.command()
@click.option("--unreferenced", is_flag=True, help="also list raw-store orphan files")
@click.pass_context
def audit(ctx, unreferenced):
    """Run provenance rules R1–R9; exit 3 on violations."""
    from . import db as dbmod, store as storemod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        violations = dbmod.audit(conn, storemod.RawStore(rt.store_root()), unreferenced=unreferenced)
        if violations:
            for line in violations:
                click.echo(line, err=True)
            ctx.exit(3)
        click.echo("audit clean")
    finally:
        conn.close()


# --- source ---------------------------------------------------------


@source.command()
@click.option("--file", "csv_path", default=None, help="register CSV (default: src/leadhs/dict/sources.csv)")
@click.pass_context
def load(ctx, csv_path):
    """Upsert the source register from the repo CSV (register of record)."""
    from . import db as dbmod, source as sourcemod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    path = csv_path or sourcemod.default_register_path()
    conn = dbmod.connect(rt.db_path)
    try:
        count = sourcemod.load(conn, path)
        click.echo(f"loaded {count} sources")
    except sourcemod.SourceLoadError as exc:
        click.echo(f"error: {exc}", err=True)
        ctx.exit(1)
    finally:
        conn.close()


@source.command("list")
@click.option("--class", "class_code", type=click.Choice(["CS", "PE", "LG", "ST", "LI", "AS"]), default=None)
@click.pass_context
def list_(ctx, class_code):
    """List sources (optionally one class)."""
    from . import db as dbmod, source as sourcemod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        sourcemod.list_(conn, class_code)
    finally:
        conn.close()


@probe.command()
@click.option("--source", "source_id", default=None, help="source ID (CS-1)")
@click.option("--all", "all_sources", is_flag=True, help="run every active adapter-backed source")
@click.option("--mode", "mode", type=click.Choice(["census", "format_check", "access_check", "recon", "capability"]), default="census")
@click.option("--sample", "sample_n", type=int, default=5, help="PE sample-page count")
@click.option("--dry-run", is_flag=True, help="plan requests; zero network calls")
@click.option("--wave", "wave", type=click.IntRange(1, 4), default=None, help="v0.2.2 wave preset (1 bulk exports / 2 register completion / 3 PE universe / 4 manual checklist)")
@click.option("--budget", "budget", type=int, default=None, help="wave budget in seconds (default 3600)")
@click.option("--staging-db", "staging_db", default=None, help="staging DB path (default: data/testdata.sqlite; i19)")
@click.pass_context
def run(ctx, source_id, all_sources, mode, sample_n, dry_run, wave, budget, staging_db):
    """One probe run per source; exit 2 when any run ended blocked/failed."""
    from . import db as dbmod, fetch as fetchmod, store as storemod
    from . import source as sourcemod
    from .fetch import FetchConfig
    from .probe import engine as probeengine

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    if wave is not None:
        _run_wave(ctx, rt, probeengine, wave=wave, budget=budget, staging_db=staging_db, dry_run=dry_run, sample_n=sample_n)
        return
    if not source_id and not all_sources:
        click.echo("error: give --source ID or --all", err=True)
        ctx.exit(1)
    if source_id and all_sources:
        click.echo("error: --source and --all are mutually exclusive", err=True)
        ctx.exit(1)

    conn = dbmod.connect(rt.db_path)
    store = storemod.RawStore(rt.store_root())
    fetcher = fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger)
    try:
        if all_sources:
            # e2: the capability sweep is the classes=["AS"] preset of the
            # generalized run filter, applied at this layer
            summaries, exit_code = probeengine.run_all(
                conn, store, fetcher, mode=mode, sample_n=sample_n, dry_run=dry_run,
                logger=rt.logger, classes=["AS"] if mode == "capability" else None,
            )
            if not summaries:
                click.echo("no sources (register empty or no active adapter-backed sources)")
                ctx.exit(0)
        else:
            source = sourcemod.get_source(conn, source_id)
            if source is None:
                click.echo(f"error: unknown source {source_id!r} (run `leadhs source load` first)", err=True)
                ctx.exit(1)
            summary = probeengine.run_one(conn, store, fetcher, source, mode=mode, sample_n=sample_n, dry_run=dry_run, logger=rt.logger)
            summaries = [summary]
            exit_code = 2 if summary["status"] in ("blocked", "failed") else 0
        for summary in summaries:
            click.echo(
                f"{summary['source']:<6} {summary['run_key']:<28} {summary['status']:<8} "
                f"docs={summary['documents']} findings={summary['findings']}"
            )
        if any(s["status"] == "blocked" for s in summaries):
            click.echo("blocked sources: " + ", ".join(s["source"] for s in summaries if s["status"] == "blocked"), err=True)
        if any(s["status"] == "failed" for s in summaries):
            click.echo("failed sources: " + ", ".join(s["source"] for s in summaries if s["status"] == "failed"), err=True)
        ctx.exit(exit_code)
    finally:
        conn.close()


# v0.2.2 wave presets (i20): (mode, source ids / class, label). W1 = bulk
# official exports; W2 = register completion (manual fallback built in);
# W3 = PE universe recon; W4 = manual-record checklist (no fetches).
_WAVE_PRESETS = {
    1: {"mode": "capability", "ids": ["AS-2", "AS-3", "AS-4", "ST-4", "CS-2"], "label": "bulk official exports"},
    2: {"mode": "capability", "ids": ["AS-5", "AS-6", "AS-7", "AS-8", "AS-9", "AS-10"], "label": "register completion"},
    3: {"mode": "recon", "classes": ["PE"], "label": "PE universe recon"},
    4: {"mode": None, "ids": None, "manual": True, "label": "manual records & LI checklist"},
}

_now = _timemod.monotonic  # module-level for the virtual-clock tests


def _run_wave(ctx, rt, probeengine, wave, budget, staging_db, dry_run, sample_n):
    from . import db as dbmod, fetch as fetchmod, staging as stagingmod, store as storemod
    from . import source as sourcemod
    from .fetch import FetchConfig

    preset = _WAVE_PRESETS[wave]
    budget = budget if budget is not None else 3600
    conn = dbmod.connect(rt.db_path)
    store = storemod.RawStore(rt.store_root())
    staging_path = staging_db or "data/testdata.sqlite"
    staging_conn = stagingmod.connect(staging_path)
    stagingmod.init(staging_conn)
    stagingmod.seed_dict(staging_conn)
    fetcher = fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger)
    try:
        click.echo(f"wave {wave} — {preset['label']} (budget {budget}s, staging {staging_path})")
        if preset.get("manual"):
            # W4: the terminal-disposition checklist over the studied
            # subset — active rows of any class, plus manual-access rows
            # even when inactive (associations/LI lists). Inactive
            # non-manual rows are deliberately retired/capped (i13/D31
            # notes) and stay outside the invariant. Never fetch.
            todo = []
            for s in sourcemod.all_sources(conn, active_only=False):
                if not s.active and s.access_method_code != "manual":
                    continue
                disp = probeengine.disposition_of(conn, s.id, staging=staging_conn)
                if disp["disposition"] not in ("counted", "manual-recorded", "blocked"):
                    todo.append((s.id, disp["disposition"]))
            if not todo:
                click.echo("checklist: nothing outstanding")
                ctx.exit(0)
            for sid, disp in todo:
                click.echo(f"  record manually: probe record --source {sid} --metric … ({disp})")
            ctx.exit(2)
        if preset.get("ids") is not None:
            wanted = [s for s in sourcemod.all_sources(conn, active_only=False) if s.id in set(preset["ids"])]
        else:
            wanted = [s for s in sourcemod.all_sources(conn, active_only=True) if s.class_code in set(preset["classes"])]
        wanted = [s for s in wanted if probeengine.adaptersmod.get_adapter(s) and s.access_method_code != "manual"]
        start = _now()
        incomplete = False
        exit_code = 0
        for source in wanted:
            if not dry_run and _now() - start > budget:
                click.echo(f"budget exhausted before {source.id} — resumable (re-run the wave)", err=True)
                incomplete = True
                break
            summary = probeengine.run_one(
                conn, store, fetcher, source, mode=preset["mode"],
                sample_n=sample_n, dry_run=dry_run, logger=rt.logger, staging=staging_conn,
            )
            disp = probeengine.disposition_of(conn, source.id, staging=staging_conn)
            click.echo(
                f"  {source.id:<6} {summary['status']:<8} staged={summary.get('staged', 0)}+{summary.get('staged_trade', 0)} "
                f"disposition={disp['disposition']}"
            )
            if summary["status"] in ("blocked", "failed"):
                exit_code = 2
        # c1 invariant: after a COMPLETED wave, no row left pending or
        # format-finding (a budget-exhausted wave is resumable, not failed)
        if not incomplete:
            disps = probeengine.dispositions(conn, [s.id for s in wanted], staging=staging_conn)
            outstanding = {i: d for i, d in disps.items() if d["disposition"] in ("pending", "format-finding")}
            for i, d in outstanding.items():
                click.echo(f"invariant: {i} disposition={d['disposition']} ({d['detail']})", err=True)
            if outstanding:
                exit_code = 2
            click.echo(
                "dispositions: " + ", ".join(f"{i}={d['disposition']}" for i, d in sorted(disps.items()))
            )
        ctx.exit(exit_code)
    finally:
        conn.close()
        staging_conn.close()


@probe.command()
@click.option("--source", "source_id", required=True, help="source ID (ST-1 for PCN)")
@click.option("--metric", "metric", required=True, help="metric code from the vocabulary")
@click.option("--value", "value", default=None, help="numeric value (numeric metrics)")
@click.option("--value-text", "value_text", default=None, help="text value (text metrics)")
@click.option("--unit", "unit", default=None, help="quantity_unit code")
@click.option("--url", "url", default=None, help="provenance URL")
@click.option("--document", "document_file", default=None, type=click.Path(exists=True), help="raw file to attach")
@click.option("--note", "note", default=None, help="note")
@click.option("--mode", "mode", type=click.Choice(["census", "recon", "capability"]), default="census", help="probe_mode label for the manual run (e8)")
@click.pass_context
def record(ctx, source_id, metric, value, value_text, unit, url, document_file, note, mode):
    """Create a manual probe run + one finding (method=manual; ST-1 PCN path)."""
    from . import db as dbmod, store as storemod
    from .probe import engine as probeengine

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    store = storemod.RawStore(rt.store_root())
    try:
        summary = probeengine.record_manual(
            conn, store, source_id, metric, value=value, value_text=value_text,
            unit=unit, url=url, document_file=document_file, note=note, logger=rt.logger, contact=rt.contact,
            mode=mode,
        )
        click.echo(f"{summary['run_key']}  done  metric={metric}")
    except probeengine.EngineError as exc:
        click.echo(f"error: {exc}", err=True)
        ctx.exit(1)
    finally:
        conn.close()


@probe.command()
@click.option("--source", "source_id", default=None, help="restrict to one source")
@click.option("--format", "fmt", type=click.Choice(["md", "csv", "json"]), default="md")
@click.option("--out", "out_path", default=None, help="write to file (else stdout)")
@click.option("--staging-db", "staging_db", default=None,
              help="staging DB path for the landscape sections (default: data/testdata.sqlite if present; i19)")
@click.pass_context
def report(ctx, source_id, fmt, out_path, staging_db):
    """Render the census report from the views (md/csv/json)."""
    from . import db as dbmod, report as reportmod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    if staging_db is None and os.path.exists("data/testdata.sqlite"):
        staging_db = "data/testdata.sqlite"
    staging_conn = None
    if staging_db:
        from . import staging as stagingmod
        staging_conn = stagingmod.connect(staging_db)
    conn = dbmod.connect(rt.db_path)
    try:
        output = reportmod.render(conn, format=fmt, source_id=source_id, staging_conn=staging_conn)
    finally:
        conn.close()
        if staging_conn is not None:
            staging_conn.close()
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(output)
        click.echo(f"wrote {out_path}")
    else:
        click.echo(output)


@probe.command("download-csv-sample")
@click.option("--n", "n", type=click.IntRange(min=1), default=100, show_default=True, help="sample size per registry")
@click.option("--seed", "seed", type=int, default=42, show_default=True, help="seeded reproducible draw (recorded in run + CSV)")
@click.option("--source", "source_ids", multiple=True, help="registry ID (default: the six-registry D36 target set)")
@click.option("--out-dir", "out_dir", default="data/report", show_default=True, help="CSV + manifest destination (D22 routing)")
@click.option("--dry-run", is_flag=True, help="plan requests; zero network, zero files")
@click.option("--from-store", is_flag=True,
              help="re-render from the newest archived exports in the raw store (D38; zero network)")
@click.pass_context
def download_csv_sample(ctx, n, seed, source_ids, out_dir, dry_run, from_store):
    """Per-registry product-row samples + manifest for management review (v0.2.4, D36)."""
    from . import db as dbmod, fetch as fetchmod, store as storemod
    from . import source as sourcemod
    from .fetch import FetchConfig
    from .probe import csv_sample as csvsample

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    wanted = list(source_ids) or list(csvsample.DEFAULT_SOURCES)
    conn = dbmod.connect(rt.db_path)
    try:
        source_rows = {}
        for sid in wanted:
            source = sourcemod.get_source(conn, sid)
            if source is None:
                click.echo(f"error: unknown source {sid!r} (run `leadhs source load` first)", err=True)
                ctx.exit(1)
            source_rows[sid] = source
        if not dry_run:
            os.makedirs(out_dir, exist_ok=True)
        if from_store:
            fetcher = csvsample.fetcher_from_store(conn, storemod.RawStore(rt.store_root()))
        else:
            fetcher = fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger)
        exit_code, entries = csvsample.sample(
            conn, storemod.RawStore(rt.store_root()),
            fetcher,
            source_rows, n=n, seed=seed, out_dir=out_dir, dry_run=dry_run, logger=rt.logger,
            from_store=from_store,
        )
    finally:
        conn.close()
    if dry_run:
        click.echo("dry-run: requests planned; zero network, zero files")
    else:
        if from_store:
            click.echo("re-render from archived exports (zero network)")
        for e in entries:
            detail = e["file"] if e["status"] == "delivered" else (e["reason"] or "")
            click.echo(f"{e['source']:<6} {e['status']:<12} {'' if e['rows'] is None else str(e['rows']):>4}  {detail}")
        click.echo(f"manifest: {out_dir}/csv-sample.manifest.md")
    ctx.exit(exit_code)


@probe.command("as-source-probe")
@click.option("--out-dir", "out_dir", default="data/report/AS-source-probe", show_default=True,
              help="CSVs + summary destination (D37)")
@click.option("--source", "source_ids", multiple=True, help="source ID (default: all AS rows in the register)")
@click.option("--reuse-dir", "reuse_dir", default="data/report", show_default=True,
              help="where to look for same-day csv-sample artifacts (AS-2/AS-3 reuse)")
@click.option("--dry-run", is_flag=True, help="plan requests; zero network, zero files")
@click.option("--rebuild-summary", "rebuild", is_flag=True,
              help="re-render the summary from DB findings (D38; zero network)")
@click.pass_context
def as_source_probe(ctx, out_dir, source_ids, reuse_dir, dry_run, rebuild):
    """One finding per AS source (v0.2.4 addendum, D37): product-row CSV
where obtainable, else why not + what is available instead, plus
exact-or-estimated record counts; associations get member-list findings."""
    from . import db as dbmod, fetch as fetchmod, store as storemod, source as sourcemod
    from .fetch import FetchConfig
    from .probe import as_probe

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        if rebuild:
            os.makedirs(out_dir, exist_ok=True)
            entries = as_probe.rebuild_summary(conn, out_dir)
            click.echo(f"summary rebuilt from findings (zero network): {out_dir}/as-source-probe.summary.md")
            ctx.exit(0)
        if source_ids:
            wanted = list(source_ids)
        else:
            wanted = [r[0] for r in conn.execute(
                "SELECT id FROM source WHERE class_code = 'AS' ORDER BY rowid")]
            if not wanted:
                click.echo("error: no AS rows in the register (run `leadhs source load` first)", err=True)
                ctx.exit(1)
        source_rows = {}
        for sid in wanted:
            source = sourcemod.get_source(conn, sid)
            if source is None:
                click.echo(f"error: unknown source {sid!r} (run `leadhs source load` first)", err=True)
                ctx.exit(1)
            source_rows[sid] = source
        if not dry_run:
            os.makedirs(out_dir, exist_ok=True)
        exit_code, entries = as_probe.sample(
            conn, storemod.RawStore(rt.store_root()),
            fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger),
            source_rows, out_dir=out_dir, dry_run=dry_run, logger=rt.logger,
            reuse_dir=reuse_dir,
        )
    finally:
        conn.close()
    if dry_run:
        click.echo("dry-run: requests planned; zero network, zero files")
    else:
        for e in entries:
            detail = e["file"] if e["status"] == "delivered" else (e["basis"] or e["reason"] or "")
            click.echo(f"{e['source']:<6} {e['status']:<12} {e['records'] or '':>24}  {detail}")
        click.echo(f"summary: {out_dir}/as-source-probe.summary.md")
    ctx.exit(exit_code)


@probe.command("basta-probe")
@click.option("--n", "n", type=click.IntRange(min=1), default=100, show_default=True,
              help="sample size (default: 100 articles)")
@click.option("--seed", "seed", type=int, default=42, show_default=True,
              help="seeded reproducible draw (recorded in run + CSV)")
@click.option("--source", "source_ids", multiple=True, default=("AS-33",),
              help="source ID (default: AS-33 BASTA online)")
@click.option("--out-dir", "out_dir", default="data/report", show_default=True,
              help="sample CSV destination (D22 routing)")
@click.option("--dry-run", is_flag=True, help="plan requests; zero network, zero files")
@click.pass_context
def basta_probe(ctx, n, seed, source_ids, out_dir, dry_run):
    """BASTA special probe (v0.2.4 addendum, D40): pin the anonymous
search route behind /sok, characterize data availability, deliver a
seeded random 100-article sample CSV — one honest state machine."""
    from . import db as dbmod, fetch as fetchmod, store as storemod, source as sourcemod
    from .fetch import FetchConfig
    from .probe import basta_probe as bastaprobe

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        wanted = list(source_ids) or [bastaprobe.DEFAULT_SOURCE_ID]
        source_rows = {}
        for sid in wanted:
            source = sourcemod.get_source(conn, sid)
            if source is None:
                click.echo(f"error: unknown source {sid!r} (run `leadhs source load` first)", err=True)
                ctx.exit(1)
            source_rows[sid] = source
        if not dry_run:
            os.makedirs(out_dir, exist_ok=True)
        exit_code, _entries = bastaprobe.sample(
            conn, storemod.RawStore(rt.store_root()),
            fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger),
            source_rows, n=n, seed=seed, out_dir=out_dir, dry_run=dry_run,
            logger=rt.logger,
        )
    finally:
        conn.close()
    if dry_run:
        click.echo("dry-run: requests planned; zero network, zero files")
    else:
        click.echo(f"sample: {out_dir}")
    ctx.exit(exit_code)


@raw.command()
@click.argument("source_id")
@click.option("--instructions-dir", "instructions_dir", default=None,
              help="instructions directory (default: raw_sources/)")
@click.pass_context
def explain(ctx, source_id, instructions_dir):
    """Render a sourcing instruction readably (file-only; no DB)."""
    from .raw import instructions as instructionsmod

    path = _instruction_path(source_id, instructions_dir)
    try:
        inst, manifest_hash = instructionsmod.load(path)
    except instructionsmod.InstructionError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"instruction:  {path}")
    click.echo(f"source:       {inst.source_id} — {inst.source_name} ({inst.source_class})")
    click.echo(f"export_kind:  {inst.export_kind}")
    click.echo(f"endpoints:")
    click.echo(f"  list:   {inst.list_url}")
    if inst.endpoints.get("detail"):
        click.echo(f"  detail: {inst.endpoints['detail']}")
    p = inst.pagination
    click.echo(f"pagination:   kind={p.kind}")
    if p.kind == "page_param":
        click.echo(f"  page_param={p.page_param} page_size={p.page_size} max_pages={p.max_pages}")
    rec = inst.records
    expected = rec["expected_count"]
    expected_label = "unknown" if expected is None else f"{expected:,}"
    click.echo(f"records:      expected_count={expected_label}")
    click.echo(f"  derivation: {rec['count_derivation']}")
    click.echo(f"columns:      {len(inst.columns)}")
    click.echo(f"  {'source_header':<28} {'column':<24} {'type':<9} {'prio':<5} description")
    for c in inst.columns:
        click.echo(
            f"  {c.source_header:<28} {c.column:<24} {c.type:<9} {c.truncation_priority:<5} {c.description or ''}"
        )
    click.echo(f"natural_key:  {', '.join(inst.natural_key)}")
    click.echo(f"payload_budget_bytes: {inst.payload_budget_bytes}")
    pol = inst.politeness
    click.echo(f"politeness:   delay={pol.delay_seconds}s crawl_delay="
               f"{'robots' if pol.crawl_delay_seconds is None else f'{pol.crawl_delay_seconds}s'} "
               f"request_budget={pol.request_budget_per_run} records_per_request="
               f"{pol.records_per_request if pol.records_per_request is not None else '?'}")
    click.echo(f"  derivation: {pol.derivation}")
    if inst.notes:
        click.echo(f"notes:        {inst.notes}")
    click.echo(f"manifest_hash: {manifest_hash}")


@probe.command("url")
@click.argument("url")
@click.option("--source", "source_id", default=None, help="source ID — also record one finding in a probe run")
@click.option("--cap", "cap", type=int, default=None, help="sample cap in bytes (default 64 KiB)")
@click.pass_context
def probe_url(ctx, url, source_id, cap):
    """Light pre-probe of an unregistered URL: ballpark only (rs5).

    Access, robots (crawl-delay), content-type, rough size, first
    bytes. No DB writes unless --source ID (then one finding inside a
    probe run)."""
    from . import db as dbmod, fetch as fetchmod, store as storemod
    from .fetch import FetchConfig
    from .fetch import Blocked, FetchError, ProbeNetworkError, RateLimited, RobotsDisallowed, SizeLimit
    from .raw import scanner as scannermod

    rt = _runtime(ctx)
    if source_id:
        _ensure_initialized(ctx, rt)
    fetcher = fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger)
    summary = {}
    exit_code = 0
    try:
        policy = fetcher.robots_policy(url)
        delay = fetcher.crawl_delay(url)
        click.echo(f"url:            {url}")
        click.echo(f"robots:         {policy}" + (f" (crawl-delay {delay}s)" if delay else ""))
        try:
            resp = fetcher.get(url, max_bytes=cap or scannermod.PROBE_URL_CAP)
        except SizeLimit:
            click.echo("size:           > cap (streamed, aborted at the cap — content intact upstream)")
            resp = None
        if resp is not None:
            ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
            length = resp.headers.get("Content-Length")
            click.echo(f"status:         {resp.status_code}")
            click.echo(f"content-type:   {ctype or '?'}")
            if length and length.isdigit():
                click.echo(f"size:           {int(length):,} bytes (content-length)")
            else:
                click.echo(f"size:           {len(resp.content):,} bytes received (no content-length)")
            click.echo(f"encoding:       {resp.encoding}")
            sample = " ".join(resp.text[:200].split())
            click.echo(f"first bytes:    {sample[:200]!r}")
            summary = {
                "status_code": resp.status_code, "content_type": ctype,
                "size": int(length) if length and length.isdigit() else len(resp.content),
                "robots": policy, "encoding": resp.encoding,
            }
    except (RobotsDisallowed, Blocked, RateLimited, ProbeNetworkError) as exc:
        click.echo(f"fetch failed:   {exc}", err=True)
        summary = {"error": type(exc).__name__, "detail": str(exc)}
        exit_code = 2
    if source_id:
        from . import source as sourcemod
        from .models import DocumentDraft, FindingDraft, ProbeResult
        from .probe import engine as probeengine

        conn = dbmod.connect(rt.db_path)
        store = storemod.RawStore(rt.store_root())
        try:
            if sourcemod.get_source(conn, source_id) is None:
                click.echo(f"error: unknown source {source_id!r} (run `leadhs source load` first)", err=True)
                ctx.exit(1)
            parameters = {"url": url, "mode": "probe-url"}
            run_id, run_key, _ = probeengine._insert_run(conn, "probe", source_id, "probeurl", parameters)
            probeengine._insert_probe_run(conn, run_id, "census")
            if summary.get("error"):
                finding = FindingDraft(
                    metric_code="access_blocked", method_code="manual",
                    value_text=f"{summary['error']}: {summary['detail']}",
                    notes="probe url ballpark",
                )
                run_status, notes = ("failed" if summary["error"] in ("ProbeNetworkError", "RateLimited") else "blocked"), None
            else:
                finding = FindingDraft(
                    metric_code="format", method_code="manual",
                    value_text=(
                        f"{summary['content_type'] or '?'}; {summary['size']:,} bytes; robots {summary['robots']}"
                    ),
                    notes="probe url ballpark (rs5)",
                )
                run_status, notes = "done", None
            probeengine.persist(conn, store, source_id, run_id, ProbeResult(findings=[finding]))
            probeengine._finish_run(conn, run_id, run_status, dbmod.utcnow(), notes)
            conn.commit()
            click.echo(f"recorded: {run_key} metric={'access_blocked' if summary.get('error') else 'format'}")
            exit_code = exit_code or (2 if run_status != "done" else 0)
        finally:
            conn.close()
    if exit_code:
        ctx.exit(exit_code)


@raw.command()
@click.argument("source_id")
@click.option("--url", "url", default=None, help="delivery URL (default: the register's export_url)")
@click.option("--instructions-dir", "instructions_dir", default=None,
              help="draft destination (default: raw_sources/)")
@click.pass_context
def scan(ctx, source_id, url, instructions_dir):
    """Profile a live delivery → draft instruction (never writes DB)."""
    from . import db as dbmod, fetch as fetchmod, source as sourcemod
    from .fetch import FetchConfig
    from .raw import scanner as scannermod
    from .raw.instructions import InstructionError as instructions_error
    from .raw.instructions import canonical_json

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path)
    try:
        source = sourcemod.get_source(conn, source_id)
        if source is None:
            click.echo(f"error: unknown source {source_id!r} (run `leadhs source load` first)", err=True)
            ctx.exit(1)
        url = url or source.export_url
        if not url:
            click.echo(f"error: no URL — pass --url or set export_url for {source_id} in the register CSV", err=True)
            ctx.exit(1)
        fetcher = fetchmod.Fetcher(FetchConfig(contact=rt.contact), logger=rt.logger)
        try:
            profile = scannermod.scan_delivery(fetcher, source, url)
        except fetchmod.FetchError as exc:
            click.echo(f"error: scan failed — {exc}", err=True)
            ctx.exit(2)
        except scannermod.ScanError as exc:
            click.echo(f"error: {exc}", err=True)
            ctx.exit(2)
        table_name = scannermod.resolve_table_name(conn, source_id)
        draft = scannermod.draft_instruction(profile, source, table_name=table_name)
        click.echo(
            f"{source_id}: {profile.export_kind} {profile.record_count:,} records, "
            f"{len(profile.columns)} columns, content-type {profile.content_type or '?'}, "
            f"size {profile.size_bytes:,} B" if profile.size_bytes else
            f"{source_id}: {profile.export_kind} {profile.record_count:,} records, {len(profile.columns)} columns"
        )
        if profile.record_count == 0:
            click.echo("warning: delivery counted 0 records", err=True)
        if profile.robots_policy != "allow-all (404/empty)" or profile.crawl_delay:
            click.echo(f"robots: {profile.robots_policy}" + (f", crawl-delay {profile.crawl_delay}s" if profile.crawl_delay else ""))
        click.echo(f"columns: {', '.join(c['column'] + ('*' if c['column'] in profile.natural_key else '') for c in profile.columns)}")
        if profile.key_note:
            click.echo(f"key: {profile.key_note}")
        drift = scannermod.drift_line(conn, source_id, draft["records"]["expected_count"])
        if drift:
            click.echo(drift)
        try:
            payload = scannermod.draft_bytes(draft)
            valid = True
        except instructions_error as exc:
            # a draft the human must complete (e.g. no natural key found)
            # is still written — canonical, loudly flagged; raw run
            # refuses it until edited (fail-closed stays intact)
            payload = canonical_json(draft)
            valid = False
            click.echo(f"warning: draft is INCOMPLETE ({exc}) — edit it before raw run", err=True)
        directory = instructions_dir or "raw_sources"
        path = _instruction_path(source_id, directory)
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(payload)
        import hashlib

        click.echo(f"draft: {path} (manifest_hash {hashlib.sha256(payload).hexdigest()[:16]}…)")
        if valid:
            click.echo("review the draft before `raw run` — nothing flows before approval")
        else:
            click.echo("review + complete the draft before `raw run` — the run refuses it as-is", err=True)
    finally:
        conn.close()


@raw.command("status")
@click.argument("source_id", required=False)
@click.pass_context
def status(ctx, source_id):
    """Raw-layer coverage: rows, runs, journal, checkpoints, drift."""
    import json as _json

    from . import db as dbmod
    from .raw import instructions as instructionsmod

    rt = _runtime(ctx)
    _ensure_initialized(ctx, rt)
    conn = dbmod.connect(rt.db_path, readonly=True)
    try:
        profiles = conn.execute(
            "SELECT * FROM raw_source_profile WHERE source_id = ? ORDER BY source_id" if source_id
            else "SELECT * FROM raw_source_profile ORDER BY source_id",
            (source_id,) if source_id else (),
        ).fetchall()
        if not profiles:
            where = f" for {source_id}" if source_id else ""
            click.echo(f"(no raw sources{where} — `raw scan` + `raw run` first)")
            return
        for prof in profiles:
            sid, table = prof["source_id"], prof["table_name"]
            rows = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            truncated = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE _truncated = 1").fetchone()[0]
            changed = conn.execute("SELECT COUNT(*) FROM raw_change WHERE source_id = ?", (sid,)).fetchone()[0]
            runs = conn.execute(
                "SELECT run_key, status_code, started_at, finished_at, parameters_json FROM run "
                "WHERE source_id = ? AND kind_code = 'acquire' ORDER BY id DESC LIMIT 1",
                (sid,),
            ).fetchone()
            click.echo(f"{sid}  table={table} rows={rows:,} truncated={truncated:,} changed={changed:,}")
            if runs:
                params = _json.loads(runs["parameters_json"] or "{}")
                cursor = params.get("cursor")
                state = "complete" if params.get("complete") else ("checkpoint: " + _json.dumps(cursor) if cursor else "no checkpoint")
                click.echo(
                    f"  last run: {runs['run_key']} {runs['status_code']} started {runs['started_at']}"
                    + (f" finished {runs['finished_at']}" if runs["finished_at"] else "")
                    + f" — {state}"
                )
            expected = None
            try:
                inst, _h = instructionsmod.load(_instruction_path(sid, None))
                expected = inst.records["expected_count"]
            except (instructionsmod.InstructionError, OSError):
                pass
            if expected is None:
                click.echo("  coverage: rows=%s vs expected=unknown (no instruction file)" % f"{rows:,}")
            elif rows == expected:
                click.echo(f"  coverage: {rows:,} / {expected:,} — exact")
            else:
                click.echo(f"  coverage: {rows:,} / {expected:,} — DRIFT {rows - expected:+,}")
    finally:
        conn.close()


@raw.command()
@click.argument("source_id", required=False)
@click.option("--all", "all_sources", is_flag=True, help="run every instruction in the instructions dir")
@click.option("--instructions-dir", "instructions_dir", default=None,
              help="instructions directory (default: raw_sources/)")
@click.option("--cap", "cap", type=int, default=None, help="stop after N records (tests)")
@click.option("--dry-run", "dry_run", is_flag=True, help="plan the run; zero network, zero DB writes")
@click.option("--resume", "resume", is_flag=True, help="continue from the persisted checkpoint")
@click.option("--workers", "workers", type=click.IntRange(min=1), default=1, show_default=True,
              help="concurrent page fetches (starts stay politeness-spaced)")
@click.option("--batch", "batch", type=click.IntRange(min=1), default=500, show_default=True,
              help="records per checkpoint commit")
@click.pass_context
def run(ctx, source_id, all_sources, instructions_dir, cap, dry_run, resume, workers, batch):
    """Init + seed per instruction: register the source, create the raw
    table, bulk-load every record verbatim (upsert + change journal,
    checkpoints). Exit 2 on partial seed (checkpoint kept)."""
    from .raw import interpreter as interp
    from .raw import instructions as instructionsmod

    rt = _runtime(ctx)
    if bool(source_id) == bool(all_sources):
        click.echo("error: give SOURCE_ID or --all (not both)", err=True)
        ctx.exit(1)
    directory = instructions_dir or "raw_sources"
    if all_sources:
        import glob as _glob

        paths = sorted(_glob.glob(os.path.join(directory, "*.instruction.json")))
        if not paths:
            click.echo(f"error: no instruction files in {directory}/", err=True)
            ctx.exit(1)
        wanted = [os.path.basename(p).split(".")[0] for p in paths]
    else:
        wanted = [source_id]

    # dry-run: pure plan, zero DB writes (house dry-run discipline)
    if dry_run:
        for sid in wanted:
            path = _instruction_path(sid, directory)
            try:
                inst, manifest_hash = instructionsmod.load(path)
            except instructionsmod.InstructionError as exc:
                click.echo(f"error: {exc}", err=True)
                ctx.exit(1)
            if inst.export_kind in instructionsmod.RESERVED_EXPORT_KINDS:
                click.echo(f"error: {sid}: export_kind {inst.export_kind!r} is reserved — not interpreted", err=True)
                ctx.exit(1)
            pages = "single request" if inst.pagination.kind == "single" else (
                f"pages of {inst.pagination.page_size} via {inst.pagination.page_param}"
                + (f", max {inst.pagination.max_pages}" if inst.pagination.max_pages else "")
            )
            click.echo(
                f"{sid}: would fetch {inst.list_url} ({pages}); politeness delay "
                f"{inst.politeness.delay_seconds}s, budget {inst.politeness.request_budget_per_run} "
                f"requests; upsert into {inst.table_name or 'raw_' + sid.lower().replace('-', '')} "
                f"(manifest {manifest_hash[:16]}…)"
            )
        click.echo("dry-run: planned; zero network, zero DB writes")
        return

    _ensure_initialized(ctx, rt)
    from . import db as dbmod, fetch as fetchmod
    from .fetch import Blocked, FetchConfig, FetchError, ProbeNetworkError, RateLimited, RobotsDisallowed

    conn = dbmod.connect(rt.db_path)

    def finalize(run_id, status_code, notes):
        probeengine._finish_run(conn, run_id, status_code, dbmod.utcnow(), notes)
        conn.commit()

    def run_one(sid) -> int:
        path = _instruction_path(sid, directory)
        try:
            inst, manifest_hash = instructionsmod.load(path)
        except instructionsmod.InstructionError as exc:
            click.echo(f"error: {exc}", err=True)
            return 1
        if inst.export_kind in instructionsmod.RESERVED_EXPORT_KINDS:
            click.echo(f"error: {sid}: export_kind {inst.export_kind!r} is reserved — not interpreted", err=True)
            return 1
        unfinished = interp.find_unfinished_run(conn, sid)
        if unfinished is not None and not resume:
            cursor = json.loads(unfinished["parameters_json"] or "{}").get("cursor")
            click.echo(
                f"error: {sid}: unfinished checkpoint in {unfinished['run_key']} "
                f"(cursor {json.dumps(cursor)}) — rerun with --resume to continue it",
                err=True,
            )
            return 1

        warnings = interp.ensure_source_row(conn, inst)
        table_name = interp.resolve_table(conn, inst)
        created = interp.ensure_table(conn, inst, table_name)
        interp.ensure_profile_row(conn, inst, table_name)
        for line in warnings:
            click.echo(f"warning: {line}", err=True)
        if created:
            click.echo(f"created table {table_name} from the instruction columns")
        elif not inst.table_name:
            click.echo(f"note: no table_name in the instruction — derived {table_name}")

        run_workers = workers if inst.pagination.kind in ("page_param", "offset") else 1
        if unfinished is not None and resume:
            run_id, run_key = unfinished["id"], unfinished["run_key"]
            conn.execute(
                "UPDATE run SET status_code = 'running', finished_at = NULL, "
                "notes = COALESCE(notes || '; ', '') || 'resumed' WHERE id = ?",
                (run_id,),
            )
            conn.commit()
        else:
            from . import ids as idsmod

            parameters = {
                "instruction_hash": manifest_hash, "table": table_name,
                "cursor": None, "complete": False,
                "workers": run_workers, "cap": cap,
            }
            run_id, run_key, _started = probeengine._insert_run(
                conn, "acquire", sid, idsmod.slug_for_source(sid) + "raw", parameters,
            )
            conn.commit()
        click.echo(f"{sid}: {run_key} seeding {table_name} (workers={run_workers}, batch={batch})")

        fetcher = fetchmod.Fetcher(
            FetchConfig(contact=rt.contact, min_spacing=inst.politeness.delay_seconds),
            logger=rt.logger,
        )
        try:
            stats = interp.seed(conn, fetcher, inst, run_id, table_name, cap=cap,
                                workers=run_workers, batch=batch)
        except KeyboardInterrupt:
            state = interp._load_cursor(conn, run_id)
            finalize(run_id, "aborted", f"interrupted at record {state.get('records', 0)}; checkpoint kept")
            raise
        except interp.BudgetExhausted as exc:
            finalize(run_id, "blocked", exc.args[0])
            click.echo(f"{sid}: {run_key} blocked — {exc}", err=True)
            return 2
        except FetchError as exc:
            status_code = "blocked" if isinstance(exc, (Blocked, RateLimited, RobotsDisallowed)) else "failed"
            finalize(run_id, status_code, f"{type(exc).__name__}: {exc}; checkpoint kept")
            click.echo(f"{sid}: {run_key} {status_code} — {exc}", err=True)
            return 2
        except (interp.InterpreterError, json.JSONDecodeError) as exc:
            finalize(run_id, "failed", f"{type(exc).__name__}: {exc}; checkpoint kept")
            click.echo(f"{sid}: {run_key} failed — {exc}", err=True)
            return 2
        summary = (
            f"inserted={stats.inserted} updated={stats.updated} skipped={stats.skipped} "
            f"truncated={stats.truncated} fetches={stats.fetches}"
            + (f" ragged={stats.ragged}" if stats.ragged else "")
        )
        finalize(run_id, "done", summary + (f"; notes: {'; '.join(stats.notes)}" if stats.notes else ""))
        click.echo(f"{sid}: {run_key} done — {summary}")
        return 0

    try:
        probeengine = _import_probeengine()
        exit_code = 0
        for sid in wanted:
            code = run_one(sid)
            exit_code = max(exit_code, code)
        if exit_code:
            ctx.exit(exit_code)
    finally:
        conn.close()


def _import_probeengine():
    from .probe import engine as probeengine

    return probeengine


cli.add_command(db)
cli.add_command(source)
cli.add_command(probe)
cli.add_command(raw)
cli.add_command(identity)
cli.add_command(doctor)


def _ensure_initialized(ctx: click.Context, rt: Runtime) -> None:
    """Guided-error preflight (i11): the DB must exist, be non-empty and
    carry the schema_version table — checked read-only (mode=ro URI
    never creates the file), BEFORE any connect() could create one."""
    import sqlite3

    ok = False
    if os.path.isfile(rt.db_path) and os.path.getsize(rt.db_path) > 0:
        conn = None
        try:
            conn = sqlite3.connect(f"file:{os.path.abspath(rt.db_path)}?mode=ro", uri=True)
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            ).fetchone()
            ok = row is not None
        except sqlite3.Error:
            ok = False
        finally:
            if conn is not None:
                conn.close()
    if not ok:
        click.echo(
            "error: database not initialized — run `make setup` (repo) or "
            "`leadhs db init` then `leadhs source load` first",
            err=True,
        )
        ctx.exit(1)


def main() -> int:
    try:
        result = cli(standalone_mode=False)
    except NoArgsIsHelpError as exc:
        click.echo(exc.format_message())
        return 0
    except Exit as exc:
        return exc.exit_code
    except Abort:
        click.echo("interrupted", err=True)
        return 130
    except KeyboardInterrupt:
        click.echo("interrupted", err=True)
        return 130
    except UsageError as exc:
        exc.show()
        return 1
    except click.ClickException as exc:
        exc.show()
        return exc.exit_code
    except Exception as exc:  # anything else is a bug (fail loudly)
        if os.environ.get("LEADHS_DEBUG"):
            raise
        click.echo(f"bug: {exc}", err=True)
        return 1
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    sys.exit(main())

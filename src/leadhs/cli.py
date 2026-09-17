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


cli.add_command(db)
cli.add_command(source)
cli.add_command(probe)
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

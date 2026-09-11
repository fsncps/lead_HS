"""click entrypoint: db, source, probe, doctor groups.

Exit-code convention (i1): 0 success; 1 usage/data error; 2 an
operation ran but ended failed/blocked (findings recorded);
3 audit found violations; 130 on KeyboardInterrupt.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional

import click

from . import __version__
from .logutil import configure_logging


@dataclass
class Runtime:
    db_path: str = "data/leadhs.sqlite"
    contact: Optional[str] = None
    verbose: bool = False
    logger: object = None

    def store_root(self) -> str:
        import os

        return os.path.join(os.path.dirname(os.path.abspath(self.db_path)), "raw")


def _runtime(ctx: click.Context) -> Runtime:
    return ctx.obj


@click.group()
@click.version_option(__version__)
@click.option("--verbose", is_flag=True, help="structured log lines")
@click.option("--db", "db_path", default="data/leadhs.sqlite", show_default=True, help="SQLite database path")
@click.option("--contact", envvar="LEADHS_CONTACT", default=None, help="user-agent contact (doctor warns when unset)")
@click.pass_context
def cli(ctx, verbose, db_path, contact):
    """leadhs — lead-in-paints evidence tool (HS 3208/3209/3213)."""
    ctx.obj = Runtime(db_path=db_path, contact=contact, verbose=verbose, logger=configure_logging(verbose))


@click.group()
def db():
    """Database: migrate, status, audit."""


@click.group()
def source():
    """Source register."""


@click.group()
def probe():
    """Probe runs and reports."""


@click.command()
@click.option("--net", is_flag=True, help="check reachability of seeded sources")
@click.option("--no-net", is_flag=True, default=True, help="skip reachability (default)")
@click.pass_context
def doctor(ctx, net, no_net):
    """Environment preflight (python, sqlite, binaries, data dir, contact)."""
    from . import doctor as doctormod

    rt = _runtime(ctx)
    ctx.exit(doctormod.main(rt, net=net or not no_net))


# --- db -------------------------------------------------------------


@db.command()
@click.option("--no-backup", is_flag=True, help="skip the timestamped backup of an existing DB")
@click.pass_context
def init(ctx, no_backup):
    """Apply pending migrations (0001–0002 in this unit)."""
    from . import db as dbmod

    rt = _runtime(ctx)
    os_parent = __import__("os").path.dirname(rt.db_path)
    __import__("os").makedirs(os_parent, exist_ok=True) if os_parent else None
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


@source.command()
@click.option("--class", "class_code", type=click.Choice(["CS", "PE", "LG", "ST", "LI"]), default=None)
@click.pass_context
def list_(ctx, class_code):
    """List sources (optionally one class)."""
    from . import db as dbmod, source as sourcemod

    rt = _runtime(ctx)
    conn = dbmod.connect(rt.db_path)
    try:
        sourcemod.list_(conn, class_code)
    finally:
        conn.close()


@probe.command()
@click.option("--source", "source_id", default=None, help="source ID (CS-1)")
@click.option("--all", "all_sources", is_flag=True, help="run every active adapter-backed source")
@click.option("--mode", "mode", type=click.Choice(["census", "format_check", "access_check"]), default="census")
@click.option("--sample", "sample_n", type=int, default=5, help="PE sample-page count")
@click.option("--dry-run", is_flag=True, help="plan requests; zero network calls")
@click.pass_context
def run(ctx, source_id, all_sources, mode, sample_n, dry_run):
    """One probe run per source; exit 2 when any run ended blocked/failed."""
    from . import db as dbmod, fetch as fetchmod, store as storemod
    from . import source as sourcemod
    from .fetch import FetchConfig
    from .probe import engine as probeengine

    rt = _runtime(ctx)
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
            summaries, exit_code = probeengine.run_all(conn, store, fetcher, mode=mode, sample_n=sample_n, dry_run=dry_run, logger=rt.logger)
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


@probe.command()
@click.option("--source", "source_id", required=True, help="source ID (ST-1 for PCN)")
@click.option("--metric", "metric", required=True, help="metric code from the vocabulary")
@click.option("--value", "value", default=None, help="numeric value (numeric metrics)")
@click.option("--value-text", "value_text", default=None, help="text value (text metrics)")
@click.option("--unit", "unit", default=None, help="quantity_unit code")
@click.option("--url", "url", default=None, help="provenance URL")
@click.option("--document", "document_file", default=None, type=click.Path(exists=True), help="raw file to attach")
@click.option("--note", "note", default=None, help="note")
@click.pass_context
def record(ctx, source_id, metric, value, value_text, unit, url, document_file, note):
    """Create a manual probe run + one finding (method=manual; ST-1 PCN path)."""
    from . import db as dbmod, store as storemod
    from .probe import engine as probeengine

    rt = _runtime(ctx)
    conn = dbmod.connect(rt.db_path)
    store = storemod.RawStore(rt.store_root())
    try:
        summary = probeengine.record_manual(
            conn, store, source_id, metric, value=value, value_text=value_text,
            unit=unit, url=url, document_file=document_file, note=note, logger=rt.logger, contact=rt.contact,
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
@click.pass_context
def report(ctx, source_id, fmt, out_path):
    """Render the census report from the views (md/csv/json)."""
    from . import db as dbmod, report as reportmod

    rt = _runtime(ctx)
    conn = dbmod.connect(rt.db_path)
    try:
        output = reportmod.render(conn, format=fmt, source_id=source_id)
    finally:
        conn.close()
    if out_path:
        import os

        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(output)
        click.echo(f"wrote {out_path}")
    else:
        click.echo(output)


cli.add_command(db)
cli.add_command(source)
cli.add_command(probe)
cli.add_command(doctor)
# list_ has a reserved-name clash with builtins under click; expose as 'list'
source.add_command(list_, name="list")


def main():
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("interrupted", err=True)
        sys.exit(130)
    except click.ClickException:
        raise
    except Exception as exc:  # anything else propagates as a bug (fail loudly)
        click.echo(f"bug: {exc}", err=True)
        if __import__("os").environ.get("LEADHS_DEBUG"):
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()

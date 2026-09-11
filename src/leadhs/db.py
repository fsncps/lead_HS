"""Database access: connect, forward-only migrate (a8), status,
audit rules R1–R9 (i5), stale-run reclaim (a11). One connection per
command; WAL, foreign_keys=ON, busy_timeout=5000.
"""

from __future__ import annotations

import datetime
import importlib.resources
import os
import re
import sqlite3
from typing import Iterable, Optional

_MIGRATION_RE = re.compile(r"^(\d{4})__(.+)\.sql$")


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def migration_files() -> list:
    """(number, name, sql) sorted by number, from the package resources."""
    files = []
    for entry in importlib.resources.files("leadhs").joinpath("migrations").iterdir():
        m = _MIGRATION_RE.match(entry.name)
        if m:
            files.append((int(m.group(1)), entry.name, entry.read_text()))
    return sorted(files)


def connect(path: str, readonly: bool = False) -> sqlite3.Connection:
    if readonly:
        uri = f"file:{os.path.abspath(path)}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.execute("PRAGMA query_only=ON")
    else:
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def _backup_dir(db_path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(db_path)), "backups")


def take_backup(conn: sqlite3.Connection, db_path: str) -> str:
    """Timestamped consistent snapshot via VACUUM INTO (PHASE02)."""
    backup_dir = _backup_dir(db_path)
    os.makedirs(backup_dir, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
    target = os.path.join(backup_dir, f"{os.path.basename(db_path)}-{stamp}.sqlite")
    conn.execute("VACUUM INTO ?", (target,))
    return target


def migrate(conn: sqlite3.Connection, backup: bool = True, db_path: Optional[str] = None) -> tuple:
    """Apply pending migrations in order, one transaction each.

    Returns (applied_names, pending_names). Idempotent via
    schema_version. A timestamped backup is taken before applying when
    an existing, non-empty DB is being upgraded (a8; skip with
    --no-backup).
    """
    preexisting = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchone()[0] > 0
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)")
    applied = {row[0] for row in conn.execute("SELECT version FROM schema_version")}
    files = migration_files()
    pending = [f for f in files if f[0] not in applied]

    if pending and backup and db_path and preexisting:
        try:
            take_backup(conn, db_path)
        except sqlite3.Error:
            pass

    if not pending:
        return [], []

    # autocommit mode: executescript() implicitly commits any pending
    # module transaction, so the BEGIN/COMMIT live inside the script —
    # each migration applies in exactly one transaction
    conn.isolation_level = None
    applied_now = []
    for number, name, sql in pending:
        stamp = utcnow()
        # number/name/stamp come from the packaged migration files and
        # the clock — runner metadata, not evidence (P4 applies to
        # evidence values; nothing user-controlled is interpolated)
        script = (
            "BEGIN;\n"
            + sql
            + f"\nINSERT INTO schema_version (version, name, applied_at) VALUES ({number}, '{name}', '{stamp}');\n"
            + "COMMIT;\n"
        )
        try:
            conn.executescript(script)
        except sqlite3.Error:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        applied_now.append(name)
    conn.isolation_level = ""

    remaining = [f[1] for f in files if f[0] not in {r[0] for r in conn.execute("SELECT version FROM schema_version")}]
    return applied_now, remaining


def stale_run_reclaim(conn: sqlite3.Connection, now: Optional[str] = None) -> int:
    """Mark `running` runs left by a hard crash as failed (a11).

    Threshold: started_at older than 1 h (or older than the current
    process). Returns the number of runs reclaimed.
    """
    now = now or utcnow()
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = conn.execute(
        "SELECT id FROM run WHERE status_code='running' AND started_at < ?", (cutoff,)
    ).fetchall()
    for row in rows:
        conn.execute(
            "UPDATE run SET status_code='failed', finished_at=?, notes=COALESCE(notes||'; ', '')||'stale run reclaimed' WHERE id=?",
            (now, row[0]),
        )
    return len(rows)


def status(conn: sqlite3.Connection) -> None:
    files = migration_files()
    applied = {r[0]: r[1] for r in conn.execute("SELECT version, name FROM schema_version")}
    print("applied migrations:")
    for number, name in sorted(applied.items()):
        print(f"  {number:04d} {name}")
    print("pending:")
    pending = [name for number, name, _ in files if number not in applied]
    print("  " + ", ".join(pending) if pending else "  (none)")
    print("tables:")
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    for table in tables:
        if table in ("schema_version", "sqlite_sequence"):
            continue
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")


def audit(conn: sqlite3.Connection, store, unreferenced: bool = False) -> list:
    """Provenance rules R1–R9; returns a list of violation lines.

    Empty list = clean (exit 0); non-empty = exit 3.
    """
    violations: list[str] = []

    # R7 first: foreign_key_check must be empty
    for row in conn.execute("PRAGMA foreign_key_check"):
        violations.append(f"R7: foreign key violation in {row[0]} (rowid {row[1]})")

    # R1: every probe_finding joins a probe_run whose run.source_id is set
    for row in conn.execute(
        """
        SELECT pf.id FROM probe_finding pf
        JOIN run r ON r.id = pf.run_id
        LEFT JOIN probe_run pr ON pr.run_id = r.id
        WHERE r.kind_code != 'probe' OR r.source_id IS NULL OR pr.run_id IS NULL
        """
    ):
        violations.append(f"R1: probe_finding {row[0]} not bound to a per-source probe run")

    # R2: document source_id + retrieved_at (NOT NULL by schema);
    #     archived => raw_hash present AND file exists in store
    for row in conn.execute(
        "SELECT id, status_code, raw_hash, url FROM document WHERE source_id IS NULL OR retrieved_at IS NULL"
    ):
        violations.append(f"R2: document {row[0]} missing source_id/retrieved_at")
    for row in conn.execute(
        "SELECT id, raw_hash FROM document WHERE status_code='archived'"
    ):
        if not row[1] or not store.verify(row[1]):
            violations.append(f"R2: document {row[0]} archived but raw file missing/unverified")

    # R3: finding document_id resolves and the referenced file exists
    for row in conn.execute(
        """
        SELECT pf.id, d.id, d.raw_hash FROM probe_finding pf
        LEFT JOIN document d ON d.id = pf.document_id
        WHERE pf.document_id IS NOT NULL AND d.id IS NULL
        """
    ):
        violations.append(f"R3: probe_finding {row[0]} references missing document {row[1]}")
    for row in conn.execute(
        """
        SELECT pf.id, d.raw_hash FROM probe_finding pf
        JOIN document d ON d.id = pf.document_id
        WHERE d.raw_hash IS NOT NULL
        """
    ):
        if not store.verify(row[1]):
            violations.append(f"R3: probe_finding {row[0]} document file missing ({row[1]})")

    # R4: value presence matches probe_metric.value_type
    for row in conn.execute(
        """
        SELECT pf.id, pf.metric_code, pm.value_type, pf.value_numeric, pf.value_text
        FROM probe_finding pf JOIN probe_metric pm ON pm.code = pf.metric_code
        """
    ):
        vt, vn, vt_ = row[2], row[3], row[4]
        if vt == "numeric" and (vn is None or vt_ is not None):
            violations.append(f"R4: probe_finding {row[0]} metric {row[1]} numeric but value missing/mismatched")
        if vt == "text" and (vt_ is None or vn is not None):
            violations.append(f"R4: probe_finding {row[0]} metric {row[1]} text but value missing/mismatched")

    # R5: finished runs have finished_at; failed/blocked/aborted carry notes
    for row in conn.execute(
        "SELECT id, run_key, status_code, finished_at, notes FROM run"
    ):
        rid, key, status_code, finished, notes = row
        if status_code in ("done", "failed", "blocked", "aborted") and not finished:
            violations.append(f"R5: run {rid} ({key}) finished status '{status_code}' without finished_at")
        if status_code in ("failed", "blocked", "aborted") and not notes:
            violations.append(f"R5: run {rid} ({key}) status '{status_code}' without notes")

    # R6: run_key present, unique (schema), well-formed
    for row in conn.execute("SELECT id, run_key FROM run WHERE run_key IS NULL OR run_key NOT GLOB '[a-z]*-[0-9]*-*'"):
        violations.append(f"R6: run {row[0]} malformed run_key '{row[1]}'")

    # R9: no evidence rows outside a run of the right kind
    for row in conn.execute(
        """
        SELECT pf.id FROM probe_finding pf
        JOIN run r ON r.id = pf.run_id WHERE r.kind_code != 'probe'
        """
    ):
        violations.append(f"R9: probe_finding {row[0]} under non-probe run")

    # R8 (--unreferenced): raw-store files without a document row
    if unreferenced:
        known = {r[0] for r in conn.execute("SELECT raw_hash FROM document WHERE raw_hash IS NOT NULL")}
        for path in store.orphans(known):
            violations.append(f"R8: orphan raw file {path}")

    return violations
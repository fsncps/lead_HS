"""identity resolve + rebuild (v0.3.4 r01) — the PHASE01 data flow:
adapter → election → match-or-create over the in-memory normalized-key
index (il13) → batched BEGIN IMMEDIATE writes → raw back-links by
rowid → identity_state consumes the manifest hash → the run row carries
per-source counts. Idempotent: a re-run over unchanged raw state
creates nothing (index hit); Ctrl-C keeps committed batches and marks
the run aborted (il5) — the re-run redoes the source from zero and
reconciles. ``--dry-run`` runs the identical read path and writes
nothing but its own run row (d25 convention).
"""

from __future__ import annotations

import json
import sqlite3

from .. import db as dbmod
from .. import ids as idsmod
from .. import normalize as normmod
from . import NAMESPACE, DOMAIN_MFR, DOMAIN_PROD, uuid_for
from . import spec
from .adapters import ADAPTERS
from .errors import (
    BackupError,
    EmptyNormError,
    ManifestDriftError,
    NormalizeError,
    SourceMissingError,
)

BATCH_RECORDS = 500


def _profile(conn, source_id):
    row = conn.execute(
        "SELECT table_name, manifest_hash FROM raw_source_profile WHERE source_id = ?",
        (source_id,),
    ).fetchone()
    if row is None:
        raise SourceMissingError(
            f"{source_id}: no raw source profile — `raw scan` + `raw run` first"
        )
    return row["table_name"], row["manifest_hash"]


def _state(conn, source_id):
    return conn.execute(
        "SELECT manifest_hash, resolved_run_id FROM identity_state WHERE source_id = ?",
        (source_id,),
    ).fetchone()


class _Index:
    """In-memory normalized-key index (il13): bulk-loaded at run start,
    write-through on create — match-or-create never touches the DB for
    an existing key."""

    def __init__(self, conn):
        self.mfr = {
            r[0]: r[1]
            for r in conn.execute("SELECT name_norm, uuid FROM manufacturer")
        }
        self.prod = {
            r[0]: (r[1], r[2])
            for r in conn.execute(
                "SELECT ident_string, uuid, manufacturer_uuid FROM product"
            )
        }


def _resolve_one(conn, source_id, run_id, dry_run, batch) -> dict:
    table, manifest_hash = _profile(conn, source_id)
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (table,)
    ).fetchone()
    if not exists:
        raise SourceMissingError(f"{source_id}: raw table {table} does not exist")
    prior = _state(conn, source_id)
    if prior is not None and prior["manifest_hash"] != manifest_hash:
        raise ManifestDriftError(
            f"{source_id}: raw table re-acquired after the last resolve "
            f"(state {prior['manifest_hash'][:12]}… != profile "
            f"{manifest_hash[:12]}…) — run `leadhs identity rebuild`"
        )

    adapter = ADAPTERS[source_id]
    groups = adapter(conn, table)
    index = _Index(conn)

    counts = {
        "rows": sum(len(g.rowids) for g in groups),
        "groups": len(groups),
        "created_mfr": 0,
        "created_prod": 0,
        "linked": 0,
        "skipped": 0,
        "refused": 0,
        "multi_gtin": 0,
        "multi_code": 0,
        "name_basis": 0,
    }

    if not dry_run:
        spec.ensure_backlink_column(conn, table)

    mfr_rows, prod_rows, link_rows = [], [], []

    def flush():
        if dry_run or not (mfr_rows or prod_rows or link_rows):
            return
        conn.execute("BEGIN IMMEDIATE")
        if mfr_rows:
            conn.executemany(
                "INSERT INTO manufacturer (uuid, name_norm, name, country, city, vat_id, created_run_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                mfr_rows,
            )
        if prod_rows:
            conn.executemany(
                "INSERT INTO product (uuid, ident_string, ident_nr, manufacturer_uuid, hs_code, eu_group, name, brand, url, created_run_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                prod_rows,
            )
        if link_rows:
            conn.executemany(
                f'UPDATE "{table}" SET product_uuid = ? WHERE rowid = ?',
                link_rows,
            )
        conn.commit()
        mfr_rows.clear()
        prod_rows.clear()
        link_rows.clear()

    for group in groups:
        mfr_norm = normmod.norm_manufacturer(group.mfr_name)
        if not mfr_norm:
            counts["skipped"] += 1
            counts["refused"] += len(group.rowids)
            continue
        name_norm = normmod.norm_name(group.name) if group.name else ""
        try:
            elected = _elect_counted(group, mfr_norm, name_norm, counts)
        except EmptyNormError:
            counts["skipped"] += 1
            continue
        if elected is None:
            counts["skipped"] += 1
            continue

        mfr_uuid = index.mfr.get(mfr_norm)
        if mfr_uuid is None:
            mfr_uuid = uuid_for(DOMAIN_MFR, mfr_norm)
            index.mfr[mfr_norm] = mfr_uuid
            counts["created_mfr"] += 1
            mfr_rows.append(
                (mfr_uuid, mfr_norm, group.mfr_name, group.mfr_country,
                 group.mfr_city, group.mfr_vat, run_id)
            )
        prod_uuid, known_mfr = index.prod.get(elected.ident_string, (None, None))
        if prod_uuid is None:
            prod_uuid = uuid_for(DOMAIN_PROD, elected.ident_string)
            index.prod[elected.ident_string] = (prod_uuid, mfr_uuid)
            counts["created_prod"] += 1
            prod_rows.append(
                (prod_uuid, elected.ident_string, elected.ident_nr, mfr_uuid,
                 None, group.eu_group, group.name, group.brand, group.url, run_id)
            )
        for rid in group.rowids:
            link_rows.append((prod_uuid, rid))
            counts["linked"] += 1
        if len(mfr_rows) + len(prod_rows) + len(link_rows) >= batch:
            flush()

    flush()

    if not dry_run:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO identity_state (source_id, manifest_hash, resolved_run_id) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT (source_id) DO UPDATE SET manifest_hash = excluded.manifest_hash, "
            "resolved_run_id = excluded.resolved_run_id",
            (source_id, manifest_hash, run_id),
        )
        conn.commit()
    return counts


def _elect_counted(group, mfr_norm, name_norm, counts):
    """Election with the il3/il17 refusal counting folded in: bad GTIN
    codes are dropped from the group's code list (counted) before the
    election; a group left keyless raises EmptyNormError (caller
    skips), a keyless-but-nameless group returns None."""
    usable = []
    for code_type, code_value in group.codes:
        try:
            klass, value = _norm_code_checked(code_type, code_value)
        except ValueError:
            counts["refused"] += 1
            continue
        if klass:
            usable.append((klass, value))
    saved = group.codes
    group.codes = usable
    try:
        elected = _elect_impl(group, mfr_norm, name_norm)
    finally:
        group.codes = saved
    if elected is not None:
        if elected.multi_gtin:
            counts["multi_gtin"] += 1
        if elected.multi_code:
            counts["multi_code"] += 1
        if elected.basis == "name":
            counts["name_basis"] += 1
    return elected


def _norm_code_checked(code_type, code_value):
    from .adapters import _norm_code

    return _norm_code(code_type, code_value)


def _elect_impl(group, mfr_norm, name_norm):
    from .adapters import elect

    if not name_norm and not any(
        _norm_code_checked(t, v)[0] for t, v in group.codes
    ):
        return None
    return elect(group, mfr_norm, name_norm)


def resolve(conn, source_ids, dry_run=False, batch=BATCH_RECORDS, logger=None) -> list:
    """One identity_resolve run row per source; returns per-source
    summaries. Named errors propagate to the CLI mapping."""
    from ..probe import engine as probeengine

    summaries = []
    for sid in source_ids:
        if sid not in ADAPTERS:
            raise SourceMissingError(
                f"{sid}: no identity adapter (known: {', '.join(sorted(ADAPTERS))})"
            )
        parameters = {"dry_run": dry_run, "batch": batch, "manifest": "consumed"}
        run_id, run_key, _ = probeengine._insert_run(
            conn, "identity_resolve", sid, idsmod.slug_for_source(sid), parameters
        )
        conn.commit()
        counts = {}
        try:
            counts = _resolve_one(conn, sid, run_id, dry_run, batch)
        except KeyboardInterrupt:
            done = {k: v for k, v in counts.items() if k != "rows"}
            probeengine._finish_run(
                conn, run_id, "aborted", dbmod.utcnow(),
                "interrupted; committed batches kept (idempotent re-run, il5); "
                "counts so far: " + json.dumps(done, sort_keys=True),
            )
            conn.commit()
            raise
        note = "dry-run; zero writes (d25)" if dry_run else "; ".join(
            f"{k}={v}" for k, v in counts.items() if k != "rows"
        )
        probeengine._finish_run(
            conn, run_id, "done", dbmod.utcnow(),
            ("dry-run; zero writes" if dry_run else "counts: " + json.dumps(counts, sort_keys=True)),
        )
        conn.commit()
        summaries.append({"source": sid, "run_key": run_key, "dry_run": dry_run, **counts})
    return summaries


def rebuild(conn, db_path, batch=BATCH_RECORDS, logger=None) -> list:
    """Backup → teardown → re-derive ALL sources (il2). Abort before any
    teardown when the backup fails; SQLite >= 3.35 required (DROP COLUMN)."""
    import sqlite3 as _sq

    if not spec.sqlite_version_ok():
        raise BackupError(
            f"identity rebuild needs SQLite >= 3.35 (found {_sq.sqlite_version}) "
            "for ALTER TABLE DROP COLUMN — nothing torn down"
        )
    try:
        backup_path = dbmod.take_backup(conn, db_path)
    except _sq.Error as exc:
        raise BackupError(f"pre-rebuild backup failed — nothing torn down: {exc}") from exc

    conn.execute("BEGIN IMMEDIATE")
    # all four canonical tables are re-created from spec DDLs below, so
    # teardown must drop all four (r02 defect: truncate-instead-of-drop
    # for linkage_candidate/identity_state collided with the CREATEs)
    conn.execute("DROP TABLE IF EXISTS product")
    conn.execute("DROP TABLE IF EXISTS manufacturer")
    conn.execute("DROP TABLE IF EXISTS linkage_candidate")
    conn.execute("DROP TABLE IF EXISTS identity_state")
    for table, has_col in spec.backlink_columns(conn).items():
        if has_col:
            spec.drop_backlink_column(conn, table)
    conn.commit()

    conn.execute(spec.IDENTITY_STATE_DDL)
    conn.execute(spec.MANUFACTURER_DDL)
    conn.execute(spec.PRODUCT_DDL)
    conn.execute(spec.LINKAGE_DDL)
    for ddl in spec._INDEX_DDLS:
        conn.execute(ddl)
    conn.commit()

    summaries = resolve(
        conn, sorted(ADAPTERS), dry_run=False, batch=batch, logger=logger
    )
    for s in summaries:
        s["backup"] = backup_path
    return summaries


def status(conn) -> None:
    """Per-source identity state for the CLI ``identity status`` verb."""
    profiles = conn.execute(
        "SELECT p.source_id, p.table_name, p.manifest_hash AS profile_hash "
        "FROM raw_source_profile p ORDER BY p.source_id"
    ).fetchall()
    if not profiles:
        print("(no raw sources — `raw scan` + `raw run` first)")
        return
    pending = conn.execute(
        "SELECT COUNT(*) FROM linkage_candidate WHERE review_status = 'pending'"
    ).fetchone()[0]
    for prof in profiles:
        sid, table = prof["source_id"], prof["table_name"]
        rows = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        state = conn.execute(
            "SELECT manifest_hash, resolved_run_id FROM identity_state WHERE source_id = ?",
            (sid,),
        ).fetchone()
        linked = 0
        try:
            linked = conn.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE product_uuid IS NOT NULL'
            ).fetchone()[0]
        except sqlite3.OperationalError:
            pass
        if state is None:
            print(f"{sid}  table={table} rows={rows:,}  NOT RESOLVED (`leadhs identity resolve`)")
            continue
        drift = state["manifest_hash"] != prof["profile_hash"]
        run_row = conn.execute(
            "SELECT run_key FROM run WHERE id = ?", (state["resolved_run_id"],)
        ).fetchone()
        print(
            f"{sid}  table={table} rows={rows:,} back-linked={linked:,} "
            f"({(100 * linked / rows if rows else 0):.1f}%)  "
            f"run={run_row[0] if run_row else state['resolved_run_id']}  "
            + ("DRIFT — raw changed after resolve (`identity rebuild`)" if drift else "hash ok")
        )
    print(f"review queue: {pending:,} pending candidates")

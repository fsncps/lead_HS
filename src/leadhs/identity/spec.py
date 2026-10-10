"""Identity-layer schema surface (v0.3.4 r01): DDL constants mirroring
migration 0013 (rebuild re-creates from these), the raw back-link
column ensurer, and the SQLite version pin for DROP COLUMN.

The back-link column is deliberately FK-less: ALTER TABLE ADD COLUMN
cannot carry a FOREIGN KEY clause on an existing table, and the raw
tables already exist — integrity is application level, checked by the
doctor (orphans) while R7 (foreign_key_check) covers the FK-bound
canonical edges (product.manufacturer_uuid).
"""

from __future__ import annotations

import sqlite3

# Mirror of 0013 (CREATE TABLE statements only; run_kind/vocabulary
# inserts and indexes are migration-once content, not rebuild targets).
MANUFACTURER_DDL = """
CREATE TABLE manufacturer (
    uuid TEXT PRIMARY KEY,
    name_norm TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT,
    city TEXT,
    vat_id TEXT,
    created_run_id INTEGER
)
"""

PRODUCT_DDL = """
CREATE TABLE product (
    uuid TEXT PRIMARY KEY,
    ident_string TEXT NOT NULL UNIQUE,
    ident_nr TEXT NOT NULL,
    manufacturer_uuid TEXT NOT NULL REFERENCES manufacturer (uuid) ON DELETE RESTRICT,
    hs_code TEXT,
    eu_group TEXT,
    name TEXT,
    brand TEXT,
    url TEXT,
    created_run_id INTEGER
)
"""

LINKAGE_DDL = """
CREATE TABLE linkage_candidate (
    id INTEGER PRIMARY KEY,
    row_a TEXT NOT NULL,
    row_b TEXT NOT NULL,
    method TEXT NOT NULL,
    score REAL,
    band TEXT,
    verdict TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'pending',
    decided_run_id INTEGER,
    created_run_id INTEGER,
    UNIQUE (row_a, row_b, method)
)
"""

IDENTITY_STATE_DDL = """
CREATE TABLE identity_state (
    source_id TEXT PRIMARY KEY REFERENCES source (id) ON DELETE RESTRICT,
    manifest_hash TEXT NOT NULL,
    resolved_run_id INTEGER NOT NULL
)
"""

_INDEX_DDLS = (
    "CREATE INDEX idx_product_manufacturer ON product (manufacturer_uuid)",
    "CREATE INDEX idx_linkage_candidate_verdict ON linkage_candidate (verdict)",
    "CREATE INDEX idx_linkage_candidate_review ON linkage_candidate (review_status)",
)


def _q(name: str) -> str:
    # Quoted identifier — 2-line helper duplicated from the interpreter
    # on purpose: identity must not grow a code dependency on raw/
    # (data reads only, design coupling rule).
    return chr(34) + name.replace(chr(34), chr(34) * 2) + chr(34)


def sqlite_version_ok() -> bool:
    """identity rebuild tears down with ALTER TABLE DROP COLUMN —
    SQLite >= 3.35 (2021) required; older versions get a named refusal
    before anything is touched."""
    return tuple(int(p) for p in sqlite3.sqlite_version.split(".")) >= (3, 35, 0)


def backlink_columns(conn: sqlite3.Connection) -> dict:
    """{raw_table: True} for every raw_* table that already carries a
    product_uuid back-link column."""
    out = {}
    for (table,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'raw\\_%' ESCAPE '\\'"
    ):
        cols = {r[1] for r in conn.execute(f"PRAGMA table_info({_q(table)})")}
        out[table] = "product_uuid" in cols
    return out


def ensure_backlink_column(conn: sqlite3.Connection, table: str) -> bool:
    """Idempotently add the ``product_uuid`` back-link column + index to
    a raw table. Returns True when the column was added now."""
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({_q(table)})")}
    if "product_uuid" in cols:
        return False
    conn.execute(f"ALTER TABLE {_q(table)} ADD COLUMN product_uuid TEXT")
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS {_q(table + '_puid')} ON {_q(table)} (product_uuid)"
    )
    return True


def drop_backlink_column(conn: sqlite3.Connection, table: str) -> None:
    """Remove the back-link column (rebuild teardown; SQLite >= 3.35
    enforced by the caller). Indexes referencing the column must drop
    BEFORE the column — SQLite refuses DROP COLUMN while an index
    depends on it (r02 defect: 0013's _puid index blocked teardown)."""
    conn.execute(f"DROP INDEX IF EXISTS {_q(table + '_puid')}")
    for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name = ? "
        "AND sql LIKE '%product_uuid%'",
        (table,),
    ).fetchall():
        conn.execute(f"DROP INDEX IF EXISTS {_q(row[0])}")
    conn.execute(f"ALTER TABLE {_q(table)} DROP COLUMN product_uuid")


def tables_present(conn: sqlite3.Connection) -> bool:
    """All four identity tables exist (0013 applied)?"""
    names = {"manufacturer", "product", "identity_state", "linkage_candidate"}
    found = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    return names <= found

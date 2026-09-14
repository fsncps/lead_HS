"""Staging DB — the L2 measurement layer (v0.2.2 fu2, i19).

``data/testdata.sqlite`` (or the ``--staging-db`` path) holds what a
source *delivered*: product rows, trade rows, the CN8 dictionary —
every row with ``source_id + run_key + doc_hash + retrieval_date``
provenance, fed **only from archived documents**. The evidence DB is
untouched by this module; run-close metric derivation reads the
staging counts (metrics == staging by construction, fu1).

Semantics (design c1–c3, e1):
- idempotent replace per ``(source_id, run_key)`` — a re-run heals the
  two-store gap, never silent drift;
- loud failure when a staging write would lack provenance (no doc
  hash / no retrieval date — no row without provenance);
- per-write single transaction (interrupt mid-ingest → no partial rows);
- schema lives here, not in the evidence-DB migration chain.
"""

from __future__ import annotations

import os
import sqlite3

_CN8_ANNEX_HEADING = "3213"

# The 13 in-scope CN8 codes (CN 2024, chapter 32): 9 × 3208, 2 × 3209
# core + 2 × 3213 annex. ``verified=0`` until checked against the
# official CN nomenclature (U6: a metric, not a gate; W1 verifies).
CN8_DICT = (
    ("32081010", "3208", "core", "Polyesters — solutions (note 4)"),
    ("32081090", "3208", "core", "Polyesters — other"),
    ("32082010", "3208", "core", "Acrylic/vinyl — solutions (note 4)"),
    ("32082090", "3208", "core", "Acrylic/vinyl — other"),
    ("32089011", "3208", "core", "Other — polyurethane solution"),
    ("32089013", "3208", "core", "Other — p-cresol/divinylbenzene solution"),
    ("32089019", "3208", "core", "Other — solutions (note 4)"),
    ("32089091", "3208", "core", "Other — synthetic polymers"),
    ("32089099", "3208", "core", "Other — modified natural polymers"),
    ("32091000", "3209", "core", "Acrylic/vinyl — aqueous"),
    ("32099000", "3209", "core", "Other — aqueous"),
    ("32131000", "3213", "annex", "Artists' colours — in sets"),
    ("32139000", "3213", "annex", "Artists' colours — other"),
)


class StagingError(Exception):
    pass


_SCHEMA = """
CREATE TABLE IF NOT EXISTS stg_source_document (
    source_id TEXT NOT NULL,
    run_key TEXT NOT NULL,
    url TEXT NOT NULL,
    doc_hash TEXT NOT NULL,
    retrieval_date TEXT NOT NULL,
    bytes INTEGER,
    PRIMARY KEY (source_id, run_key, doc_hash)
);
CREATE TABLE IF NOT EXISTS stg_register_product (
    id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL,
    run_key TEXT NOT NULL,
    doc_hash TEXT NOT NULL,
    manufacturer_raw TEXT,
    manufacturer_norm TEXT,
    ident_raw TEXT,
    ident_norm TEXT NOT NULL,
    ident_type TEXT NOT NULL DEFAULT 'none'
        CHECK (ident_type IN ('licence', 'gtin', 'article', 'none')),
    ident_basis TEXT NOT NULL CHECK (ident_basis IN ('ident', 'name')),
    name TEXT,
    category_raw TEXT,
    raw TEXT
);
CREATE INDEX IF NOT EXISTS ix_stg_register_product_run
    ON stg_register_product (source_id, run_key);
CREATE INDEX IF NOT EXISTS ix_stg_register_product_ident
    ON stg_register_product (manufacturer_norm, ident_norm);
CREATE TABLE IF NOT EXISTS stg_trade_cn8 (
    id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL,
    run_key TEXT NOT NULL,
    doc_hash TEXT NOT NULL,
    cn8 TEXT,
    flow TEXT,
    declarant TEXT,
    partner TEXT,
    year TEXT,
    kg REAL,
    eur REAL
);
CREATE INDEX IF NOT EXISTS ix_stg_trade_run
    ON stg_trade_cn8 (source_id, run_key);
CREATE INDEX IF NOT EXISTS ix_stg_trade_cn8
    ON stg_trade_cn8 (cn8, flow);
CREATE TABLE IF NOT EXISTS dict_cn8 (
    cn8 TEXT PRIMARY KEY,
    hs_heading TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('core', 'annex')),
    label TEXT,
    verified INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: str) -> sqlite3.Connection:
    """Open (creating if needed) the staging DB. Parent dirs created."""
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True) if parent else None
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def init(conn: sqlite3.Connection) -> None:
    """Idempotent schema init (no migrations; re-running is safe)."""
    conn.executescript(_SCHEMA)


def seed_dict(conn: sqlite3.Connection, verified: int = 0) -> int:
    """Idempotent CN8 dictionary seed (fu-cn8home). Returns row count."""
    with conn:
        for cn8, heading, kind, label in CN8_DICT:
            conn.execute(
                "INSERT INTO dict_cn8 (cn8, hs_heading, kind, label, verified) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT (cn8) DO UPDATE SET hs_heading=excluded.hs_heading, "
                "kind=excluded.kind, label=excluded.label",
                (cn8, heading, kind, label, verified),
            )
    return conn.execute("SELECT COUNT(*) FROM dict_cn8").fetchone()[0]


def mark_dict_verified(conn: sqlite3.Connection, verified: int = 1) -> int:
    """U6: flip the verified flag once the code list is checked against
    the official nomenclature. Returns the number of verified rows."""
    with conn:
        conn.execute("UPDATE dict_cn8 SET verified=?", (verified,))
    return conn.execute("SELECT COUNT(*) FROM dict_cn8 WHERE verified=1").fetchone()[0]


def _check_doc(source_id, run_key, doc) -> None:
    """Loud provenance check (fu2): no staging row without doc identity."""
    if not source_id or not run_key:
        raise StagingError("staging write without source_id/run_key")
    for key in ("url", "doc_hash", "retrieval_date"):
        if not doc.get(key):
            raise StagingError(f"staging write without {key} (loud failure, c3)")


def _upsert_document(conn, source_id, run_key, doc) -> None:
    conn.execute(
        "INSERT INTO stg_source_document (source_id, run_key, url, doc_hash, retrieval_date, bytes) "
        "VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT (source_id, run_key, doc_hash) DO UPDATE SET "
        "url=excluded.url, retrieval_date=excluded.retrieval_date, bytes=excluded.bytes",
        (source_id, run_key, doc["url"], doc["doc_hash"], doc["retrieval_date"], doc.get("bytes")),
    )


def replace_products(conn, source_id, run_key, doc, rows: list) -> int:
    """Idempotent product-row replace for one (source_id, run_key, doc):
    one transaction — a failure mid-write leaves no partial rows (c1 chaos
    semantics). Rows are already-normalized dicts (normalize.identity).
    Returns the staged row count."""
    _check_doc(source_id, run_key, doc)
    with conn:
        _upsert_document(conn, source_id, run_key, doc)
        conn.execute(
            "DELETE FROM stg_register_product WHERE source_id=? AND run_key=? AND doc_hash=?",
            (source_id, run_key, doc["doc_hash"]),
        )
        for row in rows:
            conn.execute(
                "INSERT INTO stg_register_product (source_id, run_key, doc_hash, "
                "manufacturer_raw, manufacturer_norm, ident_raw, ident_norm, "
                "ident_type, ident_basis, name, category_raw, raw) "
                "VALUES (?, ?, ?, ?, CAST(? AS TEXT), CAST(? AS TEXT), CAST(? AS TEXT), ?, ?, ?, ?, ?)",
                (
                    source_id,
                    run_key,
                    doc["doc_hash"],
                    row.get("manufacturer_raw"),
                    row.get("manufacturer_norm"),
                    row.get("ident_raw"),
                    row.get("ident_norm"),
                    row.get("ident_type", "none"),
                    row.get("ident_basis", "name"),
                    row.get("name"),
                    row.get("category_raw"),
                    row.get("raw") if isinstance(row.get("raw"), str) else (
                        None if row.get("raw") is None else str(row.get("raw"))
                    ),
                ),
            )
    return conn.execute(
        "SELECT COUNT(*) FROM stg_register_product WHERE source_id=? AND run_key=? AND doc_hash=?",
        (source_id, run_key, doc["doc_hash"]),
    ).fetchone()[0]


def replace_trade(conn, source_id, run_key, doc, rows: list) -> int:
    """Idempotent trade-row replace (stg_trade_cn8). Rows: dicts with
    cn8/flow/declarant/partner/year/kg/eur. Returns the row count."""
    _check_doc(source_id, run_key, doc)
    with conn:
        _upsert_document(conn, source_id, run_key, doc)
        conn.execute(
            "DELETE FROM stg_trade_cn8 WHERE source_id=? AND run_key=? AND doc_hash=?",
            (source_id, run_key, doc["doc_hash"]),
        )
        for row in rows:
            conn.execute(
                "INSERT INTO stg_trade_cn8 (source_id, run_key, doc_hash, cn8, flow, "
                "declarant, partner, year, kg, eur) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    source_id,
                    run_key,
                    doc["doc_hash"],
                    row.get("cn8"),
                    row.get("flow"),
                    row.get("declarant"),
                    row.get("partner"),
                    row.get("year"),
                    row.get("kg"),
                    row.get("eur"),
                ),
            )
    return conn.execute(
        "SELECT COUNT(*) FROM stg_trade_cn8 WHERE source_id=? AND run_key=? AND doc_hash=?",
        (source_id, run_key, doc["doc_hash"]),
    ).fetchone()[0]


def count_products(conn, source_id, run_key) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM stg_register_product WHERE source_id=? AND run_key=?",
        (source_id, run_key),
    ).fetchone()[0]


def product_aggregates(conn, source_id, run_key) -> dict:
    """Run-close derivation inputs (fu4): distinct manufacturers, distinct
    (mfr, ident) pairs, identity completeness, category distribution."""
    row = conn.execute(
        """
        SELECT COUNT(DISTINCT manufacturer_norm),
               COUNT(DISTINCT manufacturer_norm || '||' || ident_norm),
               SUM(CASE WHEN ident_basis = 'ident' THEN 1 ELSE 0 END)
        FROM stg_register_product WHERE source_id=? AND run_key=?
        """,
        (source_id, run_key),
    ).fetchone()
    n_total = count_products(conn, source_id, run_key)
    completeness = round(100.0 * (row[2] or 0) / n_total, 1) if n_total else 0.0
    cats = [
        (r[0], r[1])
        for r in conn.execute(
            "SELECT COALESCE(category_raw, '(none)'), COUNT(*) FROM stg_register_product "
            "WHERE source_id=? AND run_key=? GROUP BY 1 ORDER BY 2 DESC LIMIT 10",
            (source_id, run_key),
        )
    ]
    return {
        "distinct_manufacturers": row[0] or 0,
        "distinct_pairs": row[1] or 0,
        "identity_completeness_pct": completeness,
        "categories": cats,
    }


def doc_registry(conn, source_id=None) -> list:
    rows = conn.execute(
        "SELECT source_id, run_key, url, doc_hash, retrieval_date, bytes "
        "FROM stg_source_document" + (" WHERE source_id=?" if source_id else "") + " ORDER BY source_id, run_key",
        (source_id,) if source_id else (),
    ).fetchall()
    return [dict(r) for r in rows]

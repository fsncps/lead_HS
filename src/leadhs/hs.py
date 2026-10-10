"""hs apply + status (v0.3.4 r02) — D51 HS completion. The curated map
(dict/hs_group_map.csv) is loaded and validated in full before any
write; ``apply`` then updates ``product.hs_code`` deterministically in
one transaction: ECAT products join directly on ``product.eu_group``,
BASTA products vote per product on the indexed raw back-link
(``bk04_code`` majority; conflicting top votes skip + count). A
re-run over unchanged data changes nothing (idempotent). ORDER
DEPENDENCY: run after any ``identity resolve``/``identity rebuild`` —
rebuild recreates canonical rows, so hs values must be re-applied
after it.

    hs_group_map.csv ──load/validate──▶ (source,group)→HS4 map
                                              │
    product.eu_group ──ECAT join──────────────┤
                                              ▼
    raw_as33_basta.product_uuid ─▶ votes ─▶ majority ─▶ UPDATE product.hs_code
        (bk04_code)        ▲                    │
                           └── conflicts ──▶ skip+count ──▶ hs status
    shadow paths: unmapped group → pending · empty hs_code map row →
    reviewed (stays NULL) · mapping edit → re-apply (idempotent)

States reported by ``status``: set (hs_code written) / reviewed
(NULL; every mapped group of the product has an empty-hs map row) /
not_applied (NULL; a non-empty map value exists — run apply again) /
pending (NULL; no mapping row for the product's groups).
"""

from __future__ import annotations

import csv
import hashlib
import re
import sqlite3
from dataclasses import dataclass

HS_RE = re.compile(r"^\d{4}$")
CONFIDENCE = {"high", "medium", "flag"}
SOURCE_GROUP_COLUMN = {"AS-2": "eu_group", "AS-33": "bk04_code"}
RAW_TABLE = {"AS-2": "raw_as2_ecat", "AS-33": "raw_as33_basta"}
# status reads the canonical AS-2 group straight off product (exact);
# BASTA products carry no group column, so its raw table is the join source
STATUS_JOIN = {
    "AS-2": ("product", "uuid", "eu_group", "eu_group IS NOT NULL AND eu_group != ''"),
    "AS-33": ("raw_as33_basta", "product_uuid", "bk04_code", "product_uuid IS NOT NULL"),
}


class HsMapError(ValueError):
    """The map file is malformed — refuse before any write."""


@dataclass(frozen=True)
class MapRow:
    hs_code: str
    confidence: str
    note: str


def _field(row: dict, name: str) -> str:
    value = row.get(name)
    return (value or "").strip()


def load_map(path: str) -> dict[tuple[str, str], MapRow]:
    """Parse + validate the whole map; any problem raises HsMapError."""
    rows: dict[tuple[str, str], MapRow] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        need = {"source_id", "group_code", "hs_code", "confidence", "note"}
        if reader.fieldnames is None or not need <= set(reader.fieldnames):
            raise HsMapError(
                f"map header must contain {sorted(need)} (found {reader.fieldnames})"
            )
        for n, raw in enumerate(reader, start=2):
            sid = _field(raw, "source_id")
            gcode = _field(raw, "group_code")
            hs = _field(raw, "hs_code")
            conf = _field(raw, "confidence") or "medium"
            note = _field(raw, "note")
            if not sid or not gcode:
                raise HsMapError(f"map row {n}: empty source_id/group_code")
            if sid not in SOURCE_GROUP_COLUMN:
                raise HsMapError(
                    f"map row {n}: unknown source_id {sid!r} (known: {sorted(SOURCE_GROUP_COLUMN)})"
                )
            if hs and not HS_RE.match(hs):
                raise HsMapError(f"map row {n} ({sid},{gcode}): hs_code {hs!r} is not 4 digits")
            if conf not in CONFIDENCE:
                raise HsMapError(
                    f"map row {n} ({sid},{gcode}): confidence {conf!r} not in {sorted(CONFIDENCE)}"
                )
            key = (sid, gcode)
            if key in rows:
                raise HsMapError(f"map row {n}: duplicate mapping ({sid},{gcode})")
            rows[key] = MapRow(hs, conf, note)
    if not rows:
        raise HsMapError("map file has no rows — nothing to apply")
    return rows


def map_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_temp_map(conn, mapping) -> None:
    conn.execute(
        "CREATE TEMP TABLE IF NOT EXISTS _hs_map (source_id TEXT, group_code TEXT, hs_code TEXT)"
    )
    conn.execute("DELETE FROM _hs_map")
    conn.executemany(
        "INSERT INTO _hs_map VALUES (?, ?, ?)",
        [(sid, gcode, row.hs_code) for (sid, gcode), row in mapping.items()],
    )
    conn.execute("CREATE INDEX IF NOT EXISTS _hs_map_ix ON _hs_map (source_id, group_code)")


def _drop_temp(conn) -> None:
    for name in ("_hs_votes", "_hs_best"):
        conn.execute(f"DROP TABLE IF EXISTS temp.{name}")


def _ecat_planned(conn) -> int:
    return len(conn.execute(
        "SELECT p.uuid FROM product p JOIN _hs_map m "
        "ON m.source_id = 'AS-2' AND m.group_code = p.eu_group "
        "WHERE m.hs_code != '' AND p.eu_group IS NOT NULL AND p.eu_group != '' "
        "AND (p.hs_code IS NULL OR p.hs_code != m.hs_code)"
    ).fetchall())


def _ecat_update(conn) -> int:
    cur = conn.execute(
        "UPDATE product SET hs_code = ("
        "  SELECT m.hs_code FROM _hs_map m"
        "  WHERE m.source_id = 'AS-2' AND m.group_code = product.eu_group"
        ") "
        "WHERE eu_group IS NOT NULL AND eu_group != '' "
        "AND (SELECT m.hs_code FROM _hs_map m "
        "     WHERE m.source_id = 'AS-2' AND m.group_code = product.eu_group) IS NOT NULL "
        "AND (SELECT m.hs_code FROM _hs_map m "
        "     WHERE m.source_id = 'AS-2' AND m.group_code = product.eu_group) != '' "
        "AND (product.hs_code IS NULL OR product.hs_code != ("
        "  SELECT m.hs_code FROM _hs_map m"
        "  WHERE m.source_id = 'AS-2' AND m.group_code = product.eu_group))"
    )
    return cur.rowcount


def _basta_major(conn) -> int:
    """Vote table → per-product top-voted HS4 pick (_hs_best, indexed);
    returns the conflict count (products with ≥2 distinct top-voted
    values)."""
    conn.execute(
        "CREATE TEMP TABLE _hs_votes AS "
        "SELECT r.product_uuid AS uuid, m.hs_code AS hs, COUNT(*) AS n "
        "FROM raw_as33_basta r JOIN _hs_map m "
        "ON m.source_id = 'AS-33' AND m.group_code = r.bk04_code "
        "WHERE m.hs_code != '' AND r.product_uuid IS NOT NULL "
        "AND r.bk04_code IS NOT NULL AND r.bk04_code != '' "
        "GROUP BY 1, 2"
    )
    conn.execute("CREATE INDEX _hs_votes_ix ON _hs_votes (uuid)")
    conn.execute(
        "CREATE TEMP TABLE _hs_best AS "
        "SELECT uuid, MIN(hs) AS hs, COUNT(*) AS k FROM ("
        "  SELECT v.uuid, v.hs FROM _hs_votes v "
        "  WHERE v.n = (SELECT MAX(x.n) FROM _hs_votes x WHERE x.uuid = v.uuid)"
        ") GROUP BY uuid"
    )
    conn.execute("CREATE INDEX _hs_best_ix ON _hs_best (uuid)")
    return conn.execute("SELECT COUNT(*) FROM _hs_best WHERE k > 1").fetchone()[0]


def _basta_planned(conn) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM _hs_best b "
        "JOIN product p ON p.uuid = b.uuid "
        "WHERE b.k = 1 AND (p.hs_code IS NULL OR p.hs_code != b.hs)"
    ).fetchone()[0]


def _basta_update(conn) -> int:
    cur = conn.execute(
        "UPDATE product SET hs_code = ("
        "  SELECT b.hs FROM _hs_best b WHERE b.uuid = product.uuid) "
        "WHERE product.uuid IN (SELECT uuid FROM _hs_best WHERE k = 1) "
        "AND (product.hs_code IS NULL OR product.hs_code != ("
        "  SELECT b.hs FROM _hs_best b WHERE b.uuid = product.uuid))"
    )
    return cur.rowcount


def apply(conn: sqlite3.Connection, map_path: str, dry_run: bool = False) -> dict:
    """Apply the curated map; one run row per source pass (AS-2 join,
    AS-33 vote) inside one transaction. Dry-run: identical read path,
    zero writes, no run rows (d25). An interrupt rolls the whole
    transaction back — no partial writes, no run-row residue."""
    from . import db as dbmod
    from . import ids as idsmod
    from .probe import engine as probeengine

    mapping = load_map(map_path)
    sha = map_sha256(map_path)

    if dry_run:
        conn.execute("BEGIN")
        try:
            _load_temp_map(conn, mapping)
            ties = _basta_major(conn)
            counts = {
                "dry_run": True,
                "map_rows": len(mapping),
                "map_sha256": sha,
                "ecat_planned": _ecat_planned(conn),
                "basta_planned": _basta_planned(conn),
                "conflicts": ties,
            }
        finally:
            conn.execute("ROLLBACK")
        _drop_temp(conn)
        return counts

    conn.execute("BEGIN IMMEDIATE")
    try:
        _load_temp_map(conn, mapping)
        ecat_set = _ecat_update(conn)
        ties = _basta_major(conn)
        basta_set = _basta_update(conn)
        run_ids = {}
        for sid in ("AS-2", "AS-33"):
            run_id, run_key, _ = probeengine._insert_run(
                conn, "hs_apply", sid, idsmod.slug_for_source(sid),
                {"map_rows": len(mapping), "map_sha256": sha},
            )
            run_ids[sid] = (run_id, run_key)
        probeengine._finish_run(
            conn, run_ids["AS-2"][0], "done", dbmod.utcnow(),
            "counts: " + _json({"set": ecat_set}),
        )
        probeengine._finish_run(
            conn, run_ids["AS-33"][0], "done", dbmod.utcnow(),
            "counts: " + _json({"set": basta_set, "conflicts": ties}),
        )
    except KeyboardInterrupt:
        conn.execute("ROLLBACK")
        raise
    conn.commit()
    _drop_temp(conn)
    return {
        "map_rows": len(mapping),
        "map_sha256": sha,
        "ecat_set": ecat_set,
        "basta_set": basta_set,
        "conflicts": ties,
    }


def _json(payload: dict) -> str:
    import json

    return json.dumps(payload, sort_keys=True)


def status(conn: sqlite3.Connection, map_path: str, top: int = 15) -> dict:
    """Three-state HS coverage per source + the pending-group worklist."""
    mapping = load_map(map_path)
    conn.execute("BEGIN")
    _load_temp_map(conn, mapping)
    total = conn.execute("SELECT COUNT(*) FROM product").fetchone()[0]
    set_n = conn.execute(
        "SELECT COUNT(*) FROM product WHERE hs_code IS NOT NULL"
    ).fetchone()[0]
    out: dict = {
        "total": {
            "products": total,
            "set": set_n,
            "null": total - set_n,
            "coverage_pct": round(100.0 * set_n / total, 1) if total else 0.0,
        },
        "sources": {},
        "worklist": [],
    }
    for sid in STATUS_JOIN:
        table, uuid_col, gcol, where = STATUS_JOIN[sid]
        cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')}
        if uuid_col not in cols or gcol not in cols:
            continue
        row = conn.execute(
            f"""
            WITH pg AS (
              SELECT r.{uuid_col} AS uuid,
                     MAX(CASE WHEN m.group_code IS NOT NULL AND m.hs_code != ''
                              THEN 1 ELSE 0 END) AS val,
                     MAX(CASE WHEN m.group_code IS NOT NULL AND m.hs_code = ''
                              THEN 1 ELSE 0 END) AS rev
              FROM "{table}" r LEFT JOIN _hs_map m
                ON m.source_id = :sid AND m.group_code = r.{gcol}
              WHERE {where}
              GROUP BY r.{uuid_col}
            )
            SELECT
              COUNT(*) AS products_n,
              SUM(CASE WHEN p.hs_code IS NOT NULL THEN 1 ELSE 0 END) AS set_n,
              SUM(CASE WHEN p.hs_code IS NULL AND pg.val = 0 AND pg.rev > 0
                       THEN 1 ELSE 0 END) AS reviewed_n,
              SUM(CASE WHEN p.hs_code IS NULL AND pg.val > 0
                       THEN 1 ELSE 0 END) AS notapplied_n,
              SUM(CASE WHEN p.hs_code IS NULL AND pg.val = 0 AND pg.rev = 0
                       THEN 1 ELSE 0 END) AS pending_n
            FROM pg JOIN product p ON p.uuid = pg.uuid
            """,
            {"sid": sid},
        ).fetchone()
        out["sources"][sid] = {
            "products": row["products_n"] or 0,
            "set": row["set_n"] or 0,
            "reviewed": row["reviewed_n"] or 0,
            "not_applied": row["notapplied_n"] or 0,
            "pending": row["pending_n"] or 0,
        }
    for sid, gcol in SOURCE_GROUP_COLUMN.items():
        cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{RAW_TABLE[sid]}")')}
        if "product_uuid" not in cols:
            continue
        out["worklist"].extend(
            {"source": sid, "group_code": r[0], "products": r[1]}
            for r in conn.execute(
                f"""
                SELECT r.{gcol} AS gcode, COUNT(DISTINCT r.product_uuid) AS prods
                FROM "{RAW_TABLE[sid]}" r LEFT JOIN _hs_map m
                  ON m.source_id = :sid AND m.group_code = r.{gcol}
                WHERE r.product_uuid IS NOT NULL AND m.group_code IS NULL
                GROUP BY r.{gcol} ORDER BY prods DESC LIMIT :top
                """,
                {"sid": sid, "top": top},
            )
        )
    conn.execute("ROLLBACK")
    return out


def render_status(out: dict) -> None:
    """Human output for the CLI ``hs status`` verb."""
    t = out["total"]
    print(
        f"products={t['products']:,}  hs set={t['set']:,} ({t['coverage_pct']}%)  "
        f"null={t['null']:,}"
    )
    for sid, s in sorted(out["sources"].items()):
        print(
            f"{sid}  products={s['products']:,}  set={s['set']:,}  "
            f"reviewed={s['reviewed']:,}  not_applied={s['not_applied']:,}  "
            f"pending={s['pending']:,}"
        )
    if out["worklist"]:
        print("worklist (groups with no mapping row, by products):")
        for w in out["worklist"]:
            print(f"  {w['source']}  {w['group_code']}  {w['products']:,}")
    else:
        print("worklist: (empty — every group has a mapping row)")

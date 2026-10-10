"""hs module: map validation, ECAT join, BASTA majority vote, dry-run,
idempotence, conflict skip, reviewed-vs-pending states, status output."""

import sqlite3

import pytest

from leadhs import hs
from leadhs.hs import HsMapError, load_map


def _write_map(tmp_path, rows):
    path = tmp_path / "map.csv"
    lines = ["source_id,group_code,hs_code,confidence,note"]
    lines += [",".join(r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


ECAT_MAP = _write_map  # alias for readability below


def _fixture_db(tmp_path):
    """Minimal identity-layer-shaped DB: products + a basta raw table
    with the product_uuid back-link."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE product (uuid TEXT PRIMARY KEY, ident_string TEXT, eu_group TEXT, hs_code TEXT)")
    conn.execute("CREATE TABLE raw_as33_basta (rowid_col INTEGER PRIMARY KEY, bk04_code TEXT, product_uuid TEXT)")
    conn.execute("CREATE INDEX ix_raw_basta ON raw_as33_basta (product_uuid)")
    conn.execute("CREATE TABLE run (id INTEGER PRIMARY KEY, run_key TEXT, kind_code TEXT, source_id TEXT, started_at TEXT, status_code TEXT, parameters_json TEXT, finished_at TEXT, notes TEXT)")
    conn.execute("CREATE TABLE run_kind (code TEXT PRIMARY KEY, label TEXT, description TEXT)")
    conn.execute("INSERT INTO run_kind VALUES ('hs_apply','HS completion','apply curated map')")
    conn.commit()
    return conn


def _seed_products(conn):
    conn.executemany(
        "INSERT INTO product VALUES (?, ?, ?, ?)",
        [
            ("p-ecat-set", "a|1", "Decorative paints", None),
            ("p-ecat-rev", "a|2", "Textile products", None),
            ("p-ecat-pend", "a|3", "Unknown group", None),
            ("p-ecat-ok", "a|4", "Cosmetic Products", "3304"),
            ("p-basta-set", "b|1", None, None),
            ("p-basta-conflict", "b|2", None, None),
            ("p-basta-pend", "b|3", None, None),
            ("p-basta-rev", "b|4", None, None),
        ],
    )
    rows = [
        (1, "03104", "p-basta-set"), (2, "03104", "p-basta-set"),
        (3, "03404", "p-basta-conflict"), (4, "04101", "p-basta-conflict"),
        (5, "99999", "p-basta-pend"),
        (6, "22001", "p-basta-rev"), (7, "22001", "p-basta-rev"),
    ]
    conn.executemany("INSERT INTO raw_as33_basta VALUES (?, ?, ?)", rows)
    conn.commit()


MAP_ROWS = [
    ("AS-2", "Decorative paints", "3209", "medium", ""),
    ("AS-2", "Textile products", "", "flag", "multi-chapter"),
    ("AS-2", "Cosmetic Products", "3304", "high", ""),
    ("AS-33", "03104", "3918", "high", ""),
    ("AS-33", "03404", "3209", "high", ""),
    ("AS-33", "04101", "4418", "high", ""),
    ("AS-33", "22001", "", "flag", "generic"),
]


def test_load_map_validates(tmp_path):
    path = _write_map(tmp_path, MAP_ROWS)
    mapping = load_map(path)
    assert len(mapping) == 7
    assert mapping[("AS-2", "Textile products")].hs_code == ""


def test_load_map_rejects_duplicates(tmp_path):
    rows = MAP_ROWS + [("AS-2", "Decorative paints", "3208", "high", "")]
    path = _write_map(tmp_path, rows)
    with pytest.raises(HsMapError, match="duplicate"):
        load_map(path)


def test_load_map_rejects_non_4_digit(tmp_path):
    rows = MAP_ROWS + [("AS-2", "Bad", "320", "high", "")]
    path = _write_map(tmp_path, rows)
    with pytest.raises(HsMapError, match="4 digits"):
        load_map(path)


def test_load_map_rejects_unknown_source_and_confidence(tmp_path):
    with pytest.raises(HsMapError, match="unknown source_id"):
        load_map(_write_map(tmp_path, [("XX-1", "g", "3208", "high", "")]))
    with pytest.raises(HsMapError, match="confidence"):
        load_map(_write_map(tmp_path, [("AS-2", "g", "3208", "sure", "")]))


def test_load_map_rejects_empty_file(tmp_path):
    with pytest.raises(HsMapError, match="no rows"):
        load_map(_write_map(tmp_path, []))


def test_apply_dry_run_writes_nothing(tmp_path):
    conn = _fixture_db(tmp_path)
    _seed_products(conn)
    path = _write_map(tmp_path, MAP_ROWS)
    counts = hs.apply(conn, path, dry_run=True)
    assert counts["ecat_planned"] == 1
    assert counts["basta_planned"] == 1
    assert counts["conflicts"] == 1
    assert conn.execute("SELECT COUNT(*) FROM product WHERE hs_code IS NOT NULL").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM run WHERE kind_code = 'hs_apply'").fetchone()[0] == 0


def test_apply_real_and_idempotent(tmp_path):
    conn = _fixture_db(tmp_path)
    _seed_products(conn)
    path = _write_map(tmp_path, MAP_ROWS)
    counts = hs.apply(conn, path, dry_run=False)
    assert counts["ecat_set"] == 1
    assert counts["basta_set"] == 1
    assert counts["conflicts"] == 1
    values = dict(conn.execute("SELECT uuid, hs_code FROM product").fetchall())
    assert values["p-ecat-set"] == "3209"
    assert values["p-basta-set"] == "3918"
    assert values["p-basta-conflict"] is None
    assert values["p-ecat-rev"] is None
    assert values["p-basta-rev"] is None
    runs = conn.execute("SELECT source_id, status_code FROM run WHERE kind_code = 'hs_apply' ORDER BY source_id").fetchall()
    assert [(r["source_id"], r["status_code"]) for r in runs] == [("AS-2", "done"), ("AS-33", "done")]
    second = hs.apply(conn, path, dry_run=False)
    assert second["ecat_set"] == 0
    assert second["basta_set"] == 0


def test_apply_rerun_after_map_edit(tmp_path):
    conn = _fixture_db(tmp_path)
    _seed_products(conn)
    path = _write_map(tmp_path, MAP_ROWS)
    hs.apply(conn, path)
    rows = MAP_ROWS + [("AS-2", "Unknown group", "3213", "high", "added")]
    hs.apply(conn, _write_map(tmp_path, rows))
    v = conn.execute("SELECT hs_code FROM product WHERE uuid = 'p-ecat-pend'").fetchone()[0]
    assert v == "3213"


def test_status_three_states(tmp_path):
    conn = _fixture_db(tmp_path)
    _seed_products(conn)
    path = _write_map(tmp_path, MAP_ROWS)
    hs.apply(conn, path)
    out = hs.status(conn, path)
    assert out["total"]["products"] == 8
    assert out["total"]["set"] == 3  # 2 written by apply + 1 pre-seeded correct (p-ecat-ok)
    ecat = out["sources"]["AS-2"]
    assert ecat["set"] == 2 and ecat["reviewed"] == 1 and ecat["pending"] == 1  # set: 1 written + 1 pre-seeded
    basta = out["sources"]["AS-33"]
    assert basta["set"] == 1 and basta["reviewed"] == 1
    assert basta["pending"] + basta["not_applied"] >= 1


def test_status_worklist_ranks_unmapped(tmp_path):
    conn = _fixture_db(tmp_path)
    _seed_products(conn)
    path = _write_map(tmp_path, MAP_ROWS)
    out = hs.status(conn, path)
    codes = {w["group_code"] for w in out["worklist"]}
    assert "99999" in codes

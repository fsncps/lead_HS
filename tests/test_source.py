"""register CSV -> source rows; hostile cases."""

import os

import pytest

from leadhs.source import SourceLoadError, all_sources, get_source, list_, load

HEADER = "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes"


def _write(tmp_path, body: str):
    path = tmp_path / "reg.csv"
    path.write_text(HEADER + "\n" + body, encoding="utf-8")
    return str(path)


def test_load_and_list(loaded_conn, capsys):
    list_(loaded_conn)
    out = capsys.readouterr().out
    assert "PX-1" in out and "CX-1" in out


def test_list_class_filter(loaded_conn, capsys):
    list_(loaded_conn, "CS")
    out = capsys.readouterr().out
    assert "CX-1" in out and "PX-1" not in out


def test_load_upserts(conn, tmp_path, site):
    path = _write(tmp_path, f"PX-1,PE,Old name,{site}/,scrape,,open,1,first\n")
    assert load(conn, path) == 1
    path2 = _write(tmp_path, f"PX-1,PE,New name,{site}/terms,scrape,,open,1,second\n")
    load(conn, path2)
    assert get_source(conn, "PX-1").name == "New name"
    assert get_source(conn, "PX-1").url == f"{site}/terms"


def test_malformed_bad_class(conn, tmp_path, site):
    path = _write(tmp_path, f"PX-1,XX,Name,{site}/,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError):
        load(conn, path)


def test_malformed_missing_url(conn, tmp_path):
    path = _write(tmp_path, "PX-1,PE,Name,,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError):
        load(conn, path)


def test_malformed_duplicate_id(conn, tmp_path, site):
    alt = site.replace("127.0.0.1", "127.0.0.2")  # distinct host: only the id dups here
    path = _write(tmp_path, f"PX-1,PE,Name,{site}/,scrape,,open,1,\nPZ-1,PE,Name2,{alt}/,scrape,,open,1,\nPZ-1,PE,Dup,{alt}/terms,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError) as exc:
        load(conn, path)
    assert "duplicate" in str(exc.value)


def test_malformed_bad_id(conn, tmp_path, site):
    path = _write(tmp_path, f"PE1,PE,Name,{site}/,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError):
        load(conn, path)


def test_malformed_non_http_url(conn, tmp_path):
    """i13/pe6: url must be http(s) with a host; the failing row is named."""
    path = _write(tmp_path, "PX-1,PE,Name,ftp://example.com/x,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError) as exc:
        load(conn, path)
    assert "PX-1" in str(exc.value) and "http" in str(exc.value)


def test_duplicate_active_host_rejected(conn, tmp_path, site):
    """i13/pe6: one site must not be double-counted; both ids are named."""
    path = _write(tmp_path, f"PX-1,PE,Name,{site}/,scrape,,open,1,\nPZ-1,PE,Name2,{site}/catalog,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError) as exc:
        load(conn, path)
    assert "PX-1" in str(exc.value) and "PZ-1" in str(exc.value)


def test_same_host_different_datasets_loads(conn, tmp_path, site):
    """v0.2.2: outside PE one host may carry distinct datasets
    (host+path conflict key — the Eurostat CS-2/ST-4 case)."""
    path = _write(
        tmp_path,
        f"CX-1,CS,Comext,{site}/api/comext,api,,open,1,\n"
        f"SX-1,ST,Prodcom,{site}/api/prodcom,download,,open,1,\n"
        f"AX-1,AS,Register,{site}/export.csv,download,,open,1,\n",
    )
    assert load(conn, path) == 3


def test_duplicate_host_with_inactive_row_loads(conn, tmp_path, site):
    path = _write(tmp_path, f"PX-1,PE,Name,{site}/,scrape,,open,1,\nPZ-9,PE,Retired,{site}/old,scrape,,open,0,\n")
    assert load(conn, path) == 2


def test_preslim_register_still_loads(conn):
    """D28/U12: the pre-slim 14-row register remains loadable via --file
    (inactive LG/LI rows are exempt from the duplicate-host check)."""
    preslim = os.path.join(os.path.dirname(__file__), "data", "register_preslim.csv")
    assert load(conn, preslim) == 14
    ids = {r[0] for r in conn.execute("SELECT id FROM source")}
    assert {"CS-1", "CS-2", "PE-1", "PE-2", "PE-3", "PE-4", "ST-1", "ST-2", "ST-3"} <= ids
    assert "LG-1" in ids and "LI-1" in ids


def test_empty_register(conn, tmp_path):
    path = _write(tmp_path, "")
    with pytest.raises(SourceLoadError):
        load(conn, path)


def test_active_selection(loaded_conn):
    actives = [s.id for s in all_sources(loaded_conn, active_only=True)]
    assert "PX-1" in actives
    alls = [s.id for s in all_sources(loaded_conn, active_only=False)]
    assert len(alls) >= len(actives)


def test_unknown_source(conn):
    assert get_source(conn, "ZZ-9") is None

"""register CSV -> source rows; hostile cases."""

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
    path = _write(tmp_path, f"PX-1,PE,Name,{site}/,scrape,,open,1,\nPZ-1,PE,Name2,{site}/,scrape,,open,1,\nPZ-1,PE,Dup,{site}/terms,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError) as exc:
        load(conn, path)
    assert "duplicate" in str(exc.value)


def test_malformed_bad_id(conn, tmp_path, site):
    path = _write(tmp_path, f"PE1,PE,Name,{site}/,scrape,,open,1,\n")
    with pytest.raises(SourceLoadError):
        load(conn, path)


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

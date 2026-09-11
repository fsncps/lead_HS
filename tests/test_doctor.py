"""doctor: fake binaries, missing contact warning, unwritable dir."""

import types

import pytest

from leadhs import doctor


def _rt(tmp_path, contact="test@example.com"):
    return types.SimpleNamespace(
        db_path=str(tmp_path / "t.sqlite"), contact=contact, verbose=False, logger=None,
    )


def test_all_ok_with_fake_binaries(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda name: f"/fake/{name}")
    result = doctor.run(_rt(tmp_path), net=False)
    assert not result.has_errors
    kinds = {(name, kind) for kind, name, _ in result.items}
    assert ("mdbtools", "ok") in kinds
    assert ("contact", "ok") in kinds


def test_missing_binaries_are_warnings(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda name: None)
    result = doctor.run(_rt(tmp_path), net=False)
    assert not result.has_errors
    for kind, name, _ in result.items:
        if name in doctor.OPTIONAL_BINARIES:
            assert kind == "warn"


def test_missing_contact_is_warning(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor.shutil, "which", lambda name: None)
    result = doctor.run(_rt(tmp_path, contact=None), net=False)
    assert not result.has_errors
    assert ("contact", "warn") in {(name, kind) for kind, name, _ in result.items}


def test_unwritable_data_dir_is_error(tmp_path, monkeypatch):
    def boom(*a, **kw):
        raise OSError("read-only")

    monkeypatch.setattr(doctor.os, "makedirs", boom)
    result = doctor.run(_rt(tmp_path), net=False)
    assert result.has_errors
    assert any(kind == "error" and name == "data dir" for kind, name, _ in result.items)

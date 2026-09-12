"""Operability tests (t7): exit-code mapping enforced in main(), bare-group
help, `source list` single registration, doctor --net only, --data-dir."""

import os
import subprocess
import sys

import pytest

import leadhs.cli as climod


def _lead(*args, cwd=None):
    env = dict(os.environ, LEADHS_CONTACT="test@example.com")
    return subprocess.run(
        [sys.executable, "-m", "leadhs.cli", *args],
        capture_output=True, text=True, env=env, cwd=cwd,
    )


def test_unknown_command_exit_1():
    r = _lead("dource")
    assert r.returncode == 1
    assert "No such command" in r.stderr
    assert "Try" in r.stderr and "--help" in r.stderr


def test_missing_required_option_exit_1():
    r = _lead("probe", "record")
    assert r.returncode == 1
    assert "error:" in r.stderr.lower() or "Error" in r.stderr


def test_bad_choice_exit_1():
    r = _lead("probe", "report", "--format", "xml")
    assert r.returncode == 1
    assert "Invalid value" in r.stderr


def test_help_and_version_exit_0_stdout():
    for args in (["--help"], ["--version"]):
        r = _lead(*args)
        assert r.returncode == 0, args
        assert r.stdout, args
        assert not r.stderr, args


def test_version_is_0_2_0():
    r = _lead("--version")
    assert "0.2.0" in r.stdout


@pytest.mark.parametrize("group", [[], ["db"], ["source"], ["probe"]])
def test_bare_groups_help_stdout_exit_0(group):
    r = _lead(*group)
    assert r.returncode == 0
    assert "Usage:" in r.stdout
    assert not r.stderr


def test_source_list_registered_once(db_path, fixture_register):
    r = _lead("--db", db_path, "db", "init")
    assert r.returncode == 0
    r = _lead("--db", db_path, "source", "load", "--file", fixture_register)
    assert r.returncode == 0
    r = _lead("--db", db_path, "source", "list")
    assert r.returncode == 0
    assert "PX-1" in r.stdout
    r = _lead("--db", db_path, "source", "list-")
    assert r.returncode == 1
    assert "No such command" in r.stderr


def test_doctor_help_net_only():
    r = _lead("doctor", "--help")
    assert r.returncode == 0
    assert "--net" in r.stdout
    assert "--no-net" not in r.stdout


def test_db_and_data_dir_exclusive(db_path):
    r = _lead("--db", db_path, "--data-dir", "/tmp/leadhs-other", "db", "status")
    assert r.returncode == 1
    assert "mutually exclusive" in r.stderr


def test_data_dir_init(tmp_path):
    base = tmp_path / "dd"
    r = _lead("--data-dir", str(base), "db", "init")
    assert r.returncode == 0
    assert (base / "leadhs.sqlite").exists()
    r = _lead("--data-dir", str(base), "db", "status")
    assert r.returncode == 0


# --- main() mapping, monkeypatched (deterministic; no real signals) ------


def _patch_raise(monkeypatch, exc):
    def _raise(*a, **k):
        raise exc

    monkeypatch.setattr(climod, "cli", _raise)


def test_main_abort_130(monkeypatch):
    from click.exceptions import Abort

    _patch_raise(monkeypatch, Abort())
    assert climod.main() == 130


def test_main_keyboard_interrupt_130(monkeypatch):
    _patch_raise(monkeypatch, KeyboardInterrupt())
    assert climod.main() == 130


def test_main_usage_error_1(monkeypatch):
    from click.exceptions import UsageError

    _patch_raise(monkeypatch, UsageError("bad usage"))
    assert climod.main() == 1


def test_main_exit_code_passthrough(monkeypatch):
    from click.exceptions import Exit

    _patch_raise(monkeypatch, Exit(3))
    assert climod.main() == 3


def test_main_bug_1(monkeypatch):
    monkeypatch.delenv("LEADHS_DEBUG", raising=False)
    _patch_raise(monkeypatch, RuntimeError("boom"))
    assert climod.main() == 1


def test_main_bug_reraises_with_debug(monkeypatch):
    monkeypatch.setenv("LEADHS_DEBUG", "1")
    _patch_raise(monkeypatch, RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        climod.main()

"""ids.py: deterministic run_key builder."""

from datetime import date

from leadhs.ids import next_attempt, run_key, slug_for_source


def test_slug_for_source():
    assert slug_for_source("CS-1") == "cs1"
    assert slug_for_source("ST-12") == "st12"


def test_run_key_first_attempt():
    assert run_key("probe", date(2026, 9, 10), "cs1", 1) == "probe-20260910-cs1"


def test_run_key_suffixes():
    assert run_key("probe", date(2026, 9, 10), "cs1", 2) == "probe-20260910-cs1-2"
    assert run_key("probe", date(2026, 9, 10), "cs1", 3) == "probe-20260910-cs1-3"


def test_run_key_invalid_attempt():
    import pytest

    with pytest.raises(ValueError):
        run_key("probe", date(2026, 9, 10), "cs1", 0)


def test_next_attempt():
    base = "probe-20260910-cs1"
    assert next_attempt([], "probe", date(2026, 9, 10), "cs1") == 1
    assert next_attempt([base], "probe", date(2026, 9, 10), "cs1") == 2
    assert next_attempt([base, base + "-2"], "probe", date(2026, 9, 10), "cs1") == 3
    assert next_attempt([base, base + "-2", base + "-5"], "probe", date(2026, 9, 10), "cs1") == 6
    # unrelated keys do not count
    assert next_attempt(["acquire-20260910-cs1"], "probe", date(2026, 9, 10), "cs1") == 1

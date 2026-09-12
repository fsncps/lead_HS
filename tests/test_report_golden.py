"""Golden report tests (t3): fixture findings -> exact md/csv/json.

Time is frozen so run_keys and timestamps are deterministic. To
regenerate intentionally: delete tests/golden/* and re-run (review the
diff before committing).
"""

from datetime import date
from pathlib import Path

import pytest

from leadhs import db as dbmod
from leadhs.probe import engine
from leadhs import report as reportmod

FIXED_NOW = "2026-09-10T12:00:00Z"
FIXED_DATE = date(2026, 9, 10)
GOLDEN = Path(__file__).parent / "golden"


@pytest.fixture()
def frozen_time(monkeypatch):
    monkeypatch.setattr(dbmod, "utcnow", lambda: FIXED_NOW)
    monkeypatch.setattr(engine, "_today", lambda: FIXED_DATE)


@pytest.fixture()
def probed(loaded_conn, store, make_fetcher, frozen_time):
    from leadhs.source import get_source

    fetcher = make_fetcher()
    engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, "PX-1"), sample_n=2)
    engine.run_one(loaded_conn, store, fetcher, get_source(loaded_conn, "CX-1"))
    return loaded_conn


import re


def _normalize(text: str) -> str:
    """The fixture site port varies per session (and the fixture register
    uses 127.0.0.N loopback aliases) — normalize host:port for goldens."""
    return re.sub(r"127\.0\.0\.\d+:\d+", "127.0.0.1:PORT", text)


def _golden(name: str, content: str) -> str:
    GOLDEN.mkdir(exist_ok=True)
    path = GOLDEN / name
    if not path.exists():
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def test_golden_md(probed):
    out = _normalize(reportmod.render(probed, format="md"))
    assert out == _normalize(_golden("report.md", out))


def test_golden_csv(probed):
    out = _normalize(reportmod.render(probed, format="csv"))
    assert out == _normalize(_golden("report.csv", out))


def test_golden_json(probed):
    out = _normalize(reportmod.render(probed, format="json"))
    assert out == _normalize(_golden("report.json", out))


def test_report_source_filter(probed):
    import json

    data = json.loads(reportmod.render(probed, format="json", source_id="CX-1"))
    assert [s["id"] for s in data["sources"]] == ["CX-1"]
    assert data["report"]["source_filter"] == "CX-1"

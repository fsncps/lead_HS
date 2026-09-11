"""ST adapter: SPIN download + extraction path.

extraction_path ok is gated on the mdbtools binary (skipif);
the missing-binary path is forced and always runs (t5/t6).
"""

import shutil

import pytest

from leadhs.models import ProbeContext, SourceRef
from leadhs.probe.adapters import BinaryMissing, STAdapter


def _source(site, path="/spin"):
    return SourceRef(id="ST-2", class_code="ST", name="x", url=f"{site}{path}", access_method_code="download", active=1)


def _ctx(make_fetcher, conn, store):
    return ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=False)


@pytest.mark.mdbtools
@pytest.mark.skipif(not (shutil.which("mdb-export") or shutil.which("mdb-tables")), reason="mdbtools binary absent")
def test_extraction_path_ok(site, conn, store, make_fetcher):
    result = STAdapter().probe(_source(site), _ctx(make_fetcher, conn, store))
    extraction = [f for f in result.findings if f.metric_code == "extraction_path"][0]
    assert "mdbtools ok" in extraction.value_text
    assert len(result.documents) == 2  # landing + downloaded DB


def test_binary_missing_forced(site, conn, store, make_fetcher, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    with pytest.raises(BinaryMissing):
        STAdapter().probe(_source(site), _ctx(make_fetcher, conn, store))


def test_dry_run(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = STAdapter().probe(_source(site), ctx)
    assert result.documents == [] and result.findings == []

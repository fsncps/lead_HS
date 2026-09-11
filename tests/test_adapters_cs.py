"""CS adapter: export format/granularity/rows; UnexpectedFormat degrade."""

import pytest

from leadhs.models import ProbeContext, SourceRef
from leadhs.probe.adapters import CSAdapter, UnexpectedFormat


def _source(site, path):
    return SourceRef(id="CS-1", class_code="CS", name="x", url=f"{site}{path}", access_method_code="download", active=1)


def _ctx(make_fetcher, conn, store):
    return ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=False)


def _metrics(result):
    return {f.metric_code: f for f in result.findings}


def test_good_csv(site, conn, store, make_fetcher):
    result = CSAdapter().probe(_source(site, "/export.csv"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert {"format", "granularity", "export_rows", "free_access", "coverage_years"} <= set(m)
    assert m["export_rows"].value_numeric == 3
    assert "CSV" in m["format"].value_text
    assert m["free_access"].value_numeric == 1
    assert len(result.documents) == 1


def test_bad_layout_unexpected_format(site, conn, store, make_fetcher):
    with pytest.raises(UnexpectedFormat) as exc:
        CSAdapter().probe(_source(site, "/export-bad.csv"), _ctx(make_fetcher, conn, store))
    assert "columns" in exc.value.detail


def test_json_api(site, conn, store, make_fetcher):
    result = CSAdapter().probe(_source(site, "/api.json"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["export_rows"].value_numeric == 3
    assert "JSON" in m["format"].value_text


def test_dry_run(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_source(site, "/export.csv"), ctx)
    assert result.documents == [] and result.findings == []

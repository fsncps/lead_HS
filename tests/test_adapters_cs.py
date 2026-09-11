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


# --- od9: parameterized per-HS query (access_method = api) ---------------


def _api_source(site):
    return SourceRef(id="CS-2", class_code="CS", name="Comext", url=f"{site}/api.json",
                     access_method_code="api", active=1)


def test_query_api_per_hs_emission(site, conn, store, make_fetcher):
    result = CSAdapter().probe(_api_source(site), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["records_hs3208"].value_numeric == 3
    assert m["records_hs3209"].value_numeric == 3
    assert m["records_hs3213"].value_numeric == 0  # empty result set = honest 0
    assert all(f.method_code == "api" for f in result.findings)
    assert len(result.documents) == 3  # every response archived (verification artifact)
    assert result.parameters["query"]["3208"]["product"] == "3208"
    assert result.parameters["query"]["3213"]["format"] == "JSON"
    # findings reference their archived response
    assert m["records_hs3208"].document is result.documents[0]


def test_query_api_urls_carry_params(site, conn, store, make_fetcher, site_hits):
    CSAdapter().probe(_api_source(site), _ctx(make_fetcher, conn, store))
    queried = [p for p in site_hits if "product=" in p]
    assert len(queried) == 3
    for hs in ("3208", "3209", "3213"):
        assert any(f"product={hs}" in p and "format=JSON" in p and "flow=IMP" in p for p in queried)


def test_query_api_dry_run_plans_hs_urls(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_api_source(site), ctx)
    assert result.documents == [] and result.findings == []


def test_dry_run(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_source(site, "/export.csv"), ctx)
    assert result.documents == [] and result.findings == []

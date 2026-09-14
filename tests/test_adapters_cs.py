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
    # 3 records responses + 4 aggregation responses (2 HS × 2 indicators), all archived
    assert len(result.documents) == 7
    assert result.parameters["query"]["3208"]["product"] == "3208"
    assert result.parameters["query"]["3213"]["format"] == "JSON"
    # findings reference their archived response
    assert m["records_hs3208"].document is result.documents[0]


def test_query_api_urls_carry_params(site, conn, store, make_fetcher, site_hits):
    CSAdapter().probe(_api_source(site), _ctx(make_fetcher, conn, store))
    queried = [p for p in site_hits if "product=" in p]
    # 3 records queries + 4 aggregation queries (2 HS × 2 indicators)
    assert len(queried) == 7
    for hs in ("3208", "3209", "3213"):
        assert any(f"product={hs}" in p and "format=JSON" in p and "flow=1" in p and "indicators" not in p for p in queried)


def test_query_api_dry_run_plans_hs_urls(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_api_source(site), ctx)
    assert result.documents == [] and result.findings == []


# --- v0.2.2 W1: per-CN8 batch + U6 dictionary verification ----------------


def test_cn8_batch_verifies_dict_when_complete(site, conn, store, make_fetcher, tmp_path):
    """U6: a batch that delivers rows for all 13 in-scope codes flips the
    seeded dictionary to verified=1."""
    from leadhs import staging
    from leadhs.staging import CN8_DICT

    stg = staging.connect(str(tmp_path / "stg.sqlite"))
    staging.init(stg)
    staging.seed_dict(stg)
    assert stg.execute("SELECT SUM(verified) FROM dict_cn8").fetchone()[0] == 0
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, mode="capability", dry_run=False, staging=stg)
    result = CSAdapter().probe(_api_source(site), ctx)
    assert {r.cn8 for r in result.staged_trade} >= {c[0] for c in CN8_DICT}
    assert stg.execute("SELECT SUM(verified) FROM dict_cn8").fetchone()[0] == len(CN8_DICT)
    stg.close()


def test_cn8_batch_keeps_dict_unverified_when_staging_absent(site, conn, store, make_fetcher):
    """U6 is metric-not-gate: no staging connection → no flip, batch still done."""
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, mode="capability", dry_run=False)
    result = CSAdapter().probe(_api_source(site), ctx)
    assert result.staged_trade


def test_dry_run(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_source(site, "/export.csv"), ctx)
    assert result.documents == [] and result.findings == []


# --- v0.2.0 nu2: full-year import aggregation (e2/2A, e7) -----------------


def _api_url_source(site, path):
    return SourceRef(id="CS-2", class_code="CS", name="Comext", url=f"{site}{path}",
                     access_method_code="api", active=1)


def test_aggregation_sums_and_partner_tops(site, conn, store, make_fetcher):
    """e2/2A: value-as-object JSON-stat decoded — sums AND tops from one
    payload; flow + resolved year pinned in finding notes + parameters."""
    result = CSAdapter().probe(_api_url_source(site, "/api.json"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["trade_kg_hs3208"].value_numeric == 40000.0  # (100 + 250 + 50) × 100 kg
    assert m["trade_eur_hs3208"].value_numeric == 400.0
    assert "flow=1 (import)" in m["trade_kg_hs3208"].notes
    assert "year=2024" in m["trade_kg_hs3208"].notes
    assert "FR=250" in m["trade_kg_hs3208"].notes  # partner tops
    # the aggregation query parameters are pinned in run parameters
    assert result.parameters["query"]["3208_kg_2024"]["indicators"] == "QUANTITY_IN_100KG"
    assert "partner" not in result.parameters["query"]["3208_kg_2024"]


def test_aggregation_year_step_back(site, conn, store, make_fetcher):
    """e7: empty for 2024 → previous year used and noted."""
    result = CSAdapter().probe(_api_url_source(site, "/api-agg.json"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["trade_kg_hs3208"].value_numeric == 6000.0  # (30 + 20 + 10) × 100 kg
    assert "year=2023" in m["trade_kg_hs3208"].notes
    assert any("stepping back" in n for n in result.notes)
    # both the empty and the resolved attempt are pinned
    assert "3208_kg_2024" in result.parameters["query"]
    assert "3208_kg_2023" in result.parameters["query"]


def test_aggregation_step_back_exhausted_blocked_note(site, conn, store, make_fetcher):
    """e7: three empty years → honest 0 + documented-blocked note."""
    result = CSAdapter().probe(_api_url_source(site, "/api-empty.json"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["trade_kg_hs3208"].value_numeric == 0
    assert "blocked" in m["trade_kg_hs3208"].notes
    assert any("no data for 2024..2022" in n for n in result.notes)


def test_aggregation_malformed_payload(site, conn, store, make_fetcher):
    from leadhs.probe.adapters import UnexpectedFormat

    with pytest.raises(UnexpectedFormat) as exc:
        CSAdapter().probe(_api_url_source(site, "/api-bad.json"), _ctx(make_fetcher, conn, store))
    assert "JSON-stat" in exc.value.detail
    # findings collected before the failure are preserved as partial
    assert exc.value.partial is not None


def test_aggregation_dry_run_plans_agg_urls(site, conn, store, make_fetcher, monkeypatch, site_hits):
    """e7: dry-run plans the aggregation URLs (8), zero network."""
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = CSAdapter().probe(_api_url_source(site, "/api.json"), ctx)
    assert result.documents == [] and result.findings == []

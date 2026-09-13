"""AS adapter — register-capability sounding-out (v0.2.1 cap2/cap5, t11).

Fixture paths (conftest): /reg.csv (manufacturer + licence_no + cn_code),
/reg-manufacturer.csv (manufacturer + cn_code, no product-ident),
/reg-no-nomenclature.csv (manufacturer + licence_no, no cn_code),
/reg.json (list payload), /reg-empty.csv, /reg-bad.csv (single column).
"""

import pytest

from leadhs.models import ProbeContext, SourceRef
from leadhs.probe.adapters import ASAdapter, UnexpectedFormat


def _source(site, path, access_method="download"):
    return SourceRef(id="AS-1", class_code="AS", name="Register", url=f"{site}{path}",
                     access_method_code=access_method, active=1)


def _ctx(make_fetcher, conn, store, dry_run=False, mode="capability"):
    return ProbeContext(fetcher=make_fetcher(), store=store, conn=conn,
                        dry_run=dry_run, mode=mode)


def _metrics(result):
    return {f.metric_code: f for f in result.findings}


# --- happy path: full register CSV ---------------------------------------


def test_full_register_csv_capability(site, conn, store, make_fetcher):
    """cap2: fetch → header/shape inspect → row count → capability
    findings; the raw export is archived."""
    result = ASAdapter().probe(_source(site, "/reg.csv"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["products_identifiable"].value_numeric == 3
    assert m["cap_manufacturer"].value_numeric == 1
    assert m["cap_product_ident"].value_numeric == 1
    assert m["cap_cn8_linkage"].value_text == "category"
    assert m["cap_depth_tier"].value_numeric == 2
    assert m["cn8_reachable"].value_numeric == 2  # 32089000, 32091000
    assert all(f.method_code == "download" for f in result.findings)
    assert len(result.documents) == 1


def test_manufacturer_no_product_ident(site, conn, store, make_fetcher):
    result = ASAdapter().probe(_source(site, "/reg-manufacturer.csv"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["cap_manufacturer"].value_numeric == 1
    assert m["cap_product_ident"].value_numeric == 0
    assert m["products_identifiable"].value_numeric == 2


def test_no_nomenclature_column_manual(site, conn, store, make_fetcher):
    result = ASAdapter().probe(_source(site, "/reg-no-nomenclature.csv"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["cap_cn8_linkage"].value_text == "manual"
    assert m["cn8_reachable"].value_numeric == 0
    assert m["cap_manufacturer"].value_numeric == 1
    assert m["cap_product_ident"].value_numeric == 1


def test_json_register(site, conn, store, make_fetcher):
    result = ASAdapter().probe(_source(site, "/reg.json", access_method="api"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["products_identifiable"].value_numeric == 2
    assert m["cap_cn8_linkage"].value_text == "category"
    assert m["cn8_reachable"].value_numeric == 2
    assert all(f.method_code == "api" for f in result.findings)


# --- error / edge paths ----------------------------------------------------


def test_empty_export_unexpected_format(site, conn, store, make_fetcher):
    with pytest.raises(UnexpectedFormat) as exc:
        ASAdapter().probe(_source(site, "/reg-empty.csv"), _ctx(make_fetcher, conn, store))
    assert "empty" in exc.value.detail


def test_malformed_export_unexpected_format(site, conn, store, make_fetcher):
    with pytest.raises(UnexpectedFormat) as exc:
        ASAdapter().probe(_source(site, "/reg-bad.csv"), _ctx(make_fetcher, conn, store))
    assert "columns" in exc.value.detail


# --- mode / access-method dispatch -----------------------------------------


def test_non_capability_mode_noop(site, conn, store, make_fetcher):
    """C1: census/recon sweeps are unchanged — an AS source in census
    mode returns an empty result (no spurious findings, no fetch)."""
    result = ASAdapter().probe(_source(site, "/reg.csv"), _ctx(make_fetcher, conn, store, mode="census"))
    assert result.documents == [] and result.findings == []
    result = ASAdapter().probe(_source(site, "/reg.csv"), _ctx(make_fetcher, conn, store, mode="recon"))
    assert result.documents == [] and result.findings == []


def test_manual_access_method_noop(site, conn, store, make_fetcher):
    """cap2: manual-access_method sources are characterized by `probe
    record --mode capability`, never by the automated branch."""
    result = ASAdapter().probe(_source(site, "/reg.csv", access_method="manual"), _ctx(make_fetcher, conn, store))
    assert result.documents == [] and result.findings == []


def test_dry_run_plans_zero_fetch(site, conn, store, make_fetcher, monkeypatch):
    """i7: dry-run plans the export URL, performs zero network calls."""
    ctx = _ctx(make_fetcher, conn, store, dry_run=True)
    monkeypatch.setattr(ctx.fetcher._session, "get", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("network")))
    result = ASAdapter().probe(_source(site, "/reg.csv"), ctx)
    assert result.documents == [] and result.findings == []


def test_html_landing_page_not_parsed_as_export(site, conn, store, make_fetcher):
    """i17: an HTML landing page is not a machine-readable export — the
    adapter records a format finding + manual linkage, never a spurious
    count (an HTML page containing commas must not parse as CSV)."""
    result = ASAdapter().probe(_source(site, "/"), _ctx(make_fetcher, conn, store))
    m = _metrics(result)
    assert m["format"].value_text == "HTML landing page — not a CSV/JSON export; export mechanics to confirm"
    assert m["cap_cn8_linkage"].value_text == "manual"
    assert "products_identifiable" not in m
    assert any("HTML landing page" in n for n in result.notes)

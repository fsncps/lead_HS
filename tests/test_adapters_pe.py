import pytest

"""PE adapter: census against the fixture catalog."""

from leadhs.models import FindingDraft, ProbeContext, SourceRef
from leadhs.probe.adapters import PEAdapter, ParseError


def _source(site, path="/"):
    return SourceRef(id="PE-1", class_code="PE", name="x", url=f"{site}{path}", access_method_code="scrape", active=1)


def _ctx(make_fetcher, conn, store, **kw):
    return ProbeContext(fetcher=make_fetcher(**kw.get("fetch_cfg", {})), store=store, conn=conn, sample_n=kw.get("sample_n", 3), dry_run=False)


def _findings(result, metric):
    return [f for f in result.findings if f.metric_code == metric]


def test_pe_census(site, conn, store, make_fetcher):
    result = PEAdapter().probe(_source(site), _ctx(make_fetcher, conn, store))
    metrics = {f.metric_code for f in result.findings}
    assert {"robots", "free_access", "rate_limit", "languages", "terms", "category_list",
            "category_count", "catalog_count", "page_sample_ok", "sds_sample_ok"} <= metrics
    catalog = _findings(result, "catalog_count")[0]
    assert catalog.value_numeric == 500
    # od9: category depth — /cat/wandfarben (2 products), /cat/grundierung
    # (0 products = queried, empty); /cat/broken (404) fails with a note.
    # Category path lives in the finding notes (R4 strict — no value_text).
    cat = _findings(result, "category_count")
    assert len(cat) == 2
    by_path = {f.notes.removeprefix("category path: "): f.value_numeric for f in cat}
    assert by_path == {"/cat/wandfarben": 2, "/cat/grundierung": 0}
    assert any("/cat/broken" in n and "404" in n for n in result.notes)
    assert _findings(result, "page_sample_ok")[0].value_numeric == 3  # 3 fetched (1 of 4 sample pages is 403)
    # base + 2 category pages + 3 sample pages archived (broken category: no doc)
    assert len(result.documents) == 6
    # languages detected from html lang + hreflang
    langs = _findings(result, "languages")[0].value_text
    assert "de" in langs and "fr" in langs
    # terms link found
    assert "terms" in _findings(result, "terms")[0].value_text
    # blocked sample page degrades, run continues
    sds = _findings(result, "sds_sample_ok")[0]
    assert sds.value_numeric >= 0


def test_pe_category_failure_continues(site, conn, store, make_fetcher):
    """A failing category page appends a note and the run continues."""
    result = PEAdapter().probe(_source(site), _ctx(make_fetcher, conn, store))
    notes = [n for n in result.notes if n.startswith("category")]
    assert notes and "HTTP 404" in notes[0]
    # the other categories still produced findings
    assert len(_findings(result, "category_count")) == 2


def test_pe_parse_error(site, conn, store, make_fetcher):
    with pytest.raises(ParseError):
        PEAdapter().probe(_source(site, "/empty.html"), _ctx(make_fetcher, conn, store))


def test_pe_dry_run_plans_only(site, conn, store, make_fetcher, monkeypatch):
    ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=conn, sample_n=2, dry_run=True)

    def no_network(*a, **kw):
        raise AssertionError("network in dry-run")

    monkeypatch.setattr(ctx.fetcher._session, "get", no_network)
    result = PEAdapter().probe(_source(site), ctx)
    assert result.documents == [] and result.findings == []

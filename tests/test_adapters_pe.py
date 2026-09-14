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
            "category_count", "catalog_count", "page_sample_ok", "sds_sample_ok",
            "products_listed", "doc_links_seen", "walk_budget_exhausted"} <= metrics
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
    # D28 walk metrics: 4 landing + 2 wandfarben product links (distinct);
    # SDS links seen on the two sampled product pages share one URL;
    # the fixture walk stays within the page budget.
    products = _findings(result, "products_listed")[0]
    assert products.value_numeric == 6
    docs_seen = _findings(result, "doc_links_seen")[0]
    assert docs_seen.value_numeric == 1
    assert _findings(result, "walk_budget_exhausted")[0].value_numeric == 0


def test_pe_budget_exhausted(site, conn, store, make_fetcher):
    """D28: a walk that hits the 12-page budget (incl. homepage) emits
    walk_budget_exhausted = 1 and stops fetching category pages."""
    result = PEAdapter().probe(_source(site, "/many-cats"), _ctx(make_fetcher, conn, store))
    budget = _findings(result, "walk_budget_exhausted")[0]
    assert budget.value_numeric == 1
    assert any("walk budget exhausted" in n for n in result.notes)
    # homepage + 11 category pages fetched (budget incl. homepage)
    assert len(result.documents) == 12
    # one product link per fetched category page; c12+ never visited
    assert _findings(result, "products_listed")[0].value_numeric == 11
    assert any("c12" in n for n in result.notes)


def test_pe_walk_depth_limit(site, conn, store, make_fetcher, site_hits):
    """D28: BFS depth <= 3 — the depth-4 category discovered on a depth-3
    page is never fetched."""
    result = PEAdapter().probe(_source(site, "/nested-cats"), _ctx(make_fetcher, conn, store))
    fetched_cats = {d.url for d in result.documents}
    assert any(u.endswith("/cat/n1") for u in fetched_cats)
    assert any(u.endswith("/cat/n1sub") for u in fetched_cats)
    assert any(u.endswith("/cat/n1subsub") for u in fetched_cats)
    assert not any(u.endswith("/cat/n1subsubsub") for u in fetched_cats)
    assert all(not u.endswith("/cat/n1subsubsub") for u in site_hits)
    # n1, n1sub, n1subsub each expose one product link
    assert _findings(result, "products_listed")[0].value_numeric == 3
    assert _findings(result, "walk_budget_exhausted")[0].value_numeric == 0


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


# --- v0.2.0 recon branch (nu1/i15; e1–e8) ---------------------------------


def _recon_ctx(make_fetcher, conn, store, **kw):
    return ProbeContext(fetcher=make_fetcher(**kw.get("fetch_cfg", {})), store=store, conn=conn,
                        mode="recon", dry_run=kw.get("dry_run", False))


def _host(site, i):
    port = site.rsplit(":", 1)[1]
    return f"127.0.0.{i}", f"http://127.0.0.{i}:{port}"


def _make_recon_source(site, i, notes=None, path="/"):
    ip, base = _host(site, i)
    return SourceRef(id="PR-1", class_code="PE", name="recon", url=f"{base}{path}",
                     access_method_code="scrape", active=1, notes=notes)


def test_recon_happy_path(site, conn, store, make_fetcher):
    """robots + declared sitemap fetched only; pattern token counts;
    sitemap archived; no cap flags."""
    src = _make_recon_source(site, 20, notes="channel=mfr; product_pattern=/product")
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["robots"].value_text == "allowed"
    assert m["sitemap_products"].value_numeric == 3
    assert "product_pattern=/product" in m["sitemap_products"].notes
    assert "floor partial" not in m["sitemap_products"].notes
    assert len(result.documents) == 1  # the sitemap
    assert result.documents[0].url.endswith("/sitemap.xml")


def test_recon_generic_fallback(site, conn, store, make_fetcher):
    src = _make_recon_source(site, 20)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 3
    assert "generic product-URL fallback" in m["sitemap_products"].notes


def test_recon_gzip_sitemap(site, conn, store, make_fetcher):
    """e4: gzipped sitemap decompressed via magic-byte sniff, counted."""
    src = _make_recon_source(site, 21)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 2
    assert any("gzipped" in n for n in result.notes)


def test_recon_namespaced_sitemap(site, conn, store, make_fetcher):
    """e5: namespaced tags counted via local names — never a silent 0."""
    src = _make_recon_source(site, 22)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 2


def test_recon_index_three_children(site, conn, store, make_fetcher):
    """1A: index + 3 children — children fetched, counts summed, one note."""
    src = _make_recon_source(site, 23)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 6
    assert any("index" in n for n in result.notes)
    assert "floor partial" not in m["sitemap_products"].notes
    assert len(result.documents) == 4  # index + 3 children


def test_recon_index_cap_at_five(site, conn, store, make_fetcher):
    """1A: index + 8 children — cap 5, floor-partial flag."""
    src = _make_recon_source(site, 24)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 10  # 5 children × 2
    assert "floor partial" in m["sitemap_products"].notes
    assert len(result.documents) == 6  # index + 5 children


def test_recon_nested_index_not_reursed(site, conn, store, make_fetcher):
    """e7: a nested sitemap-index child is noted, never recursed."""
    src = _make_recon_source(site, 25)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    # the nested index yields no product counts (not recursed)
    assert m["sitemap_products"].value_numeric == 0
    assert any("nested" in n or "sitemap index" in n for n in result.notes)
    assert all(not d.url.endswith("/deep.xml") for d in result.documents)


def test_recon_no_sitemap(site, conn, store, make_fetcher):
    src = _make_recon_source(site, 26)
    result = PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 0
    assert any("no sitemap" in n for n in result.notes)


def test_recon_robots_deny_blocks(site, conn, store, make_fetcher):
    from leadhs.fetch import RobotsDisallowed

    src = _make_recon_source(site, 2, path="/private/secret")
    with pytest.raises(RobotsDisallowed):
        PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))


def test_recon_robots_unreachable_proceeds(site, conn, store, make_fetcher):
    """e6: robots fetch fails (403 on robots_path) → policy unknown →
    proceed with note."""
    src = _make_recon_source(site, 20)
    ctx = _recon_ctx(make_fetcher, conn, store, fetch_cfg={"robots_path": "/robots-403.txt"})
    result = PEAdapter().probe(src, ctx)
    m = {f.metric_code: f for f in result.findings}
    assert m["robots"].value_text == "unknown"
    assert any("unknown" in n for n in result.notes)
    assert m["sitemap_products"].value_numeric == 3


def test_recon_malformed_sitemap(site, conn, store, make_fetcher):
    from leadhs.probe.adapters import UnexpectedFormat

    src = _make_recon_source(site, 28)
    with pytest.raises(UnexpectedFormat):
        PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))


def test_recon_size_cap_floor_partial(site, conn, store, monkeypatch, make_fetcher):
    """e3: oversized sitemap → SizeLimit → count 0 + floor-partial note."""
    from leadhs.probe import adapters
    from leadhs.probe.adapters import pe as pe_mod

    monkeypatch.setattr(pe_mod, "_RECON_MAX_BYTES", 1024)
    src = _make_recon_source(site, 27)
    result = adapters.PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store))
    m = {f.metric_code: f for f in result.findings}
    assert m["sitemap_products"].value_numeric == 0
    assert "floor partial" in m["sitemap_products"].notes


def test_recon_dry_run_zero_fetches(site, conn, store, make_fetcher, site_hits):
    """i7: dry-run plans robots + base only — zero network calls."""
    src = _make_recon_source(site, 20)
    PEAdapter().probe(src, _recon_ctx(make_fetcher, conn, store, dry_run=True))
    assert site_hits == {}

"""PE adapter — catalog walks and recon sweeps (manufacturer/retail sites).

v0.2.3 PHASE02 split (TODOS watch item): one adapter class per module;
the shared helpers live in ``_common.py``; the public import surface
stays ``leadhs.probe.adapters`` (package __init__ re-exports).
"""

from __future__ import annotations

import gzip
import json
import random
import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import urljoin

from ...fetch import FetchError, RobotsDisallowed, SizeLimit
from ...models import FindingDraft, ProbeResult, SourceRef
from ._common import ParseError, UnexpectedFormat, _doc, _log, _match_link, _soup

def _local(tag: str) -> str:
    """Namespace-local name (e5): '{http://www.sitemaps.org/...}loc' → 'loc'."""
    return tag.rsplit("}", 1)[-1]

# --- PE adapter (census) --------------------------------------------------


_CATEGORY_HINTS = ("/category", "/categorie", "/kategorien", "/cat/", "/shop/nav")
_PRODUCT_HINTS = ("/product", "/produkt", "/p/", "product_", "produkt_", "product=", "products/")
_SDS_HINTS = ("sds", "sicherheitsdatenblatt", "fiche", "safety", "msds")
_TERMS_HINTS = ("terms", "agb", "cgv", "bedingungen", "conditions", "imprint", "impressum")
_COUNT_RE = re.compile(r"(\d{1,3}(?:[\s'.\u2019]\d{3})*)\s+(?:products|produkte|artikel|items|results|resultats)", re.IGNORECASE)

# D28 walk mechanics: BFS over category pages, depth <= 3, page budget
# <= 12 pages including the homepage. Every fetch attempt (success or
# not) consumes budget; sample-page fetches stay governed by sample_n.
_WALK_MAX_DEPTH = 3
_WALK_PAGE_BUDGET = 12

# Doc-link heuristic for doc_links_seen (U13: "SDS/TDS-type links"):
# a link counts when its href or text contains one of these hints;
# distinct absolute URLs are counted.
_DOC_LINK_HINTS = ("sds", "msds", "sicherheitsdatenblatt", "datenblatt", "tds", "safety", "fiche")

# v0.2.0 recon (nu1/i15): robots-compliant, counts-only sitemap
# reconnaissance. 1A bound: at most 5 sitemap-index children; e3/3A:
# ~25 MB streaming cap per sitemap fetch (census/ST stay uncapped);
# e4: gzip magic-byte sniff; e5: namespace-local tag matching.
_RECON_INDEX_CHILD_CAP = 5
_RECON_MAX_BYTES = 25 * 1024 * 1024
_RECON_PRODUCT_FALLBACK = ("/product", "/p/")
_SITEMAP_URL_FALLBACK = "/sitemap.xml"


def _pattern_of(source: SourceRef) -> str:
    """The site's product-URL shape from the register notes token
    ``product_pattern=`` (i13 extension); generic fallback otherwise."""
    m = re.search(r"product_pattern=([^;]+)", source.notes or "")
    return m.group(1).strip() if m else ""


def _fetch_maybe_gzip(ctx, url: str, notes: list):
    """Structured fetch with the recon size cap; gzip payloads are
    decompressed via magic-byte sniff (e4). Returns (raw_bytes, resp)."""
    resp = ctx.fetcher.get(url, max_bytes=_RECON_MAX_BYTES)
    raw = resp.content
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
        notes.append(f"sitemap gzipped: {url}")
    return raw, resp


def _count_product_locs(raw: bytes, pattern: str) -> int:
    """Count <loc> entries whose URL matches the product pattern
    (e5: namespace-agnostic local-name matching — a namespaced sitemap
    must never silently count 0)."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        raise
    pat = pattern.lower()
    fallback = not pat
    count = 0
    for el in root.iter():
        if _local(el.tag) != "loc" or not el.text:
            continue
        url = el.text.strip().lower()
        if fallback:
            if any(h in url for h in _RECON_PRODUCT_FALLBACK):
                count += 1
        elif pat in url:
            count += 1
    return count


_SDS_DOC_HINTS = ("sds", "msds", "sicherheitsdatenblatt", "sicherheitsdatenblatt", "safety-data", "tds", "datenblatt", "fiche")


def _count_sds_doc_locs(raw: bytes) -> int:
    """Count <loc> entries whose URL looks like an SDS/TDS document
    (v0.2.2 fu6, W3) — counts only, no URL harvesting (D31)."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return 0
    count = 0
    for el in root.iter():
        if _local(el.tag) != "loc" or not el.text:
            continue
        url = el.text.strip().lower()
        if any(h in url for h in _SDS_DOC_HINTS):
            count += 1
    return count
class PEAdapter:
    key = "PE"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "PE"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
        if ctx.mode == "recon":
            return self._probe_recon(source, ctx)
        if ctx.dry_run:
            ctx.fetcher.plan(source.url)
            return ProbeResult()
        base = source.url
        resp = ctx.fetcher.get(base)
        _log(ctx, "pe_get", url=base, status=resp.status_code)
        docs = [_doc(base, resp, retrieval_method_code="scrape")]
        findings = [
            FindingDraft(metric_code="robots", method_code="scrape", value_text=ctx.fetcher.robots_policy(base)),
            FindingDraft(metric_code="free_access", method_code="scrape", value_numeric=1),
        ]
        notes = []
        soup = _soup(resp)
        if not soup.find("body") or not (soup.get_text(" ", strip=True) or ""):
            raise ParseError("empty or unparseable page", partial=ProbeResult(documents=docs, findings=findings), url=base)

        findings.append(FindingDraft(metric_code="rate_limit", method_code="scrape", value_text="unknown — polite default <= 1 req / 2 s"))

        langs = self._languages(soup, resp)
        findings.append(FindingDraft(metric_code="languages", method_code="scrape", value_text=json.dumps(langs)))

        terms = _match_link(soup, [], text_patterns=_TERMS_HINTS)
        findings.append(FindingDraft(metric_code="terms", method_code="scrape", value_text=terms and f"link present: {terms}" or "not found"))

        categories = self._categories(soup, base)
        findings.append(FindingDraft(metric_code="category_list", method_code="scrape", value_text=json.dumps(categories)))

        product_links = self._product_links(soup, base)
        product_urls: set = set()
        doc_urls: set = set()
        self._scan(soup, base, product_urls, doc_urls)

        # D28 walk: BFS over category pages, depth <= 3, page budget
        # <= 12 pages incl. homepage; polite spacing is enforced by the
        # fetcher. A failing category page appends a note and continues
        # (sample-page pattern); budget exhaustion is recorded as the
        # numeric walk_budget_exhausted metric (ENG review 2A — no note
        # substrings), the note only carries context.
        queue = [(u, 1) for u in categories]
        visited = {base}
        fetched = 1  # the homepage
        budget_exhausted = False
        while queue:
            cat_url, depth = queue.pop(0)
            if cat_url in visited:
                continue
            if depth > _WALK_MAX_DEPTH:
                continue
            if fetched >= _WALK_PAGE_BUDGET:
                budget_exhausted = True
                skipped = [u for u, _ in queue if u not in visited]
                notes.append(
                    f"walk budget exhausted ({fetched} pages incl. homepage); "
                    f"{len(skipped) + 1} category page(s) not visited, e.g. {cat_url}"
                )
                break
            visited.add(cat_url)
            fetched += 1
            try:
                cat_resp = ctx.fetcher.get(cat_url)
            except FetchError as exc:
                notes.append(f"category {cat_url}: {exc.__class__.__name__}")
                continue
            if cat_resp.status_code != 200:
                notes.append(f"category {cat_url}: HTTP {cat_resp.status_code}")
                continue
            docs.append(_doc(cat_url, cat_resp, retrieval_method_code="scrape"))
            cat_soup = _soup(cat_resp)
            self._scan(cat_soup, base, product_urls, doc_urls)
            cat_products = self._product_links(cat_soup, base)
            findings.append(
                FindingDraft(
                    metric_code="category_count",
                    method_code="scrape",
                    value_numeric=len(cat_products),
                    unit_code="count",
                    # category path lives in notes — R4 stays strict
                    # (numeric metrics carry no value_text); interfaces.md
                    # vocabulary row clarified accordingly
                    notes=f"category path: {urllib.parse.urlparse(cat_url).path or cat_url}",
                    document=docs[-1],
                )
            )
            if depth < _WALK_MAX_DEPTH:
                queue.extend((u, depth + 1) for u in self._categories(cat_soup, base))

        catalog_count = self._catalog_count(soup) or (len(product_links) if product_links else None)
        if catalog_count:
            findings.append(FindingDraft(metric_code="catalog_count", method_code="scrape", value_numeric=catalog_count, unit_code="count"))
        notes.append(f"walk: {fetched} page(s) fetched, categories={len(categories)}")

        # D28 walk metrics (numeric, per pe4/U13): products_listed and
        # doc_links_seen are floors over the pages actually visited;
        # walk_budget_exhausted flags a budget-limited (weaker) floor.
        findings.append(FindingDraft(metric_code="products_listed", method_code="scrape", value_numeric=len(product_urls), unit_code="count"))
        findings.append(FindingDraft(metric_code="walk_budget_exhausted", method_code="scrape", value_numeric=1 if budget_exhausted else 0))

        if product_links and not ctx.dry_run:
            rng = random.Random(f"pe-sample-{source.id}")
            rng.shuffle(product_links)
            sample = product_links[: ctx.sample_n]
            ok, sds_ok = 0, 0
            for url in sample:
                try:
                    page = ctx.fetcher.get(url)
                    docs.append(_doc(url, page, retrieval_method_code="scrape"))
                    ok += 1
                    page_soup = _soup(page)
                    self._scan(page_soup, base, product_urls, doc_urls)
                    if _match_link(page_soup, _SDS_HINTS):
                        sds_ok += 1
                except FetchError as exc:
                    notes.append(f"sample {url}: {exc.__class__.__name__}")
            findings.append(FindingDraft(metric_code="page_sample_ok", method_code="scrape", value_numeric=ok, unit_code="count", notes=f"{ok}/{len(sample)}"))
            findings.append(FindingDraft(metric_code="sds_sample_ok", method_code="scrape", value_numeric=sds_ok, unit_code="count", notes=f"{sds_ok}/{len(sample)}"))
        elif product_links:
            for url in product_links[: ctx.sample_n]:
                ctx.fetcher.plan(url)
            notes.append("dry-run: planned sample page fetches")

        findings.append(FindingDraft(metric_code="doc_links_seen", method_code="scrape", value_numeric=len(doc_urls), unit_code="count"))

        return ProbeResult(documents=docs, findings=findings, notes=notes)

    def _scan(self, soup, base, product_urls: set, doc_urls: set) -> None:
        """Accumulate the distinct product/doc links seen on one page.

        Doc-link heuristic (U13 "SDS/TDS-type links"): the link's href
        or text contains one of _DOC_LINK_HINTS; distinct absolute URLs
        are counted.
        """
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(" ", strip=True).lower()
            if any(h in href for h in _PRODUCT_HINTS):
                product_urls.add(urljoin(base, a["href"]))
            if any(h in href or h in text for h in _DOC_LINK_HINTS):
                doc_urls.add(urljoin(base, a["href"]))

    def _languages(self, soup, resp) -> list:
        langs = set()
        html_lang = soup.find("html", lang=True)
        if html_lang and html_lang.get("lang"):
            langs.add(html_lang["lang"].split("-")[0].lower())
        for link in soup.find_all("link", href=True, hreflang=True):
            lang = link.get("hreflang", "").split("-")[0].lower()
            if len(lang) == 2:
                langs.add(lang)
        for a in soup.find_all("a", href=True):
            m = re.search(r"[?&]lang=([a-z]{2})", a["href"].lower())
            if m:
                langs.add(m.group(1))
        return sorted(langs)

    def _categories(self, soup, base) -> list:
        seen = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(h in href for h in _CATEGORY_HINTS) and href not in seen:
                seen.append(a["href"])
        return [urljoin(base, u) for u in seen[:50]]

    def _product_links(self, soup, base) -> list:
        seen = []
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(h in href for h in _PRODUCT_HINTS) and href not in seen:
                seen.append(a["href"])
        return [urljoin(base, u) for u in seen[:100]]

    def _catalog_count(self, soup) -> Optional[int]:
        text = soup.get_text(" ", strip=True)
        m = _COUNT_RE.search(text)
        if m:
            digits = re.sub(r"[^\d]", "", m.group(1))
            if digits:
                return int(digits)
        return None

    # --- v0.2.0 recon branch (nu1/i15) -----------------------------------

    @staticmethod
    def _robots_url_of(base: str) -> str:
        parts = urllib.parse.urlparse(base)
        return urllib.parse.urlunparse((parts.scheme, parts.netloc, "/robots.txt", "", "", ""))

    def _probe_recon(self, source: SourceRef, ctx) -> ProbeResult:
        """Robots-compliant, counts-only sitemap reconnaissance (D31):
        no URL harvesting, no page walking. Dry-run plans robots + base
        only — zero fetches (i7)."""
        docs, findings, notes = [], [], []
        base = source.url

        if ctx.dry_run:
            ctx.fetcher.plan(base)
            ctx.fetcher.plan(self._robots_url_of(base))
            return ProbeResult()

        # robots policy — e6: unreachable → "unknown" → proceed with note
        try:
            policy = ctx.fetcher.robots_policy(base)
        except FetchError as exc:
            policy = "unknown"
            notes.append(f"robots unreachable ({exc.__class__.__name__}) — proceeding with policy unknown (e6)")
        findings.append(FindingDraft(metric_code="robots", method_code="scrape", value_text=policy))
        if policy == "disallowed":
            raise RobotsDisallowed(base, "robots.txt disallows our paths")

        # sitemap discovery: robots-declared Sitemap: lines, else /sitemap.xml
        sitemap_urls = self._declared_sitemaps(ctx, base, notes)
        if not sitemap_urls:
            parts = urllib.parse.urlparse(base)
            sitemap_urls = [
                urllib.parse.urlunparse((parts.scheme, parts.netloc, _SITEMAP_URL_FALLBACK, "", "", ""))
            ]
            notes.append(f"no robots-declared sitemap — trying {_SITEMAP_URL_FALLBACK}")

        pattern = _pattern_of(source)
        pattern_note = f"product_pattern={pattern}" if pattern else "generic product-URL fallback (no register token)"
        total = 0
        sds_docs = 0
        fetches = 0
        children_fetched = 0
        cap_hit = False
        queue = [(u, 0) for u in sitemap_urls]
        seen: set = set()
        while queue:
            if fetches >= 1 + _RECON_INDEX_CHILD_CAP:
                cap_hit = True
                notes.append(f"index expansion cap {_RECON_INDEX_CHILD_CAP} reached — floor partial (1A)")
                break
            surl, depth = queue.pop(0)
            if surl in seen:
                continue
            seen.add(surl)
            fetches += 1
            try:
                raw, resp = _fetch_maybe_gzip(ctx, surl, notes)
            except SizeLimit:
                cap_hit = True
                notes.append(f"sitemap capped at {_RECON_MAX_BYTES} bytes — floor partial (e3): {surl}")
                continue
            if resp.status_code != 200:
                notes.append(f"sitemap HTTP {resp.status_code}: {surl}")
                continue
            docs.append(_doc(surl, resp, retrieval_method_code="scrape"))
            try:
                root = ET.fromstring(raw)
            except ET.ParseError as exc:
                raise UnexpectedFormat(
                    f"sitemap unparseable: {exc}",
                    partial=ProbeResult(documents=docs, findings=findings),
                    url=surl,
                )
            if _local(root.tag) == "sitemapindex":
                if depth >= 1:
                    # e7: a nested index child is noted, never recursed
                    notes.append(f"nested sitemap index (child of an index) — not recursed: {surl}")
                    continue
                child_locs = [
                    el.text.strip() for el in root.iter()
                    if _local(el.tag) == "loc" and el.text and el.text.strip()
                ]
                remaining = _RECON_INDEX_CHILD_CAP - children_fetched
                take = child_locs[:remaining]
                children_fetched += len(take)
                if len(child_locs) > len(take):
                    cap_hit = True
                    notes.append(
                        f"sitemap index with {len(child_locs)} children — fetching {len(take)}, "
                        f"cap {_RECON_INDEX_CHILD_CAP} — floor partial (1A)"
                    )
                else:
                    notes.append(f"sitemap index: {len(take)} child sitemap(s) fetched")
                queue.extend((urljoin(surl, c), depth + 1) for c in take)
                continue
            total += _count_product_locs(raw, pattern)
            sds_docs += _count_sds_doc_locs(raw)

        if not docs and not cap_hit:
            notes.append("no sitemap")
        findings.append(
            FindingDraft(
                metric_code="sitemap_products",
                method_code="scrape",
                value_numeric=total,
                unit_code="count",
                notes="; ".join([pattern_note] + ["floor partial (index/size cap)"] if cap_hit else [pattern_note]),
            )
        )
        # v0.2.2 (fu-metrics/fu6, W3): SDS/TDS document URLs visible per
        # site — counts only (no URL harvesting beyond the existing rule);
        # the Q3 SDS-reach input.
        findings.append(
            FindingDraft(
                metric_code="sds_doc_urls",
                method_code="scrape",
                value_numeric=sds_docs,
                unit_code="count",
                notes="sitemap-visible SDS/TDS document URLs (counts only)",
            )
        )
        return ProbeResult(documents=docs, findings=findings, notes=notes)

    def _declared_sitemaps(self, ctx, base: str, notes: list) -> list:
        """Sitemap: lines from robots.txt (fetched once more for its
        content; the parser itself is cached in the fetcher). Any fetch
        problem here is not fatal — discovery falls back to /sitemap.xml."""
        robots_url = self._robots_url_of(base)
        try:
            resp = ctx.fetcher.get(robots_url)
        except FetchError as exc:
            notes.append(f"robots content unavailable ({exc.__class__.__name__}) — discovery falls back")
            return []
        if resp.status_code != 200:
            return []
        urls = []
        for line in resp.text.splitlines():
            line = line.strip()
            if line.lower().startswith("sitemap:"):
                declared = line.split(":", 1)[1].strip()
                if declared:
                    urls.append(urljoin(base, declared))
        return urls

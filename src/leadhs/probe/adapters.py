"""Adapter registry and typed adapter errors.

Error taxonomy (interfaces.md): ``UnexpectedFormat`` (export layout
not as expected), ``BinaryMissing`` / ``ExtractionError`` (mdbtools
absent / SPIN extraction fails), ``ParseError`` (unparseable/empty
HTML). The engine maps them to findings. Adapters may carry a
partial ``ProbeResult`` on the error so findings collected before a
block are preserved (outcome rule: reachable with findings -> done).
"""

from __future__ import annotations

import csv
import io
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import urllib.parse
from typing import Optional, Protocol
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..fetch import Blocked, FetchError, FetchResponse
from ..logutil import log_event
from ..models import DocumentDraft, FindingDraft, ProbeResult, SourceRef

__all__ = [
    "AdapterError",
    "UnexpectedFormat",
    "BinaryMissing",
    "ExtractionError",
    "ParseError",
    "ProbeAdapter",
    "registry",
    "get_adapter",
    "register",
]


class AdapterError(Exception):
    def __init__(
        self,
        detail: str,
        partial: Optional[ProbeResult] = None,
        url: Optional[str] = None,
    ):
        self.detail = detail
        self.partial = partial
        self.url = url
        super().__init__(detail)


class UnexpectedFormat(AdapterError):
    pass


class BinaryMissing(AdapterError):
    pass


class ExtractionError(AdapterError):
    pass


class ParseError(AdapterError):
    pass


class ProbeAdapter(Protocol):
    key: str  # source class: 'CS' | 'PE' | 'ST'

    def supports(self, source: SourceRef) -> bool: ...

    def probe(self, source: SourceRef, ctx: object) -> ProbeResult: ...


registry: list = []


def get_adapter(source: SourceRef):
    for adapter in registry:
        if adapter.supports(source):
            return adapter
    return None


def register(adapter):
    registry.append(adapter)
    return adapter


# --- shared helpers -----------------------------------------------------


def _log(ctx, event, **fields):
    if ctx.logger is not None:
        log_event(ctx.logger, "adapter", event, **fields)


def _doc(url: str, resp: FetchResponse, **kw) -> DocumentDraft:
    return DocumentDraft(
        url=url,
        content=resp.content,
        content_type=resp.headers.get("Content-Type"),
        **kw,
    )


def _match_link(soup: BeautifulSoup, patterns, text_patterns=None) -> Optional[str]:
    text_patterns = text_patterns or []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(" ", strip=True).lower()
        if any(p in href for p in patterns) or any(p in text for p in text_patterns):
            return a["href"]
    return None


def _soup(resp: FetchResponse) -> BeautifulSoup:
    return BeautifulSoup(resp.text, "html.parser")


# --- CS adapter (exports) ------------------------------------------------


_EXPECTED_EXPORT_COLUMNS = {"hs_code", "year", "partner"}
_JSON_LIST_COUNTS = ("value", "obs", "records", "observations", "data")

# od9: parameterized CS-2 query — documented constants with defaults
# fixed here (exact values pinned at census execution); the parameters
# land in run.parameters_json via ProbeResult.parameters, and every
# response is archived as a document (verification artifact).
_CS_QUERY_DEFAULTS = {
    "format": "JSON",
    "freq": "A",
    "period": "2024",
    "flow": "IMP",
    "reporter": "EU27_2020",
}
_HS_CODES = ("3208", "3209", "3213")


def _query_url(base: str, params: dict) -> str:
    from urllib.parse import urlencode

    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode(params)}"


class CSAdapter:
    key = "CS"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "CS"

    def _is_query_api(self, source: SourceRef) -> bool:
        return source.access_method_code == "api"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
        if ctx.dry_run:
            if self._is_query_api(source):
                for hs in _HS_CODES:
                    ctx.fetcher.plan(_query_url(source.url, {**_CS_QUERY_DEFAULTS, "product": hs}))
            else:
                ctx.fetcher.plan(source.url)
            return ProbeResult()
        if self._is_query_api(source):
            return self._probe_query_api(source, ctx)
        resp = ctx.fetcher.get(source.url)
        _log(ctx, "cs_get", url=source.url, status=resp.status_code)
        docs = [_doc(source.url, resp, retrieval_method_code=source.access_method_code or "scrape")]
        findings = []
        notes = []
        ct = resp.headers.get("Content-Type", "")
        text = resp.text
        if "csv" in ct.lower() or (text.lstrip()[:1] in ('"', ";") and "," in text[:500]):
            findings += self._probe_csv(source, resp, ctx, docs, notes)
        elif "json" in ct.lower() or text.lstrip()[:1] in ("{", "["):
            findings += self._probe_json(source, resp, ctx, docs, notes)
        else:
            findings.append(FindingDraft(metric_code="format", method_code=source.access_method_code or "scrape", value_text="web UI (HTML); export via UI, layout to confirm"))
            findings.append(FindingDraft(metric_code="granularity", method_code=source.access_method_code or "scrape", value_text="to confirm at manual review (probe)"))
            findings.append(FindingDraft(metric_code="free_access", method_code=source.access_method_code or "scrape", value_numeric=1, unit_code=None))
            notes.append("landing page reached; export mechanics to confirm manually")
        return ProbeResult(documents=docs, findings=findings, notes=notes)

    def _probe_query_api(self, source: SourceRef, ctx) -> ProbeResult:
        """od9: one parameterized JSON query per HS heading; each response
        archived; empty result set is an honest 0."""
        docs, findings, notes = [], [], []
        query_params = {}
        for hs in _HS_CODES:
            params = {**_CS_QUERY_DEFAULTS, "product": hs}
            query_params[hs] = params
            url = _query_url(source.url, params)
            resp = ctx.fetcher.get(url)
            _log(ctx, "cs_query", url=url, status=resp.status_code, hs=hs)
            docs.append(_doc(url, resp, retrieval_method_code="api"))
            try:
                data = json.loads(resp.text)
            except ValueError:
                raise UnexpectedFormat(
                    f"HS {hs}: expected JSON but content not parseable",
                    partial=ProbeResult(documents=docs, findings=findings),
                    url=url,
                )
            rows = self._rows_of(data)
            findings.append(
                FindingDraft(
                    metric_code=f"records_hs{hs}",
                    method_code="api",
                    value_numeric=len(rows),
                    unit_code="count",
                    document=docs[-1],
                    notes=f"query params: {json.dumps(params, sort_keys=True)}",
                )
            )
            notes.append(f"HS {hs}: {len(rows)} rows")
        return ProbeResult(documents=docs, findings=findings, notes=notes, parameters={"query": query_params})

    @staticmethod
    def _rows_of(data) -> list:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in _JSON_LIST_COUNTS:
                if isinstance(data.get(key), list):
                    return data[key]
            for value in data.values():
                if isinstance(value, list):
                    return value
        return []

    def _probe_csv(self, source, resp, ctx, docs, notes):
        reader = csv.reader(io.StringIO(resp.text))
        rows = [r for r in reader if any(c.strip() for c in r)]
        if not rows:
            raise UnexpectedFormat("empty CSV export", partial=ProbeResult(documents=docs, findings=[]), url=source.url)
        header = [c.strip().lower() for c in rows[0]]
        norm = {re.sub(r"[^a-z0-9_]", "", c) for c in header}
        missing = _EXPECTED_EXPORT_COLUMNS - norm
        if missing:
            raise UnexpectedFormat(
                f"export layout missing expected columns {sorted(missing)} (got {header})",
                partial=ProbeResult(documents=docs, findings=[]),
                url=source.url,
            )
        findings = [
            FindingDraft(metric_code="format", method_code="download", value_text=f"CSV; columns: {', '.join(header)}"),
            FindingDraft(metric_code="export_rows", method_code="download", value_numeric=max(0, len(rows) - 1), unit_code="count"),
            FindingDraft(metric_code="free_access", method_code="download", value_numeric=1),
            FindingDraft(metric_code="granularity", method_code="download", value_text="CN8 x partner x year (observed columns)"),
            FindingDraft(metric_code="coverage_years", method_code="download", value_text="to confirm (year column present)"),
        ]
        notes.append(f"CSV export checked: {len(rows)-1} rows")
        return findings

    def _probe_json(self, source, resp, ctx, docs, notes):
        try:
            data = json.loads(resp.text)
        except ValueError:
            raise UnexpectedFormat("expected JSON but content not parseable", partial=ProbeResult(documents=docs, findings=[]), url=source.url)
        count = None
        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict):
            for key in _JSON_LIST_COUNTS:
                if isinstance(data.get(key), list):
                    count = len(data[key])
                    break
            if count is None:
                for value in data.values():
                    if isinstance(value, list):
                        count = len(value)
                        break
        findings = [
            FindingDraft(metric_code="format", method_code="api", value_text="JSON (API)"),
            FindingDraft(metric_code="free_access", method_code="api", value_numeric=1),
            FindingDraft(metric_code="granularity", method_code="api", value_text="to confirm from JSON structure (probe)"),
        ]
        if count is not None:
            findings.append(FindingDraft(metric_code="export_rows", method_code="api", value_numeric=count, unit_code="count"))
        notes.append("JSON API reached; structure re-check at census")
        return findings


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


class PEAdapter:
    key = "PE"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "PE"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
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


# --- ST adapter (SPIN download + extraction check) -------------------------


_ST_DOWNLOAD_HINTS = ("page_id=54", ".mdb", ".zip", "access", "download", "datenbank")
_MDB_BINARIES = ("mdb-export", "mdb-tables")


class STAdapter:
    key = "ST"

    def supports(self, source: SourceRef) -> bool:
        return source.class_code == "ST"

    def probe(self, source: SourceRef, ctx) -> ProbeResult:
        if ctx.dry_run:
            ctx.fetcher.plan(source.url)
            return ProbeResult()
        base = source.url
        resp = ctx.fetcher.get(base)
        _log(ctx, "st_get", url=base, status=resp.status_code)
        docs = [_doc(base, resp, retrieval_method_code="download")]
        findings = [
            FindingDraft(metric_code="robots", method_code="download", value_text=ctx.fetcher.robots_policy(base)),
            FindingDraft(metric_code="format", method_code="download", value_text="web site + free Access-DB download"),
            FindingDraft(metric_code="free_access", method_code="download", value_numeric=1),
        ]
        notes = []

        soup = _soup(resp)
        db_link = _match_link(soup, _ST_DOWNLOAD_HINTS)
        if not db_link:
            findings.append(FindingDraft(metric_code="extraction_path", method_code="manual", value_text="no Access-DB download link found on landing page"))
            notes.append("download link not found on landing page")
            return ProbeResult(documents=docs, findings=findings, notes=notes)

        dl_url = urljoin(base, db_link)
        try:
            dl_resp = ctx.fetcher.get(dl_url)
        except Blocked as exc:
            raise Blocked(dl_url, f"download blocked: {exc.detail}")
        _log(ctx, "st_download", url=dl_url, status=dl_resp.status_code, bytes=len(dl_resp.content))
        ext = "mdb" if ".mdb" in dl_url.lower() else ("zip" if ".zip" in dl_url.lower() else "bin")
        docs.append(_doc(dl_url, dl_resp, retrieval_method_code="download"))

        binary = next((b for b in _MDB_BINARIES if shutil.which(b)), None)
        if binary is None:
            raise BinaryMissing(
                "mdbtools not on PATH (mdb-export/mdb-tables absent)",
                partial=ProbeResult(documents=docs, findings=findings),
                url=base,
            )

        with tempfile.NamedTemporaryFile(suffix=".mdb", delete=False) as tmp:
            tmp.write(dl_resp.content)
            tmp_path = tmp.name
        try:
            out = subprocess.run([binary, "-1", tmp_path], capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            raise ExtractionError("mdb extraction timed out", partial=ProbeResult(documents=docs, findings=findings), url=base)
        except OSError as exc:
            raise BinaryMissing(f"mdbtools failed to run: {exc}", partial=ProbeResult(documents=docs, findings=findings), url=base)
        finally:
            os.unlink(tmp_path)
        if out.returncode != 0:
            raise ExtractionError(
                f"{binary} exit {out.returncode}: {out.stderr.decode(errors='replace')[:200]}",
                partial=ProbeResult(documents=docs, findings=findings),
                url=base,
            )
        tables = out.stdout.decode(errors="replace").splitlines()
        findings.append(FindingDraft(metric_code="extraction_path", method_code="download", value_text=f"mdbtools ok ({binary}); tables: {', '.join(tables[:10])}"))
        notes.append(f"extracted {len(tables)} tables")
        return ProbeResult(documents=docs, findings=findings, notes=notes)


register(CSAdapter())
register(PEAdapter())
register(STAdapter())
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
import gzip
import io
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional, Protocol
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..fetch import Blocked, FetchError, FetchResponse, RobotsDisallowed, SizeLimit
from ..logutil import log_event
from ..models import DocumentDraft, FindingDraft, ProbeResult, SourceRef

__all__ = [
    "AdapterError",
    "UnexpectedFormat",
    "BinaryMissing",
    "ExtractionError",
    "ParseError",
    "SizeLimit",
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
# fixed here (pinned at census execution 2026-09-12 against the live
# DS-045409 API: time dimension `time`, import flow code `1`,
# indicators QUANTITY_IN_100KG / VALUE_IN_EUROS); the parameters land
# in run.parameters_json via ProbeResult.parameters, and every response
# is archived as a document (verification artifact).
_CS_QUERY_DEFAULTS = {
    "format": "JSON",
    "freq": "A",
    "time": "2024",
    "flow": "1",
    "reporter": "EU27_2020",
}
_HS_CODES = ("3208", "3209", "3213")
# nu2 aggregation: the four trade-sum anchors ride HS 3208/3209 only
# (3213 stays the census annex).
_AGG_HS_CODES = ("3208", "3209")
_CS_AGG_INDICATORS = (
    ("kg", "QUANTITY_IN_100KG"),
    ("eur", "VALUE_IN_EUROS"),
)


def _query_url(base: str, params: dict) -> str:
    from urllib.parse import urlencode

    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode(params)}"


def _agg_params(hs: str, indicator: str, year: str) -> dict:
    """Full-year import aggregation query (nu2): flow + resolved year
    land in run.parameters_json; with reporter/product/flow/indicators/
    time pinned, partner is the only free dimension (all partners)."""
    return {
        **_CS_QUERY_DEFAULTS,
        "product": hs,
        "indicators": indicator,
        "time": year,
    }


def _local(tag: str) -> str:
    """Namespace-local name (e5): '{http://www.sitemaps.org/...}loc' → 'loc'."""
    return tag.rsplit("}", 1)[-1]


def _jsonstat_one_dim(data: dict) -> list:
    """Minimal JSON-stat decoder (e2/decision 2A): `value` is an object
    keyed by flat row index (row-major over id×size); with exactly one
    free dimension, map each index back to that dimension's label.
    Deliberately NOT a general reader (TODOS.md) — PRODCOM/SBS callers
    generalize it."""
    try:
        dim_ids = data["id"]
        sizes = data["size"]
        value_obj = data["value"]
    except (KeyError, TypeError):
        raise UnexpectedFormat("not a JSON-stat dataset payload (id/size/value missing)")
    if not isinstance(value_obj, dict):
        raise UnexpectedFormat("JSON-stat value is not an object keyed by flat index")
    free = [(i, d) for i, (d, s) in enumerate(zip(dim_ids, sizes)) if s > 1]
    if len(free) != 1:
        raise UnexpectedFormat(
            f"decoder supports exactly one free dimension, got {[d for _, d in free]}"
        )
    free_pos, free_dim = free[0]
    labels = _jsonstat_category_labels(data, free_dim)
    if len(labels) != sizes[free_pos]:
        raise UnexpectedFormat(f"dimension {free_dim}: label count != declared size")
    pairs = []
    for key, raw in value_obj.items():
        try:
            flat = int(key)
        except (TypeError, ValueError):
            continue
        if raw is None:
            continue
        rest = flat
        coords = []
        for s in reversed(sizes):
            coords.append(rest % s)
            rest //= s
        coords.reverse()
        label_pos = coords[free_pos]
        if label_pos < len(labels):
            pairs.append((labels[label_pos], float(raw)))
    return pairs


def _jsonstat_category_labels(data: dict, dim: str) -> list:
    cat = data.get("dimension", {}).get(dim, {}).get("category", {})
    index = cat.get("index", {})
    if isinstance(index, dict):
        return [k for k, _ in sorted(index.items(), key=lambda kv: kv[1])]
    return list(index)


def _jsonstat_sum(pairs: list) -> tuple:
    total = sum(v for _, v in pairs)
    tops = sorted(pairs, key=lambda kv: kv[1], reverse=True)[:5]
    return total, tops


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
                # nu2/e7: the aggregation queries are part of the plan
                for hs in _AGG_HS_CODES:
                    for _, indicator in _CS_AGG_INDICATORS:
                        ctx.fetcher.plan(_query_url(source.url, _agg_params(hs, indicator, _CS_QUERY_DEFAULTS["time"])))
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
        archived; empty result set is an honest 0. v0.2.0 (nu2): plus the
        full-year import aggregation for HS 3208/3209 — trade_kg/eur sums
        via the minimal one-dimension JSON-stat decoder (e2/2A)."""
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
            is_jsonstat = isinstance(data, dict) and "id" in data and "size" in data
            findings.append(
                FindingDraft(
                    metric_code="format",
                    method_code="api",
                    value_text="JSON-stat dataset" if is_jsonstat else "JSON (API)",
                )
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
        findings += self._aggregate(source, ctx, docs, query_params, notes)
        return ProbeResult(documents=docs, findings=findings, notes=notes, parameters={"query": query_params})

    def _aggregate(self, source, ctx, docs, query_params, notes) -> list:
        """nu2: per HS × indicator, full-year import sums with a bounded
        year step-back (e7): empty → previous year, max 3 tries; exhausted
        → documented-blocked. Partner tops + supplementary units land in
        the finding notes; raw JSON is archived."""
        findings = []
        base_year = int(_CS_QUERY_DEFAULTS["time"])
        for hs in _AGG_HS_CODES:
            for unit_name, indicator in _CS_AGG_INDICATORS:
                year = base_year
                tries = 0
                total, tops = None, []
                while tries < 3:
                    params = _agg_params(hs, indicator, str(year))
                    query_params[f"{hs}_{unit_name}_{year}"] = params
                    url = _query_url(source.url, params)
                    resp = ctx.fetcher.get(url)
                    _log(ctx, "cs_agg", url=url, status=resp.status_code, hs=hs, unit=unit_name, year=year)
                    docs.append(_doc(url, resp, retrieval_method_code="api"))
                    try:
                        data = json.loads(resp.text)
                    except ValueError:
                        raise UnexpectedFormat(
                            f"HS {hs} {unit_name}: expected JSON-stat but content not parseable",
                            partial=ProbeResult(documents=docs, findings=findings),
                            url=url,
                        )
                    try:
                        pairs = _jsonstat_one_dim(data)
                    except UnexpectedFormat as exc:
                        exc.partial = ProbeResult(documents=docs, findings=findings)
                        exc.url = url
                        raise
                    if pairs:
                        total, tops = _jsonstat_sum(pairs)
                        if indicator == "QUANTITY_IN_100KG":
                            # the API's supplementary unit is 100 kg —
                            # convert to the metric's kg and say so
                            total = total * 100
                        tops_txt = ", ".join(f"{lab}={val:.0f}" for lab, val in tops)
                        notes.append(
                            f"HS {hs} {unit_name} {year}: sum across partners "
                            f"(indicators={indicator}); top partners: {tops_txt}"
                        )
                        break
                    tries += 1
                    if tries < 3:
                        notes.append(f"HS {hs} {unit_name}: empty for {year} — stepping back a year (e7)")
                        year -= 1
                metric = f"trade_{unit_name}_hs{hs}"
                if total is None:
                    notes.append(f"HS {hs} {unit_name}: no data for {base_year}..{year} — documented blocked (e7)")
                    findings.append(
                        FindingDraft(
                            metric_code=metric,
                            method_code="api",
                            value_numeric=0,
                            unit_code=unit_name,
                            notes=f"empty for {base_year}..{base_year - 2} (step-back exhausted) — query family blocked, verify at od9",
                        )
                    )
                else:
                    unit_note = "; quantity converted from QUANTITY_IN_100KG (×100)" if indicator == "QUANTITY_IN_100KG" else ""
                    findings.append(
                        FindingDraft(
                            metric_code=metric,
                            method_code="api",
                            value_numeric=total,
                            unit_code=unit_name,
                            document=docs[-1],
                            notes=f"flow=1 (import), year={year}, indicators={indicator}; sum across partners; top partners: {tops_txt}{unit_note}",
                        )
                    )
        return findings

    @staticmethod
    def _rows_of(data) -> list:
        # JSON-stat datasets: the record count is the number of queried
        # cells (value object keyed by flat index, e2/2A shape)
        if isinstance(data, dict) and "id" in data and "size" in data:
            value = data.get("value")
            if isinstance(value, dict):
                return list(value.items())
            if isinstance(value, list):
                return value
            return []
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
"""probe-metric vocabulary — the runtime source of truth.

Authoritative table: 20_DESIGN/MASTER/interfaces.md §probe_metric
vocabulary. Migration 0001 + 0003 + 0004 seeds are pinned to this
list by a sync test (t6); new metrics enter via a migration INSERT,
codes are never renamed, value_type is fixed at insert (i4).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Metric:
    code: str
    label: str
    value_type: str  # 'numeric' | 'text'


METRIC_CATALOG_COUNT = "catalog_count"
METRIC_CATEGORY_COUNT = "category_count"
METRIC_CATEGORY_LIST = "category_list"
METRIC_FORMAT = "format"
METRIC_GRANULARITY = "granularity"
METRIC_COVERAGE_YEARS = "coverage_years"
METRIC_EXPORT_ROWS = "export_rows"
METRIC_ROBOTS = "robots"
METRIC_TERMS = "terms"
METRIC_RATE_LIMIT = "rate_limit"
METRIC_LANGUAGES = "languages"
METRIC_PAGE_SAMPLE_OK = "page_sample_ok"
METRIC_SDS_SAMPLE_OK = "sds_sample_ok"
METRIC_EXTRACTION_PATH = "extraction_path"
METRIC_ACCESS_BLOCKED = "access_blocked"
METRIC_ROBOTS_DENIED = "robots_denied"
METRIC_FREE_ACCESS = "free_access"
METRIC_RECORDS_HS3208 = "records_hs3208"
METRIC_RECORDS_HS3209 = "records_hs3209"
METRIC_RECORDS_HS3213 = "records_hs3213"
METRIC_CENSUS_STATUS = "census_status"
METRIC_PRODUCTS_LISTED = "products_listed"
METRIC_DOC_LINKS_SEEN = "doc_links_seen"
METRIC_WALK_BUDGET_EXHAUSTED = "walk_budget_exhausted"
METRIC_PRODUCTS_REGISTERED = "products_registered"
METRIC_SITEMAP_PRODUCTS = "sitemap_products"
METRIC_SDS_LIBRARY_VISIBLE = "sds_library_visible"
METRIC_PRODUCERS_REGISTERED = "producers_registered"
METRIC_TRADE_KG_HS3208 = "trade_kg_hs3208"
METRIC_TRADE_EUR_HS3208 = "trade_eur_hs3208"
METRIC_TRADE_KG_HS3209 = "trade_kg_hs3209"
METRIC_TRADE_EUR_HS3209 = "trade_eur_hs3209"
METRIC_PRODUCTS_IDENTIFIABLE = "products_identifiable"
METRIC_CAP_MANUFACTURER = "cap_manufacturer"
METRIC_CAP_PRODUCT_IDENT = "cap_product_ident"
METRIC_CAP_CN8_LINKAGE = "cap_cn8_linkage"
METRIC_CAP_DEPTH_TIER = "cap_depth_tier"
METRIC_CN8_REACHABLE = "cn8_reachable"
METRIC_SDS_DOC_URLS = "sds_doc_urls"
METRIC_CSV_SAMPLE_ROWS = "csv_sample_rows"
METRIC_CSV_SAMPLE_UNAVAILABLE = "csv_sample_unavailable"
METRIC_AS_PROBE_ROWS = "as_probe_rows"
METRIC_AS_PROBE_RECORDS = "as_probe_records"
METRIC_AS_PROBE_UNAVAILABLE = "as_probe_unavailable"
METRIC_AS_PROBE_ASSOC = "as_probe_assoc"


PROBE_METRIC_SEEDS = (
    Metric(METRIC_CATALOG_COUNT, "Catalog product count", "numeric"),
    Metric(METRIC_CATEGORY_COUNT, "Category product count", "numeric"),
    Metric(METRIC_CATEGORY_LIST, "Categories exposed", "text"),
    Metric(METRIC_FORMAT, "Export/download format", "text"),
    Metric(METRIC_GRANULARITY, "Statistics granularity", "text"),
    Metric(METRIC_COVERAGE_YEARS, "Coverage years", "text"),
    Metric(METRIC_EXPORT_ROWS, "Export rows", "numeric"),
    Metric(METRIC_ROBOTS, "Robots policy", "text"),
    Metric(METRIC_TERMS, "Site terms", "text"),
    Metric(METRIC_RATE_LIMIT, "Rate limit", "text"),
    Metric(METRIC_LANGUAGES, "Languages", "text"),
    Metric(METRIC_PAGE_SAMPLE_OK, "Sample pages retrievable", "numeric"),
    Metric(METRIC_SDS_SAMPLE_OK, "SDS on sample pages", "numeric"),
    Metric(METRIC_EXTRACTION_PATH, "Extraction path", "text"),
    Metric(METRIC_ACCESS_BLOCKED, "Access blocked", "text"),
    Metric(METRIC_ROBOTS_DENIED, "Robots denial", "text"),
    Metric(METRIC_FREE_ACCESS, "Free access confirmed", "numeric"),
    # 0003__probe_metrics.sql (v0.1.2, od10)
    Metric(METRIC_RECORDS_HS3208, "Records HS 3208", "numeric"),
    Metric(METRIC_RECORDS_HS3209, "Records HS 3209", "numeric"),
    Metric(METRIC_RECORDS_HS3213, "Records HS 3213", "numeric"),
    Metric(METRIC_CENSUS_STATUS, "Census status", "text"),
    # 0004__product_census.sql (v0.1.2 rework, D28)
    Metric(METRIC_PRODUCTS_LISTED, "Products listed (walk)", "numeric"),
    Metric(METRIC_DOC_LINKS_SEEN, "Doc links seen (walk)", "numeric"),
    Metric(METRIC_WALK_BUDGET_EXHAUSTED, "Walk budget exhausted", "numeric"),
    # 0005__priors_metric.sql (v0.1.3 pe2, landed by v0.2.0 PHASE01)
    Metric(METRIC_PRODUCTS_REGISTERED, "Products registered (prior)", "numeric"),
    # 0006__recon_numbers.sql (v0.2.0)
    Metric(METRIC_SITEMAP_PRODUCTS, "Products sitemap-visible", "numeric"),
    Metric(METRIC_SDS_LIBRARY_VISIBLE, "SDS library visible (manual)", "numeric"),
    Metric(METRIC_PRODUCERS_REGISTERED, "Producers registered (prior)", "numeric"),
    Metric(METRIC_TRADE_KG_HS3208, "EU imports HS 3208 (kg)", "numeric"),
    Metric(METRIC_TRADE_EUR_HS3208, "EU imports HS 3208 (EUR)", "numeric"),
    Metric(METRIC_TRADE_KG_HS3209, "EU imports HS 3209 (kg)", "numeric"),
    Metric(METRIC_TRADE_EUR_HS3209, "EU imports HS 3209 (EUR)", "numeric"),
    # 0007__capability.sql (v0.2.1, cap1)
    Metric(METRIC_PRODUCTS_IDENTIFIABLE, "Products identifiable", "numeric"),
    Metric(METRIC_CAP_MANUFACTURER, "Capability: manufacturer field", "numeric"),
    Metric(METRIC_CAP_PRODUCT_IDENT, "Capability: product-ident field", "numeric"),
    Metric(METRIC_CAP_CN8_LINKAGE, "Capability: CN8 linkage", "text"),
    Metric(METRIC_CAP_DEPTH_TIER, "Capability: depth tier", "numeric"),
    Metric(METRIC_CN8_REACHABLE, "CN8 codes reachable", "numeric"),
    # 0008__landscape.sql (v0.2.2, fu3)
    Metric(METRIC_SDS_DOC_URLS, "SDS document URLs visible", "numeric"),
    # 0009__csv_sample.sql (v0.2.4, D36)
    Metric(METRIC_CSV_SAMPLE_ROWS, "CSV sample rows drawn", "numeric"),
    Metric(METRIC_CSV_SAMPLE_UNAVAILABLE, "CSV sample unavailable", "text"),
    # 0010__as_source_probe.sql (v0.2.4 addendum, D37)
    Metric(METRIC_AS_PROBE_ROWS, "AS probe product rows obtained", "numeric"),
    Metric(METRIC_AS_PROBE_RECORDS, "AS probe record count", "text"),
    Metric(METRIC_AS_PROBE_UNAVAILABLE, "AS probe unavailable", "text"),
    Metric(METRIC_AS_PROBE_ASSOC, "AS probe association finding", "text"),
)

METRIC_CODES = frozenset(m.code for m in PROBE_METRIC_SEEDS)
_METRIC_BY_CODE = {m.code: m for m in PROBE_METRIC_SEEDS}


def is_valid(metric_code: str) -> bool:
    return metric_code in METRIC_CODES


def value_type_of(metric_code: str) -> str | None:
    m = _METRIC_BY_CODE.get(metric_code)
    return m.value_type if m else None
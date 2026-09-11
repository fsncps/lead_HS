"""probe-metric vocabulary — the runtime source of truth.

Authoritative table: 20_DESIGN/MASTER/interfaces.md §probe_metric
vocabulary. Migration 0001 + 0003 seeds are pinned to this list by a
sync test (t6); new metrics enter via a migration INSERT, codes are
never renamed, value_type is fixed at insert (i4).
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
)

METRIC_CODES = frozenset(m.code for m in PROBE_METRIC_SEEDS)
_METRIC_BY_CODE = {m.code: m for m in PROBE_METRIC_SEEDS}


def is_valid(metric_code: str) -> bool:
    return metric_code in METRIC_CODES


def value_type_of(metric_code: str) -> str | None:
    m = _METRIC_BY_CODE.get(metric_code)
    return m.value_type if m else None
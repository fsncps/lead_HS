"""D38: data_sources.csv — the confirmed-bulk source list.

Gate (de5/de6): a row exists only where a probe has CONFIRMED bulk
data carrying the identity tuple (manufacturer + product ident-nr)
with in-scope (3208/3209) membership derivable from the source's
category/group filter. The file is a review artifact — it is never
loaded by `source load`.
"""

import csv
import os

import pytest

DATA_SOURCES = os.path.join(
    os.path.dirname(__file__), "..", "src", "leadhs", "dict", "data_sources.csv")

EXPECTED_COLUMNS = (
    "ds_id", "source_id", "name", "operator", "country_scope", "url", "bulk_url",
    "format", "delimiter", "rows_total", "rows_in_scope", "size_basis", "size_date",
    "identity_manufacturer", "identity_ident", "identity_notes",
    "independence_group", "verification_status", "verified_date", "listed_by", "notes",
)


@pytest.fixture(scope="module")
def rows():
    with open(DATA_SOURCES, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_header_schema(rows):
    with open(DATA_SOURCES, newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    assert tuple(header) == EXPECTED_COLUMNS


def test_gate_confirmed_bulk_only(rows):
    """Every row carries probe-confirmed verification; no PE rows; no
    gated or claimed rows (de5/de6)."""
    assert rows, "data_sources.csv must not be empty"
    for r in rows:
        assert r["verification_status"].startswith("confirmed-by-probe"), r["ds_id"]
        assert not r["source_id"].startswith("PE"), r["ds_id"]
        assert r["bulk_url"].startswith("http"), r["ds_id"]
        assert r["identity_manufacturer"] and r["identity_ident"], r["ds_id"]
        assert r["verified_date"] and r["size_basis"], r["ds_id"]


def test_ids_unique_and_sources_exist(rows):
    ds_ids = [r["ds_id"] for r in rows]
    assert len(ds_ids) == len(set(ds_ids))
    src_ids = {r["source_id"] for r in rows}
    reg = os.path.join(os.path.dirname(__file__), "..", "src", "leadhs", "dict", "sources.csv")
    with open(reg, newline="", encoding="utf-8") as fh:
        register_ids = {r["id"] for r in csv.DictReader(fh)}
    assert src_ids <= register_ids


def test_initial_content_as2_as3(rows):
    """The file starts with exactly the two confirmed-bulk ecolabel
    catalogues; it grows only as future probes confirm the gate."""
    assert {r["source_id"] for r in rows} == {"AS-2", "AS-3"}
    assert {r["independence_group"] for r in rows} == {"ecolabel-family"}

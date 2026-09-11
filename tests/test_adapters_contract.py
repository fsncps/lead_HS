"""Adapter contract (A3): adapters complete draft-only against a
query_only connection — pins i3 (engine owns the single write path)."""

import pytest

from leadhs.db import connect
from leadhs.models import DocumentDraft, FindingDraft, ProbeContext, SourceRef
from leadhs.probe.adapters import CSAdapter, PEAdapter


def _pe_source(site):
    return SourceRef(id="PE-1", class_code="PE", name="x", url=f"{site}/", access_method_code="scrape", active=1)


def _cs_source(site):
    return SourceRef(id="CS-1", class_code="CS", name="x", url=f"{site}/export.csv", access_method_code="download", active=1)


def test_adapters_draft_only(db_path, conn, site, store, make_fetcher):
    qo = connect(db_path, readonly=True)  # PRAGMA query_only=ON
    try:
        ctx = ProbeContext(fetcher=make_fetcher(), store=store, conn=qo, sample_n=2, dry_run=False)
        for adapter, source in ((PEAdapter(), _pe_source(site)), (CSAdapter(), _cs_source(site))):
            result = adapter.probe(source, ctx)
            assert all(isinstance(d, DocumentDraft) for d in result.documents)
            assert all(isinstance(f, FindingDraft) for f in result.findings)
    finally:
        qo.close()


def test_query_only_conn_blocks_writes(db_path, conn):
    """Sanity: the connection really forbids writes."""
    qo = connect(db_path, readonly=True)
    try:
        with pytest.raises(Exception):
            qo.execute("INSERT INTO source (id, class_code, name, url, access_method_code) VALUES ('CS-1','CS','n','u','api')")
    finally:
        qo.close()


def test_registry_covers_classes(site):
    from leadhs.probe.adapters import get_adapter

    for cls in ("CS", "PE", "ST"):
        source = SourceRef(id="XX-1", class_code=cls, name="x", url=f"{site}/", access_method_code="scrape", active=1)
        assert get_adapter(source) is not None

"""store: hash-only filenames, allowlist, orphans, verify (a5/P5)."""

import os

import pytest

from leadhs.store import RawStore, StoreError


def test_put_returns_hash_and_relpath(tmp_path):
    store = RawStore(str(tmp_path))
    digest, relpath = store.put("CS-1", b"hello", "html")
    assert len(digest) == 64
    assert relpath == os.path.join("cs-1", f"{digest}.html")
    assert os.path.exists(os.path.join(str(tmp_path), relpath))


def test_put_idempotent(tmp_path):
    store = RawStore(str(tmp_path))
    d1, r1 = store.put("CS-1", b"hello", "html")
    d2, r2 = store.put("CS-1", b"hello", "html")
    assert d1 == d2 and r1 == r2


def test_put_rejects_traversal(tmp_path):
    store = RawStore(str(tmp_path))
    with pytest.raises(StoreError):
        store.put("../etc", b"x", "html")
    with pytest.raises(StoreError):
        store.put("CS-1/../../", b"x", "html")
    with pytest.raises(StoreError):
        store.put("", b"x", "html")


def test_put_rejects_bad_ext(tmp_path):
    store = RawStore(str(tmp_path))
    with pytest.raises(StoreError):
        store.put("CS-1", b"x", "abcdef")
    with pytest.raises(StoreError):
        store.put("CS-1", b"x", "..")


def test_verify_round_trip(tmp_path):
    store = RawStore(str(tmp_path))
    digest, _ = store.put("CS-1", b"payload", "csv")
    assert store.verify(digest) is True
    assert store.verify("0" * 64) is False


def test_get_round_trip(tmp_path):
    store = RawStore(str(tmp_path))
    digest, _ = store.put("CS-1", b"payload", "csv")
    assert store.get(digest) == b"payload"


def test_orphans(tmp_path):
    store = RawStore(str(tmp_path))
    d1, _ = store.put("CS-1", b"kept", "html")
    d2, _ = store.put("CS-1", b"orphan", "html")
    assert store.orphans({d1}) == [os.path.join("cs-1", f"{d2}.html")]
    assert store.orphans({d1, d2}) == []

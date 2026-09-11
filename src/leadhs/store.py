"""Raw store: hash-only filenames, source-id allowlist (a5/P5).

Layout: ``<root>/<source_id lowercased>/<sha256>.<ext>`` — the
filename is a content fingerprint; the database references it, so
any later change is detectable. The source directory name must match
``^[a-z]{2}-[0-9]+$`` after lowering (path-traversal guard).
"""

from __future__ import annotations

import hashlib
import os
import re

_SOURCE_DIR_RE = re.compile(r"^[a-z]{2}-[0-9]+$")
_EXT_RE = re.compile(r"^[a-z0-9]{1,5}$")


class StoreError(Exception):
    pass


class RawStore:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)

    def _source_dir(self, source_id: str) -> str:
        lowered = source_id.lower()
        if not _SOURCE_DIR_RE.match(lowered):
            raise StoreError(f"invalid source id for store path: {source_id!r}")
        return os.path.join(self.root, lowered)

    def put(self, source_id: str, data: bytes, ext: str) -> tuple:
        """Store bytes; returns (sha256, relpath). Idempotent on repeat."""
        ext = ext.lower().lstrip(".")
        if not _EXT_RE.match(ext):
            raise StoreError(f"invalid extension: {ext!r}")
        digest = hashlib.sha256(data).hexdigest()
        directory = self._source_dir(source_id)
        os.makedirs(directory, exist_ok=True)
        relpath = os.path.join(source_id.lower(), f"{digest}.{ext}")
        path = os.path.join(self.root, relpath)
        if os.path.exists(path):
            with open(path, "rb") as fh:
                if fh.read() != data:
                    raise StoreError(f"hash collision at {relpath}")
        else:
            with open(path, "xb") as fh:
                fh.write(data)
        return digest, relpath

    def get(self, digest: str) -> bytes:
        path = self._path_for(digest)
        with open(path, "rb") as fh:
            return fh.read()

    def verify(self, digest: str) -> bool:
        """Re-hash round-trip (and existence)."""
        path = self._path_for(digest)
        if not os.path.exists(path):
            return False
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest() == digest

    def orphans(self, documented_hashes: set) -> list:
        """Raw files whose hash has no document row (audit R8)."""
        orphans = []
        for root, _, files in os.walk(self.root):
            for name in files:
                digest, _, ext = name.partition(".")
                if not _EXT_RE.match(ext) or len(digest) != 64:
                    continue
                if digest not in documented_hashes:
                    orphans.append(os.path.relpath(os.path.join(root, name), self.root))
        return sorted(orphans)

    def _path_for(self, digest: str) -> str:
        if len(digest) != 64 or not all(c in "0123456789abcdef" for c in digest):
            raise StoreError(f"invalid digest: {digest!r}")
        for root, _, files in os.walk(self.root):
            for name in files:
                if name.startswith(digest + "."):
                    return os.path.join(root, name)
        return os.path.join(self.root, digest)  # non-existent marker path
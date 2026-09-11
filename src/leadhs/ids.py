"""Deterministic run_key builder (a6).

run_key: ``<kind>-<YYYYMMDD>-<slug>``; probe slug = source id
lowercased dash-stripped (``CS-1`` -> ``probe-20260910-cs1``);
same-day re-runs append ``-2``, ``-3``. The builder is pure — callers
query the DB for existing keys and pass the next attempt.
"""

from __future__ import annotations

import re
from datetime import date


def slug_for_source(source_id: str) -> str:
    return source_id.lower().replace("-", "")


def run_key(kind: str, date_: date, slug: str, attempt: int = 1) -> str:
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    key = f"{kind}-{date_.strftime('%Y%m%d')}-{slug}"
    return key if attempt == 1 else f"{key}-{attempt}"


_ATTEMPTED_RE = re.compile(r"^(.+)-(\d+)$")


def next_attempt(existing_keys: "Iterable[str]", kind: str, date_: date, slug: str) -> int:
    """First free attempt for a base key given already-existing keys.

    Deterministic: counts the existing keys equal to the base or to
    ``base-N`` (N >= 2); anything malformed in that name-space counts
    as an attempt too, so the builder never collides.
    """
    base = run_key(kind, date_, slug, 1)
    attempts = 0
    for key in existing_keys:
        if key == base:
            attempts = 1
        else:
            m = _ATTEMPTED_RE.match(key)
            if m and m.group(1) == base:
                attempts = max(attempts, int(m.group(2)))
    return attempts + 1
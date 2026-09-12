"""Source register load/list (i2: register of record = repo CSV).

Load validation (i13/pe6): id matches ``^[A-Z]{2}-[0-9]+$``; url
non-empty http(s) with a host; no duplicate host among active rows
(netloc lowercased, ``www.`` stripped — one site must not be
double-counted into a floor). Inactive rows are exempt from the
host check (historical rows may share hosts). A failing row is named,
exit 1.
"""

from __future__ import annotations

import csv
import importlib.resources
import re
from typing import Optional
from urllib.parse import urlparse

_ID_RE = re.compile(r"^[A-Z]{2}-[0-9]+$")
_VALID_CLASSES = {"CS", "PE", "LG", "ST", "LI"}
_REQUIRED = {
    "id",
    "class_code",
    "name",
    "url",
    "access_method_code",
    "license_note",
    "verification_status_code",
    "active",
    "notes",
}


class SourceLoadError(Exception):
    pass


def default_register_path() -> str:
    return str(importlib.resources.files("leadhs").joinpath("dict", "sources.csv"))


def _host_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _validate_row(row: dict, line: int) -> None:
    missing = _REQUIRED - set(row.keys())
    if missing:
        raise SourceLoadError(f"line {line}: missing columns {sorted(missing)}")
    sid = row["id"].strip()
    if not _ID_RE.match(sid):
        raise SourceLoadError(f"line {line}: bad source id {sid!r} (need CS-1 style)")
    if row["class_code"] not in _VALID_CLASSES:
        raise SourceLoadError(f"line {line}: {sid} bad class_code {row['class_code']!r}")
    url = row["url"].strip()
    if not url:
        raise SourceLoadError(f"line {line}: {sid} empty url")
    parts = urlparse(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise SourceLoadError(f"line {line}: {sid} url must be http(s) with a host, got {url!r}")
    if row["access_method_code"] not in ("api", "scrape", "download", "manual"):
        raise SourceLoadError(f"line {line}: {sid} bad access_method_code {row['access_method_code']!r}")
    if row["verification_status_code"] not in ("verified", "partially_verified", "open", "unverified"):
        raise SourceLoadError(f"line {line}: {sid} bad verification_status_code {row['verification_status_code']!r}")
    if row["active"] not in ("0", "1"):
        raise SourceLoadError(f"line {line}: {sid} active must be 0 or 1")


def load(conn, path: str) -> int:
    """Upsert the register; reference data, never deleted (P6/dm12)."""
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    except OSError as exc:
        raise SourceLoadError(f"cannot read {path}: {exc}")
    if not rows:
        raise SourceLoadError(f"{path}: empty register")

    seen: set = set()
    active_hosts: dict = {}
    count = 0
    for lineno, row in enumerate(rows, start=2):  # 1 = header
        _validate_row(row, lineno)
        sid = row["id"].strip()
        if sid in seen:
            raise SourceLoadError(f"line {lineno}: duplicate source id {sid}")
        seen.add(sid)
        if row["active"].strip() == "1":
            host = _host_of(row["url"])
            other = active_hosts.get(host)
            if other is not None:
                raise SourceLoadError(
                    f"line {lineno}: duplicate active host {host} — {sid} conflicts with {other}"
                )
            active_hosts[host] = sid
        conn.execute(
            """
            INSERT INTO source (id, class_code, name, url, access_method_code,
                                license_note, verification_status_code, active, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                class_code = excluded.class_code,
                name = excluded.name,
                url = excluded.url,
                access_method_code = excluded.access_method_code,
                license_note = excluded.license_note,
                verification_status_code = excluded.verification_status_code,
                active = excluded.active,
                notes = excluded.notes
            """,
            (
                sid,
                row["class_code"].strip(),
                row["name"].strip(),
                row["url"].strip(),
                row["access_method_code"].strip(),
                row["license_note"].strip() or None,
                row["verification_status_code"].strip(),
                int(row["active"]),
                row["notes"].strip() or None,
            ),
        )
        count += 1
    conn.commit()
    return count


def list_(conn, class_code: Optional[str] = None) -> None:
    if class_code:
        rows = conn.execute(
            "SELECT id, class_code, name, verification_status_code, active, url FROM source WHERE class_code = ? ORDER BY id",
            (class_code,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, class_code, name, verification_status_code, active, url FROM source ORDER BY id"
        ).fetchall()
    if not rows:
        print("(no sources loaded — run `leadhs source load`)")
        return
    print(f"{'id':<6} {'class':<6} {'name':<38} {'status':<18} {'active'}")
    for row in rows:
        print(f"{row[0]:<6} {row[1]:<6} {row[2]:<38} {row[3]:<18} {row[4]}")


def all_sources(conn, active_only: bool = True) -> list:
    """SourceRef rows for the engine; active filter for probe run --all."""
    if active_only:
        rows = conn.execute("SELECT * FROM source WHERE active = 1 ORDER BY id").fetchall()
    else:
        rows = conn.execute("SELECT * FROM source ORDER BY id").fetchall()
    from .models import SourceRef

    return [SourceRef(**dict(r)) for r in rows]


def get_source(conn, source_id: str):
    row = conn.execute("SELECT * FROM source WHERE id = ?", (source_id,)).fetchone()
    if row is None:
        return None
    from .models import SourceRef

    return SourceRef(**dict(row))
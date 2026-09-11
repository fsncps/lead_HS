"""Environment preflight (a10): the first-run de-risking surface.

Checks: Python version, sqlite3, optional binaries (mdbtools,
pdftotext, pandoc — warnings, not errors), data-dir writability,
contact configured (warning), optional network reachability of
seeded sources (--net). Exit 0 with warnings; 1 on errors.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys

import requests

from . import __version__

OPTIONAL_BINARIES = {
    "mdbtools": ("mdb-export", "mdbtools / SPIN extraction (ST-2)"),
    "pdftotext": ("pdftotext", "PDF text extraction (M2 SDS parsing)"),
    "pandoc": ("pandoc", "Markdown->PDF report rendering (M3/M4)"),
}


class DoctorResult:
    def __init__(self):
        self.items: list = []  # (kind, name, detail); kind in ok/warn/error

    def add(self, kind: str, name: str, detail: str) -> None:
        self.items.append((kind, name, detail))

    @property
    def has_errors(self) -> bool:
        return any(k == "error" for k, _, _ in self.items)

    def render(self) -> None:
        for kind, name, detail in self.items:
            marker = {"ok": "[ok]  ", "warn": "[warn]", "error": "[err] "}[kind]
            print(f"{marker} {name}: {detail}")


def run(rt, net: bool = False) -> DoctorResult:
    result = DoctorResult()

    # python
    if sys.version_info >= (3, 11):
        result.add("ok", "python", f"{sys.version.split()[0]} (>= 3.11 required)")
    else:
        result.add("error", "python", f"{sys.version.split()[0]} (< 3.11)")

    # sqlite3
    try:
        sqlite_version = sqlite3.sqlite_version
        result.add("ok", "sqlite3", f"module {sqlite_version}")
    except Exception as exc:  # pragma: no cover
        result.add("error", "sqlite3", str(exc))

    # optional binaries
    for name, (binary, purpose) in OPTIONAL_BINARIES.items():
        found = shutil.which(binary)
        if found:
            result.add("ok", name, f"{found}")
        else:
            result.add("warn", name, f"not found ({purpose})")

    # data dir writability (parent of the DB file)
    db_dir = os.path.dirname(os.path.abspath(rt.db_path)) or "."
    try:
        os.makedirs(db_dir, exist_ok=True)
        raw_dir = os.path.join(db_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        probe = os.path.join(raw_dir, ".doctor-write-test")
        with open(probe, "w") as fh:
            fh.write("ok")
        os.remove(probe)
        result.add("ok", "data dir", f"{db_dir} (writable; raw/ created)")
    except OSError as exc:
        result.add("error", "data dir", f"{db_dir}: {exc}")

    # contact
    if rt.contact:
        result.add("ok", "contact", rt.contact)
    else:
        result.add("warn", "contact", "unset (set LEADHS_CONTACT or --contact; fetch UA uses it)")

    # optional network reachability of seeded sources
    if net:
        from . import db as dbmod, source as sourcemod

        db_dir = os.path.dirname(os.path.abspath(rt.db_path)) or "."
        db_path = rt.db_path
        urls = []
        if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
            try:
                conn = dbmod.connect(db_path)
                urls = [r[0] for r in conn.execute("SELECT url FROM source WHERE active = 1")]
                conn.close()
            except sqlite3.Error:
                urls = []
        if not urls:
            urls = ["https://example.com"]
        import time

        reached = 0
        for url in urls:
            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": f"leadhs/{__version__} (+{rt.contact or 'no-contact'})"})
                reached += 1
                result.add("ok", "reach", f"{url} -> {resp.status_code}")
            except requests.RequestException as exc:
                result.add("warn", "reach", f"{url} -> {exc.__class__.__name__}")
            time.sleep(0.5)
        result.add("ok", "reach summary", f"{reached}/{len(urls)} sources reachable")
    else:
        result.add("warn", "network", "skipped (--net to check reachability)")

    return result


def main(rt, net: bool) -> int:
    result = run(rt, net=net)
    result.render()
    return 1 if result.has_errors else 0
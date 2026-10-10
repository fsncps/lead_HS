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


def _identity_checks(result: DoctorResult, db_path: str) -> None:
    """v0.3.4: canonical identity layer state — read-only, never creates
    the DB, informational (identity problems warn, never error)."""
    if not (os.path.isfile(db_path) and os.path.getsize(db_path) > 0):
        return
    try:
        conn = sqlite3.connect(f"file:{os.path.abspath(db_path)}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            have = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {"manufacturer", "product", "identity_state", "linkage_candidate"} <= have:
                result.add("ok", "identity", "not initialized (migration 0013 pending) — informational")
                return
            states = {r["source_id"]: r["manifest_hash"] for r in conn.execute("SELECT source_id, manifest_hash FROM identity_state")}
            if not states:
                result.add("ok", "identity", "tables present, no sources resolved yet (`leadhs identity resolve`)")
                return
            mfr_n = conn.execute("SELECT COUNT(*) FROM manufacturer").fetchone()[0]
            prod_n = conn.execute("SELECT COUNT(*) FROM product").fetchone()[0]
            orphans = 0
            backtables = [
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'raw\\_%' ESCAPE '\\'"
                )
            ]
            for table in backtables:
                cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')}
                if "product_uuid" not in cols:
                    continue
                total = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                linked = conn.execute(f'SELECT COUNT(*) FROM "{table}" WHERE product_uuid IS NOT NULL').fetchone()[0]
                orph = conn.execute(
                    f'SELECT COUNT(*) FROM "{table}" r LEFT JOIN product p ON p.uuid = r.product_uuid '
                    "WHERE r.product_uuid IS NOT NULL AND p.uuid IS NULL"
                ).fetchone()[0]
                orphans += orph
                result.add(
                    "ok" if orph == 0 else "warn",
                    f"identity {table}",
                    f"back-linked {linked:,}/{total:,}" + (f", {orph:,} ORPHAN" if orph else ""),
                )
            drift = [
                r["source_id"]
                for r in conn.execute(
                    "SELECT p.source_id, p.manifest_hash AS ph, s.manifest_hash AS sh "
                    "FROM raw_source_profile p JOIN identity_state s ON s.source_id = p.source_id "
                    "WHERE s.manifest_hash != p.manifest_hash"
                )
            ]
            if drift:
                result.add(
                    "warn", "identity drift",
                    f"{', '.join(drift)} re-acquired after resolve — `leadhs identity rebuild`",
                )
            result.add(
                "ok", "identity",
                f"{len(states)} source(s) resolved; manufacturers={mfr_n:,} products={prod_n:,}"
                + (f"; {orphans:,} orphan links" if orphans else ""),
            )
        finally:
            conn.close()
    except sqlite3.Error as exc:
        result.add("warn", "identity", f"check skipped ({exc})")


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

    # identity layer (v0.3.4; read-only, informational)
    _identity_checks(result, rt.db_path)

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
"""Source adapters (il12): raw table → identity groups.

One plain function per source, registered in ``ADAPTERS`` keyed by the
source id. Each adapter validates its expected columns up front
(SourceSchemaError naming the offenders), then collects groups in ONE
ordered pass (SELECT rowid … ORDER BY group keys + itertools.groupby)
so back-link UPDATEs can run by rowid lists — never a per-group WHERE
scan (the r01 review pin; il13's no-per-row-loop rule extended to the
raw read).

Group-level identity (MA12): ECAT groups on (licence_number,
product_or_service_name); BASTA on (company_id, article_number). BASTA
ident basis is always ``article:`` (il3); its ``gtin`` column is NOT
read for identity (raw-side matching evidence, r03).

Election (il17, user-confirmed): canonicalize + dedupe the group's
codes; any gtin-class code wins (multiple DISTINCT gtins →
min-lexicographic + multi_gtin); else min-sorted article code; else
the ``name:<mfr_norm>:<name_norm>`` fallback. Non-elected codes stay
raw-side; refusals (bad GTINs, blank keys) are counted, never fatal.
"""

from __future__ import annotations

import itertools
import sqlite3
from dataclasses import dataclass, field

from .. import normalize as normmod
from .errors import SourceSchemaError

# il3 code-type map (ECAT values profiled 2026-10-10: '', EAN13,
# GTIN14, GTIN8, GTIN12, ITF, 'Internal Producer ID', 'Other').
_GTIN_HINTS = ("ean", "gtin", "itf")


@dataclass
class Group:
    source_id: str
    key: tuple
    mfr_name: str
    mfr_country: str | None = None
    mfr_city: str | None = None
    mfr_vat: str | None = None
    eu_group: str | None = None
    name: str | None = None
    brand: str | None = None
    url: str | None = None
    codes: list = field(default_factory=list)  # [(code_type, code_value)]
    rowids: list = field(default_factory=list)


@dataclass
class Elected:
    ident_string: str
    ident_nr: str
    basis: str  # gtin | article | name
    multi_gtin: bool = False
    multi_code: bool = False


def _q(name: str) -> str:
    return chr(34) + name.replace(chr(34), chr(34) * 2) + chr(34)


def _require_columns(conn: sqlite3.Connection, table: str, expected: tuple) -> None:
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({_q(table)})")}
    missing = [c for c in expected if c not in cols]
    if missing:
        raise SourceSchemaError(
            f"{table}: missing expected column(s) {', '.join(missing)} — "
            "re-acquire the source (`raw run`) and re-check its instruction"
        )


def _norm_code(code_type, code_value) -> tuple:
    """il3 map: (class, norm) — gtin hints → canonical GTIN-14 (raises
    ValueError on non-GTIN digit counts), everything else → article
    (norm_ident). Blank value → (None, None) → caller skips."""
    hint = (code_type or "").casefold()
    value = normmod.norm_ident(code_value)
    if not value:
        return (None, None)
    if any(h in hint for h in _GTIN_HINTS):
        return ("gtin", normmod.norm_gtin(value))
    return ("article", value)


def elect(group: Group, mfr_norm: str, name_norm: str) -> Elected | None:
    """il17 election. Returns None when the group has no usable key at
    all (caller counts the skip)."""
    canonical: set = set()
    for code_type, code_value in group.codes:
        klass, value = _norm_code(code_type, code_value)
        if klass:
            canonical.add((klass, value))
    gtins = sorted(v for k, v in canonical if k == "gtin")
    articles = sorted(v for k, v in canonical if k == "article")
    multi_code = len(canonical) > 1
    if gtins:
        nr = gtins[0]
        return Elected(f"gtin:{nr}", nr, "gtin",
                       multi_gtin=len(gtins) > 1, multi_code=multi_code)
    if articles:
        nr = articles[0]
        return Elected(f"article:{mfr_norm}:{nr}", nr, "article",
                       multi_code=multi_code)
    if name_norm:
        return Elected(f"name:{mfr_norm}:{name_norm}", name_norm, "name")
    return None


def _iter_groups(conn, table, order_cols, build) -> list:
    """One ordered pass; groupby on the leading group-key columns."""
    col_list = ", ".join(_q(c) for c in order_cols)
    groups = []
    rowset = conn.execute(
        f"SELECT rowid AS _rid, {col_list} FROM {_q(table)} ORDER BY {col_list}"
    )
    for _key, rows in itertools.groupby(rowset, key=lambda r: tuple(r[c] for c in order_cols)):
        groups.append(build(list(rows)))
    return groups


def ecat(conn: sqlite3.Connection, table: str = "raw_as2_ecat") -> list:
    """EU Ecolabelling (ECAT) — groups per (licence_number,
    product_or_service_name); manufacturer from the company columns."""
    _require_columns(conn, table, (
        "licence_number", "product_or_service_name", "group_name",
        "code_type", "code_value", "company_name", "company_country",
        "vat_number",
    ))

    def build(rows):
        r0 = rows[0]
        g = Group(
            source_id="AS-2",
            key=(r0["licence_number"], r0["product_or_service_name"]),
            mfr_name=r0["company_name"] or "",
            mfr_country=r0["company_country"],
            mfr_vat=r0["vat_number"],
            eu_group=r0["group_name"],
            name=r0["product_or_service_name"],
        )
        g.rowids = [r["_rid"] for r in rows]
        g.codes = [(r["code_type"], r["code_value"]) for r in rows]
        return g

    return _iter_groups(
        conn, table,
        ("licence_number", "product_or_service_name"), build,
    )


def basta(conn: sqlite3.Connection, table: str = "raw_as33_basta") -> list:
    """BASTA — groups per (company_id, article_number); ident basis
    always article (il3); gtin column NOT read for identity."""
    _require_columns(conn, table, (
        "company_id", "article_number", "company_name", "article_name",
        "brand_name", "article_url",
    ))

    def build(rows):
        r0 = rows[0]
        g = Group(
            source_id="AS-33",
            key=(r0["company_id"], r0["article_number"]),
            mfr_name=r0["company_name"] or "",
            name=r0["article_name"],
            brand=r0["brand_name"],
            url=r0["article_url"],
        )
        g.rowids = [r["_rid"] for r in rows]
        g.codes = [("article", r["article_number"]) for r in rows]
        return g

    return _iter_groups(
        conn, table,
        ("company_id", "article_number"), build,
    )


ADAPTERS = {"AS-2": ecat, "AS-33": basta}

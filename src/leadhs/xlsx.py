"""Minimal XLSX reader — stdlib zipfile + ElementTree only (D24: no
openpyxl; pure Python). Reads cell text for every sheet: shared strings
(``t="s"``), inline strings (``t="inlineStr"``), literal text and
numbers (``<v>``). Returns ``{sheet_name: rows}`` with rows as string
lists (padded by cell address). Corrupt archives and missing members
raise :class:`XlsxError` (typed errors for the adapter taxonomy).
"""

from __future__ import annotations

import io
import zipfile
import xml.etree.ElementTree as ET

MAX_BYTES = 50 * 1024 * 1024  # size cap (t12)

_MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
_OFFICE_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


class XlsxError(Exception):
    pass


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _member(zf: zipfile.ZipFile, name: str) -> bytes:
    try:
        info = zf.getinfo(name)
    except KeyError:
        raise XlsxError(f"missing xlsx member: {name}")
    if info.file_size > MAX_BYTES:
        raise XlsxError(f"xlsx member too large: {name} ({info.file_size} bytes)")
    return zf.read(name)


def _sheet_path(zf: zipfile.ZipFile, rid: str) -> str:
    rels = ET.fromstring(_member(zf, "xl/_rels/workbook.xml.rels"))
    for rel in rels.iter(f"{_REL_NS}Relationship"):
        if rel.get("Id") == rid:
            target = rel.get("Target", "")
            if target.startswith("/"):
                return target.lstrip("/")
            return "xl/" + target if not target.startswith("xl/") else target
    raise XlsxError(f"workbook relationship {rid} not found")


def _cell_text(c, shared: list) -> str:
    ctype = c.get("t", "n")
    if ctype == "inlineStr":
        return "".join(t.text or "" for t in c.iter(f"{_MAIN_NS}t"))
    v = c.find(f"{_MAIN_NS}v")
    if v is None or v.text is None:
        return ""
    if ctype == "s":
        try:
            return shared[int(v.text)]
        except (ValueError, IndexError):
            raise XlsxError(f"shared-string index out of range: {v.text!r}")
    return v.text


def _col_index(ref: str) -> int:
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + (ord(ch.casefold()) - 96)
    return n - 1


def _parse_sheet(data: bytes, shared: list) -> list:
    root = ET.fromstring(data)
    rows: dict = {}
    for row in root.iter(f"{_MAIN_NS}row"):
        out: list = []
        for c in row.findall(f"{_MAIN_NS}c"):
            ref = c.get("r") or ""
            idx = _col_index(ref) if ref else len(out)
            while len(out) <= idx:
                out.append("")
            out[idx] = _cell_text(c, shared)
        if any(cell != "" for cell in out):
            rows[row.get("r") or len(rows) + 1] = out
    return list(rows.values())


def sheet_rows(data: bytes) -> dict:
    """``{sheet_name: rows}`` — rows are string lists in sheet order."""
    if not data:
        raise XlsxError("empty xlsx payload")
    if len(data) > MAX_BYTES:
        raise XlsxError(f"payload too large ({len(data)} bytes)")
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise XlsxError("not a valid XLSX (zip) payload")
    try:
        wb = ET.fromstring(_member(zf, "xl/workbook.xml"))
        shared_xml = _member(zf, "xl/sharedStrings.xml") if "xl/sharedStrings.xml" in zf.namelist() else None
    except XlsxError:
        raise
    shared: list = []
    if shared_xml is not None:
        try:
            sst = ET.fromstring(shared_xml)
            shared = [
                "".join(t.text or "" for t in si.iter(f"{_MAIN_NS}t"))
                for si in sst.findall(f"{_MAIN_NS}si")
            ]
        except ET.ParseError as exc:
            raise XlsxError(f"malformed sharedStrings: {exc}")
    sheets: dict = {}
    order = []
    for sheet in wb.iter(f"{_MAIN_NS}sheet"):
        name = sheet.get("name") or f"sheet{len(sheets) + 1}"
        rid = sheet.get(f"{_OFFICE_REL}id")
        if rid is None:
            raise XlsxError(f"sheet {name!r} has no relationship id")
        try:
            sheets[name] = _parse_sheet(_member(zf, _sheet_path(zf, rid)), shared)
        except ET.ParseError as exc:
            raise XlsxError(f"malformed sheet {name!r}: {exc}")
        order.append(name)
    if not order:
        raise XlsxError("workbook has no sheets")
    return {name: sheets[name] for name in order}


def first_named_sheet(data: bytes, names) -> list:
    """Rows of the first sheet whose name matches (case-insensitive) one
    of ``names`` — the layout pin for a known export. No match raises."""
    sheets = sheet_rows(data)
    wanted = {n.casefold() for n in names}
    for name, rows in sheets.items():
        if name.casefold() in wanted:
            return rows
    raise XlsxError(f"no sheet named any of {sorted(wanted)} (have {list(sheets)})")

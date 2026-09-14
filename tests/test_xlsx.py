"""xlsx reader (D24 stdlib-only): fixtures built in-test via zipfile —
no binary blob, no openpyxl."""

import io
import zipfile

import pytest

from leadhs import xlsx


def _write_xlsx(sheets: dict, shared=None) -> bytes:
    """Minimal OOXML writer for fixtures (workbook + rels + sheets)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        names = list(sheets)
        sheet_entries = "".join(
            f'<sheet name="{n}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, n in enumerate(names)
        )
        zf.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f"<sheets>{sheet_entries}</sheets></workbook>",
        )
        rels = "".join(
            f'<Relationship Id="rId{i + 1}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{i + 1}.xml"/>'
            for i in range(len(names))
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>',
        )
        for i, (name, rows) in enumerate(sheets.items(), start=1):
            body = "".join(
                "<row r='%d'>%s</row>" % (
                    r + 1,
                    "".join(
                        ("<c r='%s%d' t='s'><v>%d</v></c>" % (_col(c), r + 1, v))
                        if isinstance(v, int)
                        else ("<c r='%s%d' t='inlineStr'><is><t>%s</t></is></c>" % (_col(c), r + 1, v))
                        for c, v in enumerate(row)
                    ),
                )
                for r, row in enumerate(rows)
            )
            zf.writestr(
                f"xl/worksheets/sheet{i}.xml",
                f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">{body}</worksheet>',
            )
        if shared is not None:
            zf.writestr(
                "xl/sharedStrings.xml",
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                + "".join(f"<si><t>{s}</t></si>" for s in shared)
                + "</sst>",
            )
    return buf.getvalue()


def _col(i: int) -> str:
    return chr(65 + i)


def test_shared_strings_and_inline_cells():
    data = _write_xlsx({"Blue Angel": [["Manufacturer", "Product"], ["Acme", "Paint A"]]}, shared=["shared-cell"])
    sheets = xlsx.sheet_rows(data)
    assert list(sheets) == ["Blue Angel"]
    assert sheets["Blue Angel"][0] == ["Manufacturer", "Product"]
    assert sheets["Blue Angel"][1] == ["Acme", "Paint A"]


def test_shared_string_cell():
    # a t='s' cell resolves through sharedStrings (int values in the fixture)
    payload = _write_xlsx({"S": [[0, 1]]}, shared=["x", "y"])
    sheets = xlsx.sheet_rows(payload)
    assert sheets["S"][0] == ["x", "y"]


def test_multi_sheet_order():
    data = _write_xlsx({"Second": [["b"]], "First": [["a"]]})
    sheets = xlsx.sheet_rows(data)
    assert list(sheets) == ["Second", "First"]


def test_first_named_sheet():
    data = _write_xlsx({"Info": [["meta"]], "Products": [["mfr"]]})
    assert xlsx.first_named_sheet(data, ["products"]) == [["mfr"]]
    with pytest.raises(xlsx.XlsxError):
        xlsx.first_named_sheet(data, ["Missing"])


def test_corrupt_and_empty():
    with pytest.raises(xlsx.XlsxError):
        xlsx.sheet_rows(b"not a zip")
    with pytest.raises(xlsx.XlsxError):
        xlsx.sheet_rows(b"")
    with pytest.raises(xlsx.XlsxError):
        xlsx.sheet_rows(b"PK\x03\x04truncated")

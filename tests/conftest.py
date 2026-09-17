"""pytest fixtures: local fixture site, temp DB/register, fake clock."""

import gzip
import http.server
import json
import os
import socketserver
import threading

import pytest

from leadhs import db as dbmod


def _urlset(locs) -> bytes:
    items = "".join(f"<url><loc>{u}</loc></url>" for u in locs)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{items}</urlset>"
    ).encode()


def _sitemapindex(children) -> bytes:
    items = "".join(f"<sitemap><loc>{u}</loc></sitemap>" for u in children)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{items}</sitemapindex>"
    ).encode()


# Recon fixture sitemaps (v0.2.0 t10): per-host robots declares the
# sitemap; paths are unique across the fixture site.
_RECON_DECLARED = {
    "127.0.0.21": "/sitemap.xml.gz",  # gzipped urlset (e4)
    "127.0.0.22": "/ns-sitemap.xml",  # namespaced urlset (e5)
    "127.0.0.23": "/index.xml",       # index + 3 children
    "127.0.0.24": "/index8.xml",      # index + 8 children → cap 5
    "127.0.0.25": "/index-nested.xml",  # nested index → noted, not recursed
    "127.0.0.27": "/sitemap-big.xml",   # oversized → SizeLimit (e3)
    "127.0.0.28": "/sitemap-bad.xml",   # malformed XML
}
_SITEMAP_GZ = gzip.compress(_urlset([f"/product/g{i}" for i in range(2)]))


def _as_xlsx() -> bytes:
    """v0.2.4 addendum (D37): minimal real XLSX for the AS-probe
    registry delivery test (2 inline-str cells + 1 numeric header cell
    is enough — sheet_rows returns the string list)."""
    import io as _io
    import zipfile as _zf

    buf = _io.BytesIO()
    with _zf.ZipFile(buf, "w") as zf:
        zf.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Products" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            'Target="worksheets/sheet1.xml"/></Relationships>',
        )
        zf.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<row r='1'><c r='A1' t='inlineStr'><is><t>Manufacturer</t></is></c>"
            "<c r='B1' t='inlineStr'><is><t>Product</t></is></c></row>"
            "<row r='2'><c r='A2' t='inlineStr'><is><t>Acme GmbH</t></is></c>"
            "<c r='B2' t='inlineStr'><is><t>Paint A</t></is></c></row>"
            "<row r='3'><c r='A3' t='inlineStr'><is><t>Beier AG</t></is></c>"
            "<c r='B3' t='inlineStr'><is><t>Paint B</t></is></c></row></worksheet>",
        )
    return buf.getvalue()


_AS_EXPORT_XLSX = _as_xlsx()


class _FixtureSite(http.server.BaseHTTPRequestHandler):
    hits = {}

    def log_message(self, *a):
        pass

    def do_GET(self):
        _FixtureSite.hits[self.path] = _FixtureSite.hits.get(self.path, 0) + 1
        p, _, query = self.path.partition("?")
        if p == "/robots.txt":
            host = self.headers.get("Host", "")
            ip = host.rsplit(":", 1)[0]
            body = b"User-agent: *\nDisallow: /private/\n"
            if ip in _RECON_DECLARED:
                body += f"Sitemap: http://{host}{_RECON_DECLARED[ip]}\n".encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
        elif p == "/empty-robots.txt":
            self.send_response(200)
            self.end_headers()
        elif p == "/robots-403.txt":
            self.send_response(403)
            self.end_headers()
        elif p == "/":
            html = b"""<html lang="de"><head><link rel="alternate" hreflang="fr" href="/?lang=fr"/></head>
<body><nav><a href="/cat/wandfarben">Wandfarben</a><a href="/cat/grundierung">Grundierung</a><a href="/cat/broken">Kaputt</a></nav>
<p>500 Produkte</p><a href="/terms">AGB</a>
<a href="/p/1.html">Produkt 1</a><a href="/p/2.html">Produkt 2</a><a href="/p/3.html">Produkt 3</a>
<a href="/p/4.html">Produkt 4</a></body></html>"""
            self._html(html)
        elif p.startswith("/p/"):
            has_sds = "sds" if p in ("/p/1.html", "/p/2.html", "/p/4.html") else ""
            if p == "/p/4.html":
                self.send_response(403)
                self.end_headers()
                return
            sds_html = '<a href="/sds/sheet.pdf">SDS</a>' if has_sds else ""
            self._html(f"<html><body><h1>Product {p}</h1>{sds_html}</body></html>".encode())
        elif p == "/cat/wandfarben":
            self._html(b'<html><body>Wandfarben category <a href="/p/10.html">Produkt 10</a>'
                       b'<a href="/p/11.html">Produkt 11</a></body></html>')
        elif p == "/cat/grundierung":
            self._html(b"<html><body>Grundierung category</body></html>")
        elif p == "/many-cats":
            links = "".join(f'<a href="/cat/c{i}">Cat {i}</a>' for i in range(1, 16))
            self._html(f"<html><body>{links}</body></html>".encode())
        elif p == "/nested-cats":
            self._html(b'<html><body><a href="/cat/n1">N1</a></body></html>')
        elif p == "/cat/n1":
            self._html(b'<html><body><a href="/cat/n1sub">Sub</a>'
                       b'<a href="/p/n1.html">Produkt n1</a></body></html>')
        elif p == "/cat/n1sub":
            self._html(b'<html><body><a href="/cat/n1subsub">Sub2</a>'
                       b'<a href="/p/n1sub.html">Produkt n1sub</a></body></html>')
        elif p == "/cat/n1subsub":
            self._html(b'<html><body><a href="/cat/n1subsubsub">Sub3</a>'
                       b'<a href="/p/n1subsub.html">Produkt n1subsub</a></body></html>')
        elif p.startswith("/cat/c"):
            self._html(f"<html><body>Category {p} "
                       f"<a href=\"/p{p}.html\">Produkt</a></body></html>".encode())
        elif p == "/terms":
            self._html(b"<html><body>AGB</body></html>")
        elif p == "/export.csv":
            body = b"hs_code,year,partner,value\n3208,2023,DE,100\n3209,2023,FR,200\n3208,2024,AT,50\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/reg.csv":
            # v0.2.1 capability fixture: register with manufacturer,
            # product-ident and CN8 nomenclature columns.
            body = (
                b"product_name,manufacturer,licence_no,cn_code\n"
                b"Paint A,Acme GmbH,DE-1234,32089000\n"
                b"Paint B,Acme GmbH,DE-5678,32089000\n"
                b"Paint C,Beier AG,DE-9999,32091000\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/reg-manufacturer.csv":
            # manufacturer + CN8, but no product-ident column
            body = (
                b"product_name,manufacturer,cn_code\n"
                b"Paint A,Acme GmbH,32089000\n"
                b"Paint B,Acme GmbH,32091000\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/reg-no-nomenclature.csv":
            # manufacturer + product-ident, but no CN8/nomenclature column
            body = (
                b"product_name,manufacturer,licence_no\n"
                b"Paint A,Acme GmbH,DE-1234\n"
                b"Paint B,Beier AG,DE-5678\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/reg-empty.csv":
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(b"")
        elif p == "/reg-bad.csv":
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(b"product_name\n")
        elif p == "/reg.json":
            body = json.dumps([
                {"name": "Paint A", "manufacturer": "Acme GmbH", "licence_no": "DE-1234", "cn_code": "32089000"},
                {"name": "Paint B", "manufacturer": "Acme GmbH", "licence_no": "DE-5678", "cn_code": "32091000"},
            ]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/export-bad.csv":
            body = b"a,b,c\n1,2,3\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/api.json":
            # od9: parameterized CS query — empty result set for HS 3213.
            # v0.2.0 nu2: indicators queries get the JSON-stat aggregation
            # shape (partner as the one free dimension).
            # v0.2.2 W1: 8-digit product codes = the per-CN8 batch —
            # declarant × period shape (multi-dim decode).
            product = None
            for part in query.split("&"):
                if part.startswith("product="):
                    product = part.split("=", 1)[1]
            if "indicators=" in query and product and len(product) == 8:
                indicator = next(
                    (p.split("=", 1)[1] for p in query.split("&") if p.startswith("indicators=")), ""
                )
                data = _jsonstat_batch(indicator)
            elif "indicators=" in query:
                data = _jsonstat({"DE": 100.0, "FR": 250.0, "BE": 50.0})
            else:
                rows = [] if "product=3213" in query else [{"x": 1}, {"x": 2}, {"x": 3}]
                data = {"value": rows}
            self._json(data)
        elif p == "/api-agg.json":
            # nu2 fixture: JSON-stat with partner as the one free dimension;
            # empty for 2024 (one step-back to 2023 supplies data) — an
            # empty result keeps the full dimension shape, value {} only
            if "indicators=" in query:
                if "time=2024" in query:
                    data = _jsonstat({}, labels=["DE", "FR", "IT"])
                else:
                    data = _jsonstat({"DE": 10.0, "FR": 30.0, "IT": 20.0})
            else:
                rows = [] if "product=3213" in query else [{"x": 1}]
                data = {"value": rows}
            self._json(data)
        elif p == "/api-empty.json":
            # nu2 fixture: aggregation always empty → step-back exhausted
            if "indicators=" in query:
                data = _jsonstat({}, labels=["DE", "FR", "IT"])
            else:
                data = {"value": [{"x": 1}]}
            self._json(data)
        elif p == "/api-bad.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"value": "not-a-list"}')
        elif p == "/ecat.csv":
            # v0.2.2 W1 fixture: ECAT-shaped export — 2 in-scope paint rows
            # + 1 furniture row (group filter drops it)
            body = (
                b"product_or_service_name,company_name,group_name,code_value\n"
                b"Paint A,Acme GmbH,Decorative paints,0076000001\n"
                b"Paint B,Beier AG,Paints & varnishes,\n"
                b"Office chair,Chairs Ltd,Furniture,42\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/ecat-furniture.csv":
            body = (
                b"product_or_service_name,company_name,group_name,code_value\n"
                b"Office chair,Chairs Ltd,Furniture,42\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/ecat-pool.csv":
            # v0.2.4 sample fixture: 10 distinct paint products x 3
            # duplicate rows each + 2 furniture rows — a pool with
            # headroom (determinism/dedupe tests draw n=10 of 10 distinct
            # items; the furniture rows exercise the group filter).
            lines = ["product_or_service_name,company_name,group_name,code_value"]
            for i in range(10):
                for _ in range(3):
                    lines.append(f"Paint {i:02d},Acme GmbH,Decorative paints,00760000{i:02d}")
            lines.append("Office chair,Chairs Ltd,Furniture,42")
            lines.append("Desk lamp,Chairs Ltd,Furniture,43")
            body = ("\n".join(lines) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/ns-pool.csv":
            # D38 fixture: Nordic-Swan-shaped export (semicolon, the
            # real header). 20 distinct paint items (10 NS + 10 EU
            # Ecolabel rows) x 3 duplicate rows + out-of-scope rows a
            # whole-record substring filter would wrongly admit
            # ("Black" contains "lack", "painting" contains "paint") —
            # the structured product-group filter must drop them.
            hdr = ("Product;License number;Ecolabel;Category;Product group;"
                   "Criteria generation;Brand;Licensee;Address;City")
            lines = [hdr]
            for i in range(10):
                for _ in range(3):
                    lines.append(
                        f"NS Paint {i:02d};4096 00{i:02d};Nordic Swan Ecolabel;"
                        f"Indoor paints.;096 Paints and varnishes;4;Teknos;"
                        f"Teknos Oy;Takkatie 3;Helsinki"
                    )
                    lines.append(
                        f"EU Paint {i:02d};DK/044/00{i};EU Ecolabel;"
                        f"Indoor paints (EU-Ecolabel);"
                        f"EU44 Decorative paints, varnishes, and related products;"
                        f"1;PPG;PPG Coatings A/S;Gladsaxevej 300;Søborg"
                    )
            lines.append(
                "TURBON Toner Black, (TN 135C);3008 0046 (308046);"
                "Nordic Swan Ecolabel;Brother;"
                "008 Refurbished OEM Toner and Ink Cartridges;5;Turbon;"
                "Turbon SRL;Jud.Calarasi;Oltenita"
            )
            lines.append(
                "ABENA Puri Line Grundrent;5026 0015;Nordic Swan Ecolabel;"
                "Interior cleaning agent before painting;026 Cleaning products;"
                "6;ABENA;Novadan ApS;Platinvej 21;Kolding"
            )
            body = ("\n".join(lines) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/ns-furniture.csv":
            hdr = ("Product;License number;Ecolabel;Category;Product group;"
                   "Criteria generation;Brand;Licensee;Address;City")
            lines = [hdr,
                     "Mood Learn Chair;DK/049/007;EU Ecolabel;Chair (EU Ecolabel);"
                     "EU49 Furniture;1;Mood;Mood A/S;Islevdalvej 151;Rødovre"]
            body = ("\n".join(lines) + "\n").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/ecat.html":
            self._html(b"<html><body>landing page</body></html>")
        elif p == "/sitemap.xml":
            ip = (self.headers.get("Host") or "").rsplit(":", 1)[0]
            if ip != "127.0.0.20":  # only the happy-path host serves the fallback
                self.send_response(404)
                self.end_headers()
                return
            host = self.headers.get("Host", "")
            self._xml(_urlset([f"http://{host}/product/{i}" for i in range(3)] + [f"http://{host}/about"]))
        elif p == "/sitemap.xml.gz":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-gzip")
            self.end_headers()
            self.wfile.write(_SITEMAP_GZ)
        elif p == "/ns-sitemap.xml":
            body = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<ns:urlset xmlns:ns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + "".join(f'<ns:url><ns:loc>/product/ns{i}</ns:loc></ns:url>' for i in range(2))
                + "</ns:urlset>"
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/index.xml":
            self._xml(_sitemapindex([f"/c{i}.xml" for i in range(1, 4)]))
        elif p == "/index8.xml":
            self._xml(_sitemapindex([f"/d{i}.xml" for i in range(1, 9)]))
        elif (p.startswith("/c") or p.startswith("/d")) and p.endswith(".xml"):
            self._xml(_urlset([f"/product/{p[1:]}-a", f"/product/{p[1:]}-b"]))
        elif p == "/index-nested.xml":
            self._xml(_sitemapindex(["/sitemap-nested.xml"]))
        elif p == "/sitemap-nested.xml":
            self._xml(_sitemapindex(["/deep.xml"]))
        elif p == "/sitemap-big.xml":
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(b"<urlset>" + b"<url><loc>/product/x</loc></url>" * 3000 + b"</urlset>")
        elif p == "/sitemap-bad.xml":
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(b'<urlset><url><loc>/product/broken')
        elif p == "/private/secret":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"secret")
        elif p == "/forbidden":
            self.send_response(403)
            self.end_headers()
        elif p == "/ratelimited-once":
            if _FixtureSite.hits.get(p, 0) == 1:
                self.send_response(429)
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok-after-429")
        elif p == "/ratelimited-always":
            self.send_response(429)
            self.end_headers()
        elif p == "/error500":
            self.send_response(500)
            self.end_headers()
        elif p == "/empty.html":
            self._html(b"")
        elif p == "/huge.html":
            self._html(b"<html><body>" + b"<a href='/p/9.html'>x</a>" * 2000 + b"</body></html>")
        elif p == "/non-utf8.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=iso-8859-1")
            self.end_headers()
            self.wfile.write(b"<html><body>\xff\xfe broken</body></html>")
        elif p == "/as-export.xlsx":
            # v0.2.4 addendum (D37): real XLSX export for the AS-probe
            # registry path (sniff → xlsx → sheet_rows → CSV rendering).
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.end_headers()
            self.wfile.write(_AS_EXPORT_XLSX)
        elif p == "/as-count.html":
            # landing page with a visible record count (estimate pass)
            self._html(b"<html><body>12,400 certified products in this database</body></html>")
        elif p == "/assoc.html":
            # association landing with a visible member count
            self._html(b"<html><body>1,200 member companies across the sector</body></html>")
        elif p == "/basta-robots.txt":
            # D40 decision 4B: a robots file declaring Crawl-delay —
            # the fetcher must pace at max(min_spacing, crawl_delay).
            body = b"User-agent: *\nAllow: /\nCrawl-delay: 10\n"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)
        elif p == "/sok":
            # D40: the client-shell SSR nav, no result rows; variant per
            # loopback host — HAPPY (pin found), NF (bundles 404), AUTH
            # (shell itself auth-gated).
            ip = (self.headers.get("Host") or "").rsplit(":", 1)[0]
            scripts = {
                "127.0.0.60": ['<script src="/assets/app-a.js"></script>',
                               '<script src="/assets/app-b.js"></script>'],
                "127.0.0.61": ['<script src="/assets/missing.js"></script>'],
                "127.0.0.62": ['<script src="/assets/app-c.js"></script>'],
            }.get(ip, ['<script src="/assets/app-a.js"></script>',
                       '<script src="/assets/app-b.js"></script>'])
            if ip == "127.0.0.63":
                self.send_response(401)
                self.end_headers()
                return
            self._html(('<html><body><div data-component="Search"></div>' + "".join(scripts)
                        + "</body></html>").encode())
        elif p == "/assets/app-a.js":
            body = (b'var cfg={search:"/api-articles",cdn:"https://cdn.example.com/'
                    b'search-ui.js"};function go(){fetch(cfg.search)}')
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/assets/app-c.js":
            body = b'var cfg={search:"/api-articles-meta"};function g2(){fetch(cfg.search)}'
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/assets/app-b.js":
            body = b"var cfg={};console.log(cfg)"
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            self.wfile.write(body)
        elif p == "/basta.json":
            data = json.dumps({"total": 25, "items": [
                {"name": "Paint A", "articleNumber": "AR-0001", "company": "Acme AB",
                 "bastaId": "B0001", "gtin": "7300000000011", "bk04": "211", "category": "paints"},
                {"name": "Paint B", "articleNumber": "AR-0002", "company": "Acme AB",
                 "bastaId": "B0002", "gtin": "", "bk04": "211", "category": "paints"},
            ]}).encode()
            self._json(data)
        elif p.startswith("/api-articles"):
            # paginated article route: honors page, pageSize, the
            # category=paint filter, and a `fixed=1` mode that serves the
            # same overflow-size batch every page (a route whose total is
            # unknown — the truncated head-of-pool exercise).
            params = dict(kv.split("=", 1) for kv in query.split("&") if "=" in kv)
            page = int(params.get("page", "1"))
            size = int(params.get("pageSize", "2"))
            all_items = [
                {
                    "name": f"Paint {i:02d}", "articleNumber": f"AR-{i:04d}",
                    "company": ("Acme AB" if i % 2 else "Beier AB"),
                    "bastaId": f"B{i:04d}", "gtin": (f"73000000000{i:02d}" if i % 3 else ""),
                    "bk04": "211", "category": ("toner" if i == 6 else "paints"),
                }
                for i in range(1, 7)
            ]
            if params.get("category") in ("paint", "paints"):
                all_items = [x for x in all_items if x["category"] == "paints"]
            if params.get("fixed") == "1":
                self._json(all_items[: size])
            elif "meta" in p:
                self._json({
                    "total": len(all_items),
                    "items": all_items[(page - 1) * size: page * size],
                })
            else:
                self._json(all_items[(page - 1) * size: page * size])
        elif p == "/api-keyfigures":
            self._json({"text": "195390 articles and 1925 companies"})
        elif p == "/api-lock":
            self.send_response(401)
            self.end_headers()
        elif p == "/spin":
            self._html(b'<html><body><a href="/data.mdb">SPIN database download</a></body></html>')
        elif p == "/data.mdb":
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(b"MDBDATA")
        else:
            self.send_response(404)
            self.end_headers()

    def _html(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def _xml(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


def _jsonstat(partner_values: dict, labels=None) -> dict:
    """JSON-stat 2.0 payload with partner as the one free dimension
    (value object keyed by flat index — the e2/2A shape). ``labels``
    keeps the full dimension shape when the result set is empty."""
    keys = labels or list(partner_values)
    index = {k: i for i, k in enumerate(keys)}
    return {
        "version": "2.0",
        "class": "dataset",
        "id": ["partner"],
        "size": [len(keys)],
        "dimension": {"partner": {"category": {"index": index, "label": {}}}},
        "value": {str(i): v for i, v in enumerate(partner_values.values())},
    }


def _jsonstat_batch(indicator: str) -> dict:
    """v0.2.2 W1 batch shape: declarant × period free; flow/product/
    indicators pinned at size 1 — the multi-dim decode shape."""
    return {
        "version": "2.0",
        "class": "dataset",
        "id": ["declarant", "time", "flow", "product", "indicators"],
        "size": [2, 1, 1, 1, 1],
        "dimension": {
            "declarant": {"category": {"index": {"DE": 0, "FR": 1}, "label": {}}},
            "time": {"category": {"index": {"2024": 0}, "label": {}}},
            "flow": {"category": {"index": {"1": 0}, "label": {}}},
            "product": {"category": {"index": {"32081010": 0}, "label": {}}},
            "indicators": {"category": {"index": {indicator: 0}, "label": {}}},
        },
        "value": {"0": 10.0, "1": 20.0},
    }


@pytest.fixture(scope="session")
def site():
    # Binds all interfaces (not just 127.0.0.1) so the loopback aliases
    # 127.0.0.2..127.0.0.15 (all of 127.0.0.0/8 routes to localhost on
    # Linux) reach the fixture server — the fixture register gives every
    # active row its own host because the duplicate-active-host load
    # validation (i13) requires one host per active register row.
    _FixtureSite.hits.clear()
    srv = socketserver.TCPServer(("", 0), _FixtureSite)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{port}"
    srv.shutdown()


@pytest.fixture()
def site_hits():
    _FixtureSite.hits.clear()
    yield _FixtureSite.hits


@pytest.fixture()
def db_path(tmp_path):
    return str(tmp_path / "t.sqlite")


@pytest.fixture()
def conn(db_path):
    c = dbmod.connect(db_path)
    dbmod.migrate(c, db_path=db_path)
    yield c
    c.close()


@pytest.fixture()
def store(db_path):
    from leadhs.store import RawStore

    return RawStore(os.path.join(os.path.dirname(db_path), "raw"))


@pytest.fixture()
def fixture_register(tmp_path, site):
    port = site.rsplit(":", 1)[1]

    def h(i: int) -> str:
        return f"http://127.0.0.{i}:{port}"

    path = tmp_path / "register.csv"
    rows = [
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes",
        f"PX-1,PE,Fixture catalog,{h(1)}/,scrape,,open,1,census good catalog",
        f"PX-2,PE,Robots-denied,{h(2)}/private/secret,scrape,,open,1,robots deny",
        f"PX-3,PE,Blocked 403,{h(3)}/forbidden,scrape,,open,1,403",
        f"PX-4,PE,Persistent 429,{h(4)}/ratelimited-always,scrape,,open,1,429",
        f"PX-5,PE,429 once,{h(5)}/ratelimited-once,scrape,,open,1,429-then-ok",
        f"PX-6,PE,Empty page,{h(6)}/empty.html,scrape,,open,1,parse error",
        f"PX-7,PE,Huge page,{h(7)}/huge.html,scrape,,open,1,hostile",
        f"PX-8,PE,Non-utf8,{h(8)}/non-utf8.html,scrape,,open,1,hostile",
        f"PX-9,PE,Missing page,{h(9)}/missing,scrape,,open,1,404",
        f"CX-1,CS,Fixture export,{h(10)}/export.csv,download,,open,1,good csv",
        f"CX-2,CS,Fixture bad export,{h(11)}/export-bad.csv,download,,open,1,bad layout",
        f"CX-3,CS,Fixture api,{h(12)}/api.json,api,,open,1,json",
        f"CX-4,CS,Fixture 500,{h(13)}/error500,api,,open,1,network fail",
        f"SX-1,ST,Fixture spin,{h(14)}/spin,download,,open,1,mdbtools",
        f"ST-1,ST,PCN stats,{h(15)}/missing,manual,,open,0,manual-web via probe record",
        f"AX-1,AS,Fixture register,{h(16)}/reg.csv,download,,open,1,capability fixture (mfr+ident+cn8)",
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return str(path)


@pytest.fixture()
def loaded_conn(conn, fixture_register):
    from leadhs.source import load

    load(conn, fixture_register)
    return conn


class FakeClock:
    def __init__(self, start: float = 1000.0):
        self.t = start

    def now(self) -> float:
        return self.t

    def sleep(self, s: float) -> None:
        self.t += s


@pytest.fixture()
def fake_clock():
    return FakeClock()


@pytest.fixture()
def make_fetcher():
    from leadhs.fetch import FetchConfig, Fetcher

    def _make(fake_clock=None, contact="test@example.com", **cfg):
        if fake_clock is None:
            fake_clock = FakeClock()  # t2: no real waiting in the suite
        cfg.setdefault("clock", fake_clock.now)
        cfg.setdefault("sleeper", fake_clock.sleep)
        return Fetcher(FetchConfig(contact=contact, **cfg), logger=None)

    return _make


@pytest.fixture()
def fetcher(make_fetcher):
    return make_fetcher()


# ------------------------------------------------------------------
# v0.2.3 shared synthetic-staging builder (ENG 2A): one builder feeds
# the refinement, benchmark and verdict-path tests. Groups control the
# key-tier structure exactly — (n_rows, n_eans, n_names, n_licences)
# makes the per-tier collapse factors n_rows/n_eans, n_rows/n_names,
# n_rows/n_licences known a priori, so hostile distributions can flip
# the factor ranking deterministically.
# ------------------------------------------------------------------

@pytest.fixture()
def make_synthetic_staging(tmp_path):
    import json as _json

    from leadhs import db as dbmod
    from leadhs import staging as stgmod

    def _doc(i: int) -> dict:
        return {
            "url": f"https://fixture.invalid/export-{i}",
            "doc_hash": f"hash-{i:04d}",
            "retrieval_date": "2026-09-14",
        }

    def _register_rows(source_id: str, groups) -> list:
        rows = []
        i = 0
        for n_rows, n_eans, n_names, n_licences in groups:
            for _ in range(n_rows):
                ean = f"E{i % n_eans:06d}" if n_eans else ""
                name = f"Name {i % n_names:04d}" if n_names else ""
                rows.append(
                    {
                        "manufacturer_raw": "MFR",
                        "manufacturer_norm": "mfr",
                        "ident_raw": ean or name,
                        "ident_norm": ean or name,
                        "ident_type": "gtin" if ean else "none",
                        "ident_basis": "ident" if ean else "name",
                        "name": name,
                        "category_raw": "Decorative paints, varnishes, and related products (2014 criteria)",
                        "raw": _json.dumps(
                            {"licence_number": f"XX/044/{i % n_licences:03d}", "company_name": "MFR"}
                        ),
                    }
                )
                i += 1
        return rows

    def _make(
        ecat_groups=None,
        ecat_source="AS-2",
        trade_rows=None,
        dk=None,
        sources=None,
    ):
        """``sources``: [(source_id, class_code, notes, [(metric_code, value), …])]
        — inserted into the evidence DB (source + done probe run +
        findings), so ``metric_value``/``pe_distribution`` see them."""
        stg = stgmod.connect(":memory:")
        stgmod.init(stg)
        stgmod.seed_dict(stg)
        if ecat_groups:
            stgmod.replace_products(stg, ecat_source, "synthetic-001", _doc(1), _register_rows(ecat_source, ecat_groups))
        if dk:
            dk_source, dk_groups = dk
            stgmod.replace_products(stg, dk_source, "synthetic-dk", _doc(2), _register_rows(dk_source, dk_groups))
        if trade_rows:
            stgmod.replace_trade(
                stg, "CS-2", "synthetic-trade", _doc(3),
                [{"cn8": cn8, "flow": "1", "declarant": "EU", "partner": "WLD", "year": "2024", "kg": kg, "eur": kg} for cn8, kg in trade_rows],
            )

        ev = dbmod.connect(str(tmp_path / "ev-synth.sqlite"))
        dbmod.migrate(ev, db_path=str(tmp_path / "ev-synth.sqlite"))
        for source_id, class_code, notes, findings in sources or []:
            ev.execute(
                "INSERT INTO source (id, class_code, name, url, access_method_code, active, notes) "
                "VALUES (?, ?, 'synthetic', 'https://fixture.invalid', 'manual', 1, ?)",
                (source_id, class_code, notes),
            )
            run_key = f"synthetic-{source_id.lower()}"
            ev.execute(
                "INSERT INTO run (run_key, kind_code, source_id, started_at, finished_at, status_code) "
                "VALUES (?, 'probe', ?, '2026-09-14T00:00:00Z', '2026-09-14T00:00:00Z', 'done')",
                (run_key, source_id),
            )
            run_id = ev.execute("SELECT id FROM run WHERE run_key=?", (run_key,)).fetchone()[0]
            ev.execute("INSERT INTO probe_run (run_id, mode_code) VALUES (?, 'census')", (run_id,))
            for metric_code, value in findings:
                ev.execute(
                    "INSERT INTO probe_finding (run_id, metric_code, value_numeric, method_code) "
                    "VALUES (?, ?, ?, 'manual')",
                    (run_id, metric_code, value),
                )
        ev.commit()
        return stg, ev

    return _make
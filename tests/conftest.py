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
            if "indicators=" in query:
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
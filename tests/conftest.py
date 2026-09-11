"""pytest fixtures: local fixture site, temp DB/register, fake clock."""

import http.server
import json
import os
import socketserver
import threading

import pytest

from leadhs import db as dbmod


class _FixtureSite(http.server.BaseHTTPRequestHandler):
    hits = {}

    def log_message(self, *a):
        pass

    def do_GET(self):
        _FixtureSite.hits[self.path] = _FixtureSite.hits.get(self.path, 0) + 1
        p, _, query = self.path.partition("?")
        if p == "/robots.txt":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"User-agent: *\nDisallow: /private/\n")
        elif p == "/empty-robots.txt":
            self.send_response(200)
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
            # od9: parameterized CS query — empty result set for HS 3213
            rows = [] if "product=3213" in query else [{"x": 1}, {"x": 2}, {"x": 3}]
            data = json.dumps({"value": rows}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
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


@pytest.fixture(scope="session")
def site():
    _FixtureSite.hits.clear()
    srv = socketserver.TCPServer(("127.0.0.1", 0), _FixtureSite)
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
    path = tmp_path / "register.csv"
    rows = [
        "id,class_code,name,url,access_method_code,license_note,verification_status_code,active,notes",
        f"PX-1,PE,Fixture catalog,{site}/,scrape,,open,1,census good catalog",
        f"PX-2,PE,Robots-denied,{site}/private/secret,scrape,,open,1,robots deny",
        f"PX-3,PE,Blocked 403,{site}/forbidden,scrape,,open,1,403",
        f"PX-4,PE,Persistent 429,{site}/ratelimited-always,scrape,,open,1,429",
        f"PX-5,PE,429 once,{site}/ratelimited-once,scrape,,open,1,429-then-ok",
        f"PX-6,PE,Empty page,{site}/empty.html,scrape,,open,1,parse error",
        f"PX-7,PE,Huge page,{site}/huge.html,scrape,,open,1,hostile",
        f"PX-8,PE,Non-utf8,{site}/non-utf8.html,scrape,,open,1,hostile",
        f"PX-9,PE,Missing page,{site}/missing,scrape,,open,1,404",
        f"CX-1,CS,Fixture export,{site}/export.csv,download,,open,1,good csv",
        f"CX-2,CS,Fixture bad export,{site}/export-bad.csv,download,,open,1,bad layout",
        f"CX-3,CS,Fixture api,{site}/api.json,api,,open,1,json",
        f"CX-4,CS,Fixture 500,{site}/error500,api,,open,1,network fail",
        f"SX-1,ST,Fixture spin,{site}/spin,download,,open,1,mdbtools",
        f"ST-1,ST,PCN stats,{site}/missing,manual,,open,0,manual-web via probe record",
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
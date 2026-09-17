"""BASTA special probe (v0.2.4 addendum, D40) — pin an anonymous
search route behind the BASTA online client shell (bastaonline.se
/sok), characterize data availability and structure, and deliver a
seeded random sample of 100 articles as CSV with the identity tuple
(manufacturer + product ident) and the BK04/BSAB category proxy.

`leadhs probe basta-probe` runs the D40 state machine for AS-33:

    pending ──▶ delivered            (basta_special_rows; exit 0)
         ────▶ unavailable-mech      (basta_special_unavailable, expected → exit 0)
         ────▶ failed                (network failure on pinned URLs only → exit 2)

Recon record (accessed 2026-09-17): robots.txt `Allow: /` with
`Crawl-delay: 10` (the fetcher honors it, decision 4B); API v3 at
api.bastaonline.se is auth-gated (401 anonymous — the agreement route
is documented, never pursued under D4); exact public counts at
/api/keyfigures/1 = 195,390 articles and /api/keyfigures/2 = 1,925
companies; article pages carry the identity tuple; /sok is a client
shell with no SSR result rows — the one unproven assumption this
pin stage exists to answer.

Pool method (decision 2C): full pagination up to the pinned pool
threshold → exact pool → seeded reproducible draw (D2); above the
threshold the method falls back to random-page draws when the route
advertises a total, else an honest head-of-pool prefix — the method
actually used is recorded in the finding notes, never silently
switched. A pinned paint filter (db5) sharpens the pool when (and
only when) its parameters were pinned; otherwise all articles are
sampled with the category column kept.
"""

from __future__ import annotations

import json
import os
import random
import re

from .. import ids
from ..fetch import Blocked, FetchError, ProbeNetworkError, RateLimited
from ..logutil import log_event
from ..models import DocumentDraft, FindingDraft, ProbeResult
from . import engine as probeengine
from .csv_sample import (
    PROVENANCE_COLUMNS,
    _finish,
    _identity_key,
    _today,
    _utc_ts,
    _write_sample_csv,
)

# db1 — pinned surfaces (recon 2026-09-17); in live runs the register
# URL is the base, these are the pinned paths exercised on it.
DEFAULT_SOURCE_ID = "AS-33"
SOK_PATH = "/sok"
KEYFIGURES_ARTICLES = "/api/keyfigures/1"
KEYFIGURES_COMPANIES = "/api/keyfigures/2"

# db2 — the discovery budget: /sok + up to four asset bundles; route
# verification gets its own small budget (first-page probes).
_PIN_MAX_GETS = 5
_SHAPE_MAX_GETS = 3

# db3 — the pool threshold (decision 2C); db4 n/seed defaults live in
# the CLI.
_POOL_THRESHOLD = 20_000
_PAGE_SIZE = 250

# db5 — the paint-filter mechanism. None at recon time (2026-09-17
# desk pass did not pin the parameter set) → the default method is
# all-articles sampling with the category column kept. Pinned value
# = (query param, value) applied server-side per page.
_PAINT_FILTER_PARAM = None

# db6 — the article field schema pinned from an SSR article page
# (accessed 2026-09-17); the pinned route's JSON keys supersede this
# for the CSV header, and the pinned JSON names feed the key chains.
_KEY_FIELDS_BASTA = (
    ("company", "company_name", "companyName", "manufacturer"),
    ("articleNumber", "article_number", "articleNo", "art_no"),
    ("bastaId", "basta_id", "id"),
)
_IDENTITY_REPORT_CHAINS = (
    ("articleNumber", "article_number", "articleNo", "gtin"),
    ("bastaId", "basta_id", "id"),
    ("gtin", "articleNumber", "article_number"),
)

# db7 — the auth/agreement wording: why-not only, never contacted (D4).
_AUTH_NOTE = (
    "the documented API v3 (api.bastaonline.se, 24 endpoints per the public "
    "swagger) is auth-gated (401 anonymous); access requires a signed "
    "agreement (bastaonline@ivl.se, contact route documented, never acted "
    "on — no accounts under D4). "
    "https://api.bastaonline.se/swagger/v3/swagger.json (accessed 2026-09-17)"
)
_PIN_NOT_FOUND_TAIL = (
    "; no anonymous JSON route pinned within the polite bundle budget — "
    "the manual browser pass is the next step (TODOS.md, v0.2.4 D40)"
)

_INT_RE = re.compile(r"\d{2,}")
_ASSET_RE = re.compile(r"""(?:src|href)=["']([^"']+\.js(?:\?[^"']*)?)["']""")
_CANDIDATE_RE = re.compile(
    r"""['"]((?:https?://[^'" ]{0,120}|/[^'" ]{0,120}?)"""
    r"""(?:article|sok|search)[^'" ]{0,120})['"]""",
    re.IGNORECASE,
)
_BAD_CANDIDATE = re.compile(
    r"\.(?:css|html|svg|woff2?|png|jpe?g|xml)\b|[ \"<>{}]|robots\.txt|sitemap",
    re.IGNORECASE,
)


# --- run bookkeeping (engine write path, i3) --------------------------------


def _begin_run(conn, source_id: str, parameters: dict) -> tuple:
    slug = ids.slug_for_source(source_id) + "bastaprobe"
    run_id, run_key, _started = probeengine._insert_run(conn, "probe", source_id, slug, parameters)
    probeengine._insert_probe_run(conn, run_id, "basta_special_probe")
    conn.execute("UPDATE run SET seed=? WHERE id=?", (parameters.get("seed"), run_id))
    conn.commit()
    return run_id, run_key


def _entry(status, run_key=None, rows=None, pool=None, method=None, file=None,
           route=None, reason=None):
    return {"status": status, "run_key": run_key, "rows": rows, "pool": pool,
            "method": method, "file": file, "route": route, "reason": reason}


def _unavailable(conn, store, source_id, run_id, run_key, reason, logger=None):
    probeengine.persist(conn, store, source_id, run_id, ProbeResult(
        findings=[FindingDraft(metric_code="basta_special_unavailable",
                               method_code="download", value_text=reason)]))
    _finish(conn, run_id, "unavailable", ["BASTA unavailable"])
    if logger:
        log_event(logger, "basta_probe", "unavailable", source=source_id)
    return _entry("unavailable", run_key, reason=reason)


def _failed(conn, store, source_id, run_id, run_key, detail, logger=None):
    probeengine.persist(conn, store, source_id, run_id, ProbeResult(
        findings=[FindingDraft(metric_code="basta_special_unavailable",
                               method_code="download", value_text=f"FAILED: {detail}")]))
    _finish(conn, run_id, "failed", [detail])
    if logger:
        log_event(logger, "basta_probe", "failed", source=source_id, detail=detail)
    return _entry("failed", run_key, reason=detail)


# --- pin stage (PHASE01) — bundle-chain route discovery ---------------------


def _candidates(text: str) -> list:
    out = []
    for m in _CANDIDATE_RE.finditer(text):
        c = m.group(1).strip()
        if not _BAD_CANDIDATE.search(c) and c not in out:
            out.append(c)
    return out


def _pin(fetcher, base: str, logger=None) -> tuple:
    """PHASE01: fetch /sok, follow the asset bundle chain (≤ db2 GETs
    total; code-grep only — never executes JS), extract candidate
    search-route literals. Returns (candidates, detail, kind) where
    kind is the state-machine kind of a short-circuit: None means the
    chain completed and candidates must be verified."""
    shell_url = base + SOK_PATH
    try:
        resp = fetcher.get(shell_url)
    except (Blocked, RateLimited) as exc:
        return [], f"{exc}", "auth-gated"
    except FetchError as exc:
        if isinstance(exc, ProbeNetworkError):
            return [], f"network failure on the pinned URL: {exc}", "failed"
        return [], f"{exc}", "failed"
    if resp.status_code != 200:
        return [], (f"HTTP {resp.status_code} at {shell_url}"), "unavailable"
    shell_text = resp.content.decode("utf-8", "replace")
    assets = _ASSET_RE.findall(shell_text)
    candidates: list = []
    detail = f"shell {len(assets)} asset script(s)"
    for url in assets[: max(_PIN_MAX_GETS - 1, 0)]:
        url = url if url.startswith("http") else base + url
        try:
            bresp = fetcher.get(url)
        except FetchError as exc:
            # a guessed bundle URL failing is discovery, not delivery
            detail += f"; bundle unreachable ({exc.detail})"
            continue
        if bresp.status_code != 200:
            detail += f"; HTTP {bresp.status_code} on a bundle"
            continue
        candidates.extend(_candidates(bresp.content.decode("utf-8", "replace")))
    return [_c if _c.startswith("http") else base + _c for _c in candidates], detail, None


# --- shape stage (PHASE02) — verify a candidate + counts --------------------


def _items_of(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "articles", "value", "results", "rows"):
            v = payload.get(key)
            if isinstance(v, list):
                return v
    return None


def _total_of(payload) -> int | None:
    if isinstance(payload, dict):
        total = payload.get("total")
        if isinstance(total, int):
            return total
    return None


def _page_url(route: str, page: int, extra_param=None) -> str:
    sep = "&" if "?" in route else "?"
    paged = f"{route}{sep}page={page}&pageSize={_PAGE_SIZE}"
    if extra_param is not None:
        paged += f"&{extra_param[0]}={extra_param[1]}"
    return paged


def _first_payload(fetcher, base: str, candidate: str, extra_param=None) -> tuple:
    """One polite GET of the candidate with a small page size; returns
    (payload, status_note). payload is None when the candidate is not
    usable (auth/blocked/non-JSON/empty)."""
    from .adapters._common import sniff_kind as _sniff
    url = _page_url(candidate, 1, extra_param)
    try:
        resp = fetcher.get(url)
    except (Blocked, RateLimited) as exc:
        return None, f"auth route at {url} ({exc.detail}) {db7_auth()}"
    except FetchError as exc:
        return None, f"unreachable candidate {url} ({exc.detail})"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code} at {url} {db7_auth()}"
    if _sniff(resp.headers.get("Content-Type"), resp.content[:256]) != "json":
        return None, f"non-JSON at {url}"
    try:
        return json.loads(resp.content.decode("utf-8", "replace")), None
    except ValueError:
        return None, f"unparsable JSON at {url}"


def db7_auth() -> str:
    return _AUTH_NOTE


def _counts(fetcher, base: str, logger=None) -> tuple:
    """Exact public counts (recon-pinned keyfigures endpoints; findings
    ride the existing catalog_count metric, notes carry endpoints +
    access date). Returns (articles_count_or_None, companies_or_None,
    network_failed)."""
    articles = companies = None
    try:
        resp = fetcher.get(base + KEYFIGURES_ARTICLES)
        if resp.status_code == 200:
            m = _INT_RE.search(resp.content.decode("utf-8", "replace"))
            articles = int(m.group(0).replace(" ", "")) if m else None
        resp2 = fetcher.get(base + KEYFIGURES_COMPANIES)
        if resp2.status_code == 200:
            m2 = _INT_RE.search(resp2.content.decode("utf-8", "replace"))
            companies = int(m2.group(0).replace(" ", "")) if m2 else None
    except FetchError:
        return articles, companies, True
    return articles, companies, False


# --- draw stage (PHASE03) — pool build + seeded sample ----------------------


def _paginate(fetcher, base: str, route: str, extra_param=None,
              cap: int | None = None) -> tuple:
    """Pool build (decision 2C): paginate the route full-range up to
    the pinned threshold. Returns (rows, total, truncated) — total is
    the route-advertised total when present, truncated = the capsule
    cap before the well ran dry. Raises FetchError on network
    failure (→ honest failed run, exit 2)."""
    rows: list = []
    total: int | None = None
    empty_hit = False
    page = 0
    cap = cap if cap is not None else _POOL_THRESHOLD
    while len(rows) < cap and not empty_hit:
        page += 1
        try:
            resp = fetcher.get(_page_url(route, page, extra_param))
        except (Blocked, RateLimited) as exc:
            first = (page == 1)
            if first:
                raise
            break  # a later page hitting an auth wall — keep what we have
        payload = json.loads(resp.content.decode("utf-8", "replace"))
        if page == 1:
            total = _total_of(payload)
        items = _items_of(payload)
        if items is None:
            if page == 1:
                raise ValueError(f"pinned route returned no article items at page 1: {route}")
            break
        rows.extend(items)
        if len(items) < _PAGE_SIZE:
            empty_hit = True
    truncated = not empty_hit
    return rows, total, truncated


def _random_page_draw(fetcher, base: str, route: str, total: int, n: int,
                      seed: int, extra_param=None) -> tuple:
    """Above-threshold fallback when the route advertises a total:
    seed-fixed random-page draws (decision 2C). Never silently pads —
    returns what the visited pages yield."""
    rng = random.Random(seed)
    pages = max(1, (total + _PAGE_SIZE - 1) // _PAGE_SIZE)
    wanted: list = []
    for p in rng.sample(range(1, pages + 1), min(pages, max(2 * n // _PAGE_SIZE + 1, 1))):
        try:
            resp = fetcher.get(_page_url(route, p, extra_param))
        except FetchError as exc:
            break
        items = _items_of(json.loads(resp.content.decode("utf-8", "replace"))) or []
        for item in items:
            if len(wanted) >= max(n + int(n * 0.5), n):
                break
            wanted.append(item)
    return wanted


def _draw(conn, store, fetcher, source_id, run_id, run_key, base, route,
          n, seed, out_dir, ts, total, pool_rows, method, parameters,
          logger=None) -> tuple:
    """Seeded draw over the canonical distinct pool + CSV + findings
    (reuses the csv_sample draw/write mechanics — D36 machinery)."""
    keys_fallback = _KEY_FIELDS_BASTA
    pool: dict = {}
    for rec in pool_rows:
        pool.setdefault(_identity_key(rec, keys_fallback), rec)
    pool_size = len(pool)
    ordered = [pool[k] for k in sorted(pool)]
    k = min(n, pool_size)
    sampled = random.Random(seed).sample(ordered, k)
    shortfall = k < n
    header = _header_from(sampled)
    method_col = f"basta-pool-method: {method}"
    digest, _rel = store.put(source_id, json.dumps({"route": route, "total": total, "pool": pool_size}).encode(), "json")
    doc = DocumentDraft(url=_page_url(route, 1, _PAINT_FILTER_PARAM),
                        content=json.dumps({"route": route, "total": total, "pool": pool_size}).encode(),
                        content_type="application/json", retrieval_method_code="download")
    findings = [FindingDraft(
        metric_code="basta_special_rows", method_code="download",
        value_numeric=float(k), unit_code="count", document=doc,
        notes=(f"sample draw n={n} seed={seed} route={route}; pool distinct={pool_size} "
               f"(from {len(pool_rows)} rows); method={method}; shortfall={shortfall}; "
               f"fields: {', '.join(header)}; identity share: {', '.join(completeness(pool_rows))}"),
    )]
    probeengine.persist(conn, store, source_id, run_id, ProbeResult(documents=[doc], findings=findings))
    file_name = f"basta-probe.{ts}.{source_id}.csv"
    _write_sample_csv(os.path.join(out_dir, file_name), header, sampled, source_id,
                      run_key, _today(), digest, seed)
    _finish(conn, run_id, "delivered",
            [f"basta sample: {k}/{pool_size} distinct articles (n={n}, seed={seed})"])
    if logger:
        log_event(logger, "basta_probe", "drawn", source=source_id,
                  run_key=run_key, rows=k, pool=pool_size)
    reason = (f"pool smaller than n: {k} of {n} requested (distinct articles: {pool_size})"
              if shortfall else None)
    return _entry("delivered", run_key, rows=k, pool=pool_size, method=method_col,
                  file=file_name, route=route, reason=reason), shortfall


def _header_from(rows) -> list:
    fields = []
    for rec in rows:
        for key in rec or {}:
            if key not in fields:
                fields.append(key)
    return fields


def completeness(pool_rows) -> list:
    """Identity completeness per the pinned chains (db6): for each
    chain that has at least one field name present in the data, the
    share of pool rows carrying a non-empty value in any of them."""
    fieldnames = set()
    for rec in pool_rows:
        fieldnames.update(rec or {})
    out = []
    n = max(len(pool_rows), 1)
    for names in _KEY_FIELDS_BASTA:
        if any(nm in fieldnames for nm in names):
            share = sum(
                1 for rec in pool_rows
                if any(str(rec.get(nm) or "").strip() for nm in names)
            ) / n
            out.append(f"{names[0]}={share:.1%}")
    if "gtin" in fieldnames:
        share = sum(1 for rec in pool_rows if str(rec.get("gtin") or "").strip()) / n
        out.append(f"gtin={share:.1%}")
    return out


def run_probe(conn, store, fetcher, source, n: int = 100, seed: int = 42,
              out_dir: str = "data/report", dry_run: bool = False,
              ts: str | None = None, logger=None) -> tuple:
    """The D40 flow for one BASTA source row (AS-33). Returns
    (exit_code, entry); the finding record is ALWAYS written and tells
    the truth (review 1A) — unless --dry-run, which plans requests and
    writes nothing."""
    ts = ts or _utc_ts()
    base = (source.export_url or source.url).rstrip("/")
    parameters = {"n": n, "seed": seed, "dry_run": dry_run}
    if dry_run:
        fetcher.plan(base + SOK_PATH)
        fetcher.plan(base + KEYFIGURES_ARTICLES)
        fetcher.plan(base + KEYFIGURES_COMPANIES)
        return 0, _entry("dry-run", "planned")
    os.makedirs(out_dir, exist_ok=True)
    run_id, run_key = _begin_run(conn, source.id, parameters)

    # PHASE01 — pin
    candidates, detail, kind = _pin(fetcher, base, logger)
    if kind == "failed":
        return 2, _failed(conn, store, source.id, run_id, run_key, f"pin stage: {detail}", logger)
    if kind == "auth-gated":
        return 0, _unavailable(conn, store, source.id, run_id, run_key,
                               f"the /sok surface blocked the anonymous probe (robots/auth layer): {detail} {db7_auth()}", logger)
    if kind == "unavailable":
        return 0, _unavailable(conn, store, source.id, run_id, run_key,
                               f"the /sok surface not serving anonymously: {detail} {db7_auth()}", logger)

    # PHASE02 — verify candidates + exact counts
    route, route_note = None, None
    for candidate in candidates[:_SHAPE_MAX_GETS]:
        payload, note = _first_payload(fetcher, base, candidate, _PAINT_FILTER_PARAM)
        items = _items_of(payload) if payload is not None else None
        if items:
            route, route_note = candidate, f"pinned route {candidate} ({note or 'first page OK'})"
            break
        route_note = note
    articles, companies, counts_failed = _counts(fetcher, base, logger)
    if route is None:
        counts_note = (f"exact public article count via {base}{KEYFIGURES_ARTICLES} "
                       f"(accessed {_today()})" if articles is not None else "")
        findings = [FindingDraft(
            metric_code="basta_special_unavailable", method_code="download",
            value_text=(f"pin-not-found after the bundle chain ({detail}); last "
                        f"verification: {route_note or 'no candidate verified'}{_PIN_NOT_FOUND_TAIL}"
                        + (f"; {counts_note}" if counts_note else "")
                        + f" {db7_auth()}"))]
        if articles is not None:
            findings.append(FindingDraft(
                metric_code="catalog_count", method_code="download",
                value_numeric=float(articles), unit_code="count",
                notes=counts_note + "; route unverified"))
        probeengine.persist(conn, store, source.id, run_id, ProbeResult(findings=findings))
        _finish(conn, run_id, "unavailable", ["BASTA pin-not-found"])
        return 0, _entry("unavailable", run_key, reason=_AUTH_NOTE)
    # route pinned — deliver
    try:
        pool_rows, total, truncated = _paginate(fetcher, base, route, _PAINT_FILTER_PARAM)
    except (Blocked, RateLimited) as exc:
        return 0, _unavailable(conn, store, source.id, run_id, run_key,
                               f"the pinned route serves no anonymous rows ({exc.detail}) {db7_auth()}", logger)
    except FetchError as exc:
        return 2, _failed(conn, store, source.id, run_id, run_key, f"pool build: {exc}", logger)
    except ValueError as exc:
        return 0, _unavailable(conn, store, source.id, run_id, run_key,
                               f"pinned route is not an article route: {exc} {db7_auth()}", logger)
    method = "full-pool paginated"
    if truncated:
        if total is not None:
            method = "random-page draws above the pinned threshold (total advertised)"
            extra_rows = _random_page_draw(fetcher, base, route, total, n, seed, _PAINT_FILTER_PARAM)
            if extra_rows:
                pool_rows = extra_rows
        else:
            method = "head-of-pool paginated prefix (route advertises no total)"
    entry, shortfall = _draw(conn, store, fetcher, source.id, run_id, run_key,
                             base, route, n, seed, out_dir, ts, total, pool_rows,
                             method, parameters, logger)
    if articles is not None:
        probeengine.persist(conn, store, source.id, run_id, ProbeResult(
            findings=[FindingDraft(
                metric_code="catalog_count", method_code="download",
                value_numeric=float(articles), unit_code="count",
                notes=(f"BASTA exact public article count via {base}{KEYFIGURES_ARTICLES} "
                       f"(accessed {_today()}; companies via {KEYFIGURES_COMPANIES} = "
                       f"{companies if companies is not None else 'not verified'}); "
                       f"route: {route}"))]))
        conn.commit()
    entry["counts"] = (
        f"articles={articles}" + (f"; companies={companies}" if companies is not None else "")
        if articles is not None else ""
    ) or None
    return 0, entry


# --- orchestration -----------------------------------------------------------


def sample(conn, store, fetcher, source_rows: dict, n: int = 100, seed: int = 42,
           out_dir: str = "data/report", dry_run: bool = False, ts: str | None = None,
           logger=None) -> tuple:
    """Run the BASTA probe over the (single) requested source rows —
    mirrors the other probe entry points for the CLI. Returns
    (exit_code, entries)."""
    ts = ts or _utc_ts()
    exit_code, entries = 0, []
    for source in source_rows.values():
        code, entry = run_probe(conn, store, fetcher, source, n=n, seed=seed,
                                out_dir=out_dir, dry_run=dry_run, ts=ts, logger=logger)
        entries.append(entry)
        exit_code = code if code > exit_code else exit_code
    return exit_code, entries
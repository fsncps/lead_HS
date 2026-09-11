"""The single fetch seam (a1): robots, rate limit, UA, retry/backoff.

Typed errors (interfaces.md exception taxonomy):

- ``RobotsDisallowed`` — robots.txt disallows our paths
- ``Blocked``          — HTTP 403 or paywall/login wall
- ``RateLimited``      — HTTP 429: one capped backoff then retry;
                         persistent 429 -> RateLimited (engine maps it
                         to an access_blocked finding + blocked run)
- ``ProbeNetworkError`` — wraps ``requests.RequestException`` after
                         2 retries (DNS/TLS/timeout/5xx)

Deterministic tests: injectable clock + sleeper (a4); >= 2 s spacing
per domain (DATA_SOURCE.md discipline); dry-run ``plan()`` performs
zero network calls (i7).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests

from . import __version__
from .logutil import log_event

MIN_SPACING = 2.0
RETRIES = 2
BACKOFF_BASE = 2.0
RATE_LIMIT_CAP = 60.0
REQUEST_TIMEOUT = 30


class FetchError(Exception):
    """Base class: carries the URL that failed."""

    def __init__(self, url: str, detail: str):
        self.url = url
        self.detail = detail
        super().__init__(f"{url}: {detail}")


class RobotsDisallowed(FetchError):
    pass


class Blocked(FetchError):
    pass


class RateLimited(FetchError):
    pass


class ProbeNetworkError(FetchError):
    def __init__(self, url: str, detail: str, cause: BaseException | None = None):
        self.cause = cause
        super().__init__(url, detail)


@dataclass(frozen=True)
class PlannedRequest:
    url: str
    method: str = "GET"


@dataclass(frozen=True)
class FetchResponse:
    url: str
    status_code: int
    headers: dict
    content: bytes
    text: str
    encoding: str
    elapsed_ms: int

    @classmethod
    def from_requests(cls, resp: requests.Response) -> "FetchResponse":
        started = getattr(resp, "_leadhs_started", time.monotonic())
        return cls(
            url=resp.url,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            content=resp.content,
            text=resp.text,
            encoding=resp.encoding or "utf-8",
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )


@dataclass
class FetchConfig:
    contact: Optional[str] = None
    version: str = __version__
    min_spacing: float = MIN_SPACING
    retries: int = RETRIES
    backoff_base: float = BACKOFF_BASE
    rate_limit_cap: float = RATE_LIMIT_CAP
    robots_path: str = "/robots.txt"
    timeout: float = REQUEST_TIMEOUT
    clock: Callable[[], float] = field(default=time.monotonic)
    sleeper: Callable[[float], None] = field(default=time.sleep)

    def user_agent(self) -> str:
        if self.contact:
            return f"leadhs/{self.version} (+{self.contact})"
        return f"leadhs/{self.version}"


class Fetcher:
    def __init__(self, config: Optional[FetchConfig] = None, logger=None):
        self.config = config or FetchConfig()
        self.logger = logger
        self._last_request: dict[str, float] = {}
        self._robots_cache: dict[str, Optional[RobotFileParser]] = {}
        self._session = requests.Session()
        self._session.headers["User-Agent"] = self.config.user_agent()

    def _log(self, event: str, **fields) -> None:
        if self.logger is not None:
            log_event(self.logger, "fetch", event, **fields)

    # --- spacing -------------------------------------------------------

    def _domain(self, url: str) -> str:
        return urlparse(url).netloc

    def _wait_for_spacing(self, domain: str) -> None:
        now = self.config.clock()
        last = self._last_request.get(domain)
        if last is not None:
            delta = now - last
            if delta < self.config.min_spacing:
                self.config.sleeper(self.config.min_spacing - delta)
                now = self.config.clock()
        self._last_request[domain] = now

    # --- robots --------------------------------------------------------

    def _robots_url(self, url: str) -> str:
        parts = urlparse(url)
        return urlunparse((parts.scheme, parts.netloc, self.config.robots_path, "", "", ""))

    def robots_policy(self, url: str, log: bool = True) -> str:
        """Fetch (once per domain) and summarize robots.txt for our paths."""
        domain = self._domain(url)
        if domain not in self._robots_cache:
            robots_url = self._robots_url(url)
            try:
                resp = self._request(robots_url, log=False)
            except FetchError as exc:
                # robots unreachable is treated as a network finding at the
                # call site; cache the exception as policy "unknown"
                self._log("robots", url=robots_url, status="error", detail=str(exc))
                self._robots_cache[domain] = None
                raise
            parser = RobotFileParser()
            parser.set_url(robots_url)
            if resp.status_code == 404 or not resp.content.strip():
                parser.allow_all = True  # 404/empty = allow-all
                self._robots_cache[domain] = parser
            else:
                parser.parse(resp.text.splitlines())
                self._robots_cache[domain] = parser
            self._log("robots", url=robots_url, status=resp.status_code)
        parser = self._robots_cache[domain]
        if parser is None:
            return "unknown"
        if parser.allow_all:
            return "allow-all (404/empty)"
        token = "leadhs"
        can = parser.can_fetch(token, url)
        return "allowed" if can else "disallowed"

    def check_robots(self, url: str) -> None:
        if self.robots_policy(url) == "disallowed":
            raise RobotsDisallowed(url, "robots.txt disallows our path")

    # --- the request pipeline -------------------------------------------

    def _request(self, url: str, log: bool = True) -> FetchResponse:
        domain = self._domain(url)
        self._wait_for_spacing(domain)
        started = time.monotonic()

        def do_attempt() -> requests.Response:
            resp = self._session.get(url, timeout=self.config.timeout)
            resp._leadhs_started = started  # type: ignore[attr-defined]
            return resp

        resp = None
        attempt = 0
        last_exc: Optional[Exception] = None
        while True:
            attempt += 1
            try:
                resp = do_attempt()
            except requests.RequestException as exc:
                last_exc = exc
                if attempt <= self.config.retries:
                    self.config.sleeper(self.config.backoff_base * (2 ** (attempt - 1)))
                    continue
                raise ProbeNetworkError(url, "network error after retries", cause=exc)

            if resp.status_code == 429:
                # one capped backoff then a single retry (i8)
                self.config.sleeper(min(self.config.rate_limit_cap, self.config.backoff_base))
                try:
                    resp = do_attempt()
                except requests.RequestException as exc:
                    raise ProbeNetworkError(url, "network error on 429 retry", cause=exc)
                if resp.status_code == 429:
                    raise RateLimited(url, "persistent 429 after one capped backoff")
                break

            if resp.status_code in (401, 403):
                raise Blocked(url, f"HTTP {resp.status_code}")
            if resp.status_code >= 500:
                if attempt <= self.config.retries:
                    self.config.sleeper(self.config.backoff_base * (2 ** (attempt - 1)))
                    continue
                raise ProbeNetworkError(url, f"HTTP {resp.status_code} after retries")

            break

        result = FetchResponse.from_requests(resp)
        if log:
            self._log("get", url=url, status=result.status_code, ms=result.elapsed_ms, bytes=len(result.content))
        return result

    # --- public API ------------------------------------------------------

    def get(self, url: str) -> FetchResponse:
        """Polite GET with robots check, spacing, retry, error taxonomy."""
        self.check_robots(url)
        return self._request(url)

    def plan(self, url: str, method: str = "GET") -> PlannedRequest:
        """Dry-run: log the would-be request; zero network calls (i7)."""
        self._log("plan", url=url, method=method)
        return PlannedRequest(url, method)
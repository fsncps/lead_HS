"""fetch seam: spacing, robots, error taxonomy, retries, dry-run (t2)."""

import pytest
import requests

from leadhs.fetch import Blocked, ProbeNetworkError, RateLimited, RobotsDisallowed


def test_spacing_per_domain(site, fake_clock, make_fetcher, site_hits):
    f = make_fetcher(fake_clock)
    f.get(f"{site}/")
    t1 = fake_clock.t
    f.get(f"{site}/terms")
    t2 = fake_clock.t
    assert t2 - t1 >= 2.0  # same domain -> >= 2 s spacing


def test_robots_deny(site, make_fetcher):
    f = make_fetcher()
    with pytest.raises(RobotsDisallowed):
        f.get(f"{site}/private/secret")


def test_robots_cached(site, make_fetcher, site_hits):
    f = make_fetcher()
    f.get(f"{site}/")
    first = site_hits.get("/robots.txt", 0)
    f.get(f"{site}/terms")
    assert site_hits.get("/robots.txt", 0) == first  # not re-fetched


def test_robots_404_is_allow_all(site, make_fetcher):
    f = make_fetcher(robots_path="/nonexistent-robots.txt")
    assert f.robots_policy(f"{site}/") == "allow-all (404/empty)"
    f.get(f"{site}/anything")  # no raise


def test_robots_empty_is_allow_all(site, make_fetcher):
    f = make_fetcher(robots_path="/empty-robots.txt")
    assert f.robots_policy(f"{site}/") == "allow-all (404/empty)"


def test_403_blocked(site, make_fetcher):
    f = make_fetcher()
    with pytest.raises(Blocked):
        f.get(f"{site}/forbidden")


def test_429_once_capped_backoff_then_success(site, fake_clock, make_fetcher):
    f = make_fetcher(fake_clock)
    resp = f.get(f"{site}/ratelimited-once")
    assert resp.status_code == 200
    assert resp.text == "ok-after-429"


def test_429_persistent_rate_limited(site, fake_clock, make_fetcher):
    f = make_fetcher(fake_clock)
    with pytest.raises(RateLimited):
        f.get(f"{site}/ratelimited-always")


def test_5xx_retries_then_network_error(site, fake_clock, make_fetcher):
    f = make_fetcher(fake_clock)
    with pytest.raises(ProbeNetworkError):
        f.get(f"{site}/error500")


def test_connection_error_retries_then_network_error(site, make_fetcher, monkeypatch):
    f = make_fetcher()
    calls = {"n": 0}

    def flaky(*a, **kw):
        calls["n"] += 1
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(f._session, "get", flaky)
    with pytest.raises(ProbeNetworkError):
        f.get(f"{site}/")
    assert calls["n"] == 3  # initial + 2 retries


def test_connection_error_recovers(site, make_fetcher, monkeypatch):
    f = make_fetcher()
    calls = {"n": 0}
    real_get = f._session.get

    def flaky(*a, **kw):
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.ConnectionError("boom")
        return real_get(*a, **kw)

    monkeypatch.setattr(f._session, "get", flaky)
    resp = f.get(f"{site}/")
    assert resp.status_code == 200


def test_dry_run_zero_network(site, make_fetcher, monkeypatch):
    f = make_fetcher()

    def no_network(*a, **kw):
        raise AssertionError("network call attempted in dry-run")

    monkeypatch.setattr(f._session, "get", no_network)
    plan = f.plan(f"{site}/robots.txt")
    assert plan.url == f"{site}/robots.txt"
    assert plan.method == "GET"


def test_user_agent_contact():
    from leadhs.fetch import FetchConfig

    assert "leadhs/" in FetchConfig(contact="a@b.c").user_agent()
    assert "(+a@b.c)" in FetchConfig(contact="a@b.c").user_agent()
    ua = FetchConfig(contact=None).user_agent()
    assert "leadhs/" in ua and "(+" not in ua

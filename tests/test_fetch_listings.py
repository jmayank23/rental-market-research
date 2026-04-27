"""Tests for fetch_listings retry behavior."""

from unittest.mock import patch

import pytest
import requests

import fetch_listings


class _FakeResponse:
    def __init__(self, status_code: int, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload or []
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.HTTPError(f"HTTP {self.status_code}")
            err.response = self
            raise err

    def json(self):
        return self._payload


def test_request_with_retry_succeeds_after_transient_503(monkeypatch):
    monkeypatch.setattr(fetch_listings.time, "sleep", lambda *_: None)

    responses = [
        _FakeResponse(503),
        _FakeResponse(503),
        _FakeResponse(200, payload=[{"id": "x"}], headers={"X-Total-Count": "1"}),
    ]
    calls = {"n": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        r = responses[calls["n"]]
        calls["n"] += 1
        return r

    with patch.object(fetch_listings.requests, "get", side_effect=fake_get):
        resp = fetch_listings._request_with_retry("http://x", {}, {})
    assert resp.status_code == 200
    assert calls["n"] == 3


def test_request_with_retry_does_not_retry_4xx(monkeypatch):
    monkeypatch.setattr(fetch_listings.time, "sleep", lambda *_: None)

    calls = {"n": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        calls["n"] += 1
        return _FakeResponse(404)

    with patch.object(fetch_listings.requests, "get", side_effect=fake_get):
        with pytest.raises(requests.HTTPError):
            fetch_listings._request_with_retry("http://x", {}, {})
    assert calls["n"] == 1


def test_request_with_retry_gives_up_after_max_attempts(monkeypatch):
    monkeypatch.setattr(fetch_listings.time, "sleep", lambda *_: None)

    calls = {"n": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        calls["n"] += 1
        return _FakeResponse(503)

    with patch.object(fetch_listings.requests, "get", side_effect=fake_get):
        with pytest.raises(requests.HTTPError):
            fetch_listings._request_with_retry("http://x", {}, {})
    assert calls["n"] == len(fetch_listings.RETRY_BACKOFFS)


def test_fetch_all_listings_warns_when_total_count_missing(monkeypatch, capsys):
    monkeypatch.setattr(fetch_listings.time, "sleep", lambda *_: None)

    response = _FakeResponse(200, payload=[{"id": "a"}, {"id": "b"}], headers={})
    with patch.object(fetch_listings.requests, "get", return_value=response):
        results = fetch_listings.fetch_all_listings("/listings/sale", {})
    assert len(results) == 2
    out = capsys.readouterr().out
    assert "X-Total-Count missing" in out

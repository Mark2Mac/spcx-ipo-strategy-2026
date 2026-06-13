"""Regression: non-numeric prices must not crash search_markets (bug #9)."""
import json

import src.connectors.polymarket as pm


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _event(prices, outcomes, volume="100"):
    return {"events": [{"title": "E", "markets": [
        {"question": "Q", "outcomePrices": prices, "outcomes": outcomes, "volume": volume}]}]}


def test_bad_price_does_not_crash(monkeypatch):
    payload = _event(json.dumps(["0.6", "abc"]), json.dumps(["Yes", "No"]))
    monkeypatch.setattr(pm.requests, "get", lambda *a, **k: _FakeResp(payload))
    out = pm.search_markets("x")
    assert out and out[0]["outcomes"] == {}  # bad price -> empty, no exception


def test_bad_volume_does_not_crash(monkeypatch):
    payload = _event(json.dumps(["0.6", "0.4"]), json.dumps(["Yes", "No"]), volume="oops")
    monkeypatch.setattr(pm.requests, "get", lambda *a, **k: _FakeResp(payload))
    out = pm.search_markets("x")
    assert out[0]["volume"] == 0.0
    assert out[0]["outcomes"] == {"Yes": 0.6, "No": 0.4}


def test_valid_market_parses(monkeypatch):
    payload = _event(json.dumps(["0.7", "0.3"]), json.dumps(["Yes", "No"]), volume="500")
    monkeypatch.setattr(pm.requests, "get", lambda *a, **k: _FakeResp(payload))
    out = pm.search_markets("x")
    assert out[0]["outcomes"] == {"Yes": 0.7, "No": 0.3}
    assert pm.implied_probability(out[0], "Yes") == 0.7

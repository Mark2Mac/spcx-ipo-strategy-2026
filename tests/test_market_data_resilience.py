"""Regression: (a) Stooq fallback must use real index symbols (^spx/^ndx/^vix), not the
broken lstrip('^') forms that 404; (b) get_universe must isolate a per-ticker failure so one
dead ticker can't wipe the whole universe snapshot."""
import numpy as np
import pandas as pd
import pytest

import src.connectors.market_data as md


def _fake_df():
    idx = pd.bdate_range("2024-01-01", periods=40)
    return pd.DataFrame({"Open": 1.0, "High": 1.0, "Low": 1.0,
                         "Close": np.linspace(10, 12, len(idx)), "Volume": 100.0}, index=idx)


@pytest.mark.parametrize("ticker,expected", [
    ("^GSPC", "^spx"), ("^NDX", "^ndx"), ("^VIX", "^vix"),
    ("GOOGL", "googl.us"), ("BRK-B", "brk-b.us"),
])
def test_stooq_symbol_mapping(ticker, expected):
    assert md._stooq_symbol(ticker) == expected


class _Resp:
    def __init__(self, text, status=200):
        self.text, self.status_code = text, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")


def test_from_stooq_rejects_antibot_html(monkeypatch):
    # stooq 200 + JS challenge HTML must NOT be parsed as CSV (silent corruption); raise instead
    html = "<!DOCTYPE html><html><head><meta charset=utf-8></head><body>verify</body></html>"
    monkeypatch.setattr(md.requests, "get", lambda *a, **k: _Resp(html))
    with pytest.raises(ValueError, match="non-CSV"):
        md._from_stooq("^VIX")


def test_from_stooq_parses_real_csv(monkeypatch):
    csv = "Date,Open,High,Low,Close,Volume\n2026-06-18,10,11,9,10.5,1000\n"
    monkeypatch.setattr(md.requests, "get", lambda *a, **k: _Resp(csv))
    df = md._from_stooq("GOOGL")
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert float(df["Close"].iloc[-1]) == 10.5


def test_get_universe_isolates_failing_ticker(monkeypatch):
    # ^VIX dies on BOTH sources; the other two must still land in the frame, ^VIX in reports
    def _maybe(ticker, period, force=False):
        if ticker == "^VIX":
            raise RuntimeError("both sources down")
        df = _fake_df()
        df.attrs["source"] = "yfinance"
        return df

    monkeypatch.setattr(md, "get_ohlcv", _maybe)
    prices, reports = md.get_universe(["GOOGL", "TSLA", "^VIX"], period="6mo", force=True)

    assert list(prices.columns) == ["GOOGL", "TSLA"]  # good tickers preserved
    assert not prices.empty
    rep = {r["ticker"]: r for r in reports}
    assert rep["^VIX"]["rows"] == 0
    assert any("fetch failed" in i for i in rep["^VIX"]["issues"])
    assert not any("fetch failed" in i for i in rep["GOOGL"]["issues"])  # healthy unaffected
    assert rep["GOOGL"]["source"] == "yfinance"


def test_get_universe_all_fail_returns_empty_not_crash(monkeypatch):
    monkeypatch.setattr(md, "get_ohlcv",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("down")))
    prices, reports = md.get_universe(["GOOGL", "TSLA"], period="6mo", force=True)
    assert prices.empty
    assert all(r["rows"] == 0 for r in reports)

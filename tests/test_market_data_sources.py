"""Second independent price source: yfinance -> Yahoo chart API (keyless, different code path)
-> Stooq. Removes the yfinance-library single point of failure for the SPCX close that scoring
depends on. Verifies the fallback ORDER, the source labels, and the chart-JSON parse."""
import time

import numpy as np
import pandas as pd
import pytest

import src.connectors.market_data as md


def _fake_df(source=None):
    idx = pd.bdate_range("2024-01-01", periods=40)
    df = pd.DataFrame({"Open": 1.0, "High": 1.0, "Low": 1.0,
                       "Close": np.linspace(10, 12, len(idx)), "Volume": 100.0}, index=idx)
    if source:
        df.attrs["source"] = source
    return df


def _boom(*a, **k):
    raise ValueError("source down")


def test_chain_prefers_yfinance(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", lambda t, p: _fake_df())
    monkeypatch.setattr(md, "_from_yahoo_chart", _boom)
    monkeypatch.setattr(md, "_from_stooq", _boom)
    df = md.get_ohlcv("SPCX", "1mo", force=True)
    assert df.attrs["source"] == "yfinance"


def test_chain_falls_to_yahoo_chart_when_yfinance_down(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", _boom)
    monkeypatch.setattr(md, "_from_yahoo_chart", lambda t, p: _fake_df())
    monkeypatch.setattr(md, "_from_stooq", _boom)
    df = md.get_ohlcv("SPCX", "1mo", force=True)
    assert df.attrs["source"] == "yahoo-chart"


def test_chain_falls_to_stooq_last(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", _boom)
    monkeypatch.setattr(md, "_from_yahoo_chart", _boom)
    monkeypatch.setattr(md, "_from_stooq", lambda t: _fake_df())
    df = md.get_ohlcv("SPCX", "1mo", force=True)
    assert df.attrs["source"] == "stooq"


def test_all_sources_down_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", _boom)
    monkeypatch.setattr(md, "_from_yahoo_chart", _boom)
    monkeypatch.setattr(md, "_from_stooq", _boom)
    with pytest.raises(Exception, match="all price sources failed"):
        md.get_ohlcv("SPCX", "1mo", force=True)


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_yahoo_chart_parses_json(monkeypatch):
    ts = [int(time.mktime((2026, 6, 12, 0, 0, 0, 0, 0, 0))),
          int(time.mktime((2026, 6, 15, 0, 0, 0, 0, 0, 0)))]
    payload = {"chart": {"result": [{
        "timestamp": ts,
        "indicators": {
            "quote": [{"open": [135.0, 161.0], "high": [165.0, 195.0],
                       "low": [130.0, 160.0], "close": [160.95, 192.5],
                       "volume": [5e8, 3e8]}],
            "adjclose": [{"adjclose": [160.95, 192.5]}],
        }}]}}
    monkeypatch.setattr(md.requests, "get", lambda *a, **k: _Resp(payload))
    df = md._from_yahoo_chart("SPCX", "1mo")
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert float(df["Close"].iloc[0]) == 160.95
    assert df.index.tz is None  # tz-naive, matching the yfinance path


def test_yahoo_chart_raises_on_empty(monkeypatch):
    monkeypatch.setattr(md.requests, "get",
                        lambda *a, **k: _Resp({"chart": {"result": [None]}}))
    with pytest.raises(ValueError):
        md._from_yahoo_chart("ZZZZ", "1mo")

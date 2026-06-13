"""Regression: source provenance survives parquet cache + force bypasses cache (bugs #1, #3)."""
import numpy as np
import pandas as pd

import src.connectors.market_data as md


def _fake_df():
    idx = pd.bdate_range("2024-01-01", periods=40)
    return pd.DataFrame({"Open": 1.0, "High": 1.0, "Low": 1.0,
                         "Close": np.linspace(10, 12, len(idx)), "Volume": 100.0}, index=idx)


def test_source_in_quality_report(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", lambda t, p: _fake_df())
    df = md.get_ohlcv("GOOGL", "6mo", force=True)
    assert df.attrs["source"] == "yfinance"
    rep = md.quality_report(df, "GOOGL")
    assert rep["source"] == "yfinance"


def test_source_survives_cache_hit(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", lambda t, p: _fake_df())
    md.get_ohlcv("GOOGL", "6mo", force=True)  # writes parquet + .source sidecar

    # cache hit must NOT call the network and must restore source from sidecar
    def _boom(*a, **k):
        raise AssertionError("network called on cache hit")

    monkeypatch.setattr(md, "_from_yfinance", _boom)
    monkeypatch.setattr(md, "_from_stooq", _boom)
    df = md.get_ohlcv("GOOGL", "6mo", force=False)
    assert df.attrs["source"] == "yfinance"  # would be "unknown" without sidecar fix


def test_stooq_fallback_source(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    monkeypatch.setattr(md, "_from_yfinance", lambda t, p: (_ for _ in ()).throw(ValueError("yf down")))
    monkeypatch.setattr(md, "_from_stooq", lambda t: _fake_df())
    df = md.get_ohlcv("GOOGL", "6mo", force=True)
    assert df.attrs["source"] == "stooq"


def test_force_bypasses_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    calls = {"n": 0}

    def _counted(t, p):
        calls["n"] += 1
        return _fake_df()

    monkeypatch.setattr(md, "_from_yfinance", _counted)
    md.get_ohlcv("GOOGL", "6mo", force=True)
    md.get_ohlcv("GOOGL", "6mo", force=True)
    assert calls["n"] == 2  # force always refetches


def test_get_universe_propagates_force(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "DATA_DIR", tmp_path)
    calls = {"n": 0}

    def _counted(t, p):
        calls["n"] += 1
        return _fake_df()

    monkeypatch.setattr(md, "_from_yfinance", _counted)
    md.get_universe(["GOOGL"], period="6mo", force=True)
    md.get_universe(["GOOGL"], period="6mo", force=True)
    assert calls["n"] == 2

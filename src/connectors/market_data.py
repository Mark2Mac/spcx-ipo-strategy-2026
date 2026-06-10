"""OHLCV connector: yfinance primary, Stooq fallback, parquet cache, data-quality checks."""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CACHE_MAX_AGE_H = 12


def _cache_path(ticker: str, period: str) -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    safe = ticker.replace("^", "IDX_").replace(".", "_")
    return DATA_DIR / f"ohlcv_{safe}_{period}.parquet"


def _from_yfinance(ticker: str, period: str) -> pd.DataFrame:
    import yfinance as yf

    df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    if df.empty:
        raise ValueError(f"yfinance empty for {ticker}")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])


def _from_stooq(ticker: str) -> pd.DataFrame:
    sym = ticker.lower().lstrip("^") + (".us" if not ticker.startswith("^") else "")
    r = requests.get(f"https://stooq.com/q/d/l/?s={sym}&i=d", timeout=20)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), parse_dates=["Date"], index_col="Date")
    if df.empty:
        raise ValueError(f"stooq empty for {ticker}")
    return df.rename(columns=str.title)[["Open", "High", "Low", "Close", "Volume"]]


def quality_report(df: pd.DataFrame, ticker: str) -> dict:
    bd = pd.bdate_range(df.index.min(), df.index.max())
    missing = len(bd.difference(df.index))
    stale_days = (pd.Timestamp.now() - df.index.max()).days
    issues, warnings = [], []
    if df["Close"].isna().any():
        issues.append("NaN in Close")
    if (df["Close"] <= 0).any():
        issues.append("non-positive prices")
    if stale_days > 5:
        issues.append(f"stale: last bar {stale_days}d old")
    if missing / max(len(bd), 1) > 0.05:
        warnings.append(f"{missing} business days missing (>5%)")
    jumps = df["Close"].pct_change().abs()
    if (jumps > 0.5).any():
        warnings.append(f"jump >50% on {jumps.idxmax().date()} (verify: real move or bad print)")
    return {"ticker": ticker, "rows": len(df), "first": str(df.index.min().date()),
            "last": str(df.index.max().date()), "missing_bdays": missing,
            "issues": issues, "warnings": warnings}


def get_ohlcv(ticker: str, period: str = "2y", force: bool = False) -> pd.DataFrame:
    cache = _cache_path(ticker, period)
    if not force and cache.exists() and (time.time() - cache.stat().st_mtime) < CACHE_MAX_AGE_H * 3600:
        return pd.read_parquet(cache)
    try:
        df = _from_yfinance(ticker, period)
        df.attrs["source"] = "yfinance"
    except Exception:
        df = _from_stooq(ticker)
        df.attrs["source"] = "stooq"
    df.to_parquet(cache)
    return df


def get_universe(tickers: list[str], period: str = "2y") -> tuple[pd.DataFrame, list[dict]]:
    closes, reports = {}, []
    for t in tickers:
        df = get_ohlcv(t, period)
        closes[t] = df["Close"]
        reports.append(quality_report(df, t))
    return pd.DataFrame(closes).sort_index(), reports


if __name__ == "__main__":
    px, reps = get_universe(["GOOGL", "TSLA", "^GSPC"], period="6mo")
    for r in reps:
        print(r)
    assert not px.empty and px.notna().mean().min() > 0.9, "pipeline FAIL"
    print(f"TEST OK — shape {px.shape}, last row {px.index[-1].date()}")

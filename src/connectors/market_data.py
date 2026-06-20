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


def _source_path(cache: Path) -> Path:
    return cache.with_suffix(".source")


def _from_yfinance(ticker: str, period: str) -> pd.DataFrame:
    import yfinance as yf

    df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    if df.empty:
        raise ValueError(f"yfinance empty for {ticker}")
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])


# Stooq names indices with a caret prefix and a stooq-specific code, not the Yahoo symbol.
# lstrip('^') produced 'gspc'/'ndx'/'vix' which 404 — the fallback silently failed for every
# index, the exact tickers most likely to need it on a yfinance outage.
_STOOQ_INDEX = {"^GSPC": "^spx", "^NDX": "^ndx", "^VIX": "^vix", "^DJI": "^dji", "^RUT": "^rut"}


def _stooq_symbol(ticker: str) -> str:
    if ticker in _STOOQ_INDEX:
        return _STOOQ_INDEX[ticker]
    if ticker.startswith("^"):
        return ticker.lower()  # unknown index: keep the caret rather than mangle it
    return ticker.lower() + ".us"


# A browser-like UA: stooq serves a JS anti-bot challenge (HTTP 200 + HTML, no CSV) to bare
# clients from some IPs. Without it the fallback can get HTML instead of data.
_STOOQ_UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) spcx-ipo-strategy research"}


def _from_stooq(ticker: str) -> pd.DataFrame:
    sym = _stooq_symbol(ticker)
    r = requests.get("https://stooq.com/q/d/l/", params={"s": sym, "i": "d"},
                     headers=_STOOQ_UA, timeout=20)
    r.raise_for_status()
    # Guard the worst silent-corruption path: a 200 challenge/error page is HTML, not CSV.
    # Parsing it as CSV would yield garbage columns; detect non-CSV and fail explicitly so the
    # per-ticker isolation in get_universe records a clean error instead of a malformed frame.
    head = r.text.lstrip()[:200].lower()
    if not r.text.lstrip().startswith("Date,") or "<html" in head or "<meta" in head:
        raise ValueError(f"stooq returned non-CSV for {ticker} (sym {sym}): "
                         f"likely anti-bot challenge or unknown symbol")
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
            "source": df.attrs.get("source", "unknown"),
            "issues": issues, "warnings": warnings}


def get_ohlcv(ticker: str, period: str = "2y", force: bool = False) -> pd.DataFrame:
    cache = _cache_path(ticker, period)
    src_file = _source_path(cache)
    if not force and cache.exists() and (time.time() - cache.stat().st_mtime) < CACHE_MAX_AGE_H * 3600:
        df = pd.read_parquet(cache)
        # parquet drops .attrs; restore source from sidecar so provenance survives a cache hit.
        df.attrs["source"] = src_file.read_text().strip() if src_file.exists() else "unknown"
        return df
    try:
        df = _from_yfinance(ticker, period)
        df.attrs["source"] = "yfinance"
    except Exception:
        df = _from_stooq(ticker)
        df.attrs["source"] = "stooq"
    df.to_parquet(cache)
    src_file.write_text(df.attrs["source"])
    return df


def get_universe(tickers: list[str], period: str = "2y",
                 force: bool = False) -> tuple[pd.DataFrame, list[dict]]:
    # Isolate each ticker: a single symbol failing on BOTH yfinance and Stooq must not abort
    # the whole snapshot. The failure is recorded as a blocking issue in that ticker's report
    # (so the run gate trips), while every healthy series is still frozen.
    closes, reports = {}, []
    for t in tickers:
        try:
            df = get_ohlcv(t, period, force=force)
            closes[t] = df["Close"]
            reports.append(quality_report(df, t))
        except Exception as e:
            reports.append({"ticker": t, "rows": 0, "first": None, "last": None,
                            "missing_bdays": None, "source": "unavailable",
                            "issues": [f"fetch failed (yfinance+stooq): {type(e).__name__}: {str(e)[:120]}"],
                            "warnings": []})
    frame = pd.DataFrame(closes).sort_index() if closes else pd.DataFrame()
    return frame, reports


if __name__ == "__main__":
    px, reps = get_universe(["GOOGL", "TSLA", "^GSPC"], period="6mo")
    for r in reps:
        print(r)
    assert not px.empty and px.notna().mean().min() > 0.9, "pipeline FAIL"
    print(f"TEST OK — shape {px.shape}, last row {px.index[-1].date()}")

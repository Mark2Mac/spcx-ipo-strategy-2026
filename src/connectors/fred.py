"""Connector FRED via endpoint CSV pubblico (no API key): tassi risk-free e macro."""
from __future__ import annotations

import io

import pandas as pd
import requests


def get_series(series_id: str = "DGS3MO") -> pd.Series:
    r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv",
                     params={"id": series_id}, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), na_values=".")
    df.columns = ["date", series_id]
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")[series_id].dropna()


def risk_free_rate() -> float:
    try:
        return float(get_series("DGS3MO").iloc[-1]) / 100.0
    except Exception:
        import yfinance as yf

        irx = yf.Ticker("^IRX").history(period="5d")["Close"].dropna()
        if irx.empty:
            raise
        return float(irx.iloc[-1]) / 100.0


if __name__ == "__main__":
    rf = risk_free_rate()
    assert 0.0 <= rf <= 0.15, f"risk-free fuori range: {rf}"
    print(f"TEST OK — T-bill 3M: {rf:.2%}")

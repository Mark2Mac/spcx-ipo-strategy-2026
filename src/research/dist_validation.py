"""Distributional validation: do real returns have fat tails? Student-t vs Normal fit on the SPCX proxy."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.connectors.market_data import get_ohlcv


def fit_distributions(ticker: str = "TSLA", period: str = "2y") -> dict:
    px = get_ohlcv(ticker, period)["Close"]
    r = np.log(px / px.shift(1)).dropna().values
    t_dof, t_loc, t_scale = stats.t.fit(r)
    n_loc, n_scale = stats.norm.fit(r)
    ll_t = stats.t.logpdf(r, t_dof, t_loc, t_scale).sum()
    ll_n = stats.norm.logpdf(r, n_loc, n_scale).sum()
    kurt = float(stats.kurtosis(r))
    return {"ticker": ticker, "n_obs": len(r), "returns": r,
            "t_dof": float(t_dof), "t_scale": float(t_scale),
            "excess_kurtosis": kurt,
            "loglik_t": float(ll_t), "loglik_norm": float(ll_n),
            "t_wins": bool(ll_t > ll_n)}


def qq_data(r: np.ndarray, dist, *params) -> tuple[np.ndarray, np.ndarray]:
    q = np.linspace(0.005, 0.995, 200)
    return dist.ppf(q, *params), np.quantile(r, q)


if __name__ == "__main__":
    f = fit_distributions()
    assert f["t_wins"], "Normal beats t: revisit MC assumption"
    assert f["excess_kurtosis"] > 0.5, "tails not fat: revisit MC assumption"
    print(f"TEST OK — {f['ticker']}: t-dof={f['t_dof']:.1f}, excess kurtosis={f['excess_kurtosis']:.1f}, "
          f"loglik t {f['loglik_t']:.0f} > norm {f['loglik_norm']:.0f} -> Student-t justified")

"""Risk metrics: returns, correlations (Pearson + EWMA), VaR/ES, drawdown."""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1)).dropna(how="all")


def corr_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def ewma_corr(returns: pd.DataFrame, lam: float = 0.94) -> pd.DataFrame:
    w = np.array([(1 - lam) * lam**i for i in range(len(returns))][::-1])
    w /= w.sum()
    x = returns.fillna(0).values - np.average(returns.fillna(0).values, axis=0, weights=w)
    cov = (x * w[:, None]).T @ x
    d = np.sqrt(np.diag(cov))
    return pd.DataFrame(cov / np.outer(d, d), index=returns.columns, columns=returns.columns)


def var_es(pnl: np.ndarray, level: float = 0.95) -> tuple[float, float]:
    var = -np.percentile(pnl, (1 - level) * 100)
    es = -pnl[pnl <= -var].mean() if (pnl <= -var).any() else var
    return float(var), float(es)


def max_drawdown(prices: pd.Series) -> float:
    cum_max = prices.cummax()
    return float(((prices - cum_max) / cum_max).min())


def annualized_vol(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(TRADING_DAYS))


def beta(asset: pd.Series, market: pd.Series) -> float:
    a, m = asset.align(market, join="inner")
    return float(np.cov(a, m)[0, 1] / np.var(m))


def summary_table(prices: pd.DataFrame, market_col: str = "^GSPC") -> pd.DataFrame:
    rets = log_returns(prices)
    rows = {}
    for c in prices.columns:
        rows[c] = {"vol_annua": annualized_vol(rets[c]),
                   "beta_vs_SP500": beta(rets[c], rets[market_col]) if market_col in rets else np.nan,
                   "max_drawdown": max_drawdown(prices[c].dropna()),
                   "ret_tot_periodo": float(prices[c].dropna().iloc[-1] / prices[c].dropna().iloc[0] - 1)}
    return pd.DataFrame(rows).T.round(4)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    fake = pd.DataFrame(rng.normal(0.0005, 0.02, (500, 2)), columns=["A", "^GSPC"])
    prices = pd.DataFrame(100 * np.exp(fake.cumsum()), columns=fake.columns)
    t = summary_table(prices)
    v, e = var_es(rng.normal(0, 100, 10000))
    assert e >= v > 0 and not t.isna().any().any(), "metrics FAIL"
    print(f"TEST OK — VaR95 {v:.1f}, ES95 {e:.1f} (ES>=VaR ✓)\n{t}")

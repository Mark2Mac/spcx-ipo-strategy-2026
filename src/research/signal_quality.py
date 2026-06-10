"""Signal-quality framework: score every data source on skin-in-the-game, timeliness, verifiability; clean noisy series."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SignalSource:
    name: str
    skin_in_game: float
    timeliness: float
    verifiability: float
    noise: float
    note: str

    @property
    def score(self) -> float:
        return round(0.40 * self.skin_in_game + 0.25 * self.timeliness
                     + 0.25 * self.verifiability - 0.10 * self.noise, 2)


REGISTRY = [
    SignalSource("SEC filings (EDGAR)", 9, 6, 10, 1, "legal documents; slow but authoritative; Form 4 = insiders' real trades"),
    SignalSource("Polymarket odds", 9, 9, 8, 3, "real money on outcomes; thin books can be moved"),
    SignalSource("Market prices / IV", 10, 10, 9, 5, "the deepest aggregator; reflexive (price moves itself)"),
    SignalSource("Sell-side fair values", 5, 6, 7, 4, "reasoned DCF (Morningstar) but no position behind it"),
    SignalSource("Insider behavior (Form 4 flow)", 10, 7, 10, 2, "what insiders DO, not say; 2-day legal lag"),
    SignalSource("HN / tech-crowd attention", 2, 9, 6, 7, "early signal for tech narratives; zero skin in the game"),
    SignalSource("Wikipedia pageviews", 1, 9, 8, 6, "mass attention proxy; pure interest, no direction"),
    SignalSource("Reddit retail sentiment", 2, 9, 4, 9, "loud, unverifiable, herding; useful only as contrarian extreme"),
    SignalSource("Financial news headlines", 3, 8, 6, 8, "lagging, narrative-driven; confirms, rarely predicts"),
    SignalSource("CEO/insider public statements", 4, 9, 5, 9, "promotional by construction during an IPO window"),
]


def ranking_table() -> pd.DataFrame:
    df = pd.DataFrame([{"source": s.name, "skin": s.skin_in_game, "timely": s.timeliness,
                        "verifiable": s.verifiability, "noise": s.noise,
                        "score": s.score, "note": s.note} for s in REGISTRY])
    return df.sort_values("score", ascending=False).reset_index(drop=True)


def clean_series(s: pd.Series, winsor_q: float = 0.01, max_ffill: int = 3) -> pd.Series:
    s = s[~s.index.duplicated(keep="first")].sort_index()
    s = s.ffill(limit=max_ffill)
    lo, hi = s.quantile(winsor_q), s.quantile(1 - winsor_q)
    return s.clip(lo, hi)


def zscore(s: pd.Series, window: int = 30) -> pd.Series:
    return (s - s.rolling(window).mean()) / s.rolling(window).std()


def lead_lag_corr(signal: pd.Series, returns: pd.Series, max_lag: int = 5) -> pd.DataFrame:
    sig, ret = signal.align(returns, join="inner")
    rows = []
    for lag in range(-max_lag, max_lag + 1):
        rows.append({"lag_days": lag, "corr": sig.shift(lag).corr(ret)})
    return pd.DataFrame(rows).set_index("lag_days")


if __name__ == "__main__":
    t = ranking_table()
    assert t.iloc[0]["score"] > t.iloc[-1]["score"], "ranking broken"
    rng = np.random.default_rng(0)
    dirty = pd.Series(rng.normal(100, 5, 200), index=pd.date_range("2026-01-01", periods=200))
    dirty.iloc[50] = 10_000
    cleaned = clean_series(dirty)
    assert cleaned.max() < 1000, "winsorization failed"
    print(f"TEST OK — top signal: {t.iloc[0]['source']} ({t.iloc[0]['score']}), "
          f"bottom: {t.iloc[-1]['source']} ({t.iloc[-1]['score']}); outlier 10000 -> {cleaned.iloc[50]:.0f}")

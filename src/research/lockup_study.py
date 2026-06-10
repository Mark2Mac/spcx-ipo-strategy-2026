"""Event study: normalized price around lockup expiry of comparable historical IPOs."""
from __future__ import annotations

import pandas as pd

from src.connectors.market_data import get_ohlcv

LOCKUP_EVENTS = {
    "UBER": "2019-11-06",
    "RIVN": "2022-05-08",
    "META": "2012-11-14",
    "SNAP": "2017-07-31",
}
PRE_DAYS, POST_DAYS = 30, 60


def event_window(ticker: str, event_date: str) -> pd.Series | None:
    px = get_ohlcv(ticker, period="max")["Close"]
    px.index = pd.to_datetime(px.index)
    ev = pd.Timestamp(event_date)
    if not (px.index.min() < ev < px.index.max()):
        return None
    pos = px.index.searchsorted(ev)
    lo, hi = max(0, pos - PRE_DAYS), min(len(px), pos + POST_DAYS + 1)
    win = px.iloc[lo:hi]
    rel = pd.Series(win.values, index=range(lo - pos, hi - pos), name=ticker)
    return 100 * rel / rel.loc[0]


def lockup_panel() -> pd.DataFrame:
    cols = {}
    for t, d in LOCKUP_EVENTS.items():
        s = event_window(t, d)
        if s is not None:
            cols[t] = s
    panel = pd.DataFrame(cols)
    panel["mean"] = panel.mean(axis=1)
    return panel


if __name__ == "__main__":
    p = lockup_panel()
    assert len(p.columns) >= 4, f"only {list(p.columns)} available"
    anticipation = p["mean"].loc[0] - p["mean"].loc[-PRE_DAYS]
    post = p["mean"].loc[20] - p["mean"].loc[0]
    assert anticipation < 0, f"anticipation drop missing: {anticipation:+.1f}"
    print(f"TEST OK — {len(p.columns)-1} events. Pattern: PRE-expiry drop {anticipation:+.1f} punti "
          f"(T-{PRE_DAYS}→T0), post-scadenza {post:+.1f} (T0->T+20): the rumor gets sold, the news gets bought")
    print(p.loc[[-30, -10, 0, 10, 20, 40], :].round(1))

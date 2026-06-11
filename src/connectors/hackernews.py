"""Hacker News connector via Algolia API (free, no auth): story flow as a tech-crowd attention signal."""
from __future__ import annotations

import time

import pandas as pd
import requests

API = "https://hn.algolia.com/api/v1/search_by_date"


def _fetch_window(query: str, t0: int, t1: int, max_pages: int) -> list[dict]:
    rows, page = [], 0
    while page < max_pages:
        r = requests.get(API, params={"query": query, "tags": "story",
                                      "numericFilters": f"created_at_i>{t0},created_at_i<{t1}",
                                      "hitsPerPage": 100, "page": page}, timeout=30)
        r.raise_for_status()
        data = r.json()
        hits = data.get("hits", [])
        for h in hits:
            rows.append({"date": pd.Timestamp(h["created_at_i"], unit="s").normalize(),
                         "title": h.get("title"), "points": h.get("points") or 0,
                         "comments": h.get("num_comments") or 0, "url": h.get("url")})
        if page >= data.get("nbPages", 1) - 1 or not hits:
            break
        page += 1
    return rows


def search_stories(query: str, days: int = 90, max_pages: int = 10,
                   window_days: int | None = 20) -> pd.DataFrame:
    now = int(time.time())
    since = now - days * 86400
    rows: list[dict] = []
    if window_days is None:
        rows = _fetch_window(query, since, now, max_pages)
    else:
        t0 = since
        while t0 < now:
            t1 = min(t0 + window_days * 86400, now)
            rows.extend(_fetch_window(query, t0, t1, max_pages))
            t0 = t1
    df = pd.DataFrame(rows)
    return df.drop_duplicates(subset=["title"]) if not df.empty else df


def daily_attention(query: str, days: int = 90) -> pd.DataFrame:
    df = search_stories(query, days)
    if df.empty:
        return pd.DataFrame(columns=["stories", "points", "comments"])
    g = df.groupby("date").agg(stories=("title", "count"), points=("points", "sum"),
                               comments=("comments", "sum"))
    idx = pd.date_range(pd.Timestamp.now().normalize() - pd.Timedelta(days=days),
                        g.index.max(), freq="D")
    cov = len(g) and (g.index.min() - idx[0]).days
    out = g.reindex(idx, fill_value=0)
    out.attrs["coverage_gap_days"] = int(cov or 0)
    return out


if __name__ == "__main__":
    att = daily_attention("spacex ipo", days=60)
    assert not att.empty and att["points"].sum() > 100, "HN FAIL"
    peak = att["points"].idxmax()
    print(f"TEST OK — {att['stories'].sum()} stories/60d, peak {peak.date()} ({att.loc[peak,'points']} pts)")

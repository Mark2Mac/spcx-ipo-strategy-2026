"""Wikipedia pageviews connector (Wikimedia REST, free): mass-attention proxy, with disk cache and 429 backoff."""
from __future__ import annotations

import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

UA = {"User-Agent": "spcx-ipo-strategy research Mark2Mac@users.noreply.github.com"}
API = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CACHE_MAX_AGE_H = 12


def _get_with_backoff(url: str, retries: int = 4) -> dict:
    for attempt in range(retries):
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code == 429:
            time.sleep(2 ** attempt * 5)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()
    return {}


def pageviews(article: str, days: int = 180) -> pd.Series:
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / f"wiki_{article.replace(',', '').replace('.', '')}_{days}.parquet"
    if cache.exists() and (time.time() - cache.stat().st_mtime) < CACHE_MAX_AGE_H * 3600:
        return pd.read_parquet(cache)[article.replace(",", "").replace(".", "")]
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days)
    items = _get_with_backoff(f"{API}/{article}/daily/{start:%Y%m%d}00/{end:%Y%m%d}00").get("items", [])
    name = article.replace(",", "").replace(".", "")
    s = pd.Series({pd.Timestamp(i["timestamp"][:8]): i["views"] for i in items}, name=name).sort_index()
    s.to_frame().to_parquet(cache)
    return s


def attention_panel(articles: list[str], days: int = 180) -> pd.DataFrame:
    return pd.DataFrame({a: pageviews(a, days) for a in articles})


if __name__ == "__main__":
    pv = pageviews("SpaceX", days=120)
    assert len(pv) > 100 and pv.sum() > 100_000, "Wikipedia FAIL"
    print(f"TEST OK — SpaceX: {len(pv)} days, mean {pv.mean():,.0f} views/day, "
          f"peak {pv.idxmax().date()} ({pv.max():,.0f})")

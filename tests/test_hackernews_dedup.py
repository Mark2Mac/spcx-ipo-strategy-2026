"""Regression: dedup must drop only true duplicates (same story re-fetched at a window
overlap, identified by objectID), not collapse a recurring identical title posted on
different days — which silently undercounts attention on the later days."""
import pandas as pd

import src.connectors.hackernews as hn


def test_same_title_different_days_both_kept(monkeypatch):
    d1 = pd.Timestamp("2026-06-01")
    d2 = pd.Timestamp("2026-06-08")
    rows = [
        {"date": d1, "title": "SpaceX Starship launch thread", "points": 100,
         "comments": 50, "url": None, "id": "1"},
        {"date": d2, "title": "SpaceX Starship launch thread", "points": 200,
         "comments": 80, "url": None, "id": "2"},
    ]
    monkeypatch.setattr(hn, "_fetch_window", lambda *a, **k: rows)
    df = hn.search_stories("spacex", days=30, window_days=None)
    assert len(df) == 2  # distinct stories, not collapsed by identical title


def test_same_objectid_collapsed(monkeypatch):
    # window-overlap re-fetch: the SAME story (same objectID) appears twice -> one row
    d1 = pd.Timestamp("2026-06-01")
    rows = [
        {"date": d1, "title": "X", "points": 10, "comments": 1, "url": None, "id": "42"},
        {"date": d1, "title": "X", "points": 10, "comments": 1, "url": None, "id": "42"},
    ]
    monkeypatch.setattr(hn, "_fetch_window", lambda *a, **k: rows)
    df = hn.search_stories("spacex", days=30, window_days=None)
    assert len(df) == 1


def test_daily_attention_counts_both_days(monkeypatch):
    d1 = pd.Timestamp.now().normalize() - pd.Timedelta(days=20)
    d2 = pd.Timestamp.now().normalize() - pd.Timedelta(days=5)
    rows = [
        {"date": d1, "title": "same headline", "points": 100, "comments": 10, "url": None, "id": "a"},
        {"date": d2, "title": "same headline", "points": 300, "comments": 30, "url": None, "id": "b"},
    ]
    monkeypatch.setattr(hn, "_fetch_window", lambda *a, **k: rows)
    out = hn.daily_attention("spacex", days=40)
    assert out.loc[d1, "points"] == 100
    assert out.loc[d2, "points"] == 300  # later day not zeroed by title-collapse

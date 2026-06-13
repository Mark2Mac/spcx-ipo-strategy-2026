"""Regression: coverage_gap_days metadata exists so checkpoint can persist it (bug #11)."""
import pandas as pd

import src.connectors.hackernews as hn


def test_coverage_gap_days_attr_set(monkeypatch):
    recent = pd.Timestamp.now().normalize() - pd.to_timedelta([10, 5, 1], unit="D")
    rows = pd.DataFrame({
        "date": recent, "title": ["a", "b", "c"], "points": [10, 20, 30],
        "comments": [1, 2, 3], "url": [None, None, None],
    })
    monkeypatch.setattr(hn, "search_stories", lambda *a, **k: rows)
    out = hn.daily_attention("spacex", days=30)
    assert "coverage_gap_days" in out.attrs
    assert isinstance(out.attrs["coverage_gap_days"], int)


def test_data_older_than_window_does_not_crash(monkeypatch):
    # all stories predate the now-days window -> date_range was empty -> idx[0] IndexError
    old = pd.Timestamp.now().normalize() - pd.to_timedelta([120, 119, 118], unit="D")
    rows = pd.DataFrame({
        "date": old, "title": ["a", "b", "c"], "points": [10, 20, 30],
        "comments": [1, 2, 3], "url": [None, None, None],
    })
    monkeypatch.setattr(hn, "search_stories", lambda *a, **k: rows)
    out = hn.daily_attention("spacex", days=30)  # window ends well after the data
    assert not out.empty
    assert isinstance(out.attrs["coverage_gap_days"], int)

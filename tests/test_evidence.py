"""Regression: every post-IPO visual reads the same frozen evidence (bug 19)."""
import json

import pandas as pd

import evidence as ev


def _snap(root, name, created, iv=None):
    d = root / name
    d.mkdir()
    pd.DataFrame({"Close": [160.95, 135.27]},
                 index=pd.to_datetime(["2026-06-12", "2026-07-15"])).to_parquet(d / "spcx_ohlcv.parquet")
    (d / "MANIFEST.json").write_text(json.dumps({"created_utc": created}))
    if iv is not None:
        (d / "spcx_market.json").write_text(json.dumps({"derived_atm_iv": iv}))
    return d


def test_latest_checkpoint_uses_created_utc_not_dir_name(tmp_path):
    # Same-day milestone labels sort AFTER HHMM-auto tags lexically; created_utc must win.
    _snap(tmp_path, "2026-07-16-entry-window-close", "2026-07-16T09:38:00+00:00")
    newer = _snap(tmp_path, "2026-07-16-1457-auto", "2026-07-16T14:57:00+00:00")
    assert ev.latest_checkpoint(tmp_path) == newer


def test_latest_checkpoint_skips_snapshots_without_price_history(tmp_path):
    with_prices = _snap(tmp_path, "2026-06-13-ci-verify", "2026-06-13T00:00:00+00:00")
    bare = tmp_path / "2026-07-01-no-parquet"
    bare.mkdir()
    (bare / "MANIFEST.json").write_text(json.dumps({"created_utc": "2026-07-01T00:00:00+00:00"}))
    assert ev.latest_checkpoint(tmp_path) == with_prices


def test_realized_closes_starts_at_debut(tmp_path):
    d = tmp_path / "snap"
    d.mkdir()
    pd.DataFrame({"Close": [100.0, 160.95, 135.27]},
                 index=pd.to_datetime(["2026-06-11", "2026-06-12", "2026-07-15"])).to_parquet(
        d / "spcx_ohlcv.parquet")
    r = ev.realized_closes(d)
    assert list(r) == [160.95, 135.27]  # pre-debut bars excluded, plain ndarray


def test_unlock_month_iv_means_aug_expiries_only(tmp_path):
    iv = {"2026-07-24": {"avg_iv": 0.71}, "2026-08-07": {"avg_iv": 0.80},
          "2026-08-21": {"avg_iv": 0.90}, "2026-09-18": {"avg_iv": 0.82}}
    d = _snap(tmp_path, "2026-07-16-1457-auto", "2026-07-16T14:57:00+00:00", iv=iv)
    assert ev.unlock_month_iv(d) == 0.85

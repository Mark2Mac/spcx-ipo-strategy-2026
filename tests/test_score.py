"""Regression: day-1 predictions (P1/P2) must score on the FROZEN day-1 close, never on the
latest checkpoint's rolling close. A correctly-TRUE day-1 fact must not flip FALSE when the
live price later drifts below the threshold (the scoring-drift bug).

Window predictions (P3) must score on the min close over a CLOSED date window, pinned to the
earliest checkpoint that covers it — a later drop outside the window cannot flip the outcome."""
import json
from datetime import date

import pandas as pd
import score as sc

SHARES = sc.SPCX_SHARES_424B4  # 13,075,865,175


def _mk_ckpt(root, name, created_utc, close, debut_bar="2026-06-12", extra=None, closes=None):
    d = root / name
    d.mkdir()
    spcx = {"listed": True, "last_close": close,
            "ohlcv_tail": [{"Date": f"{debut_bar} 00:00:00", "Close": close, "Volume": 5e8}]}
    if extra:
        spcx.update(extra)
    (d / "spcx_market.json").write_text(json.dumps(spcx))
    (d / "MANIFEST.json").write_text(json.dumps({"created_utc": created_utc}))
    if closes:
        idx = pd.to_datetime(list(closes))
        pd.DataFrame({"Close": list(closes.values())}, index=idx).to_parquet(
            d / "spcx_ohlcv.parquet")
    return d


def test_day1_snapshot_pins_to_debut_bar(tmp_path):
    # day-1 checkpoint holds the 12/6 close; a later one holds a drifted close on a 18/6 bar.
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    _mk_ckpt(tmp_path, "2026-06-18-auto", "2026-06-18T23:00:00+00:00", 130.0,
             debut_bar="2026-06-18")
    name, _, close = sc.day1_snapshot(tmp_path)
    assert close == 160.95
    assert name == "2026-06-15-day1"


def test_p2_stays_true_when_live_price_drifts_below_threshold(tmp_path):
    # day-1 close 160.95 -> cap $2.105T (P2 >$2T TRUE). A later checkpoint at 130 -> $1.7T.
    # Bug: scoring off the latest close would flip P2 to FALSE. Must stay TRUE.
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    _mk_ckpt(tmp_path, "2026-08-01-auto", "2026-08-01T23:00:00+00:00", 130.0,
             debut_bar="2026-08-01")
    res = sc.score(tmp_path, today=date(2026, 8, 1))
    assert res["P2"]["outcome"] == "TRUE", res["P2"]["detail"]
    assert res["P1"]["outcome"] == "TRUE"
    assert "2.105" in res["P2"]["detail"]  # cap from frozen day-1 close, not 130


def test_pending_before_verify_date(tmp_path):
    _mk_ckpt(tmp_path, "2026-06-11-auto", "2026-06-11T21:00:00+00:00", 0.0, debut_bar="x")
    res = sc.score(tmp_path, today=date(2026, 6, 11))
    assert res["P1"]["outcome"] == "pending"


def test_unverifiable_when_no_day1_bar_yet(tmp_path):
    # past verify date but no checkpoint captured the debut bar -> unverifiable, never guessed
    _mk_ckpt(tmp_path, "2026-06-13-auto", "2026-06-13T21:00:00+00:00", 99.0, debut_bar="2026-06-13")
    res = sc.score(tmp_path, today=date(2026, 6, 20))
    assert res["P1"]["outcome"] == "unverifiable"


# --- P3: window-minimum basis -------------------------------------------------------------

WINDOW_OK = {"2026-06-12": 160.95, "2026-06-25": 145.30, "2026-07-10": 150.0}


def test_p3_true_when_window_min_holds_above_threshold(tmp_path):
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    _mk_ckpt(tmp_path, "2026-07-13-auto", "2026-07-13T21:00:00+00:00", 139.14,
             debut_bar="2026-07-13", closes=WINDOW_OK)
    res = sc.score(tmp_path, today=date(2026, 7, 13))
    assert res["P3"]["outcome"] == "TRUE", res["P3"]["detail"]
    assert "145.30" in res["P3"]["detail"]


def test_p3_stays_true_when_price_drops_after_the_window(tmp_path):
    # The whole point: SPCX closed at $115 in late July. That is OUTSIDE the 4-week window and
    # must not flip a prediction that already resolved on Jul 10.
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    late = dict(WINDOW_OK, **{"2026-07-24": 115.07})
    _mk_ckpt(tmp_path, "2026-07-27-auto", "2026-07-27T22:00:00+00:00", 115.07,
             debut_bar="2026-07-27", closes=late)
    res = sc.score(tmp_path, today=date(2026, 7, 27))
    assert res["P3"]["outcome"] == "TRUE", res["P3"]["detail"]
    assert "115" not in res["P3"]["detail"]


def test_p3_false_when_a_close_breaks_the_threshold_inside_the_window(tmp_path):
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    broken = dict(WINDOW_OK, **{"2026-07-02": 130.0})
    _mk_ckpt(tmp_path, "2026-07-13-auto", "2026-07-13T21:00:00+00:00", 130.0,
             debut_bar="2026-07-13", closes=broken)
    res = sc.score(tmp_path, today=date(2026, 7, 13))
    assert res["P3"]["outcome"] == "FALSE", res["P3"]["detail"]


def test_p3_pins_to_earliest_checkpoint_covering_the_window(tmp_path):
    # Two snapshots both cover the window; the score must cite the earlier one, so the source
    # of a resolved prediction never drifts forward with the tape.
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    _mk_ckpt(tmp_path, "2026-07-13-auto", "2026-07-13T21:00:00+00:00", 139.14,
             debut_bar="2026-07-13", closes=WINDOW_OK)
    _mk_ckpt(tmp_path, "2026-07-27-auto", "2026-07-27T22:00:00+00:00", 113.50,
             debut_bar="2026-07-27", closes=dict(WINDOW_OK, **{"2026-07-24": 115.07}))
    res = sc.score(tmp_path, today=date(2026, 7, 27))
    assert res["P3"]["source"] == "2026-07-13-auto"


def test_p3_unverifiable_when_no_checkpoint_covers_the_window_end(tmp_path):
    # Verify date passed but evidence stops short of it -> never extrapolate, say unverifiable.
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    _mk_ckpt(tmp_path, "2026-07-02-auto", "2026-07-02T21:00:00+00:00", 155.0,
             debut_bar="2026-07-02", closes={"2026-06-12": 160.95, "2026-07-02": 155.0})
    res = sc.score(tmp_path, today=date(2026, 7, 13))
    assert res["P3"]["outcome"] == "unverifiable"


def test_p3_pending_before_its_verify_date(tmp_path):
    _mk_ckpt(tmp_path, "2026-06-15-day1", "2026-06-15T09:00:00+00:00", 160.95)
    res = sc.score(tmp_path, today=date(2026, 7, 1))
    assert res["P3"]["outcome"] == "pending"

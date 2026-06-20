"""Regression: day-1 predictions (P1/P2) must score on the FROZEN day-1 close, never on the
latest checkpoint's rolling close. A correctly-TRUE day-1 fact must not flip FALSE when the
live price later drifts below the threshold (the scoring-drift bug)."""
import json
from datetime import date

import score as sc

SHARES = sc.SPCX_SHARES_424B4  # 13,075,865,175


def _mk_ckpt(root, name, created_utc, close, debut_bar="2026-06-12", extra=None):
    d = root / name
    d.mkdir()
    spcx = {"listed": True, "last_close": close,
            "ohlcv_tail": [{"Date": f"{debut_bar} 00:00:00", "Close": close, "Volume": 5e8}]}
    if extra:
        spcx.update(extra)
    (d / "spcx_market.json").write_text(json.dumps(spcx))
    (d / "MANIFEST.json").write_text(json.dumps({"created_utc": created_utc}))
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

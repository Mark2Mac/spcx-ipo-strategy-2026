"""Regression: NaN in ohlcv_tail -> JSON null, not the string "nan" (bug #8)."""
import json

import numpy as np
import pandas as pd

import checkpoint as cp


def test_finite_sanitizes_nan_inf():
    assert cp._finite(float("nan")) is None
    assert cp._finite(float("inf")) is None
    assert cp._finite({"a": float("nan"), "b": [1.0, float("-inf")]}) == {"a": None, "b": [1.0, None]}


def test_select_expiries_always_includes_study_expiries():
    # Bug 18: [:6] near-expiry slice never archived the Sep 18 spread expiry (the entry gate
    # reads Sep ATM IV) nor late-Aug unlock-month expiries once the chain grew past 6 weeklies.
    exps = ["2026-07-17", "2026-07-24", "2026-07-31", "2026-08-07", "2026-08-14",
            "2026-08-21", "2026-08-28", "2026-09-18", "2026-10-16", "2027-01-15"]
    sel = cp._select_expiries(exps)
    assert "2026-09-18" in sel          # spread expiry = gate IV, must be frozen evidence
    assert "2026-08-28" in sel          # unlock-month expiry beyond the near-6 slice
    assert sel[:6] == exps[:6]          # near-term structure still archived
    assert len(sel) == len(set(sel))    # no duplicate fetches


def test_select_expiries_empty_chain_is_safe():
    assert cp._select_expiries([]) == []


def test_ohlcv_tail_nan_becomes_null_not_string():
    # mimic checkpoint: reset_index().to_dict("records") then _finite (the #8 fix path)
    df = pd.DataFrame({"Close": [10.0, np.nan], "Volume": [100.0, 200.0]},
                      index=pd.to_datetime(["2026-01-01", "2026-01-02"]))
    records = df.reset_index().to_dict("records")
    payload = cp._finite(records)
    dumped = json.dumps(payload, default=str, allow_nan=False)
    assert '"nan"' not in dumped  # the old astype(str) produced the literal string "nan"
    assert payload[1]["Close"] is None

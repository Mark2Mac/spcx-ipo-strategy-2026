"""Regression: NaN in ohlcv_tail -> JSON null, not the string "nan" (bug #8)."""
import json

import numpy as np
import pandas as pd

import checkpoint as cp


def test_finite_sanitizes_nan_inf():
    assert cp._finite(float("nan")) is None
    assert cp._finite(float("inf")) is None
    assert cp._finite({"a": float("nan"), "b": [1.0, float("-inf")]}) == {"a": None, "b": [1.0, None]}


def test_ohlcv_tail_nan_becomes_null_not_string():
    # mimic checkpoint: reset_index().to_dict("records") then _finite (the #8 fix path)
    df = pd.DataFrame({"Close": [10.0, np.nan], "Volume": [100.0, 200.0]},
                      index=pd.to_datetime(["2026-01-01", "2026-01-02"]))
    records = df.reset_index().to_dict("records")
    payload = cp._finite(records)
    dumped = json.dumps(payload, default=str, allow_nan=False)
    assert '"nan"' not in dumped  # the old astype(str) produced the literal string "nan"
    assert payload[1]["Close"] is None

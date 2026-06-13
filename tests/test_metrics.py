"""Regression: beta() must use ddof=1 on both cov and var (bug #10)."""
import numpy as np
import pandas as pd

from src.risk.metrics import beta, var_es


def test_beta_self_is_one():
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(0, 0.02, 250))
    assert abs(beta(s, s) - 1.0) < 1e-9


def test_beta_matches_consistent_ddof():
    rng = np.random.default_rng(1)
    a = pd.Series(rng.normal(0, 0.02, 250))
    m = pd.Series(rng.normal(0, 0.02, 250))
    expected = np.cov(a, m)[0, 1] / np.var(m, ddof=1)  # both ddof=1
    assert abs(beta(a, m) - expected) < 1e-12
    # the old buggy form (var ddof=0) differs by factor n/(n-1)
    buggy = np.cov(a, m)[0, 1] / np.var(m, ddof=0)
    assert abs(beta(a, m) - buggy) > 1e-9


def test_var_es_ordering():
    rng = np.random.default_rng(2)
    v, e = var_es(rng.normal(0, 100, 10_000))
    assert e >= v > 0

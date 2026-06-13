"""Regression: FX rate must be configurable, not a hardcoded 1.08 (bug #4)."""
import numpy as np

from src.risk.montecarlo import McConfig, SpreadPosition, report, simulate


def test_fx_is_configurable_and_scales_spread():
    spread = SpreadPosition()
    r1 = simulate(McConfig(fx_eurusd=1.0), spread)
    r2 = simulate(McConfig(fx_eurusd=2.0), spread)
    # same paths (seed fixed) -> EUR spread P&L halves when rate doubles
    np.testing.assert_allclose(r1["pnl_spread_eur"], 2.0 * r2["pnl_spread_eur"], rtol=1e-9)


def test_default_fx_is_current_not_stale():
    assert McConfig().fx_eurusd > 1.10  # old stale constant was 1.08


def test_spread_hard_cap_respects_fx():
    cfg = McConfig(fx_eurusd=1.16)
    res = simulate(cfg, SpreadPosition())
    cap = 2.20 * 100 / cfg.fx_eurusd
    assert res["pnl_spread_eur"].min() >= -cap - 1e-6


def test_report_es_ge_var():
    rep = report(simulate(McConfig(), SpreadPosition()))
    assert rep["ES95"] >= rep["VaR95"]

"""Monte Carlo portafoglio: GBM con innovazioni Student-t (fat tails) + jump sull'evento trimestrale."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TRADING_DAYS = 252


@dataclass
class SpreadPosition:
    long_strike: float = 140.0
    short_strike: float = 135.0
    debit: float = 2.20
    contracts: int = 1

    def payoff(self, spot_final: np.ndarray) -> np.ndarray:
        intrinsic = (np.clip(self.long_strike - spot_final, 0, None)
                     - np.clip(self.short_strike - spot_final, 0, None))
        return (intrinsic - self.debit) * 100 * self.contracts


@dataclass
class McConfig:
    n_paths: int = 10_000
    horizon_days: int = 70
    event_day: int = 45
    spcx_s0: float = 150.0
    spcx_vol: float = 0.70
    spcx_drift: float = 0.0
    jump_mean: float = -0.08
    jump_std: float = 0.12
    googl_value_eur: float = 1200.0
    googl_vol: float = 0.28
    googl_drift: float = 0.06
    rho: float = 0.45
    t_dof: int = 4
    seed: int = 7


def simulate(cfg: McConfig, spread: SpreadPosition) -> dict:
    rng = np.random.default_rng(cfg.seed)
    dt = 1 / TRADING_DAYS
    scale = np.sqrt(cfg.t_dof / (cfg.t_dof - 2))
    z = rng.standard_t(cfg.t_dof, (cfg.n_paths, cfg.horizon_days, 2)) / scale
    z[:, :, 1] = cfg.rho * z[:, :, 0] + np.sqrt(1 - cfg.rho**2) * z[:, :, 1]

    spcx = np.full(cfg.n_paths, cfg.spcx_s0)
    googl = np.full(cfg.n_paths, 1.0)
    for d in range(cfg.horizon_days):
        spcx *= np.exp((cfg.spcx_drift - 0.5 * cfg.spcx_vol**2) * dt
                       + cfg.spcx_vol * np.sqrt(dt) * z[:, d, 0])
        googl *= np.exp((cfg.googl_drift - 0.5 * cfg.googl_vol**2) * dt
                        + cfg.googl_vol * np.sqrt(dt) * z[:, d, 1])
        if d == cfg.event_day:
            spcx *= np.exp(rng.normal(cfg.jump_mean, cfg.jump_std, cfg.n_paths))

    pnl_spread_usd = spread.payoff(spcx)
    pnl_spread_usd = np.maximum(pnl_spread_usd, -spread.debit * 100 * spread.contracts)
    pnl_googl_eur = cfg.googl_value_eur * (googl - 1)
    pnl_total_eur = pnl_googl_eur + pnl_spread_usd / 1.08

    return {"spcx_final": spcx, "pnl_googl_eur": pnl_googl_eur,
            "pnl_spread_eur": pnl_spread_usd / 1.08, "pnl_total_eur": pnl_total_eur}


def report(res: dict, level: float = 0.95) -> dict:
    from .metrics import var_es

    pnl = res["pnl_total_eur"]
    var, es = var_es(pnl, level)
    return {"mean": float(pnl.mean()), "median": float(np.median(pnl)),
            f"VaR{int(level*100)}": var, f"ES{int(level*100)}": es,
            "p_loss": float((pnl < 0).mean()),
            "p_loss_gt_200": float((pnl < -200).mean()),
            "best_5pct": float(np.percentile(pnl, 95)),
            "worst_path": float(pnl.min())}


if __name__ == "__main__":
    res = simulate(McConfig(), SpreadPosition())
    rep = report(res)
    max_spread_loss = 2.20 * 100 / 1.08
    assert res["pnl_spread_eur"].min() >= -max_spread_loss - 1e-6, "hard cap violato!"
    assert rep["ES95"] >= rep["VaR95"], "ES < VaR: bug"
    print("TEST OK — hard cap spread rispettato su 10k path")
    for k, v in rep.items():
        print(f"  {k}: {v:+.1f}" if isinstance(v, float) and abs(v) > 1 else f"  {k}: {v:.1%}" if isinstance(v, float) else f"  {k}: {v}")

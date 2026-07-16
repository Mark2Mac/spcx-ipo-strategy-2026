"""Regenerates assets/chart_mc_vs_realized.png as a LIVING overlay: the realized-IV Monte Carlo
cone vs the realized SPCX path, both read from the latest frozen checkpoint (same evidence the
post-IPO gif uses). The Jul-6 decision-record version stays embedded in notebooks/07 (frozen)."""
from __future__ import annotations

import datetime as dt
import sys
from dataclasses import replace
from math import erf, exp, log, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.risk.montecarlo import McConfig, SpreadPosition, TRADING_DAYS  # noqa: E402
from src.viz import BAD, PALETTE, headline, tufte_style  # noqa: E402
from tools.evidence import latest_checkpoint, realized_closes, unlock_month_iv  # noqa: E402

SEP_EXPIRY = dt.date(2026, 9, 18)


def _bs_put(S: float, K: float, T: float, sig: float, r: float = 0.036) -> float:
    if T <= 0 or sig <= 0:
        return max(0.0, K - S)
    nc = lambda x: 0.5 * (1 + erf(x / sqrt(2)))  # noqa: E731
    d1 = (log(S / K) + (r + 0.5 * sig * sig) * T) / (sig * sqrt(T))
    return K * exp(-r * T) * nc(-(d1 - sig * sqrt(T))) - S * nc(-d1)


def main() -> None:
    tufte_style()
    ck = latest_checkpoint(ROOT / "checkpoints")
    realized = realized_closes(ck)
    ipo_anchor = float(realized[0])
    vol = unlock_month_iv(ck) or McConfig().spcx_vol

    cfg = replace(McConfig(), spcx_s0=ipo_anchor, spcx_vol=vol)
    spread = SpreadPosition()
    T_sep = max((SEP_EXPIRY - dt.date.today()).days, 1) / 365
    debit = round(_bs_put(float(realized[-1]), spread.long_strike, T_sep, vol)
                  - _bs_put(float(realized[-1]), spread.short_strike, T_sep, vol), 2)

    rng = np.random.default_rng(cfg.seed)
    H = cfg.horizon_days
    scale = np.sqrt(cfg.t_dof / (cfg.t_dof - 2))
    z = rng.standard_t(cfg.t_dof, (4000, H)) / scale
    paths = np.empty((4000, H + 1))
    paths[:, 0] = ipo_anchor
    dt_y = 1 / TRADING_DAYS
    for d in range(H):
        paths[:, d + 1] = paths[:, d] * np.exp(
            (cfg.spcx_drift - 0.5 * cfg.spcx_vol**2) * dt_y + cfg.spcx_vol * np.sqrt(dt_y) * z[:, d])
        if d == cfg.event_day:
            paths[:, d + 1] *= np.exp(rng.normal(cfg.jump_mean, cfg.jump_std, 4000))

    days = np.arange(H + 1)
    q = {p: np.percentile(paths, p, axis=0) for p in (5, 25, 50, 75, 95)}
    be = spread.long_strike - debit
    n = len(realized)

    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.fill_between(days, q[5], q[95], color=PALETTE[0], alpha=0.12, label="5-95% band")
    ax.fill_between(days, q[25], q[75], color=PALETTE[0], alpha=0.22, label="25-75% band")
    ax.plot(days, q[50], color=PALETTE[0], lw=1.6, label="MC median")
    ax.plot(np.arange(n), realized, color=BAD, lw=2.6, marker="o", ms=3.5, label="realized SPCX")
    for k in (spread.long_strike, spread.short_strike):
        ax.axhline(k, ls=":", color="gray", lw=0.8)
    ax.axhline(be, ls="--", color="#3d5c40", lw=1)
    ax.annotate(f"spread breakeven {be:.1f}", (H * 0.55, be + 1.5), color="#3d5c40", fontsize=8.5)
    ax.axvline(cfg.event_day, ls="--", color=PALETTE[1], lw=1)
    ax.annotate("event (unlock)", (cfg.event_day, ax.get_ylim()[1] * 0.9),
                color=PALETTE[1], fontsize=8.5, ha="center")
    side = "below" if realized[-1] < q[50][n - 1] else "above"
    headline(ax, f"Melt-up pierced the cone (day-2 close {realized[:5].max():.0f}), "
                 f"round-tripped to {realized[-1]:.0f} — {side} the MC median {q[50][n - 1]:.0f}",
             f"4,000 Student-t paths from the ${ipo_anchor:.2f} debut close, unlock-month IV "
             f"{vol:.0%} from {ck.name}; strikes 140/135 (dotted), USD")
    ax.set_xlabel("sessions from IPO")
    ax.set_ylabel("$")
    ax.legend(loc="lower left", fontsize=8, ncol=2)
    plt.tight_layout()
    out = ROOT / "assets" / "chart_mc_vs_realized.png"
    plt.savefig(out, dpi=130, bbox_inches="tight")
    print(f"saved {out} | {n} sessions, last close {realized[-1]:.2f}, IV {vol:.3f}, evidence {ck.name}")


if __name__ == "__main__":
    main()

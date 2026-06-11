"""Generates assets/mc_paths.gif: animated Monte Carlo fan chart for SPCX with percentile bands."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.risk.montecarlo import McConfig, TRADING_DAYS  # noqa: E402
from src.viz import PALETTE, tufte_style  # noqa: E402


def simulate_paths(cfg: McConfig, n_show: int = 60) -> np.ndarray:
    rng = np.random.default_rng(cfg.seed)
    dt = 1 / TRADING_DAYS
    scale = np.sqrt(cfg.t_dof / (cfg.t_dof - 2))
    z = rng.standard_t(cfg.t_dof, (cfg.n_paths, cfg.horizon_days)) / scale
    paths = np.empty((cfg.n_paths, cfg.horizon_days + 1))
    paths[:, 0] = cfg.spcx_s0
    for d in range(cfg.horizon_days):
        paths[:, d + 1] = paths[:, d] * np.exp(
            (cfg.spcx_drift - 0.5 * cfg.spcx_vol**2) * dt + cfg.spcx_vol * np.sqrt(dt) * z[:, d])
        if d == cfg.event_day:
            paths[:, d + 1] *= np.exp(rng.normal(cfg.jump_mean, cfg.jump_std, cfg.n_paths))
    return paths


def main() -> None:
    tufte_style()
    cfg = McConfig(n_paths=2000)
    paths = simulate_paths(cfg)
    show = paths[:: len(paths) // 60][:60]
    days = np.arange(paths.shape[1])
    p5, p50, p95 = (np.percentile(paths, q, axis=0) for q in (5, 50, 95))

    be = 140 - 2.20
    pct_below = (paths[:, -1] < be).mean()
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.set_xlim(0, days[-1])
    ax.set_ylim(paths.min() * 0.95, np.percentile(paths, 99.5))
    ax.axvline(cfg.event_day, color=PALETTE[1], lw=1, ls="--")
    ax.annotate("earnings +\ninsider unlock", (cfg.event_day, ax.get_ylim()[1] * 0.93),
                fontsize=9, ha="center", color=PALETTE[1])
    ax.axhspan(ax.get_ylim()[0], be, color="#7A9E7E", alpha=0.07)
    ax.axhline(be, color="gray", lw=0.8, ls=":")
    ax.annotate(f"spread breakeven {be:.1f} — {pct_below:.0%} of paths end below it",
                (2, be + 1.5), fontsize=8.5, color="#3d5c40", fontweight="bold")
    ax.text(0, 1.10, f"{pct_below:.0%} of 2,000 simulated paths end below the spread breakeven",
            transform=ax.transAxes, fontsize=12.5, fontweight="bold", va="bottom")
    ax.text(0, 1.04, "SPCX Monte Carlo — Student-t fat tails + jump on the August event, 70 sessions, 5th-95th percentile band",
            transform=ax.transAxes, fontsize=9, color="#666666", va="bottom")
    ax.set_xlabel("sessions from mid-July"); ax.set_ylabel("$")

    lines = [ax.plot([], [], lw=0.5, color=PALETTE[0], alpha=0.25)[0] for _ in show]
    med, = ax.plot([], [], lw=2.2, color=PALETTE[1])
    band = [None]

    def update(frame: int):
        d = days[: frame + 1]
        for ln, p in zip(lines, show):
            ln.set_data(d, p[: frame + 1])
        med.set_data(d, p50[: frame + 1])
        if band[0] is not None:
            band[0].remove()
        band[0] = ax.fill_between(d, p5[: frame + 1], p95[: frame + 1], color=PALETTE[0], alpha=0.12)
        return lines + [med]

    frames = list(range(2, paths.shape[1], 2))
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    out = ROOT / "assets" / "mc_paths.gif"
    ani.save(out, writer=animation.PillowWriter(fps=12))
    print(f"saved {out} ({out.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()

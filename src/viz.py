"""Tufte chart style: max data-ink ratio, direct labels, zero junkchart."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PALETTE = ["#2E5266", "#C0392B", "#7A9E7E", "#8E6C8A", "#B8860B", "#5D6D7E"]


def tufte_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
        "axes.prop_cycle": plt.cycler(color=PALETTE),
        "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
        "legend.frameon": False, "figure.dpi": 110,
    })


def direct_label_lines(ax: plt.Axes, df: pd.DataFrame) -> None:
    for i, col in enumerate(df.columns):
        s = df[col].dropna()
        ax.annotate(col, (s.index[-1], s.iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=9,
                    color=PALETTE[i % len(PALETTE)], fontweight="bold")


def corr_heatmap(ax: plt.Axes, corr: pd.DataFrame, title: str) -> None:
    n = len(corr)
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(n), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(n), corr.index)
    for i in range(n):
        for j in range(n):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(v) > 0.6 else "black")
    ax.set_title(title)
    ax.grid(False)
    plt.colorbar(im, ax=ax, shrink=0.8)


def pnl_distribution(ax: plt.Axes, pnl: np.ndarray, var95: float, es95: float, title: str) -> None:
    ax.hist(pnl, bins=120, color=PALETTE[0], alpha=0.85, edgecolor="none")
    ax.axvline(0, color="black", lw=0.8)
    ax.axvline(-var95, color=PALETTE[1], lw=1.2, ls="--")
    ax.axvline(-es95, color=PALETTE[1], lw=1.2, ls=":")
    ymax = ax.get_ylim()[1]
    ax.annotate(f"VaR95 = -€{var95:.0f}", (-var95, ymax * 0.9), fontsize=9, color=PALETTE[1], ha="right", xytext=(-4, 0), textcoords="offset points")
    ax.annotate(f"ES95 = -€{es95:.0f}", (-es95, ymax * 0.75), fontsize=9, color=PALETTE[1], ha="right", xytext=(-4, 0), textcoords="offset points")
    ax.annotate(f"media = €{pnl.mean():+.0f}", (pnl.mean(), ymax * 0.55), fontsize=9, ha="left", xytext=(4, 0), textcoords="offset points")
    ax.set_title(title)
    ax.set_xlabel("P&L (€)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)


if __name__ == "__main__":
    tufte_style()
    fig, ax = plt.subplots(figsize=(6, 4))
    rng = np.random.default_rng(1)
    pnl_distribution(ax, rng.normal(10, 120, 10000), 180.0, 230.0, "smoke test")
    fig.savefig("/tmp/viz_smoke.png", bbox_inches="tight")
    print("TEST OK — /tmp/viz_smoke.png")

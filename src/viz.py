"""Tufte chart style: max data-ink ratio, finding-as-title headlines, direct labels, zero junkchart."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PALETTE = ["#2E5266", "#C0392B", "#7A9E7E", "#8E6C8A", "#B8860B",
           "#5D6D7E", "#D4793C", "#4C8C8C", "#A3586E", "#6B7F3A"]
GOOD, BAD, NEUTRAL = "#7A9E7E", "#C0392B", "#9AA5AE"


def tufte_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.22, "grid.linewidth": 0.5,
        "axes.prop_cycle": plt.cycler(color=PALETTE),
        "font.size": 10, "axes.titlesize": 12,
        "legend.frameon": False, "figure.dpi": 130,
    })


def headline(ax: plt.Axes, finding: str, method: str = "") -> None:
    ax.set_title("")
    ax.text(0, 1.13, finding, transform=ax.transAxes, fontsize=12.5,
            fontweight="bold", va="bottom", ha="left")
    if method:
        ax.text(0, 1.055, method, transform=ax.transAxes, fontsize=9,
                color="#666666", va="bottom", ha="left")


def direct_label_lines(ax: plt.Axes, df: pd.DataFrame, fmt: dict[str, str] | None = None) -> None:
    ends = {c: float(df[c].dropna().iloc[-1]) for c in df.columns if df[c].notna().any()}
    order = sorted(ends, key=ends.get)
    y0, y1 = ax.get_ylim()
    min_gap = (y1 - y0) * 0.035
    placed: list[float] = []
    positions: dict[str, float] = {}
    for c in order:
        y = ends[c]
        if placed and y - placed[-1] < min_gap:
            y = placed[-1] + min_gap
        placed.append(y)
        positions[c] = y
    colors = {c: ax.lines[i].get_color() for i, c in enumerate(df.columns) if i < len(ax.lines)}
    for c in df.columns:
        if c not in positions:
            continue
        s = df[c].dropna()
        label = fmt[c] if fmt and c in fmt else c
        ax.annotate(label, (s.index[-1], positions[c]), xytext=(7, 0),
                    textcoords="offset points", va="center", fontsize=8.5,
                    color=colors.get(c, "#333333"), fontweight="bold",
                    annotation_clip=False)


def corr_heatmap(ax: plt.Axes, corr: pd.DataFrame, title: str,
                 highlight: tuple[str, str] | None = None) -> None:
    n = len(corr)
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(n), corr.columns, rotation=45, ha="right", fontsize=8.5)
    ax.set_yticks(range(n), corr.index, fontsize=8.5)
    for i in range(n):
        for j in range(n):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                    color="white" if abs(v) > 0.6 else "black")
    if highlight and highlight[0] in corr.index and highlight[1] in corr.columns:
        i, j = list(corr.index).index(highlight[0]), list(corr.columns).index(highlight[1])
        for a, b in {(i, j), (j, i)}:
            ax.add_patch(plt.Rectangle((b - 0.5, a - 0.5), 1, 1, fill=False,
                                       edgecolor="#111111", lw=2))
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(False)
    plt.colorbar(im, ax=ax, shrink=0.75)


def pnl_distribution(ax: plt.Axes, pnl: np.ndarray, var95: float, es95: float,
                     title: str = "", subtitle: str = "") -> None:
    n, b, patches = ax.hist(pnl, bins=120, edgecolor="none")
    for patch, edge in zip(patches, b[:-1]):
        patch.set_facecolor(BAD if edge < 0 else PALETTE[0])
        patch.set_alpha(0.55 if edge < 0 else 0.9)
    ax.axvline(0, color="black", lw=0.8)
    ymax = ax.get_ylim()[1]
    for x, lbl, ls, ytxt in [(-var95, f"VaR95  -€{var95:.0f}", "--", 0.92),
                             (-es95, f"ES95  -€{es95:.0f}", ":", 0.78)]:
        ax.axvline(x, color="#7a1f12", lw=1.2, ls=ls)
        ax.annotate(lbl, (x, ymax * ytxt), fontsize=8.5, color="#7a1f12",
                    ha="right", xytext=(-5, 0), textcoords="offset points")
    p50, p95 = np.percentile(pnl, [50, 95])
    ax.annotate(f"median €{p50:+.0f}", (p50, ymax * 0.55), fontsize=9, ha="left",
                xytext=(6, 0), textcoords="offset points")
    ax.annotate(f"P95 €{p95:+.0f}", (p95, ymax * 0.20), fontsize=8.5, color="#555555",
                ha="left", xytext=(4, 0), textcoords="offset points")
    if title:
        headline(ax, title, subtitle)
    ax.set_xlabel("P&L (€)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)


if __name__ == "__main__":
    tufte_style()
    rng = np.random.default_rng(1)
    fig, ax = plt.subplots(figsize=(7, 4))
    pnl_distribution(ax, rng.normal(10, 120, 10000), 180.0, 230.0,
                     "Smoke test finding", "method subtitle")
    df = pd.DataFrame(rng.normal(0, 1, (50, 3)).cumsum(0) + 100, columns=list("ABC"))
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    for c in df.columns:
        ax2.plot(df.index, df[c])
    direct_label_lines(ax2, df, fmt={"A": "A +12%"})
    fig.savefig("/tmp/viz_smoke.png", bbox_inches="tight")
    print("TEST OK — /tmp/viz_smoke.png")

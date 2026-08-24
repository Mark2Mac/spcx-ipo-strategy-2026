"""Generates assets/mc_paths_post_ipo.gif: the baseline Monte Carlo cone re-anchored to the REAL
$160.95 debut close, with the realized SPCX path revealed on top. Post-IPO layer — it does not
touch the frozen baseline gif (assets/mc_paths.gif)."""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.risk.montecarlo import McConfig  # noqa: E402
from src.viz import BAD, PALETTE, tufte_style  # noqa: E402
from tools.evidence import latest_checkpoint, realized_closes  # noqa: E402
from tools.make_gif import simulate_paths  # noqa: E402
from tools.score import day1_snapshot  # noqa: E402


def assert_fits(fig) -> None:
    """Refuse to write a figure whose text runs off the canvas.

    The defect this pins shipped for a month without anyone seeing an error: matplotlib does not
    wrap and does not warn — it draws the headline past the right edge and saves happily, so the
    only symptom is a title that ends mid-word in the committed asset. A chart is a deliverable;
    a deliverable that cannot be read is not one, and 'it rendered' is not the same as 'it fits'.

    Measured, not assumed: every Text artist is asked for its own drawn extent in display pixels
    and held against the canvas. Nothing here inspects the strings.
    """
    fig.canvas.draw()
    largh = fig.get_size_inches()[0] * fig.dpi
    fuori = []
    for t in fig.findobj(match=lambda o: isinstance(o, matplotlib.text.Text)):
        if not t.get_text().strip():
            continue
        bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
        if bb.x1 > largh + 0.5 or bb.x0 < -0.5:
            fuori.append((t.get_text()[:60], round(bb.x0), round(bb.x1)))
    if fuori:
        detail = "; ".join(f"{txt!r} spans {a}..{b}px of {round(largh)}" for txt, a, b in fuori)
        raise SystemExit(f"text runs off the canvas, refusing to save: {detail}")


def main() -> None:
    tufte_style()
    _, _, close_d1 = day1_snapshot(ROOT / "checkpoints")
    if close_d1 is None:
        raise SystemExit("no frozen day-1 close found; run a checkpoint first")

    cfg = replace(McConfig(n_paths=2000), spcx_s0=close_d1)
    paths = simulate_paths(cfg)
    show = paths[:: len(paths) // 60][:60]
    days = np.arange(paths.shape[1])
    p5, p50, p95 = (np.percentile(paths, q, axis=0) for q in (5, 50, 95))

    # Same committed evidence as make_mc_vs_realized.py — a live fetch here once let the gif
    # and the static chart show different values (bug 19).
    realized = realized_closes(latest_checkpoint(ROOT / "checkpoints"))
    rx = np.arange(len(realized))
    side = "above" if realized[-1] >= p50[len(realized) - 1] else "below"

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.set_xlim(0, days[-1])
    ax.set_ylim(min(paths.min(), realized.min()) * 0.95, max(np.percentile(paths, 99.5), realized.max() * 1.05))
    ax.axvline(cfg.event_day, color=PALETTE[1], lw=1, ls="--")
    ax.annotate("earnings +\ninsider unlock", (cfg.event_day, ax.get_ylim()[1] * 0.93),
                fontsize=9, ha="center", color=PALETTE[1])
    # THE HEADLINE RAN OFF THE CANVAS. Written as one line it measured wider than the 9in figure
    # and matplotlib does not wrap: every version shipped since 28/07/2026 ended mid-word, at
    # "anchored to the $160.95 de". The anchor belongs in the subtitle anyway — it is the setup,
    # not the finding — and the second line has room for it. Asserted below, so a longer title
    # cannot silently start clipping again.
    ax.text(0, 1.10, "Realized SPCX path vs the frozen-config Monte Carlo cone",
            transform=ax.transAxes, fontsize=11.5, fontweight="bold", va="bottom")
    ax.text(0, 1.04, f"anchored to the ${close_d1:.2f} debut close · {len(realized)} sessions in, "
                     f"the realized close sits {side} the median",
            transform=ax.transAxes, fontsize=9, color="#666666", va="bottom")
    ax.set_xlabel("sessions since debut"); ax.set_ylabel("$")

    lines = [ax.plot([], [], lw=0.5, color=PALETTE[0], alpha=0.22)[0] for _ in show]
    med, = ax.plot([], [], lw=2.0, color=PALETTE[1], ls="--")
    realized_ln, = ax.plot([], [], lw=2.4, color=BAD, marker="o", ms=4)
    band = [None]

    def update(frame: int):
        d = days[: frame + 1]
        for ln, p in zip(lines, show):
            ln.set_data(d, p[: frame + 1])
        med.set_data(d, p50[: frame + 1])
        if band[0] is not None:
            band[0].remove()
        band[0] = ax.fill_between(d, p5[: frame + 1], p95[: frame + 1], color=PALETTE[0], alpha=0.12)
        k = min(frame + 1, len(realized))
        realized_ln.set_data(rx[:k], realized[:k])
        return lines + [med, realized_ln]

    frames = list(range(2, paths.shape[1], 2))
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    assert_fits(fig)
    out = ROOT / "assets" / "mc_paths_post_ipo.gif"
    ani.save(out, writer=animation.PillowWriter(fps=12))
    print(f"saved {out} ({out.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()

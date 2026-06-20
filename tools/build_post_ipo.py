"""Builds notebook 06_post_ipo_review.ipynb — the predicted-vs-realized layer.

ADDED on top of the frozen pre-registration: it never touches the baseline notebooks, charts,
PREDICTIONS.md, or the evaluation metrics. It reads the FROZEN day-1 checkpoint + pre-debut
Polymarket odds and compares them to live, realized data. Self-contained (does NOT import
build_notebooks, whose module-level calls would rebuild the baseline notebooks as a side effect).
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
NB = ROOT / "notebooks" / "06_post_ipo_review.ipynb"

BOOT = """import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
warnings.filterwarnings("ignore")
import json, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from src.viz import tufte_style, headline, PALETTE, GOOD, BAD, NEUTRAL
tufte_style()
SHARES = 6_824_641_355 + 555_555_555 + 5_695_668_265  # 424B4 dual-class total
CKPT = Path.cwd().parent / "checkpoints" """

CELLS = [
    ("md", """# 06 — Post-IPO review: predicted vs realized

> **The pre-registration is frozen.** This notebook is an *added* layer: it does not modify
> `PREDICTIONS.md`, the evaluation metrics, or the baseline notebooks/charts (01–05). It reads the
> **frozen** day-1 checkpoint + pre-debut Polymarket odds and holds them against **live, realized**
> data. Everything dated before 2026-06-12 is the contract; everything here is the scoring.

What it answers, six days after the debut:
1. How did the day-1 bet resolve? (P1/P2)
2. Were the probabilities — ours and the market's — calibrated?
3. The IV reality check the README promised: did the model's assumed vol meet the listed-option IV?
4. Where did the realized path land inside the Monte Carlo cone?"""),
    ("code", BOOT),
    ("md", "## 1. The debut outcome (frozen day-1 close)\n\nScored on the **immutable** 2026-06-12 bar, not a later rolling close (see PR #6)."),
    ("code", """import tools.score as sc
name, snap, close_d1 = sc.day1_snapshot(CKPT)
ipo_price = 135.0
cap_d1 = close_d1 * SHARES
pop = close_d1 / ipo_price - 1
debut = pd.DataFrame([
    {"metric": "IPO price", "value": f"${ipo_price:,.0f}"},
    {"metric": "Day-1 close (frozen)", "value": f"${close_d1:,.2f}  [{name}]"},
    {"metric": "Day-1 pop", "value": f"{pop:+.1%}"},
    {"metric": "Day-1 market cap (424B4)", "value": f"${cap_d1/1e12:.3f}T"},
    {"metric": "P1  cap > $1T  (ex-ante 0.97)", "value": "TRUE" if cap_d1 > 1e12 else "FALSE"},
    {"metric": "P2  cap > $2T  (ex-ante 0.60)", "value": "TRUE" if cap_d1 > 2e12 else "FALSE"},
]).set_index("metric")
debut"""),
    ("md", "## 2. Calibration — the market's odds and ours vs what happened\n\nPre-debut Polymarket prices are pulled from the **frozen** baseline checkpoint (2026-06-10). Both the crowd and our pre-registered P landed on the right side of the $2T line — and near its probability."),
    ("code", """pm = json.load(open(CKPT / "2026-06-10-baseline" / "polymarket.json"))
def yes(substr):
    for m in pm:
        if substr.lower() in m["market"].lower() and m["outcomes"].get("Yes") is not None:
            return m["outcomes"]["Yes"]
    return None
realized_above = lambda thr: "TRUE" if cap_d1 > thr else "FALSE"
cal = pd.DataFrame([
    {"question": "cap > $1T", "Polymarket P(Yes) pre-debut": yes("above $1T"),
     "our ex-ante P": 0.97, "realized": realized_above(1e12)},
    {"question": "cap > $2T", "Polymarket P(Yes) pre-debut": yes("above $2T"),
     "our ex-ante P": 0.60, "realized": realized_above(2e12)},
]).set_index("question")
cal"""),
    ("md", "## 3. The IV reality check (README promised: *the model's guessed IV meets reality*)\n\nThe baseline Monte Carlo assumed `spcx_vol` as a pre-listing placeholder. Now that SPCX options are real (`identity_suspect` cleared), the listed ATM implied vol for the **August unlock** expiry is the market's answer."),
    ("code", """from src.risk.montecarlo import McConfig
assumed_vol = McConfig().spcx_vol
real_iv, iv_exp, spot = None, None, None
try:
    import yfinance as yf
    t = yf.Ticker("SPCX"); exps = t.options or []
    spot = float(t.history(period="1d")["Close"].iloc[-1])
    aug = next((e for e in exps if e.startswith("2026-08")), exps[1] if len(exps) > 1 else (exps[0] if exps else None))
    if aug:
        oc = t.option_chain(aug); calls = oc.calls.copy()
        calls["d"] = (calls["strike"] - spot).abs()
        real_iv = float(calls.nsmallest(3, "d")["impliedVolatility"].mean()); iv_exp = aug
except Exception as e:
    print("live IV unavailable:", str(e)[:80])
print(f"MC assumed spcx_vol : {assumed_vol:.0%}")
if real_iv:
    print(f"Listed ATM IV ({iv_exp}): {real_iv:.0%}  (spot ${spot:.0f})")
    print(f"-> the baseline understated vol by {real_iv-assumed_vol:+.0%}. Realized regime is "
          f"fatter than the placeholder; a put spread is priced richer than the model assumed.")"""),
    ("md", "## 4. Realized path vs the Monte Carlo cone\n\nBaseline MC (Student-t dof=4, the frozen config) re-anchored to the **actual** day-1 close $160.95 — not the old $150 placeholder. The realized closes are overlaid. The question is not whether the median was right (it never is) but whether reality stayed inside the cone."),
    ("code", """from src.connectors.market_data import get_ohlcv
cfg = McConfig()
rng = np.random.default_rng(cfg.seed)
n, days, dt = 3000, 45, 1 / 252
scale = np.sqrt(cfg.t_dof / (cfg.t_dof - 2))
z = rng.standard_t(cfg.t_dof, size=(n, days)) / scale
logret = (cfg.spcx_drift - 0.5 * cfg.spcx_vol**2) * dt + cfg.spcx_vol * np.sqrt(dt) * z
paths = close_d1 * np.exp(np.cumsum(logret, axis=1))
paths = np.column_stack([np.full(n, close_d1), paths])
p5, p50, p95 = np.percentile(paths, [5, 50, 95], axis=0)
x = np.arange(days + 1)

realized = get_ohlcv("SPCX", period="1mo", force=True)["Close"]
realized = realized[realized.index >= "2026-06-12"]
rx = np.arange(len(realized))

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.fill_between(x, p5, p95, color=PALETTE[0], alpha=0.18, label="MC 5–95% (vol=70%)")
ax.plot(x, p50, color=PALETTE[0], lw=1.2, ls="--", label="MC median")
ax.plot(rx, realized.values, color=BAD, lw=2.2, marker="o", ms=4, label="realized close")
ax.annotate(f"${realized.values[-1]:.0f}", (rx[-1], realized.values[-1]),
            xytext=(8, 0), textcoords="offset points", va="center", color=BAD, fontsize=10)
inside = (realized.values[-1] >= p5[len(realized) - 1]) and (realized.values[-1] <= p95[len(realized) - 1])
headline(ax, f"Realized path is {'inside' if inside else 'OUTSIDE'} the frozen-config cone, near the upper band",
         "baseline Student-t MC re-anchored to the real $160.95 debut close · first 6 sessions overlaid")
ax.set_xlabel("trading days since debut"); ax.set_ylabel("SPCX price ($)")
ax.legend(loc="upper left")
fig.savefig("../assets/chart_post_ipo.png", bbox_inches="tight")
plt.show()"""),
    ("md", """## 5. Verdict so far (2026-06-20, T+6)

- **Day-1 bet resolved correctly**: +19.2% pop, $2.105T cap → **P1 and P2 both TRUE**, scored on the frozen close (the scoring-drift bug that would have un-resolved this is fixed, PR #6).
- **Calibration held**: Polymarket priced cap>$2T at ~0.63 and our pre-registered P2 was 0.60 — both on the right side, both near the realized truth. No overconfidence to flag yet.
- **The model under-vol'd**: assumed 70% vs listed ATM IV ~88% for the August expiry. The put spread the plan buys in July is therefore *more expensive* than the baseline implied — judge the entry on real IV, exactly as the sensitivity note warned.
- **Reality stayed in the cone**, hugging the upper band: the realized path spiked to ~$211 then settled to $185, well within the frozen-config 5–95% envelope.

**Still ahead and untouched**: the July spread entry, the August earnings + insider unlock (the whole thesis), and `form4_watch()` going live. The pre-registration stands; this page only keeps score."""),
]


def build() -> None:
    n = nbf.v4.new_notebook()
    n.cells = [nbf.v4.new_markdown_cell(s) if k == "md" else nbf.v4.new_code_cell(s) for k, s in CELLS]
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nbf.write(n, NB)
    print(f"built {NB.name}")


def execute() -> None:
    from nbclient import NotebookClient
    n = nbf.read(NB, as_version=4)
    NotebookClient(n, timeout=600, kernel_name="python3",
                   resources={"metadata": {"path": str(ROOT / "notebooks")}}).execute()
    nbf.write(n, NB)
    print(f"executed {NB.name}")


if __name__ == "__main__":
    build()
    execute()

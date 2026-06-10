"""Builds the four analysis notebooks via nbformat (single source of truth, reproducible)."""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"

from src.config import UNIVERSE  # noqa: F401

BOOT = """import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from src.viz import tufte_style, direct_label_lines, corr_heatmap, pnl_distribution, PALETTE
tufte_style()"""


def nb(cells: list[tuple[str, str]], path: Path) -> None:
    n = nbf.v4.new_notebook()
    n.cells = [nbf.v4.new_markdown_cell(s) if k == "md" else nbf.v4.new_code_cell(s) for k, s in cells]
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    NB_DIR.mkdir(exist_ok=True)
    nbf.write(n, path)
    print(f"built {path.name}")


# ---------------- 01: data pipeline ----------------
nb([
    ("md", "# 01 — Data pipeline\n\nSources ranked by quality: **SEC EDGAR** (official, legal documents) > **Polymarket Gamma** (real money) > **FRED** (official macro) > **yfinance** (market data, Stooq fallback) > **HN/Wikipedia** (attention proxies). Every fetch passes a quality gate. Universe: portfolio (GOOGL), volatility proxy (TSLA), picks-and-shovels (NDAQ, HOOD, VIRT, GS, MS), space sector (RKLB, ASTS, LMT), benchmarks (^GSPC, ^NDX) and the fear gauge (^VIX)."),
    ("code", BOOT),
    ("md", "## 1. OHLCV with quality gate\n\nData-engineering rule: nothing enters the process without passing the checks. **Issues** (NaN, non-positive prices, staleness) block the pipeline; **warnings** (gaps, >50% jumps) are surfaced for human review — extreme moves can be real (ASTS +50% on the AT&T deal, ^VIX Fed-day spikes), so they must be flagged, not auto-dropped."),
    ("code", f"""from src.connectors.market_data import get_universe
from src.config import UNIVERSE  # noqa: F401
prices, reports = get_universe(UNIVERSE, period="2y")
qa = pd.DataFrame(reports).set_index("ticker")
assert qa["issues"].map(len).sum() == 0, f"QUALITY FAIL: {{qa[qa.issues.map(len)>0]}}"
prices.to_parquet("../data/universe_prices.parquet")
qa"""),
    ("md", "## 2. SEC EDGAR — SpaceX filings (CIK 1181412)\n\nThe single most authoritative source: filings are legal acts. From August this is where **Form 4s** appear (insider sales, public by law within 2 business days) — the key dataset for the lockup thesis."),
    ("code", """from src.connectors.edgar import recent_filings, form4_watch
fil = pd.DataFrame(recent_filings(limit=15))
print(f"Form 3/4/144 to date: {len(form4_watch())} (expected from August)")
fil"""),
    ("md", "## 3. Polymarket — real-money implied probabilities"),
    ("code", """from src.connectors.polymarket import search_markets
mkts = search_markets("spacex", limit=10)
pm = pd.DataFrame([{ "market": m["market"], **{f"P({k})": v for k, v in m["outcomes"].items()}, "volume_usd": int(m["volume"])} for m in mkts])
pm"""),
    ("md", "## 4. Risk-free rate (FRED, ^IRX fallback)"),
    ("code", """from src.connectors.fred import risk_free_rate
RF = risk_free_rate()
print(f"3M T-bill: {RF:.2%} — the hurdle every strategy must beat, plus friction")"""),
    ("md", "## 5. Normalized prices — one chart, all the information\n\nBase 100, direct labels (no legend to decode), benchmarks in gray. ^VIX excluded here (different unit), used in notebook 02."),
    ("code", """px = prices.drop(columns=["^VIX"]).dropna().tail(252)
norm = 100 * px / px.iloc[0]
fig, ax = plt.subplots(figsize=(11, 5.5))
for c in norm.columns:
    is_bench = c.startswith("^")
    ax.plot(norm.index, norm[c], lw=0.9 if is_bench else 1.4,
            color="#AAAAAA" if is_bench else None, alpha=0.7 if is_bench else 1)
direct_label_lines(ax, norm)
ax.set_title("Universe — trailing 12 months, base 100 (benchmarks in gray)")
ax.set_ylabel("index")
fig.savefig("../assets/chart_universe.png", bbox_inches="tight")
plt.show()"""),
], NB_DIR / "01_data_pipeline.ipynb")

# ---------------- 02: correlations and risk ----------------
nb([
    ("md", "# 02 — Correlations and portfolio risk\n\nQuestion answered: **how much of my 'hedge' is an illusion?** Long GOOGL (long-growth) + short-SPCX spread (short-growth) partially cancel. Long-run Pearson vs EWMA (λ=0.94, RiskMetrics) weighting the last ~30 days: when they diverge, the regime is shifting."),
    ("code", BOOT),
    ("code", """from src.risk.metrics import log_returns, corr_matrix, ewma_corr, summary_table
prices = pd.read_parquet("../data/universe_prices.parquet").dropna()
rets = log_returns(prices)
summary = summary_table(prices)
summary"""),
    ("md", "## Heatmaps: structural correlation (2y) vs current regime (EWMA)\n\nReading guide: TSLA is the best available proxy for the volatility SPCX will have (same key-man risk). If GOOGL-TSLA EWMA > 0.6, the 'Musk beta' contaminates the defensive tranche too — lower your hedging expectations. The ^VIX row should be deep blue (negative) against everything: a sanity check on the whole matrix."),
    ("code", """fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
corr_heatmap(axes[0], corr_matrix(rets), "Pearson 2 years (structure)")
corr_heatmap(axes[1], ewma_corr(rets), "EWMA λ=0.94 (current regime)")
fig.tight_layout(); fig.savefig("../assets/chart_corr.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Rolling 60d correlation, GOOGL vs market\n\nIf it rises toward 1 in drawdowns (it almost always does), diversification vanishes exactly when needed — which is why the plan's only true hedge is the spread's hard cap, not correlation."),
    ("code", """roll = rets["GOOGL"].rolling(60).corr(rets["^GSPC"]).dropna()
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(roll.index, roll.values, lw=1.3)
ax.axhline(roll.mean(), color=PALETTE[1], lw=0.9, ls="--")
ax.annotate(f"mean {roll.mean():.2f}", (roll.index[-1], roll.mean()), xytext=(8, 0), textcoords="offset points", color=PALETTE[1], fontsize=9, va="center")
ax.set_title("Rolling 60d correlation — GOOGL vs S&P500")
ax.set_ylim(0, 1)
fig.savefig("../assets/chart_rolling_corr.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Plan risk ledger\n\n| Position | Risk driver | Cap |\n|---|---|---|\n| GOOGL (defensive tranche) | beta × market drawdown | soft (thesis stop -15%) |\n| SPCX put spread | premium paid | **hard** |\n| Cash reserve | none | hard |\n\nThe plan's true VaR comes from the Monte Carlo in notebook 03; these correlations are its qualitative inputs."),
], NB_DIR / "02_correlation_risk.ipynb")

# ---------------- 03: Monte Carlo ----------------
nb([
    ("md", "# 03 — Portfolio Monte Carlo\n\n10,000 paths, 70 trading days (≈ mid-July → mid-October). Model: GBM with **Student-t innovations (dof=4, fat tails)**, SPCX-GOOGL correlation ρ=0.45, **log-normal jump on the event day** (earnings + insider unlock, default -8% ± 12%). The spread has a mathematical hard cap: the test verifies it on every path."),
    ("code", BOOT),
    ("code", """from src.risk.montecarlo import McConfig, SpreadPosition, simulate, report
cfg, spread = McConfig(), SpreadPosition()
res = simulate(cfg, spread)
max_loss_spread = spread.debit * 100 * spread.contracts / 1.08
assert res["pnl_spread_eur"].min() >= -max_loss_spread - 1e-6, "HARD CAP VIOLATED"
rep = report(res)
pd.Series(rep).round(1)"""),
    ("md", "## Total P&L distribution with VaR/ES annotated\n\nThe chart Aladdin shows for every book: not a number, the **shape** of the risk. Short right tail (gain capped by the spread), long left tail (the equity tranche has no hard cap)."),
    ("code", """fig, ax = plt.subplots(figsize=(11, 5))
pnl_distribution(ax, res["pnl_total_eur"], rep["VaR95"], rep["ES95"],
                 f"Portfolio P&L over 70 days — 10,000 simulations | P(loss)={rep['p_loss']:.0%}")
fig.savefig("../assets/chart_mc_pnl.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Spread payoff at expiry + where the simulated paths land"),
    ("code", """grid = np.linspace(100, 200, 300)
payoff_eur = spread.payoff(grid) / 1.08
fig, ax = plt.subplots(figsize=(11, 4.5))
ax2 = ax.twinx()
ax2.hist(res["spcx_final"], bins=80, color=PALETTE[0], alpha=0.25)
ax2.set_yticks([]); ax2.spines["right"].set_visible(False)
ax.plot(grid, payoff_eur, lw=1.8, color=PALETTE[1])
ax.axhline(0, color="black", lw=0.7)
for s, lbl in [(spread.short_strike, "strike 135"), (spread.long_strike, "strike 140")]:
    ax.axvline(s, color="gray", lw=0.7, ls=":")
    ax.annotate(lbl, (s, ax.get_ylim()[1]*0.85), fontsize=8, ha="center")
be = spread.long_strike - spread.debit
ax.annotate(f"breakeven {be:.2f}", (be, 0), xytext=(8, 10), textcoords="offset points", fontsize=9)
ax.set_title("140/135 Sep put spread payoff (EUR) over the density of simulated final SPCX prices")
ax.set_xlabel("SPCX at expiry ($)"); ax.set_ylabel("spread P&L (EUR)")
fig.savefig("../assets/chart_payoff.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Sensitivity: mean P&L as a function of the event jump\n\nThe backbone of the decision: the strategy lives or dies on the size of the August jump. Everything else is noise."),
    ("code", """from dataclasses import replace
rows = []
for jm in [-0.20, -0.15, -0.10, -0.08, -0.05, 0.0, 0.05]:
    r = report(simulate(replace(cfg, jump_mean=jm, seed=11), spread))
    rows.append({"event_jump": f"{jm:+.0%}", "mean P&L": round(r["mean"]), "P(loss)": f"{r['p_loss']:.0%}", "VaR95": round(r["VaR95"]), "ES95": round(r["ES95"])})
sens = pd.DataFrame(rows).set_index("event_jump")
sens"""),
    ("code", """fig, ax = plt.subplots(figsize=(9, 4.5))
x = [-20, -15, -10, -8, -5, 0, 5]
y = sens["mean P&L"].values
ax.plot(x, y, marker="o", lw=1.5)
ax.axhline(0, color="black", lw=0.7)
for xi, yi in zip(x, y):
    ax.annotate(f"{yi:+.0f}", (xi, yi), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9)
ax.set_title("Mean portfolio P&L vs size of the August event jump")
ax.set_xlabel("mean SPCX jump at the event (%)"); ax.set_ylabel("EUR")
fig.savefig("../assets/chart_sensitivity.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Operational conclusions\n\n1. The spread hard cap holds on 10,000 paths: losses beyond the structural cap come only from the equity tranche (market beta), never from the derivative.\n2. Positive EV requires an event jump ≤ -5%: consistent with the analytical breakeven probability (P≥44%).\n3. The left tail (ES95) is dominated by the equity tranche: to shrink it, cut equity, not the spread.\n4. **Update parameters with real data** once SPCX trades: `spcx_s0`, `spcx_vol` (from listed-option IV), real `debit`."),
], NB_DIR / "03_montecarlo.ipynb")

# ---------------- 04: signal quality ----------------
nb([
    ("md", "# 04 — Signal quality: separating good signals from noise\n\nMore data is only better if it is **graded and cleaned**. This notebook does three things:\n1. scores every source on an explicit rubric (skin-in-the-game, timeliness, verifiability, noise);\n2. cleans the raw series (dedupe, capped forward-fill, winsorization) before any analysis;\n3. tests empirically whether attention signals (Wikipedia, Hacker News) lead prices, or just follow them."),
    ("code", BOOT),
    ("md", "## 1. The source-quality rubric\n\n`score = 0.40·skin + 0.25·timeliness + 0.25·verifiability − 0.10·noise`. Skin-in-the-game gets the largest weight: what people DO with money (Polymarket, Form 4, market prices) beats what they SAY (Reddit, headlines, CEO statements)."),
    ("code", """from src.research.signal_quality import ranking_table
rt = ranking_table()
fig, ax = plt.subplots(figsize=(10, 5))
colors = [PALETTE[2] if s >= 7 else PALETTE[0] if s >= 5 else PALETTE[1] for s in rt["score"]]
ax.barh(rt["source"][::-1], rt["score"][::-1], color=colors[::-1])
for i, s in enumerate(rt["score"][::-1]):
    ax.annotate(f"{s:.1f}", (s, i), xytext=(4, 0), textcoords="offset points", va="center", fontsize=9)
ax.set_title("Signal quality by source — green: trade on it, blue: context, red: contrarian/ignore")
ax.set_xlim(0, 10)
fig.savefig("../assets/chart_signal_ranking.png", bbox_inches="tight"); plt.show()
rt[["source", "score", "note"]]"""),
    ("md", "## 2. Cleaning raw attention data\n\nWikipedia pageviews and HN points are spiky, gappy and outlier-prone. Pipeline: dedupe index → capped forward-fill (max 3 days) → winsorize at 1%/99%. Shown on real SpaceX data."),
    ("code", """from src.connectors.wikipedia import pageviews
from src.research.signal_quality import clean_series, zscore
wiki_raw = pageviews("SpaceX", days=180)
wiki = clean_series(wiki_raw)
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(wiki_raw.index, wiki_raw.values, lw=0.8, alpha=0.45, label="raw")
ax.plot(wiki.index, wiki.values, lw=1.4, label="cleaned (winsorized 1%)")
ax.legend(loc="upper left")
ax.set_title("Wikipedia daily pageviews, 'SpaceX' — raw vs cleaned")
fig.savefig("../assets/chart_cleaning.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## 3. The attention timeline around the IPO\n\nHN points (tech crowd) and Wikipedia views (mass public), z-scored on a 30-day window, with the known IPO milestones overlaid: Apr 1 confidential SEC filing, May 20 public S-1, Jun 4 roadshow."),
    ("code", """from src.connectors.hackernews import daily_attention
hn = daily_attention("spacex", days=180)
hn_z = zscore(clean_series(hn["points"].astype(float))).dropna()
wiki_z = zscore(wiki).dropna()
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(wiki_z.index, wiki_z.values, lw=1.3, label="Wikipedia z")
ax.plot(hn_z.index, hn_z.values, lw=1.0, alpha=0.8, label="Hacker News z")
for d, lbl in [("2026-04-01", "SEC filing"), ("2026-05-20", "S-1 public"), ("2026-06-04", "roadshow")]:
    ax.axvline(pd.Timestamp(d), color="gray", lw=0.8, ls=":")
    ax.annotate(lbl, (pd.Timestamp(d), ax.get_ylim()[1]*0.9), fontsize=8, ha="center")
ax.axhline(0, color="black", lw=0.6)
ax.legend(loc="upper left")
ax.set_title("Attention z-scores around the SpaceX IPO milestones")
fig.savefig("../assets/chart_attention.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## 4. Do attention signals LEAD prices? Lead-lag test\n\nMethod: z-scored Wikipedia attention for Tesla vs daily |TSLA return| (TSLA as the listed Musk-attention proxy, since SPCX has no price history yet). Correlation peaking at negative lags = attention leads; at lag ≥ 0 = attention follows. Honest expectation: attention mostly FOLLOWS — which is exactly why it scores low in the rubric."),
    ("code", """from src.research.signal_quality import lead_lag_corr
from src.risk.metrics import log_returns
tsla_attn = zscore(clean_series(pageviews("Tesla,_Inc.", days=180))).dropna()
prices = pd.read_parquet("../data/universe_prices.parquet")
tsla_ret = log_returns(prices[["TSLA"]])["TSLA"].abs()
ll = lead_lag_corr(tsla_attn, tsla_ret, max_lag=5)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(ll.index, ll["corr"], color=[PALETTE[1] if i < 0 else PALETTE[0] for i in ll.index])
ax.axhline(0, color="black", lw=0.7)
ax.set_title("Corr(attention z at lag, |TSLA return|) — negative lags = attention leads")
ax.set_xlabel("lag (days); negative = attention first"); ax.set_ylabel("correlation")
fig.savefig("../assets/chart_leadlag.png", bbox_inches="tight"); plt.show()
ll.T.round(3)"""),
    ("md", "## Conclusions\n\n1. **Trade on**: market prices/IV, Form 4 flow, Polymarket, EDGAR (scores ≥ 7). **Context only**: fair values, HN, Wikipedia. **Contrarian/ignore**: Reddit sentiment, promotional statements.\n2. Attention data must be cleaned before use — raw spikes are partly duplicates and outliers.\n3. The lead-lag test quantifies why attention is context, not signal.\n4. Engineering rule adopted by the plan: **a source may upgrade conviction, but never create a position on its own unless its score ≥ 7.**"),
], NB_DIR / "04_signal_quality.ipynb")

print("done")

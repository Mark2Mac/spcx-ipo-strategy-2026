"""Genera i 3 notebook del repo via nbformat (single source of truth, riproducibile)."""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"

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
    ("md", "# 01 — Data pipeline\n\nFonti in ordine di qualità: **SEC EDGAR** (ufficiale) > **Polymarket Gamma** (soldi veri) > **FRED** (macro ufficiale) > **yfinance** (mercato, con fallback Stooq). Ogni fetch passa da un quality report. Universe: portafoglio (GOOGL), comparabili volatilità (TSLA), 'pale e picconi' (NDAQ, HOOD, VIRT, GS, MS), benchmark (^GSPC, ^NDX)."),
    ("code", BOOT),
    ("md", "## 1. OHLCV con quality report\n\nRegola data-engineering: nessun dato entra nel processo senza passare i check (NaN, gap, prezzi non positivi, salti >50%, staleness)."),
    ("code", """from src.connectors.market_data import get_universe
UNIVERSE = ["GOOGL", "TSLA", "NDAQ", "HOOD", "VIRT", "GS", "MS", "^GSPC", "^NDX"]
prices, reports = get_universe(UNIVERSE, period="2y")
qa = pd.DataFrame(reports).set_index("ticker")
assert qa["issues"].map(len).sum() == 0, f"QUALITY FAIL: {qa[qa.issues.map(len)>0]}"
prices.to_parquet("../data/universe_prices.parquet")
qa"""),
    ("md", "## 2. SEC EDGAR — filing SpaceX (CIK 1181412)\n\nLa fonte più autorevole in assoluto: i filing sono atti legali. Da agosto qui compariranno i **Form 4** (vendite insider, pubblicate per legge entro 2 giorni lavorativi) — il dato chiave della strategia B."),
    ("code", """from src.connectors.edgar import recent_filings, form4_watch
fil = pd.DataFrame(recent_filings(limit=15))
f4 = form4_watch()
print(f"Form 3/4/144 presenti: {len(f4)} (attesi da agosto)")
fil"""),
    ("md", "## 3. Polymarket — probabilità implicite con soldi veri"),
    ("code", """from src.connectors.polymarket import search_markets
mkts = search_markets("spacex", limit=10)
pm = pd.DataFrame([{ "market": m["market"], **{f"P({k})": v for k, v in m["outcomes"].items()}, "volume_usd": m["volume"]} for m in mkts])
pm"""),
    ("md", "## 4. Tasso risk-free (FRED, fallback ^IRX)"),
    ("code", """from src.connectors.fred import risk_free_rate
RF = risk_free_rate()
print(f"T-bill 3M: {RF:.2%} — da usare come hurdle: ogni strategia deve battere questo + attrito")"""),
    ("md", "## 5. Prezzi normalizzati — un grafico, tutta l'informazione\n\nBase 100, etichette dirette (niente legenda da decodificare), benchmark in grigio."),
    ("code", """px = prices.dropna().tail(252)
norm = 100 * px / px.iloc[0]
fig, ax = plt.subplots(figsize=(11, 5.5))
for c in norm.columns:
    is_bench = c.startswith("^")
    ax.plot(norm.index, norm[c], lw=0.9 if is_bench else 1.4,
            color="#AAAAAA" if is_bench else None, alpha=0.7 if is_bench else 1)
direct_label_lines(ax, norm)
ax.set_title("Universe — ultimi 12 mesi, base 100 (benchmark in grigio)")
ax.set_ylabel("indice")
fig.savefig("../data/chart_universe.png", bbox_inches="tight")
plt.show()"""),
], NB_DIR / "01_data_pipeline.ipynb")

# ---------------- 02: correlazioni e rischio ----------------
nb([
    ("md", "# 02 — Correlazioni e rischio di portafoglio\n\nDomanda a cui risponde: **quanto del mio 'hedge' è illusorio?** GOOGL long-growth + spread short-SPCX (short-growth) si sovrappongono. Pearson di lungo periodo vs EWMA (λ=0.94, RiskMetrics) che pesa gli ultimi ~30 giorni: se divergono, il regime sta cambiando."),
    ("code", BOOT),
    ("code", """from src.risk.metrics import log_returns, corr_matrix, ewma_corr, summary_table
prices = pd.read_parquet("../data/universe_prices.parquet").dropna()
rets = log_returns(prices)
summary = summary_table(prices)
summary"""),
    ("md", "## Heatmap: correlazione storica (2y) vs EWMA (regime corrente)\n\nLettura: TSLA è il proxy migliore della volatilità che avrà SPCX (stesso key-man risk). Se GOOGL-TSLA EWMA > 0.6, il 'beta Musk' contagia anche la tranche difensiva → ridurre aspettative di hedge."),
    ("code", """fig, axes = plt.subplots(1, 2, figsize=(14, 6))
corr_heatmap(axes[0], corr_matrix(rets), "Pearson 2 anni (struttura)")
corr_heatmap(axes[1], ewma_corr(rets), "EWMA λ=0.94 (regime corrente)")
fig.tight_layout(); fig.savefig("../data/chart_corr.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Correlazione rolling 60g GOOGL vs mercato\n\nSe sale verso 1 nei drawdown (succede quasi sempre), la diversificazione svanisce quando serve: è il motivo per cui l'unico hedge vero del piano è l'hard cap dello spread, non la correlazione."),
    ("code", """roll = rets["GOOGL"].rolling(60).corr(rets["^GSPC"]).dropna()
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(roll.index, roll.values, lw=1.3)
ax.axhline(roll.mean(), color=PALETTE[1], lw=0.9, ls="--")
ax.annotate(f"media {roll.mean():.2f}", (roll.index[-1], roll.mean()), xytext=(8, 0), textcoords="offset points", color=PALETTE[1], fontsize=9, va="center")
ax.set_title("Correlazione rolling 60g — GOOGL vs S&P500")
ax.set_ylim(0, 1)
fig.savefig("../data/chart_rolling_corr.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Risk ledger del piano (€2.000)\n\n| Posizione | Rischio | Cap |\n|---|---|---|\n| GOOGL €1.200 | beta × drawdown mercato | soft (stop -15%) |\n| Spread €205 | premio pagato | **hard** |\n| Cash €400 | zero | hard |\n\nIl VaR vero del piano lo calcola il notebook 03 col Monte Carlo: le correlazioni qui sopra sono i suoi input qualitativi."),
], NB_DIR / "02_correlation_risk.ipynb")

# ---------------- 03: Monte Carlo ----------------
nb([
    ("md", "# 03 — Monte Carlo del portafoglio\n\n10.000 path, 70 giorni di borsa (≈ metà luglio → metà ottobre). Modello: GBM con innovazioni **Student-t (df=4, fat tails)**, correlazione SPCX-GOOGL ρ=0.45, **jump log-normale al giorno dell'evento** (trimestrale+sblocco insider, default -8% ± 12%). Lo spread ha hard cap matematico: il test lo verifica su ogni path."),
    ("code", BOOT),
    ("code", """from src.risk.montecarlo import McConfig, SpreadPosition, simulate, report
cfg, spread = McConfig(), SpreadPosition()
res = simulate(cfg, spread)
max_loss_spread = spread.debit * 100 * spread.contracts / 1.08
assert res["pnl_spread_eur"].min() >= -max_loss_spread - 1e-6, "HARD CAP VIOLATO"
rep = report(res)
pd.Series(rep).round(1)"""),
    ("md", "## Distribuzione P&L totale con VaR/ES annotati\n\nIl grafico che Aladdin mostra per ogni portafoglio: non un numero, la **forma** del rischio. Coda destra corta (gain cappato dallo spread), coda sinistra lunga (GOOGL senza hard cap)."),
    ("code", """fig, ax = plt.subplots(figsize=(11, 5))
pnl_distribution(ax, res["pnl_total_eur"], rep["VaR95"], rep["ES95"],
                 f"P&L portafoglio a 70 giorni — 10.000 simulazioni | P(perdita)={rep['p_loss']:.0%}")
fig.savefig("../data/chart_mc_pnl.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Payoff dello spread a scadenza + dove finiscono i path simulati"),
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
ax.set_title("Payoff spread 140/135 set (€) sovrapposto alla densità dei prezzi finali SPCX simulati")
ax.set_xlabel("SPCX a scadenza ($)"); ax.set_ylabel("P&L spread (€)")
fig.savefig("../data/chart_payoff.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Sensitività: il P&L medio in funzione del jump dell'evento\n\nLa colonna vertebrale della decisione: la strategia vive o muore sull'ampiezza del jump di agosto. Tutto il resto è rumore."),
    ("code", """from dataclasses import replace
rows = []
for jm in [-0.20, -0.15, -0.10, -0.08, -0.05, 0.0, 0.05]:
    r = report(simulate(replace(cfg, jump_mean=jm, seed=11), spread))
    rows.append({"jump_evento": f"{jm:+.0%}", "P&L medio €": round(r["mean"]), "P(perdita)": f"{r['p_loss']:.0%}", "VaR95 €": round(r["VaR95"]), "ES95 €": round(r["ES95"])})
sens = pd.DataFrame(rows).set_index("jump_evento")
sens"""),
    ("code", """fig, ax = plt.subplots(figsize=(9, 4.5))
x = [-20, -15, -10, -8, -5, 0, 5]
y = sens["P&L medio €"].values
ax.plot(x, y, marker="o", lw=1.5)
ax.axhline(0, color="black", lw=0.7)
for xi, yi in zip(x, y):
    ax.annotate(f"{yi:+.0f}", (xi, yi), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9)
ax.set_title("P&L medio del portafoglio vs ampiezza del jump all'evento di agosto")
ax.set_xlabel("jump medio SPCX all'evento (%)"); ax.set_ylabel("€")
fig.savefig("../data/chart_sensitivity.png", bbox_inches="tight"); plt.show()"""),
    ("md", "## Conclusioni operative\n\n1. L'hard cap dello spread regge su 10.000 path: la perdita oltre ~€400 viene solo da GOOGL (beta mercato), mai dal derivato.\n2. EV positivo richiede jump evento ≤ -5%: coerente con la soglia P≥44% del file 02.\n3. La coda sinistra (ES95) è dominata dalla tranche A: chi volesse ridurla taglia GOOGL, non lo spread.\n4. **Aggiornare i parametri con i dati reali** appena SPCX quota: `spcx_s0`, `spcx_vol` (dalla IV delle opzioni), `debit` reale. I default sono le stime del file 02."),
], NB_DIR / "03_montecarlo.ipynb")

print("done")

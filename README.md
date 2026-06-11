<div align="center">

<img src="assets/spacex-logo.png" alt="SpaceX" width="420"/>

# One retail investor, a small account, and an AI<br>vs the largest IPO in history

**A documented, falsifiable experiment**: can a frontier model (Fable 5, Anthropic) close the
information and competence gap between a small retail investor and institutional players?
Test bench: the SpaceX IPO of June 12, 2026 — a $1.75T valuation, 94x revenue, and the most
unusual insider lockup ever filed.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Fable 5](https://img.shields.io/badge/AI-Fable%205%20·%20Anthropic-D4A27F)
![Data](https://img.shields.io/badge/data-SEC%20EDGAR%20·%20Polymarket%20·%20FRED%20·%20yfinance%20·%20HN%20·%20Wikipedia-555)
![Status](https://img.shields.io/badge/status-experiment%20running-FFBE00)

<img src="assets/mc_paths.gif" alt="SPCX Monte Carlo" width="640"/><br>
<sub><b>2,000 Monte Carlo paths</b> — Student-t innovations (empirically validated fat tails) + jump on the earnings/insider-unlock event</sub>

</div>

---

## The story so far

Two days before the largest IPO in human history, a retail investor with a small account
asked an AI a simple question: *is this a once-in-a-generation opportunity, or the most
elaborate exit liquidity event ever staged?*

The honest answer turned out to be neither — and getting there took an evening of actual
work. Analysts call SpaceX 55% overvalued (Morningstar). Reddit calls it "the theft of the
century". Polymarket prices the day-1 pop at 60%. And the S-1 contains a lockup clause
nobody has seen before: insiders free to sell 20% of their stock **two days after the first
earnings report**, instead of the usual six months.

A retail investor normally walks into this with FOMO and a brokerage app. This repo walks
in with what an institutional desk would bring instead: multi-source research, valuation
work, defined-risk strategies, a Monte Carlo validated against real return distributions,
an event study on every comparable lockup since 2012, signal-quality engineering, tax math —
and a **ledger of falsifiable predictions, written and frozen before the debut**.

In a few months everything gets reopened and scored. [**PREDICTIONS.md**](PREDICTIONS.md)
is the contract with the future; git history is the notary.

## Follow along — the experiment in real time

| | Date | Milestone | Evidence frozen |
|---|---|---|---|
| ✅ | Jun 10, 2026 | Research, plan, predictions — all pre-registered | `checkpoints/2026-06-10-baseline` |
| ⏳ | Jun 12 | **The debut** — P1 and P2 resolve on day one | checkpoint `day1` |
| ⏳ | ~Jun 24 | SPCX options list: the model's guessed IV meets reality | checkpoint `options-listed` |
| ⏳ | Jul 6-17 | Spread entry window — or its written fallbacks | checkpoint `entry-window` |
| ⏳ | ~Aug | First earnings + the insider unlock (the whole thesis) | checkpoints `earnings-T`, `unlock-T7` |
| ⏳ | ~Oct 25 | Day 135: lockup fully open, first "true" price | checkpoint `day135` |
| ⏳ | Dec 31 | Final scoring — every prediction gets its Outcome | checkpoint `final`, then `VERDICT.md` |

<sub>The record keeps itself: a GitHub Action snapshots every data source twice a week
(Polymarket odds, SPCX option chains with IV, prices, filings — the things that cannot be
reconstructed later), with no local machine involved. Milestone labels are fired manually
from the Actions tab.</sub>

## The numbers on June 10, 2026 (T-2 to the debut)

| | |
|---|---|
| IPO pricing | $135/share · $1.75T valuation · $75B raise (all-time record) |
| Morningstar fair value | $780B (**-55%** from IPO price) · 94x revenue vs Nvidia's ~22x |
| The structural flaw | xAI burns >$6B/year inside SpaceX; Starlink (61% of revenue) is profitable |
| The anomaly | insiders may sell 20% **two days after the first earnings report** (vs the standard 180 days) |
| Polymarket (real money) | 99% day-1 close above $1T · 60.5% above $2T |
| The plan | 60% quality proxy (GOOGL) · 20% defined-risk put spread on the lockup · 20% cash · max loss hard-capped ~20% |

## Retail vs enterprise, with no sugarcoating

How much of each institutional layer can a retail investor + AI actually reach today?
Full analysis in [EVALUATION.md](EVALUATION.md) §5, mitigation playbook in
[docs/08-closing-the-gap.md](docs/08-closing-the-gap.md).

| Layer | Reachable today | | How |
|---|---|---|---|
| Process discipline | `▰▰▰▰▰▰▰▰▰▱` | ~90% | pre-registration, journals, checkpoints — pure will, €0 |
| Models | `▰▰▰▰▰▰▰▱▱▱` | ~50-70% | open-source MC/GARCH, free academic factors, validated fat tails |
| Data | `▰▰▰▰▰▱▱▱▱▱` | ~40-60% | EDGAR, Polymarket, FRED free; intraday/IV for <$300; self-archived checkpoints |
| Execution | `▰▰▱▱▱▱▱▱▱▱` | ~20% | refuse the speed game: limit orders, weeks-long horizons, smallness as edge |
| Access | `▰▱▱▱▱▱▱▱▱▱` | ~10-20% | securities lending, defined-risk option replication — the rest is bought |

> Summed up where it matters for position trading: **roughly half** of a desk's capability,
> up from ~5% pre-AI. The bet of this experiment: the reachable half is the half that
> prevents ruin.

**A note on currency.** Amounts are in EUR on purpose: this is deliberately a *European*
retail experiment, and the frictions that come with that — EUR/USD exposure, the PRIIPs
rules that block US ETFs, local taxation — are not glossed over but engineered around
([docs/02](docs/02-strategies.md), [docs/05](docs/05-tax-italy.md)). The EURUSD rate is
frozen in every checkpoint, the prediction hard-caps are expressed in percentages, and a
US reader can mentally substitute dollars everywhere except those two documents. An
experiment that pretended to be currency-less would be hiding exactly the constraints
that make retail reality different from a textbook.

## The quant research, at a glance

<div align="center">
<table>
<tr>
<td align="center"><img src="assets/chart_mc_pnl.png" width="420"/><br><sub><b>Plan P&L distribution</b> — 10k simulations; red mass = losing region; the left tail is all equity beta, the spread is hard-capped</sub></td>
<td align="center"><img src="assets/chart_payoff.png" width="420"/><br><sub><b>Spread payoff vs simulated outcomes</b> — profit/loss zones shaded over the density of final SPCX prices</sub></td>
</tr>
<tr>
<td align="center"><img src="assets/chart_sensitivity.png" width="420"/><br><sub><b>Sensitivity, decomposed</b> — judge the trade on the spread-only line: the total is padded by the GOOGL drift assumption</sub></td>
<td align="center"><img src="assets/chart_signal_ranking.png" width="420"/><br><sub><b>Signal quality rubric</b> — what people DO with money outranks what they SAY; thresholds mark context vs trade-on-it</sub></td>
</tr>
<tr>
<td align="center"><img src="assets/chart_corr.png" width="420"/><br><sub><b>Correlations</b> — 2-year structure vs current regime; the boxed cell is the "Musk beta" (GOOGL×TSLA)</sub></td>
<td align="center"><img src="assets/chart_attention.png" width="420"/><br><sub><b>Attention timeline</b> — cleaned Wikipedia/HN z-scores spike ON the milestones: they confirm, they don't anticipate</sub></td>
</tr>
<tr>
<td align="center"><img src="assets/chart_universe.png" width="420"/><br><sub><b>Universe</b> — direct labels with 12-month change; the best risk-adjusted shovel is VIRT, not HOOD</sub></td>
<td align="center"><img src="assets/chart_rolling_corr.png" width="420"/><br><sub><b>Diversification dead zone</b> — how often the defensive tranche stops diversifying exactly when needed</sub></td>
</tr>
</table>
</div>

## Data quality engineering — garbage in, garbage out, audited

A dedicated notebook (`05_data_quality`) audits every input: coverage scorecards,
issues-vs-warnings triage, and the pipeline bugs the gates caught — **shown, not hidden**.

<div align="center">
<table>
<tr>
<td align="center"><img src="assets/chart_dq_scorecard.png" width="420"/><br><sub><b>Coverage scorecard</b> — per-ticker business-day coverage; blocking issues vs human-review warnings</sub></td>
<td align="center"><img src="assets/chart_dq_jumps.png" width="420"/><br><sub><b>Flagged outliers, inspected</b> — every >50% move survived review (real events): warn, never auto-drop</sub></td>
</tr>
<tr>
<td align="center"><img src="assets/chart_dq_hn_truncation.png" width="420"/><br><sub><b>The pagination bug, visualized twice</b> — naive fixes lost history silently; only time-windowed pagination covers the request</sub></td>
<td align="center"><img src="assets/chart_cleaning.png" width="420"/><br><sub><b>Winsorization, accounted for</b> — every clipped point marked and counted; for prices the spikes are information, for attention they are noise</sub></td>
</tr>
</table>
</div>

**The finding that corrected the thesis** — an event study on 4 historical lockups (UBER,
RIVN, META, SNAP) shows the drop happens in *anticipation* (-37 points on average in the 30
sessions before expiry) and the unlock day itself is often a local bottom. Sell the rumor,
buy the news: the exit rule was rewritten accordingly (close within T+5 of the unlock).

## What's in the repo

```
notebooks/00_master_report.ipynb     ← OPEN THIS: runs everything, outputs embedded
notebooks/01..05                     data pipeline · correlations · Monte Carlo · signal quality ·
                                     data-quality audit
docs/01..08                          thesis · strategies with full math · timeline ·
                                     risk management · tax case study · trade journal ·
                                     capital tiers (€1k to €10M+) · closing the enterprise gap
docs/html/                           the notebooks as plain HTML (double-click, zero setup)
src/connectors/                      SEC EDGAR · Polymarket · FRED · yfinance+Stooq · HN · Wikipedia
src/risk/ · src/research/            metrics, Monte Carlo, lockup event study,
                                     fat-tail validation, signal-quality framework
PREDICTIONS.md                       the falsifiable ledger — the heart of the experiment
EVALUATION.md                        pre-registered evaluation protocol + honest limits
LOGBOOK.md                           append-only build chronology: decisions and bugs, dated
checkpoints/                         frozen data snapshots at every milestone (tools/checkpoint.py)
```

## Reproduce everything

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build_master.py          # rebuilds + executes all 6 notebooks on fresh data
./tools/run_tests.sh                            # full smoke-test suite (12 modules, must print 12/12 PASS)
.venv/bin/python tools/checkpoint.py <label>    # freeze a dated evidence snapshot (see EVALUATION.md)
```

To read the notebooks with no setup at all: open `docs/html/` in a browser, or let GitHub
render them online. In VS Code: Jupyter extension + the venv kernel created above.

## Why this repo exists

Not for the P&L — a small account with declared EV≈0 changes nobody's life. It exists to
answer, with data and at the cost of public embarrassment, a serious question: **can AI give
someone with two thousand euros the tools of someone managing two trillion?** The working
hypothesis after building it (see `docs/07`): AI compresses the *analysis* gap to nearly
zero; the *access* gap — allocations, OTC, borrow, pre-IPO secondaries — is still plumbing
that no model can route around. The honest answer lands in the Outcome column of
[PREDICTIONS.md](PREDICTIONS.md).

## A note to whoever reopens this repo months from now

Maybe it's the author. Maybe it's another AI, asked to grade the first one. Either way:

1. Don't trust your memory of how this played out — load `checkpoints/` and compare frozen
   snapshots. Live data sources revise themselves; the snapshots don't.
2. The rules of the game are in [EVALUATION.md](EVALUATION.md) and they were written before
   the events. Changing the metrics now is cheating; say so if you catch yourself doing it.
3. [LOGBOOK.md](LOGBOOK.md) records what was decided when, and which bugs the process caught.
   The mistakes are part of the dataset — that was the point.
4. Whatever the P&L says, the question to answer is the one above: did the analysis hold up,
   were the probabilities calibrated, did the discipline survive contact with the market?

Write `VERDICT.md`. Be harsher than feels polite.

---

<div align="center">
<sub>
Nothing in this repo is financial advice. It is a documented experiment, run with capital the
author can afford to lose and rules written before the events.<br>
The SpaceX logo belongs to Space Exploration Technologies Corp. — used here for identification only.
</sub>
</div>

# 08 — Closing the gap: a retail playbook against the enterprise stack

[EVALUATION.md](../EVALUATION.md) §5 froze the honest positioning. This document is its
constructive counterpart: **layer by layer, what a retail investor can actually deploy today
to shrink each gap, what it costs, and what stays structurally closed no matter what.**
The "gap closed" estimates are deliberately blunt; they refer to position/swing horizons
(days-months). At HFT horizons every number below collapses to ~0%.

> The one-line thesis: **retail closes gaps top-down (process → data → models), enterprise
> defends them bottom-up (execution → access). The two fronts barely overlap — and that is
> precisely the opportunity.** Don't fight where they defend; build where they can't be
> bothered.

---

## Layer 1 — Process discipline ▰▰▰▰▰▰▰▰▰▱ ~90% closeable

| Enterprise has | Retail counter | Cost |
|---|---|---|
| Investment committees, risk sign-off, compliance journals | Pre-registered predictions ([PREDICTIONS.md](../PREDICTIONS.md)), falsification criteria written ex-ante, trade journal with mandatory pre-order entries ([06-trade-journal.md](06-trade-journal.md)), frozen checkpoints with hashes | **€0** |
| Mandates that force discipline | The 24-hour rule, hard caps, written invalidation conditions ([04-risk-management.md](04-risk-management.md)) | €0 |

**What stays closed**: nothing structural. This layer is pure will. It is also where most
retail (and some funds) actually fail. This repo IS the layer-1 playbook.

## Layer 2 — Data ▰▰▰▰▰▱▱▱▱▱ ~40-60% closeable

| Enterprise has | Retail counter | Cost |
|---|---|---|
| Bloomberg/Refinitiv terminal | **OpenBB** (open-source terminal), yfinance/Stooq with quality gates (this repo's `market_data.py`) | €0 |
| Filing-parsing NLP pipelines | **SEC EDGAR API** — the same legal documents, same instant, free (`edgar.py`); Form 4 = insider trades within 2 business days | €0 |
| Prediction/positioning data | **Polymarket/Kalshi** odds (`polymarket.py`); CFTC COT reports (free, weekly) | €0 |
| Intraday + options chains | **Polygon.io / Databento** pay-as-you-go | ~$30-200/mo |
| Historical IV surfaces (OptionMetrics) | **ORATS / CBOE DataShop** slices; or self-archive going forward (this repo's checkpoint system does exactly this — IV history is built, not bought) | ~$50-300 one-off |
| Alt-data ($100k+/yr) | Wikipedia pageviews + HN flow (`wikipedia.py`, `hackernews.py`), Google Trends, app-ranking scrapes — **after** signal-quality grading (notebook 04: attention follows price; use as context only) | €0 |

**What stays closed**: consolidated tick tape, order-flow data, broker-dealer internalization
flows, exclusive datasets. **Key insight**: for horizons ≥ days, the marginal value of the
closed part is small; the checkpoint discipline converts "data you can't buy backwards" into
"data you own going forward".

## Layer 3 — Models ▰▰▰▰▰▰▰▱▱▱ ~50-70% closeable

| Enterprise has | Retail counter | Cost |
|---|---|---|
| Barra/Axioma factor risk models | **Ken French data library** (free academic factors) + open-source regressions; this repo's EWMA/beta/correlation stack (`metrics.py`) | €0 |
| Calibrated vol models (Heston/SABR) | **arch** (GARCH family), QuantLib — CPU-grade, laptop-sized | €0 |
| Monte Carlo risk engines | This repo's validated-fat-tail MC (`montecarlo.py` + `dist_validation.py` — the t-dof is *fitted*, not assumed) | €0 |
| Survivorship-free backtests (CRSP) | Honest partial: vectorbt/backtrader on survivor-biased free data, with the bias **declared** (as in the n=4 lockup study) | €0 |
| NLP at scale | FinBERT-class models on Colab T4 (the one justified GPU use — see [EVALUATION.md](../EVALUATION.md) §6) | €0-10/mo |

**What stays closed**: decades of clean point-in-time data to validate against. A model is
only as honest as its backtest database, and the free ones lie by survivorship. Mitigation:
prefer event-anchored studies with explicit n (this repo: n=4, stated) over sweeping
backtests with hidden bias.

## Layer 4 — Execution ▰▰▱▱▱▱▱▱▱▱ ~20% closeable (by refusing to play)

| Enterprise has | Retail counter | Cost |
|---|---|---|
| Co-location, microseconds | **Don't compete on speed. Compete on time.** Holding periods of weeks make microseconds irrelevant | €0 |
| Smart order routing | Limit orders only, combo orders for spreads, liquid hours, round strikes, never chase >$0.10 ([04-risk-management.md](04-risk-management.md) §5) | €0 |
| Market impact models | Irrelevant below ~$1M per name — **smallness is the edge**: full entry/exit without moving the tape | €0 |

**What stays closed**: any strategy whose edge IS execution (market making, arbitrage,
news-reaction). The mitigation is selection, not technology: retail should never hold a
position whose thesis decays in minutes.

## Layer 5 — Access ▰▱▱▱▱▱▱▱▱▱ ~10-20% closeable, fee-eaten

| Enterprise has | Retail counter | Cost / catch |
|---|---|---|
| IPO allocations | US brokers occasionally distribute (Fidelity/SoFi); EU retail: effectively no | strings attached (flipping bans) |
| Pre-IPO secondaries | EquityZen/Forge | accredited-only, $10k+ minimums, 2-5% fees that eat most of the edge |
| Securities lending revenue | **IBKR Stock Yield Enhancement Program** — genuinely available to retail; lending hot stocks (a post-IPO SPCX!) pays real carry | the one underused access tool |
| OTC structures | Defined-risk listed spreads replicate crude versions (a 135-day put ladder ≈ a lockup-matched OTC put, worse pricing) | wider spreads |
| Borrow for shorts | Listed puts = pre-packaged borrow with capped cost (the debit IS the maximum borrow fee) | IV premium |

**What stays closed**: most of it. This is the gap that capital alone opens
([07-capital-tiers.md](07-capital-tiers.md), Tier 4). The honest play is to harvest the two
crumbs that ARE available (securities lending, defined-risk option replication) and stop
pretending the rest exists.

## Layer 6 — The AI multiplier (the experiment's subject)

Everything in layers 1-3 used to cost analyst-hours — the scarcest retail resource. The
measurable claim of this repo: **one human evening + a frontier model produced the
process layer, the data plumbing, a validated risk model and an event study** that would
have been a multi-day job for a junior quant, and impossible for a non-programmer.

What AI did NOT do: open a single door in layers 4-5, or substitute for the discipline of
actually following the rules in [04-risk-management.md](04-risk-management.md). The model
writes the journal template; only the human can refuse to lie to it. Whether the multiplier
holds up out-of-sample is exactly what [PREDICTIONS.md](../PREDICTIONS.md) will answer.

---

## The deployment roadmap

| Horizon | Action | Cost | Gap attacked |
|---|---|---|---|
| **Today, free** | This repo's pattern: pre-registration, quality-gated free data, validated MC, checkpoints, journals | €0 | Layers 1-3 |
| **This quarter, cheap** | Polygon/Databento for intraday+chains; ORATS slice for IV history; OpenBB; FinBERT notebook on Colab | <$300 | Layer 2-3 residual |
| **Structural, capital** | Tier climbing per [07-capital-tiers.md](07-capital-tiers.md): portfolio margin at T3, lending/secondaries at T4 | capital | Layers 4-5 |

**Closing honesty**: summed up, a disciplined retail investor with free tools and an AI
reaches maybe **half** of an institutional desk's capability where it matters for
position trading — up from perhaps 5% pre-AI. The remaining half is bought, not learned.
The experiment's bet is that the reachable half is the half that prevents ruin.

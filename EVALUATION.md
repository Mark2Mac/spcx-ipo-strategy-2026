# EVALUATION — pre-registered protocol for the ex-post review

This file defines, BEFORE the events, how the experiment will be judged months from now.
Pre-registering the evaluation protocol matters as much as pre-registering the predictions:
an evaluator free to choose metrics after the fact can make any outcome look good.

## 1. Checkpoint system (frozen evidence)

`tools/checkpoint.py` freezes every data source + model output into `checkpoints/<date>/`
with SHA256 manifest, git HEAD and pip freeze. Some of today's data is **unrecoverable
later** (Polymarket odds vanish when markets resolve; option IV is never archived for free;
yfinance silently revises), so the snapshots ARE the evidence base.

```bash
.venv/bin/python tools/checkpoint.py [label]   # e.g. tools/checkpoint.py earnings-T
```

**Mandatory checkpoint schedule** (add to calendar):

| When | Label | Why |
|---|---|---|
| 2026-06-10 | `baseline` | T-2 state: everything the predictions were based on |
| 2026-06-11 | `T-1-pricing` | final pre-debut odds + benchmark closes (VWCE/EURUSD) |
| 2026-06-12 eve | `day1` | debut close, Polymarket resolution of P1/P2 |
| ~2026-06-24 | `options-listed` | first real IV — the MC's guessed parameters meet reality |
| Jul 6-17 (entry or cancel) | `entry-window` | spread executed or fallback triggered: record which |
| Earnings day | `earnings-T` | the xAI burn number, pre-unlock state |
| T+7 | `unlock-T7` | P4/P5 raw evidence, Form 4 filings |
| ~Oct 25 | `day135` | lockup fully open: SPCX's first "true" price |
| Dec 31 | `final` | P6, K1-K3, year-end state |

Checkpoints are committed to git and never edited. A missing checkpoint is itself a
recorded outcome (process failure).

**Automation**: `.github/workflows/checkpoint.yml` snapshots automatically every Monday
and Thursday after the US close (runs on GitHub's servers — no local machine needed) and
each automated commit keeps the schedule alive. Milestone checkpoints are fired manually:
`gh workflow run scheduled-checkpoint -f label=day1` (or the Actions tab). Every snapshot
includes the SPCX option chains with IV once listed, guarded by an `identity_suspect` flag
(the ticker currently collides with a pre-2026 ETF — see LOGBOOK bug 8).

## 2. Evaluation metrics (fixed now)

1. **Prediction scoring**: fill the Outcome column of [PREDICTIONS.md](PREDICTIONS.md);
   compute the Brier score on P1-P6 and K1-K3 using the **P(ex-ante) column** (fixed
   2026-06-11, pre-debut, by dated amendment). Honest caveat: n=9 predictions has
   near-zero statistical power — report the score, do not oversell it.
2. **P&L attribution**: realized plan P&L vs the two trivial benchmarks frozen in the
   checkpoints (100% cash at the checkpointed 3M T-bill rate; 100% world equity ETF —
   VWCE.DE close and EURUSD are in each checkpoint's `benchmarks.json` from
   `T-1-pricing` onward). Attribution by tranche (equity / spread / cash) per K2.
3. **Process compliance**: journal audit ([docs/06](docs/06-trade-journal.md)) — every
   order preceded by an entry? Any rule of [docs/04](docs/04-risk-management.md) violated?
   Score = violations count, weighted by severity. This metric dominates: K3 says the
   experiment is about process, not direction.
4. **Model audit**: compare the baseline MC's guessed parameters (`spcx_vol=0.70`,
   `jump=-8%±12%`) against realized values (realized vol from actual SPCX bars; actual
   earnings-day move). Was the model wrong in a way that mattered?
5. **Counterfactual cost of AI errors**: list every factual error the AI made during the
   build (the repo's git history records several: cache-key bug, quality-gate false
   positives, Wikipedia 429) and classify: caught by tests / caught by human / would have
   cost money.

## 3. Instructions to the future evaluator (human or AI)

1. Clone the repo at HEAD; do NOT use live data to reconstruct the past — load
   `checkpoints/2026-06-10-baseline/` and compare with later checkpoints. Read
   [LOGBOOK.md](LOGBOOK.md) for the decision-and-bug chronology; the rendered state of
   every chart/notebook at each date is recoverable from git history (`docs/html/`,
   `assets/` are committed at every milestone).
2. Fill PREDICTIONS.md Outcome column with citations (checkpoint file + field).
3. Run `tools/build_master.py` on current data; diff conclusions vs the frozen notebooks
   (`docs/html/` archives the rendered versions of today).
4. Write the verdict as a new file `VERDICT.md`; never edit this one or PREDICTIONS.md.
5. Apply section 4's limits BEFORE judging: several findings cannot be scored at all
   (n=1 event), and saying so is the correct conclusion, not a cop-out.

## 4. Known limits of this work (written now, no sugarcoating)

1. **n=1**: one IPO, one macro regime. The experiment can validate process quality, never edge. Any P&L outcome is statistically meaningless.
2. **The event study is n=4** with hand-picked, survivor-known names from different regimes (2012-2022). It informs a prior; it proves nothing.
3. **The MC's core parameters are priors, not estimates**: SPCX vol (70%) and the event jump (-8%±12%) were invented before any SPCX price existed. The sensitivity table mitigates; it does not cure.
4. **No options data existed at build time**: the central trade (the spread) was costed on guesses. First contact with real IV (checkpoint `options-listed`) may invalidate the entire B-strategy math.
5. **Daily bars, free feeds**: no intraday, no order flow, no IV surface, no consolidated tape. yfinance revises history silently (the checkpoint system exists partly for this).
6. **Static correlations** (ρ=0.45 SPCX-GOOGL is a guess; EWMA helps for the listed names only).
7. **Calibration unmeasurable**: 9 predictions cannot produce a meaningful Brier score; this experiment must be repeated across many events for the calibration axis to mean anything.
8. **The AI cannot be blinded**: its training data may embed knowledge adjacent to the events; a clean-room test would require future events only (it partially gets this: everything after 2026-06-10 is genuinely out-of-sample for the frozen analyses).
9. **Execution assumptions untested**: mid fills, $0.10 chase tolerance, combo liquidity on a freshly listed name — all hopeful.
10. **The access gap is untouched** (docs/07): no allocations, no OTC, no borrow, no secondaries. AI compressed the analysis layer only.

## 5. Honest positioning vs enterprise (frozen now, to be re-judged later)

| Layer | This repo | Enterprise desk | Gap |
|---|---|---|---|
| Process discipline (pre-registration, falsifiability, journals) | yes | sometimes | **smallest gap — arguably ahead of most retail AND some funds** |
| Public-data plumbing (EDGAR, prediction markets, quality gates) | yes, free | yes, industrialized | small |
| Models | toy MC + 1 event study | multi-factor risk models, calibrated vol surfaces, survivorship-free DBs (CRSP), thousands of backtested events | **huge** |
| Data | 6 free sources, daily bars | Bloomberg/Refinitiv terminals, tick data, OptionMetrics, $100k+/yr alt-data | **huge** |
| Execution & microstructure | none | co-location, order-flow, smart routing | **total** |
| Access (allocations, OTC, borrow, secondaries) | none | the actual business | **total** |

Realistic summary: top few percent of retail by process; a competent intern's first-month
project by quant-fund standards; ~the cheapest 20% of an institutional stack. The 20% that
AI made nearly free is real and was previously inaccessible to retail — that IS the
experiment's positive finding so far. The remaining 80% is bought with money, not
intelligence. The constructive counterpart — what retail can deploy to shrink each layer,
at what cost — is [docs/08-closing-the-gap.md](docs/08-closing-the-gap.md).

## 6. High-compute extensions: what's worth a Colab T4 (and what is compute theater)

| Idea | Verdict |
|---|---|
| 10M-path Monte Carlo | **Theater.** MC error shrinks as 1/√N; our uncertainty is parametric (vol, jump priors), not sampling noise. 10k paths already suffice |
| Hyperparameter sweeps on attention signals | **Theater + dangerous.** With ~180 daily observations, sweeps = guaranteed overfitting |
| GARCH / stochastic-vol calibration on TSLA/universe | Worth doing, but it is CPU work — no GPU needed |
| **NLP on filings and crowd text** (FinBERT-class sentiment on the S-1 risk factors vs other mega-IPO S-1s; classification of 1000+ HN/Reddit comments into the signal-quality rubric instead of hand-scoring) | **The one genuinely sensible T4 use.** Embedding/classifying thousands of documents is exactly what a T4 accelerates, and it would replace the rubric's hand-assigned scores with measured ones |
| Fine-tuning a model on financial text | Theater at this scale: nothing here needs it |

If the NLP extension is built, it gets its own notebook (05) and its outputs join the
checkpoint schedule.

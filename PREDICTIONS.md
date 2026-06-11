# PREDICTIONS — the falsifiable ledger

Written on **June 10, 2026**, two days before the SPCX debut, by a human + Fable 5 (Anthropic).
The *Outcome* column stays empty until each verification date. Predictions are never edited retroactively: git history is the witness.

## Market predictions

> **Amendment 2026-06-11 (pre-debut, T-1)**: explicit ex-ante probabilities added so the
> Brier score in EVALUATION.md §2 is computable. Set before any market outcome was known;
> no other field touched. Git diff is the proof.

| # | Prediction | Source/rationale | P(ex-ante) | Verify on | Criterion | Outcome |
|---|---|---|---|---|---|---|
| P1 | SPCX closes day-1 above $1T market cap | Polymarket 99% on Jun 10 | **0.97** | Jun 12, 2026 | close cap > $1T | |
| P2 | SPCX closes day-1 above $2T | Polymarket 60.5% on Jun 10 | **0.60** | Jun 12, 2026 | close cap > $2T | |
| P3 | In the first 4 weeks the stock does NOT close below $135 (index-inclusion support + 4x demand) | own thesis, docs/01 §6 | **0.70** | Jul 10, 2026 | min close ≥ $135 | |
| P4 | The lockup-driven drop starts BEFORE the insider unlock (anticipation), not after | event study UBER/RIVN/META/SNAP: -37 pts avg T-30→T0 | **0.65** | T+10 from first earnings | pre-unlock drawdown > post-unlock drawdown | |
| P5 | At T+30 from first earnings SPCX trades below its pre-earnings price | lockup thesis + xAI burn ($2.5B/q) | **0.55** | T+30 | close(T+30) < close(T-1) | |
| P6 | Through end-2026 SPCX never touches Morningstar fair value ($780B ≈ -55%) — the "theft of the century" crash does NOT materialize within the year | markets stay irrational longer | **0.80** | Dec 31, 2026 | min 2026 cap > $780B | |

## Plan predictions (reference implementation)

| # | Prediction | P(ex-ante) | Verify on | Criterion | Outcome |
|---|---|---|---|---|---|
| K1 | Plan P&L lands inside the structural hard-cap range (≈ -21% to +23% of capital) | **0.97** | Dec 31, 2026 | realized P&L in range | |
| K2 | The worst loss, if any, comes from the equity tranche (beta), not the spread | **0.75** | Dec 31, 2026 | P&L attribution | |
| K3 | EV ≈ 0 declared ex-ante: the final P&L is explained by process, not directional luck | **0.60** | Dec 31, 2026 | journal retrospective | |

## The experiment's real question

> **Can a frontier AI model close the information and competence gap between a small retail
> investor and institutional players, enough to produce aware, professional-grade financial
> decisions?**

To be judged ex-post — not on P&L (one trade is noise) but on these axes:

| Axis | What to check later |
|---|---|
| Information quality | Were the sources (S-1, EDGAR, Morningstar, Polymarket) the right ones? Did professionals have something we missed? |
| Calibration | Were the probabilities (P1-P6) calibrated, or systematically optimistic/pessimistic? |
| Risk management | Did the hard caps hold? Were the behavioral rules followed or gamed? |
| Mistakes avoided | Did the model prevent the classic retail errors (buying day-1, naked options on inflated IV, uncapped shorts, non-PRIIPs ETFs)? |
| Mistakes introduced | Did the model add its own (overconfidence in illustrative numbers, unnecessary complexity)? |
| Value vs alternatives | Compare with the two trivial benchmarks: 100% cash, and 100% world-ETF bought on Jun 10 |
| Analysis vs access | Which part of the institutional gap did AI actually close? (Working hypothesis in docs/07: the analysis gap, not the access gap) |

**Methodological note**: the experiment is honest only if the journal (docs/06) is filled in real time and this file's predictions are never touched — only the Outcome column gets filled.

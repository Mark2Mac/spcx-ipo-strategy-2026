# 05 — Italian taxation (declarative regime, foreign broker)

> Case study for the reference implementation (Italian resident, foreign broker, declarative regime). Verify with an accountant before filing. 2026 rates assumed unchanged; re-check in early 2027. Readers in other jurisdictions: the structure of the analysis transfers, the numbers do not.

## 1. The picture

With a foreign broker (e.g. IBKR) you are in the **declarative regime**: no withholding agent — you compute and file. Consequences:
- Upside: taxation deferred to the following year (26% on 2026 gains is paid mid-2027) → small financing benefit.
- Downside: RW + RT forms to fill; mistakes = penalties.

## 2. The categories that matter

| Instrument | Tax category | Rate | Offsets prior losses? |
|---|---|---|---|
| Stocks — capital gains | "Redditi diversi" | 26% | YES, generates and absorbs losses |
| Options and spreads — P&L | "Redditi diversi" | 26% | YES |
| Foreign dividends | "Redditi di capitale" | 26% on the net-of-treaty amount | **NO** |
| ETFs/funds — gains | "Redditi di capitale" | 26% | **NO (the Italian ETF trap)** |

**The ETF trap**: ETF gains cannot absorb carried losses (ETF losses, however, DO offset stock/option gains). One more reason — besides PRIIPs — this plan holds no ETFs.

## 3. Plan-specific calculations

### GOOGL dividends (equity tranche)
- Yield ~0.4%; US treaty withholding 15% (file the W-8BEN!), then Italian 26% on the remainder → effective ~37.1%.

### Strategy B — profit case
- Net profit × 26% tax; e.g. +€155 → -€40.30 → **€114.70 in pocket**.

### Strategy B — loss case
- The loss is a carryforward: offsets "redditi diversi" gains realized through **Dec 31, 2030**.
- Fiscal value: up to 26% of the loss in future tax saved — IF you generate offsettable gains in time.

### GOOGL — no taxable event until sale
- Unrealized gains are untaxed: holding 12+ months = full control of tax timing.
- Year-end optimization (Phase 6 of the timeline): if B closed at a loss and GOOGL is up, selling and rebuying GOOGL before Dec 31 realizes a gain that absorbs the loss (mind transaction costs and repurchase price risk; do it only if you wanted to rebalance anyway).

### IVAFE
- 0.2%/year on foreign financial products held at Dec 31 (pro-rata on holding days). Filed with the return.

## 4. Filing forms (2027 return for FY2026)

| Form | Declares | Notes |
|---|---|---|
| **RW** | Foreign account (asset monitoring) + IVAFE | Mandatory even with zero P&L. Max and year-end values |
| **RT** | Capital gains/losses ("redditi diversi") | LIFO for lots; broker reports help but the EUR conversion (ECB daily rate) is on you |
| **RM** | Foreign dividends | 26% on the net-of-treaty amount |

Practical tooling: the broker's annual activity statement + a spreadsheet with daily ECB rates; or a specialized online accountant (~€100-200, worth it from year two or with many trades).

## 5. Mistakes not to make

1. Skipping the RW form: penalties of 3-15% of undeclared amounts (even with no income!).
2. Not filing the W-8BEN: US dividend withholding at 30% instead of 15%.
3. Thinking in gross P&L: every take-profit decision should be evaluated net of 26%.
4. "Parking" the cash reserve in an ETF: capital-income category, no loss offsetting.
5. Using unlicensed prediction-market platforms "because it's small": undefined tax treatment, no loss offsetting, plus regulatory exposure. Out of the plan.

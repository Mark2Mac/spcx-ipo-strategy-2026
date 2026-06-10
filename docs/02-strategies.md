# 02 — Strategies with full calculations (reference implementation: small account)

This file documents the **reference implementation** on a small account (~€2,000, EU retail, IBKR, declarative tax regime) because that was the experiment's starting point — the math is fully worked and auditable. For how the same theses scale (or change entirely) across capital tiers from thousands to millions, see [07-capital-tiers.md](07-capital-tiers.md). Assumed EUR/USD = 1.08 (refresh at every real calculation). Declared priority: **safety > return**.

## Regulatory constraints (verified, non-negotiable for EU retail)

- **PRIIPs/KID**: XOVR, NASA ETF, DXYZ and any US vehicle without a KID are **blocked** for EU retail. No ETF proxies.
- **US stock options**: accessible (exempt from the KID requirement).
- **Polymarket**: not licensed in the EU/Italy → excluded (legal risk + undefined taxation + counterparty).
- **Direct SPCX short**: technically possible, excluded (borrow cost estimated 20-100%+ annualized in the first weeks, unlimited loss, squeeze risk with 4x oversubscribed demand).

## Base friction (the cost of playing)

| Item | Cost | Frequency |
|---|---|---|
| EUR→USD conversion | min $2 | 1-2 times |
| Stock order (IBKR) | ~$1-2 | per order |
| Option (IBKR) | ~$1/contract/leg; spread = 2 legs × 2 (open+close) = ~$4-8 | per round trip |
| IVAFE (IT wealth tax on foreign assets) | 0.2%/year | annual |
| Tax filing (RW form) | own time or accountant €100-200 | annual |
| **Total annual friction on a small account** | **~€15-25 (0.8-1.2%)** | |

Mathematical consequence: every strategy must clear ~1% just to break even. On small accounts the number-one enemy is fixed costs, not the market.

---

## STRATEGY A — Defensive long proxy: GOOGL (60% of capital)

### Edge
Alphabet holds ~5% of SpaceX (≈$90B at IPO price) on a ~$3.5T market cap: a partially unpriced catalyst (~2.5% of GOOGL's value). Underneath: a dominant business, cash, buybacks. The only low-risk way for EU retail to be "long SpaceX".

### Execution
- Limit orders only, never market. Liquid window: 16:00-17:30 CET.
- No leverage, no options on this tranche.

### Scenario math (on a €1,200 tranche)
| SpaceX scenario | Stake effect | GOOGL effect | Tranche P&L |
|---|---|---|---|
| SPCX +50% | +$45B | +~1.3% | **+€16** |
| SPCX flat | 0 | 0 | €0 |
| SPCX -50% | -$45B | -~1.3% | **-€16** |
| GOOGL own drivers +10% | — | +10% | **+€120** |
| Market -15% (beta ~1.3) | — | -~19% | **-€230** |

**Honest reading**: this tranche's risk/return is dominated by Alphabet itself, not SpaceX. Its function: park most of the capital in quality instead of in the circus, keeping symbolic exposure to the theme. This IS the "more safety, less return" strategy.

### Tranche risk management
- Thesis stop (mental, not resting): **-15%**. Reassessment, not auto-sale.
- Horizon: 12+ months (also tax-efficient: no taxable event until sale).

---

## STRATEGY B — Short on a dated catalyst: SPCX bear put spread (≤20% of capital)

### Edge (declared and falsifiable)
The market prices the debut pop well (Polymarket: 99% above $1T) but underprices the August window: first earnings (the ~$2.5B/quarter xAI burn made visible) + 20% insider unlock 2 days later. Historical precedents: RIVN -20% in one day, UBER -40% at lockup expiry. Morningstar fair value -55% from IPO price.

**The thesis is falsified if**: insiders don't sell in size in August, or earnings show the xAI burn sharply down, or the stock has already lost >30% before the window (edge consumed).

### Structure: bear put spread (vertical debit)
Illustrative numbers with SPCX at $150 post-pop and IV 75% → recompute on real late-June/July prices.

```
BUY  1 SPCX put, 18 Sep 2026 expiry, strike $140
SELL 1 SPCX put, 18 Sep 2026 expiry, strike $135
Width: $5 | Estimated debit: $2.20/share → total cost $220
```

### Full math
| Quantity | Formula | Value |
|---|---|---|
| Max risk | debit paid | $220 (**hard cap**) |
| Max gain | (width − debit) × 100 | $280 |
| Breakeven at expiry | long strike − debit | **$137.80** |
| Risk/reward | max gain / max loss | 1 : 1.27 |
| Min P(profit) for EV=0 | debit / width | **44%** |
| Round-trip commissions | 2 legs × 2 × $1 | ~$4-8 (2-4% of premium: counted) |

### Expected value — sensitivity table
| P(SPCX ≤ $135 by Sep 18) | Spread EV |
|---|---|
| 30% | **-$60** |
| 40% | **-$18** |
| 44% | $0 (probabilistic breakeven) |
| 50% | **+$30** |
| 55% | **+$55** |
| 60% | **+$80** |

**Honesty**: positive EV ONLY if you assign the lockup thesis P > 44%. Polymarket and the 4x demand suggest the market prices it lower. The presumed edge: the market stares at day-1, you stare at August. If you don't believe P ≥ 50%, do NOT run strategy B — hold cash instead.

### Execution rules (binding)
1. **NEVER buy the spread in the first 10-15 trading days**: post-IPO IV is at maximum (~75-90%). Typical IV crush is 20-30 points in 3-4 weeks → the same spread will cost ~$1.50-1.80 instead of $2.20.
2. Entry window: **July 6-17** (see timeline), ONLY if IV < 55% and SPCX > $140.
3. Expiry MUST contain the earnings date plus 2 days: September minimum, October if affordable.
4. **Take profit at +70% of max gain**: close without waiting for expiry (the last 30% requires holding into gamma/pin risk).
5. **Stop on the thesis, not the price**: if earnings pass and the stock does NOT fall within 5 sessions of the unlock, the thesis is falsified → close and recover residual time value (~30-50% of premium).
6. **Event-study exit rule**: close within T+5 of the unlock regardless of P&L — historically the drop is anticipation-driven and T0 is often a local bottom (see notebook 00, section 7).
7. The +30% trap: if SPCX holds +30% for 5 of 10 sessions, an extra 10% insider tranche unlocks — thesis reinforced but your strike is farther. Roll up ONLY if the roll costs ≤ 30% of the original debit and before Aug 1.

### Variant B2 — if the view becomes "stall" rather than "drop": bear call spread (credit)
```
SELL 1 SPCX call Sep, strike ~$165 | BUY 1 SPCX call Sep, strike ~$170
Estimated credit: $1.80 → max risk $320, breakeven $166.80
P(profit) for EV=0: 64% → you need P(SPCX < $165) ≥ 64%
```
Monetizes the inflated IV instead of paying it; wins if SPCX rises a little, stalls or drops. Pick B or B2, **never both** (stacked risk breaches the tranche cap).

### Variant B3 — explicitly excluded at this scale: iron condor
Four legs ≈ $8 round-trip commissions plus active management on a stock with no price history. Complexity/benefit ratio is unjustifiable on a small account. Revisit at ≥ €10k (see 07-capital-tiers).

---

## STRATEGY C — Optionality reserve: cash (20% of capital)

### Why cash is a position
After August earnings there will be information that does not exist today: real xAI burn, actual insider behavior, price reaction. Holding cash then allows:
1. **Buying SPCX after a 35-45% drop** toward Morningstar fair value ($780B ≈ $60-77/share equivalent): at that price the long risk/reward flips.
2. **Doubling strategy B** (a second spread on Oct/Nov expiry) if the thesis confirms with momentum.
3. **Doing nothing** — a perfectly valid outcome.

Keep it in EUR until used (no FX risk); don't park it "in the meantime" anywhere else: its function is being available within 24h.

---

## Portfolio summary — 6-month scenarios (net of friction)

| Scenario | Subjective prob. | A (GOOGL) | B (spread) | C (cash) | **Total** |
|---|---|---|---|---|---|
| SPCX -30%+ in August, market holds | 30% | ~0 | +max gain | 0 | **strongly positive** |
| SPCX stalls (±10%), market holds | 30% | ~0 | -50/-100% of debit | 0 | **moderately negative** |
| SPCX soars (+40%+), market rallies | 25% | small + | -100% of debit | 0 | **moderately negative** |
| Broad market -15% | 15% | -beta × 15% | +most of max gain | 0 | **small negative** |

**Probability-weighted EV ≈ 0.** The plan is not a money machine: it is exposure with a known maximum loss (~20% of capital, hard-capped on the derivative side), capped upside, and a repeatable process. If EV≈0 is unacceptable, the rational alternative is: 100% strategy A, or 100% out.

# 04 — Risk management

The most important document in the repo. The rules written here override any future conviction. If a rule feels wrong during live trading, close the position FIRST and rewrite the rule AFTER — never the reverse.

## 1. Hard loss caps (plan structure)

| Position | Max loss | Cap type |
|---|---|---|
| A — equity proxy (60%) | thesis stop at -15% of tranche | Soft (requires discipline) |
| B — put spread (≤20%) | premium paid | **Hard (mathematical: you cannot lose more than the debit)** |
| C — cash (20%) | zero | Hard |
| Friction/taxes | ~1% | Fixed |
| **Whole plan** | **~20% of capital** | |

No combination of events can zero the account. This is "safety > return" translated into structure: 60% of the capital never touches SPCX, 20% is cash, and the only position on the stock has its maximum loss carved into the contract.

## 2. Position sizing — why these numbers

- Classic rule: risk 1-2% per trade. On a small account this is **incompatible with options** (minimum spread ticket ≈ 10% of a €2k account).
- Declared adaptation: ONE defined-risk trade at ~10% of capital, compensated by (a) the mathematical hard cap, (b) 80% of capital outside the trade, (c) the ban on adding contracts.
- Pre-order check: `max_order_risk / total_capital ≤ 0.105` → if false, the order does not go out.
- Kelly check (intellectual honesty): with P=0.50 and 1.27 odds, f* ≈ 0.11 → 10% is already full Kelly, i.e. AGGRESSIVE. Half-Kelly would be below the minimum ticket. Conclusion: trade B sits at the upper bound of rational sizing; that is why it is single and unrepeatable before the event. (At larger capital tiers this constraint disappears — see [07-capital-tiers.md](07-capital-tiers.md).)

## 3. Behavioral rules (where real losses are born)

1. **No market orders** on SPCX or its options: limit only. Bid/ask on a freshly listed name can exceed 1%.
2. **No trading in the first/last 30 minutes** of the US session except planned take-profits.
3. **Never add to a losing position** ("averaging" a spread = doubling a mistake at twice the psychological cost).
4. **Never more than 1 open derivatives position** at a time.
5. Every order requires a journal line BEFORE submission (thesis, invalidation, max loss). No line → no order.
6. **24-hour rule**: any deviation from the written plan waits 24h between idea and execution. Perceived urgency is the most reliable signal you are about to make a mistake.
7. Day-1 FOMO check: if SPCX opens +40% and you "feel" you must get in — re-read the Rivian/Uber line in [01-context-and-thesis.md](01-context-and-thesis.md). The opening pop IS the mechanism by which retail buys from institutions.

## 4. Thesis-invalidation conditions (written NOW, with a cold head)

The August-short thesis is DEAD (close B, open nothing else short) on any of:
- Earnings: xAI burn < $1.5B (sharply down) AND Starlink growth > 15% QoQ.
- T+7 after the unlock: price ≥ the T price (the market absorbs insider selling).
- SpaceX announces an xAI spin-off (removes the loss driver from the perimeter).
- SPCX below $135 BEFORE spread entry (edge consumed by the market).

The long-proxy thesis (GOOGL) is DEAD if:
- Alphabet sells/writes down the SpaceX stake, or GOOGL-specific problems change its fundamentals (at which point it is a GOOGL decision, not a SpaceX one).

## 5. Non-market risks (often ignored, often fatal)

| Risk | Mitigation |
|---|---|
| EUR/USD | Equity tranche exposed: -5% EUR/USD ≈ -5% on it. Accepted (long horizon). Reserve kept in EUR until used |
| Assignment (short leg) | Never carry the spread into expiry with spot between strikes (Phase 5 rule). Assignment = buying 100 shares ≈ $13,500 notional → margin call on a small account |
| Options liquidity | Freshly listed names can have empty books on fine strikes: round $5 strikes only, combo orders, never chase the mid by more than $0.10 |
| Broker/operational | 2FA; no trading API keys on shared machines; re-read order confirmations (one contract = 100× the displayed price) |
| Information | Earnings/unlock dates verified on SEC filings (sec.gov), not on Reddit |
| Tax | Mentally reserve 26% of every realized gain: the real P&L is net |

## 6. Weekly control metrics (Friday, 15 minutes)

- Total account value vs initial.
- Current drawdown vs accepted maximum (-20%).
- For the spread: mark-to-market, residual theta, days to the event.
- One journal line even if nothing happened ("no action" is a data point).

## 7. The most underrated risk: yourself

At small scale no strategy changes your life on the upside; a bad habit formed now (averaging down, revenge trading, pulling stops) scales with future capital and THAT can change it on the downside. Judge this plan 90% on process (rules respected?) and 10% on outcome (P&L). A win obtained by breaking the rules is a WORSE result than a loss obtained by following them.

# 06 — Trade journal

Rule: **one entry BEFORE every order** (section 2), weekly update (section 3), retrospective at close (section 4). No entry → no order (rule 5 in [04-risk-management.md](04-risk-management.md)).

## 1. Account status

| Date | Total value | vs initial | Drawdown | Notes |
|---|---|---|---|---|
| 2026-06-10 | baseline | 0% | 0% | Plan created. No positions |
| 2026-07-06 | baseline | 0% | 0% | Entry-window check (Jul 6-17). No SPCX position opened — IV gate not met (see §2 #001) |

## 2. Orders (fill in BEFORE submitting)

### Template
```
ID:               #001
Date/time:
Instrument:       (e.g. GOOGL shares / SPCX put spread 140-135 Sep26)
Direction:        long / short
Thesis (1 line):
Invalidation:     (objective condition that closes the trade)
Max risk:         ____ ( ___% of capital — must be ≤ 10.5%)
Take profit:      (level and rule)
Order:            limit type, price, validity
Emotional state:  (one honest word: calm / FOMO / revenge / boredom)
```

> If "Emotional state" ≠ calm → 24-hour rule ([04-risk-management.md](04-risk-management.md), rule 6).

### Orders placed

```
ID:               #001
Date/time:        2026-07-06 (entry window Jul 6-17, Phase 2)
Instrument:       SPCX bear put spread 140/135 Sep26
Direction:        short (bearish, defined-risk debit spread)
Thesis (1 line):  lockup/earnings drop ~August; profit if SPCX falls toward 135-140 by Sep expiry
Invalidation:     spot < 135 before entry (front-run) OR IV never crushes below gate
Max risk:         debit paid × 100 (~$199 at BS-IV) — within 10.5% cap; NOT PLACED
Take profit:      spread value ≥ 70% of width, close on combo limit
Order:            NOT SUBMITTED — see decision below
Emotional state:  calm
```

**Decision: NO ENTRY (stand-down).** Entry conditions checked on 2026-07-06:

| Condition (Phase 2) | Threshold | Realized | Met |
|---|---|---|---|
| September ATM IV | < 55% | ~83% (Aug ~87%) | ❌ |
| SPCX spot | > $140 | $162.00 (close Jul 2) | ✅ |
| 140/135 Sep debit | ≤ $2.30 | ~$1.99 BS / $2.25 last | ✅ |

The IV crush the plan waited for has not happened — SPCX still trades at post-IPO frenzy vol (~83-87% vs the ≤55% gate). Per Phase 2 **Fallback 1**: do not buy inflated IV (that is "a gift to the market maker"); retry Jul 24 at the relaxed 60% threshold — which ~83% still fails — else cancel Strategy B and cash stays cash. No order placed. Data caveat: yfinance free feed had zero option bid/ask; IV back-solved from ATM `lastPrice` via Black-Scholes, cross-checked against ~120% realized vol (ex-day1).

**Window-close check (2026-07-16, close Jul 15).** Re-checked at the end of the Jul 6-17 window:

| Condition (Phase 2) | Threshold | Realized | Met |
|---|---|---|---|
| September ATM IV | < 55% | ~80% (Aug ~86%) | ❌ |
| SPCX spot | > $140 | $135.27 (close Jul 15) | ❌ |
| 140/135 Sep debit | ≤ $2.30 | ~$2.89 BS ($2.87 last-last) | ❌ |

All three gates now fail. The anticipated drop happened **without a position**: spot fell $162 → $135.27 (Jul 6 → Jul 15), a hair above the $135 invalidation level ("spot < 135 before entry = front-run"). The 140/135 spread is now near-ATM, so its price ($2.89) exceeds the $2.30 cap — the edge the entry was priced on is gone. The Jul 24 retry (relaxed 60% IV) is effectively moot: IV ~80% still fails it AND the spot gate is dead. Strategy B heads to formal cancellation unless spot recovers above $140 with IV < 60% by Jul 24. No order placed; process held under a front-run — the gates did their job in both directions.

## 3. Weekly checks (Friday, 15 min)

| Date | SPCX spot | Sep ATM IV | Spread value | GOOGL | Account value | Action |
|---|---|---|---|---|---|---|
| 2026-07-06 | $162.00 | ~83% (Aug ~87%) | 140/135 debit ~$1.99 | n/a | baseline | Stand-down: IV > 55% gate, no entry (§2 #001) |
| 2026-07-16 | $135.27 (close Jul 15) | ~80% (Aug ~86%) | 140/135 debit ~$2.89 | n/a | baseline | Window close: all 3 gates fail (IV, spot, debit) — front-run, no entry (§2 #001) |

## 4. Closed trades — retrospective

### Template
```
ID:                 #
Gross P&L:
Net P&L (26%):
Rules respected:    yes/no (which were violated)
Was the thesis right?   yes/no/partially
Was the process right?  yes/no
Lesson (1 line):
```

## 5. Market events log

| Date | Event | Data | Plan implication |
|---|---|---|---|
| 2026-06-11 | IPO pricing | priced $135 | at low end; short thesis intact |
| 2026-06-12 | Day-1: open/high/close/volume | open 150.00 / high 176.52 / close 160.95 / vol 519.2M | +19% day-1; observe only, no trade (Phase 1) |
| ~2026-06-19 | SPCX options listed | ticker resolves to SpaceX (was colliding with defunct SPCX SPAC ETF) | IV tracking started |
| 2026-07-06 | Entry-window check | spot $162.00, Aug ATM IV ~87% / Sep ~83%, 140/135 Sep debit ~$1.99 | IV > 55% gate → stand-down (§2 #001) |
| 2026-07-16 | Entry-window close check | spot $135.27, Aug ATM IV ~86% / Sep ~80%, 140/135 Sep debit ~$2.89 | all 3 gates fail; drop front-ran entry → Strategy B toward cancel |
| | Nasdaq-100 inclusion | | |
| | Earnings date announced | | update timeline Phase 4 |
| | Earnings: xAI burn / Starlink subs / guidance | | thesis confirmed or falsified |
| | T+2: insider selling volumes (Form 4) | | |

## 6. Deadline reminders

- [ ] ~Jun 19-24: check SPCX options listing
- [x] Jul 6-17: strategy B entry window — checked 2026-07-06: IV ~83-87% > 55% gate → stand-down, no entry (§2 #001). Retry Jul 24 @ 60%. Window-close check 2026-07-16: spot $135.27 < $140, IV ~80-86%, debit $2.89 > $2.30 — all gates fail, front-run. Jul 24 retry moot unless spot > $140 AND IV < 60%.
- [ ] Jul 24: Fallback-1 retry decision — expected outcome: formal cancel of Strategy B (spot gate dead)
- [ ] Sep 16: final spread decision (NEVER into expiry between the strikes)
- [ ] ~Oct 25: day 135, full review
- [ ] Dec: year-end tax optimization ([05-tax-italy.md](05-tax-italy.md))
- [ ] Mar 2027: filing documents (RW, RT, RM, IVAFE)

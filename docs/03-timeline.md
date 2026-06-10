# 03 — Operational timeline (June 10 → December 31, 2026)

Every action has: date, trigger condition, exact operation, fallback. Post-August dates depend on the first earnings date (to be announced by SpaceX: update this file as soon as known).

---

## PHASE 0 — Preparation (Tue Jun 10 → Thu Jun 11)

**Goal: be operational BEFORE the debut, without placing a single trade.**

- [ ] Open/verify the broker account. Request options-spread permissions (MiFID questionnaire for EU accounts).
- [ ] Fund the account (SEPA: 1-2 business days → do it NOW).
- [ ] Convert the equity-tranche amount to USD (min $2 FX fee). Keep the reserve in EUR.
- [ ] Build the watchlist: SPCX, GOOGL. Price alerts: SPCX at $120, $135, $150, $175.
- [ ] Jun 11 evening: read the final pricing. If priced above $150, overvaluation worsens, short thesis reinforced; no action.
- [ ] **Forbidden**: any SPCX order in this phase.

## PHASE 1 — Debut: observation only (Fri Jun 12 → Fri Jun 26)

**Goal: collect data. Day-1 is when retail loses the most. You do not trade SPCX.**

- [ ] Jun 12: log in the journal: open, high, close, volume. Compare with Polymarket (99% above $1T was near-certain; what matters is BY HOW MUCH).
- [ ] Jun 12-13 (optional, recommended): execute tranche A — GOOGL limit order at ≤ last close, GTC 3 days. GOOGL does not depend on SPCX timing: no rush, no chasing. If unfilled after 3 days, raise the limit 0.5% once.
- [ ] ~Jun 19-24: **check SPCX options listing** (typically 4-7 trading days post-IPO). Once listed, log daily: ATM IV for September expiry, spot.
- [ ] Every Friday: IV percentile vs days observed. Operational threshold: **ATM IV < 55%**.
- [ ] **Forbidden**: buying options in this phase (IV 75-90%: every purchase is a gift to the market maker).

## PHASE 2 — Index inclusion and IV crush (Mon Jun 29 → Fri Jul 17)

**Goal: let passive flows inflate the price (better for the spread) and let IV deflate (better for the cost).**

- [ ] ~Jul 3: expected Nasdaq-100 inclusion (15 trading days from Jun 12). ~$30B passive flows → possible push higher. Do NOT read it as "the thesis is wrong": it is mechanics, not fundamentals.
- [ ] **Strategy B entry window: Jul 6-17**, at the FIRST occurrence of ALL conditions:
  - September ATM IV < 55%
  - SPCX spot > $140 (the 140/135 spread must be OTM; if spot is already below, the edge is consumed → see fallbacks)
  - 140/135 Sep spread debit ≤ $2.30
- [ ] Execution: combo order "bear put spread" (never the two legs separately — leg risk), limit at mid, up to 3 days of patience.
- [ ] Log: debit paid, IV at entry, spot, spread greeks (delta, theta).
- [ ] **Fallback 1**: IV not below 55% by Jul 17 → retry Jul 24 with threshold relaxed to 60%. Still no → **cancel strategy B**; cash stays cash.
- [ ] **Fallback 2**: SPCX already below $135 before entry → the market front-ran the thesis; do NOT chase with lower strikes. Strategy B cancelled.
- [ ] **Fallback 3**: earnings date announced after Sep 18 → move expiry to October; recompute budget (Oct costs ~15-20% more; if debit > $2.60 narrow the width or cancel).

## PHASE 3 — Disciplined waiting (Jul 20 → earnings)

**Goal: touch nothing. The debit spread's theta bleeds slowly while spot stays above 140; that is the planned cost of waiting.**

- [ ] Weekly check (15 min, Friday): spot, spread value, earnings-date news. Log it.
- [ ] If SPCX holds +30% above $135 (> $175.50) for 5 of 10 sessions: the extra 10% insider tranche unlocks. Consider rolling the long strike 140 → 150 ONLY if roll cost ≤ 30% of original debit AND before Aug 1.
- [ ] If the spread loses 50% of value before earnings with the thesis intact (pure theta/rally): HOLD. The payoff is binary on the August event; selling early throws away the part of the premium that pays for the event.
- [ ] **Forbidden**: adding contracts, "averaging down", opening B2 on top of B.

## PHASE 4 — The event: earnings + insider unlock (~August, dates TBC)

**Goal: execute the rules written in July, not the emotions of August.**

T = first earnings release. T+2 = first insider selling day (20% of holdings).

- [ ] T: read the numbers. Three data points decide everything: quarterly xAI burn (expected ~$2.5B), Starlink subscriber growth, guidance. Log them.
- [ ] T+2 → T+7: critical window. Daily monitoring (open + close).
- [ ] **Take profit**: spread value ≥ 70% of max gain → close with a combo limit order.
- [ ] **Event-study exit rule** (notebook 00, sec. 7 — UBER/RIVN/META/SNAP): the lockup drop is ANTICIPATION-driven (-37 pts avg T-30→T0) and T0 is often a local bottom (+19 pts T0→T+20). Therefore: close the spread WITHIN T+5 of the unlock, whatever the P&L — do not wait for a continuation that historically does not come.
- [ ] **Falsification**: at T+7 SPCX not below the T price (insiders don't sell or the market absorbs): close recovering residual value (~30-50% of debit). Log the lesson.
- [ ] **Violent-crash scenario** (SPCX < $120 in days): spread near max value. Close at ≥ 90% of width without waiting for 100% (ITM spread liquidity worsens).
- [ ] Reserve (tranche C) decision: ONLY after T+7.
  - SPCX below ~fair value +10%: consider a small long position for the long run, conditional on xAI burn declining QoQ.
  - Thesis confirmed with momentum (more unlocks coming through day 135): consider a second spread, Oct/Nov expiry, same sizing rules.
  - Neither: cash stays cash. A valid outcome.

## PHASE 5 — Lockup tail (September → ~Oct 25, day 135)

- [ ] Sep 18: spread expiry (if still open, decide by Sep 16: NEVER carry a spread into expiry with spot between the strikes — short-leg assignment risk).
- [ ] 7% tranches unlock at regular intervals through day ~135 (~Oct 25): recurring sell pressure. Tailwind for any short from tranche C; headwind for an early long.
- [ ] Late October: full plan review. The post-lockup price is SPCX's first "true" price.

## PHASE 6 — Year-end and taxes (November → December)

- [ ] Download the broker's annual activity statement.
- [ ] Compute realized gains/losses (see [05-tax-italy.md](05-tax-italy.md)): 2026 realized losses offset gains through 2030.
- [ ] If strategy B closed at a loss and GOOGL is well up: consider realizing part of the GOOGL gain before Dec 31 to absorb the loss → tax saving of 26% of the loss. Only if sensible for other reasons too (transaction costs, repurchase price risk).
- [ ] 2027 filing reminders: RW form (foreign account), RT form (capital gains), IVAFE.
- [ ] Written retrospective in the journal: what worked, what didn't, ex-ante EV vs ex-post result.

---

## Date summary table

| Date | Event | Action |
|---|---|---|
| Jun 10-11 | Pre-IPO | Account setup, funding, FX, alerts. Zero trades |
| Jun 11 eve | Pricing | Read only |
| Jun 12 | SPCX debut | Observe. Optional GOOGL limit order |
| ~Jun 19-24 | Options listing | Start daily IV tracking |
| ~Jul 3 | Nasdaq-100 | No action (mechanics, not thesis) |
| Jul 6-17 | Strategy B window | Spread ONLY if IV<55% + spot>$140 + debit≤$2.30 |
| ~Aug (T) | First earnings | Read the xAI burn |
| T+2 | 20% insider unlock | Daily monitoring |
| T+2→T+7 | Critical window | Take profit ≥70% / falsification → close; exit by T+5 regardless |
| post T+7 | Reserve decision | Long near fair value / second spread / nothing |
| Sep 16-18 | Spread expiry | Never into expiry between the strikes |
| ~Oct 25 | Day 135, lockup done | Full review |
| Dec | Taxes | Offsets, statements, retrospective |

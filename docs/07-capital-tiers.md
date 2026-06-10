# 07 — Capital tiers: the same theses from €2k to €10M+

The theses (don't buy the debut; the August lockup is the dated catalyst; long only via quality proxies until fair value) do not change with capital. What changes is **which instruments become available, which risks become manageable, and which edges stop being theoretical**. Each tier inherits everything from the tier below and adds tools.

A structural truth first: **edge per euro SHRINKS as capital grows** (your size starts moving prices, and the inefficiencies you can harvest get arbitraged by professionals at scale), but **edge variety GROWS** (more instruments, more venues, more structures). Small accounts have one advantage no fund has: they can do nothing without being fired for it.

---

## Tier 1 — €1k-10k (the reference implementation)

**Binding constraints**: minimum option ticket = 10-20% of capital → textbook sizing impossible; fixed costs ≈ 1%/year hurdle; PRIIPs blocks US ETFs (EU); no portfolio margin.

| Available | Not available |
|---|---|
| Defined-risk verticals (1-2 contracts) | Proper 1-2% sizing on derivatives |
| Quality proxy stocks (GOOGL) | Direct shorts (borrow + unlimited risk) |
| Cash optionality | Iron condors (commission drag), calendars |

**Playbook**: exactly [02-strategies.md](02-strategies.md). One defined-risk spread on the catalyst, majority in a quality proxy, reserve in cash. Expected edge after friction: ≈ 0; you are buying process and a track record.

**The one luxury of this tier**: zero market impact, total freedom to abstain.

---

## Tier 2 — €10k-100k (sizing unlocks)

**What changes**: the spread ticket falls to 0.5-5% of capital → real position sizing exists; multi-leg structures stop being eaten by commissions; you can run a small book of uncorrelated expressions instead of one bet.

New instruments/structures:
- **Iron condors** on the "stall" thesis (sell both inflated wings post-IV-crush, defined risk, now ~$8 commissions on a $1,500+ structure is noise).
- **Calendar spreads**: short front-month IV (inflated by the event), long back-month — monetizes the IV term-structure kink around the earnings date.
- **Collared proxy**: GOOGL + protective put financed by covered call → beta exposure with capped drawdown; the put cost is the explicit price of removing the left tail that dominated the Tier-1 Monte Carlo.
- **Laddered entries**: 3 tranches on the spread (Jul / pre-earnings / post-falsification-check) instead of one shot.
- **A shovels basket**: NDAQ + VIRT + GS/MS sized by risk parity (notebook 02 data: VIRT is the best risk-adjusted shovel, HOOD the worst despite the narrative).

**Sizing rule**: max 2% capital-at-risk per expression, max 3 correlated expressions, total SpaceX-theme risk ≤ 10% of capital.

**Tax (IT)**: same as Tier 1; from ~50 trades/year a specialized accountant pays for itself.

---

## Tier 3 — €100k-1M (the professional toolkit)

**What changes**: portfolio margin (risk-based instead of rule-based), securities lending income, access to better data, and shorts become genuinely manageable.

New instruments/structures:
- **Direct short post-unlock**, properly sized (≤5% of capital, hard stop): borrow on a mega-cap with a $75B+ float is findable; the borrow fee (est. 5-25% annualized early, falling) is now a calculable cost, not a wall.
- **Risk reversals** (sell call, buy put) on SPCX into the lockup window: collects the call-skew richness that retail FOMO creates. Margin-intensive: needs portfolio margin.
- **Pairs**: long GOOGL / short SPCX beta-matched — isolates the "SpaceX premium vs its own largest outside shareholder" spread, removes market direction entirely.
- **Index-event flows**: the Nasdaq-100 fast-entry creates forced buying around inclusion day; NDX futures/options around rebalance dates express it cleanly (this is a crowded professional trade — expect thin edge, but at this tier you can at least sit at the table).
- **Form 4 systematic monitoring** (`src/connectors/edgar.py` becomes a cron job): position-adjust within hours of insider-sale disclosures, not days.

**Risk framework**: daily VaR (the repo's Monte Carlo extended to the full book), Greek limits (net delta, vega caps), pre-defined drawdown circuit breakers (-5% month → halve all sizes).

**Tax (IT)**: declarative regime gets heavy; evaluate regime amministrato trade-offs or professional structures; the GOOGL-gain/spread-loss offsetting from Tier 1 now moves four-digit amounts — plan it, don't improvise it.

---

## Tier 4 — €1M-10M+ (access replaces structure)

**What changes**: the edge stops being "which option structure" and becomes **access** — to inventory, to OTC, to primary allocations, to people.

New instruments/venues:
- **Pre-IPO secondaries** (the trade that mattered happened BEFORE this repo existed: SpaceX secondaries traded at $400-700B valuations in 2023-25 — accredited platforms and SPVs; the retail version of this repo could only watch). For the NEXT SpaceX, this tier plays a different game entirely.
- **IPO allocations** via prime-broker relationships: being IN the book at $135 with a 4x oversubscribed deal is a near-mechanical day-1 profit — the exact profit the retail plan refuses to chase on the secondary.
- **OTC options**: strikes/expiries that don't exist on screen (e.g. a 135-day put matching the full lockup schedule), at institutional spreads.
- **Securities-lending revenue**: holding SPCX long? Lending it to the shorts at 10-25% annualized in the early weeks pays you the volatility either way — the purest "picks and shovels" trade in the whole document, available only to size.
- **Structured notes**: capital-protected SPCX participation (buy the bond floor, spend the coupon on calls) — the institutional version of "I want exposure but cannot lose much".
- **Block liquidity**: exiting 50k shares without moving the tape requires dark pools/crossing networks; at this tier execution quality IS a strategy.

**The honest inversion**: at this tier the August-lockup spread from Tier 1 is almost too small to bother with. The real questions become tax structuring, custody, counterparty risk, and whether the position is worth its operational overhead. Many Tier-4 players would express the entire thesis as: lend shares to shorts, sell the call skew, and let both sides pay them.

---

## Cross-tier summary

| | T1 €1k-10k | T2 €10k-100k | T3 €100k-1M | T4 €1M+ |
|---|---|---|---|---|
| Core short expression | 1 put spread | laddered spreads + condor | direct short + risk reversal | OTC puts + lend stock to shorts |
| Core long expression | proxy stock | collared proxy | pairs (long proxy/short target) | pre-IPO secondaries, allocations |
| Sizing per idea | 10% (forced) | 2% | 0.5-2% + Greek limits | mandate-level |
| Friction | ~1%/yr (dominant) | ~0.3%/yr | bps + borrow | bps + structure costs |
| The binding constraint | ticket size | discipline | risk infrastructure | access, tax, ops |
| Edge per euro | ≈0 after friction | thin | thin but multi-expression | comes from access, not analysis |

**The experiment's meta-finding so far**: AI compresses the ANALYSIS gap between tiers to near zero — this repo's research, validation and risk engine are tier-agnostic. What AI cannot compress (yet) is the ACCESS gap: allocations, OTC, borrow, secondaries. The information playing field is flattening; the plumbing one is not.

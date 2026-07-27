# LOGBOOK — what was decided when, and what broke

Chronological process record for the ex-post evaluation. One entry per working session.
The mistakes are data: this experiment grades the AI's process, and a process that hides
its own bugs cannot be graded. Append-only; entries are never rewritten.

---

## 2026-06-10 (T-2) — research, plan, quant stack, pre-registration

**Built**: multi-source research (76 items) → thesis (docs/01) → strategies with full math
(docs/02) → timeline (docs/03) → risk rules (docs/04) → tax case study (docs/05) → journal
(docs/06) → capital tiers (docs/07) → gap playbook (docs/08). Quant stack: 6 connectors,
risk metrics, Monte Carlo, lockup event study, fat-tail validation, signal-quality
framework, 6 notebooks, checkpoint system, predictions + evaluation protocol.

**Key decisions**:
- Defined-risk only; no day-1 trades; the August lockup is the dated catalyst.
- Student-t MC after FITTING dof on real data (5.3 on TSLA 2y) rather than assuming it.
- Issues-vs-warnings split in the quality gate after two false positives (see bugs).

**Bugs caught and fixed** (each found by a test or by reading the output, not by luck):
1. Parquet cache ignored the `period` argument — TSLA "5y" silently returned 6 cached
   months; first distribution fit was wrong (Normal beat t). Found because the validation
   assert failed. Fix: period in the cache key.
2. Quality gate flagged ASTS +50% (real: AT&T deal) and ^VIX Fed-day spike as data errors.
   Fix: jumps demoted from blocking issues to human-review warnings.
3. Wikipedia API 429 after repeated runs. Fix: disk cache + exponential backoff.
4. Event-study assert assumed the lockup drop happens AFTER expiry; data showed the
   opposite (anticipation, -37 pts T-30→T0; T0 often a local bottom). The "bug" was in the
   thesis, not the code — exit rule rewritten to close within T+5 of the unlock.

**Frozen**: `checkpoints/2026-06-10-baseline` (9 artifacts, incl. 20 live Polymarket markets).

## 2026-06-11 (T-1, pricing day) — chart overhaul, data-quality audit, evaluation hardening

**Built**: finding-as-title chart style; decomposed sensitivity (total vs spread-only);
notebook 05 (data-quality audit); README gap bars + follow-along timeline; explicit
ex-ante probabilities added to PREDICTIONS (amendment, pre-debut); benchmarks
(VWCE.DE, EURUSD=X) added to checkpoints; this logbook.

**Bugs caught and fixed**:
5. Italian leftover ("media") inside the MC chart — found by LOOKING at the rendered PNG.
6. HN attention line invisible: Algolia caps any single query at ~1,000 hits → 180 requested
   days, 25 delivered, z-score all-NaN. Naive fix (more pages) reached only 57 days. Real
   fix: time-windowed pagination (20-day slices) → 181/180 days. Now visualized in
   notebook 05 and guarded by an assert (fails loudly below 60 days of coverage).
7. Sensitivity chart contradicted the written conclusion ("EV>0 requires jump ≤ -5%"):
   the total was padded by the GOOGL drift assumption. Fix: decompose, and state that the
   crossover is prior-dependent until real IV exists.

**Later the same day — autonomy + a ticker-collision catch**:
- Checkpoints extended to capture SPCX OHLCV + full option chains (with IV) once listed.
- **Bug 8, the best catch so far**: yfinance already answers for "SPCX" — with a $135
  zero-volume placeholder quote AND option chains (strikes $21-32) belonging to the
  pre-2026 SPCX ETF. Without a guard, the snapshots would have archived the WRONG
  instrument as SpaceX. Fix: identity validation (volume + strike/price coherence) writes
  `identity_suspect` + `quality_flags` into every snapshot instead of trusting the symbol.
- GitHub Actions workflow added: automated snapshots Mon+Thu after US close, plus manual
  `workflow_dispatch` with milestone labels. The historical record now collects itself;
  the human only fires milestone labels and keeps the trade journal.

**Disaster recovery**: private mirror `spcx-ipo-strategy-2026-mirror` created with full
history + tags. Its `mirror-ops` default branch runs a daily pull-based sync (no secrets:
it clones the public repo anonymously and force-updates its own `main` + tags). Degrades
gracefully while the upstream is private; activates automatically upon publication. If the
public repo is ever banned/deleted, the mirror holds the last good state of everything.

**Open items for the next session**: checkpoint `day1` on Jun 12 evening (manual dispatch);
real IV into `McConfig` once options list and `identity_suspect` turns false (~Jun 24).

## 2026-06-15 (T+3) — first real run, audit, dual-class fix

**Built**: auto-scoring of elapsed predictions (`tools/score.py`, read-only on PREDICTIONS).
Self-archived first post-debut snapshots.

**Bugs caught and fixed** (PRs #1–#5, full write-up in the private mirror `AUDIT-2026-06-15.md`):
9. Benchmark/SPCX fetch failures were not surfaced in MANIFEST `errors{}` — routed in.
10. **CRITICAL: dual-class market-cap undercount.** `yfinance.sharesOutstanding` returns Class A
    only (~7.49B) → cap $1.205T → would have scored **P2 FALSE**. The 424B4 prospectus is
    dual-class: 13,075,865,175 total shares → cap **$2.105T → P2 TRUE**. Caught because two
    yfinance fields disagreed. Scoring now uses the authoritative 424B4 count.
11. Empty-payload-as-success, no alert on partial failure, yfinance monoculture on SPCX, share
    drift — hardened (`note_empty`, `tools/gate.py`, Stooq fallback, drift flag).

## 2026-06-20 (T+8) — second audit, resilience fixes, post-IPO review

**Built**: CI test workflow (`.github/workflows/tests.yml` — the suite never ran in CI before),
`tools/verify_checkpoints.py` (automates the immutability claim; 10/10 checkpoints verified
clean), QA plan (`docs/09`), and this notebook 06 post-IPO review layer.

**Bugs caught and fixed** (PRs #6–#9, mirror `AUDIT-2026-06-20.md`):
12. **HIGH: scoring drift.** `score.py` scored the day-1 predictions off the *latest* checkpoint's
    rolling close (185 → $2.419T) instead of the frozen 2026-06-12 close (160.95 → $2.105T). Once
    SPCX closed below $152.95 on any checkpoint day, P2 would auto-flip to FALSE — a resolved fact
    un-resolved. Fixed: `day1_snapshot()` pins to the immutable debut bar.
13. Stooq fallback 404'd for every index (`^GSPC/^NDX/^VIX`: wrong symbols) and one dead ticker
    wiped the whole universe (no per-ticker isolation). Both fixed; also guard against Stooq's new
    anti-bot challenge serving HTML-as-CSV.
14. HN dedup by `title` collapsed recurring headlines across days → dedup by `objectID`.

**Key decision**: keep the pre-registration frozen. Notebook 06 is an *added* predicted-vs-realized
layer — it never touches PREDICTIONS.md, the metrics, or the baseline notebooks/charts.

**Resolved (from the Jun 11 open items)**: `day1` checkpoint captured (the 2026-06-12 close is
frozen and immutable); `identity_suspect` cleared by Jun 18, real options listed.

**The debut, scored**: $135 IPO → $160.95 day-1 close (+19.2%), $2.105T cap → **P1 and P2 both
TRUE**. Calibration held (Polymarket cap>$2T ~0.63, our P2 0.60, both right). The model under-vol'd:
assumed 70% vs listed ATM IV ~88% for the August expiry — the put spread is richer than baseline.

**Open items**: add a second independent SPCX price source (yfinance near-monoculture; Stooq
degrading); July spread entry; August earnings + insider unlock; `form4_watch()` goes live.

---

## 2026-07-06 (entry window, T+24) — real IV meets the model, first live decision

**Built**: post-IPO realized layer. Closed the open item from Jun 11 (*real IV into McConfig
once identity_suspect turns false*).
- `notebooks/07_entry_decision.ipynb` (+ self-contained `tools/build_notebook_07.py`): identity
  re-check on live data, baseline-vs-realized params, MC re-run, and the MC-cone-vs-realized
  overlay chart. Baseline notebooks 00-05 and `PREDICTIONS.md` left frozen.
- `checkpoints/2026-07-06-entry-window`: the pre-registered `entry-window` snapshot
  (EVALUATION.md schedule). `identity_suspect` now **false**; McConfig frozen on real params.
- `checkpoint.py` now archives `derived_atm_iv` (BS-inverted from option `lastPrice`) per
  expiry — the free feed's `impliedVolatility` column is broken and there are no live bid/ask,
  so this is the study's only usable vol signal, and it is now captured on every auto-snapshot.
- `checkpoint.py` also archives the full SPCX price history (`spcx_ohlcv.parquet`) into every
  snapshot — the non-reconstructible target series is now committed evidence, not just a
  10-row tail (and not the gitignored `data/`).

**Key decisions**:
- **Stand-down, no order.** Entry gate is *Sep ATM IV < 55%*; realized IV ~83-87%. Spot
  ($162) and debit (~$1.99) passed, IV did not. Bought nothing — inflated post-IPO IV is a
  gift to the market maker (Phase 2 Fallback 1). Retry Jul 24 @ 60%, else cancel B.
- `McConfig` kept **frozen** at the ex-ante baseline (150/0.70/2.20) — it is the object
  notebook 06 scores "assumed vs realized IV" against, so mutating it would break that
  calibration. Realized params (close, Aug ATM IV, BS debit) are derived from archived
  checkpoint evidence and applied **explicitly** in notebook 07. (An earlier revision of this
  work wrongly edited the McConfig defaults; reverted once the parallel 06 layer surfaced.)
- P1/P2 (resolved TRUE on the Jun 12 debut) are left to the existing scoring path
  (`tools/score.py` + `checkpoints/SCORING.md`); `PREDICTIONS.md` stays frozen, untouched.
- This layer is notebook **07** (`07_entry_decision`), distinct from the frozen **06**
  post-IPO *calibration* review — the two are complementary, not duplicates.

**Bugs caught** (continuing the shared numbering):
- **Bug 15**: importing `tools.build_notebooks` runs its module-level build → silently
  regenerated (output-stripped) the frozen baseline notebooks 01-05. Restored from git; made
  `build_notebook_07.py` self-contained so generating the new layer never touches the baseline.
- **Bug 16**: MC `__main__` hard-cap assert hardcoded the literal `2.20` instead of
  `spread.debit`; would have gone stale the moment the debit changed. Now tracks `SpreadPosition().debit`.
- **Bug 17**: `make_gif.py` breakeven hardcoded `140 - 2.20`; now `long_strike - debit`.

**Frozen**: `checkpoints/2026-07-06-entry-window` (14 artifacts, SHA256 manifest, 0 errors).

**Open items**: monitor Jul 24 fallback (IV still ~83% → likely cancel B); `earnings-T`
checkpoint when SpaceX announces the first earnings date (drives the whole Phase 4).

---

## 2026-07-16 (entry-window close, T+34) — window closes with no entry, front-run confirmed

**Built**: window-close re-check (issue #18). No new model layer — notebook 07 stays frozen
as the record of the Jul 6 decision; this entry only measures the window's final state.
- `checkpoints/2026-07-16-entry-window-close`: frozen via workflow_dispatch (label
  deliberately *not* `entry-window` — that name belongs to the pre-registered Jul 6 snapshot).
  `identity_suspect` false; close $135.27; derived Aug ATM IV ~86%, Sep ~80%.
- MC re-run with realized params (s0=135.27, vol=0.858 Aug ATM IV mean, debit=2.89, notebook 07
  derivation, McConfig untouched): hard cap held on all 10k paths (worst spread -€249.1 = cap).
  p_loss 0.38 / VaR95 €332 / ES95 €404 / mean €55 vs baseline 0.38 / €306 / €378 / €69.
- `docs/06-trade-journal.md`: §2 window-close table, §3 weekly row, §5 event, §6 reminders (additive).
- Notebook 06 realized overlay + post-IPO gif refreshed through Jul 15 close (baseline cells frozen).

**Key decisions**:
- **Window closes with NO ENTRY — all three gates fail.** IV ~80-86% (gate <55%), spot $135.27
  (gate >$140), debit $2.89 (cap $2.30). The anticipated drop happened *without* a position:
  spot $162 → $135.27 in seven sessions, a hair above the $135 front-run invalidation. The
  thesis was directionally right and the entry gates still said no — buying the spread now
  would pay $2.89 for a $5 width with the move already spent. Process held in both directions.
- Jul 24 Fallback-1 retry is effectively moot (IV still fails 60%, spot gate dead); expected
  outcome is formal cancellation of Strategy B unless spot > $140 with IV < 60% by then.

**Bugs caught** (continuing the shared numbering, second pass same day — autonomy audit):
- **Bug 18**: `checkpoint.py` archived only the first 6 option expiries — the **Sep 18 spread
  expiry (the entry-gate IV) was never frozen evidence**, and late-Aug unlock-month expiries
  fell off as weeklies accumulated. Every gate decision so far cited Sep IV from a *live*
  fetch, not the archived snapshot. Fixed: `_select_expiries()` = near-6 + all 2026-08 + the
  2026-09-18 study expiry, deduped; regression tests added.
- Stale ops docs: weekly-health reminder prompt still expected "13 artifacts" (now 14) and
  never checked Sep IV presence; no reminder existed for the Jul 24 Fallback-1 decision.
  Both fixed in `tools/reminders.json` (new dated reminder `fallback1-retry`, lead 2 days).
- `docs/html/06_post_ipo_review.html` was a stale Jul 6 render and `nbconvert` wasn't even in
  the venv (README promises zero-setup HTML). Re-rendered; `nbconvert>=7.16` pinned in
  requirements so the render step is reproducible.
- **Bug 19** (third pass, user-reported): the README showed **two "cone vs realized" visuals
  telling different stories** — `chart_mc_vs_realized.png` was notebook 07's frozen Jul-6 export
  (realized ending $156, "back inside") next to a gif refreshed through Jul 15 ($135). Root
  causes: (a) a *decision-record* export doubling as a *living* README asset, (b) three visuals
  reading three data sources (pinned checkpoint / live fetch / live fetch), (c) same-day
  checkpoint dirs sorting wrong lexically (`-entry-window-close` > `-1457-auto`). Fixes:
  `tools/evidence.py` (single evidence reader: latest checkpoint by MANIFEST `created_utc`,
  realized closes, unlock-month IV) now feeds **all** post-IPO visuals; new
  `tools/make_mc_vs_realized.py` regenerates the png as a living overlay from the same evidence
  (the Jul-6 record stays embedded in frozen notebook 07); notebook 06's cone horizon now grows
  with the tape (fixed 45 would IndexError ~mid-Aug); README captions updated to the window-close
  reality. 4 regression tests (`test_evidence.py`).

**Frozen**: `checkpoints/2026-07-16-entry-window-close` (0 errors).

**Open items**: Jul 24 formal Fallback-1 decision (likely cancel B; reminder now automated);
`earnings-T` checkpoint when SpaceX announces the first earnings date; first post-fix
auto-snapshot must show `derived_atm_iv["2026-09-18"]` (verify triggered same day).

## 2026-07-27 (Fallback-1 decision, T+45) — Strategy B formally cancelled, cash stays cash

**Built**: the Fallback-1 retry check (issue #23). No new model layer — notebook 07 stays frozen
as the Jul 6 record; this entry closes out Strategy B.
- `checkpoints/2026-07-27-fallback1-decision`: frozen via workflow_dispatch, 14 artifacts,
  0 errors, `identity_suspect` false, no quality flags. Evidence close **Fri Jul 24 $115.07**;
  archived `derived_atm_iv` gives **Sep 18 ATM 101.3%**, Aug mean **128.5%**. All three gates
  read from this snapshot only — no live fetch anywhere in the decision.
- Counterfactual MC (s0=115.07, vol=1.285 Aug ATM mean, debit=3.66 BS-derived at Sep IV,
  notebook-07 derivation, `McConfig` untouched): hard cap held on all 10k paths (worst spread
  path −€315.5 = the cap exactly). Spread-only p_loss 0.24, mean +€12.1, **max gain €115.5 vs
  max loss €315.5** — the payoff has inverted versus the ex-ante €241/€190.
- `docs/06-trade-journal.md`: §1 account row, §2 dated Fallback-1 decision table, §3 weekly row,
  §5 event, §6 reminder ticked + Sep 16 expiry reminder struck as moot (all additive).
- Post-IPO visuals refreshed off the new evidence (`chart_mc_vs_realized.png`,
  `chart_post_ipo.png`, `mc_paths_post_ipo.gif`, notebook 06 re-executed); README post-IPO
  section and milestone table updated from "expected to cancel" to the decision itself.
- `docs/html/07_entry_decision.html` added — the entry-decision notebook was the only one
  missing from the zero-setup HTML render the README promises.

**Key decisions**:
- **Strategy B is CANCELLED. No order was ever placed; the 20% tranche stays cash to Dec 31.**
  Relaxed Fallback-1 gates: Sep ATM IV 101.3% (gate < 60%), spot $115.07 (gate > $140), debit
  $3.66 (cap $2.30) — three for three, by wider margins than at the window close. Spot is
  $19.93 *below* the $135 line, so **Fallback 2 fires independently** ("front-run → do NOT
  chase with lower strikes"). Two pre-registered fallbacks converge on the same branch.
- **The thesis was right and the trade is still a no.** SPCX went $162 → $115 in three weeks —
  the lockup-anticipation drop the plan called. Entering now would pay $3.66 for a $5-wide
  structure whose move is spent: $1.34 of remaining upside against $3.66 at risk, needing ~73%
  just to break even. Being directionally right does not licence chasing a consumed edge; that
  is exactly the failure mode the front-run invalidation was pre-registered to prevent.
- IV never crushed — it *expanded* into the drop (Sep ATM 80% → 101%, Aug 86% → 129%). The
  Phase-2 premise ("index inclusion inflates price, IV deflates") was falsified by the tape.
  Recorded as a falsified premise, not smoothed over.

**Bugs caught**: none this pass. Integrity re-verified: `gate.py` clean on the new snapshot,
`verify_checkpoints.py` 24/24 hash-matched, mirror at sha parity with public `main`.

**Frozen**: `checkpoints/2026-07-27-fallback1-decision` (14 artifacts, 0 errors).

**Open items**: Strategy A (GOOGL proxy) and the experiment's scoring track continue unchanged;
`earnings-T` / `unlock-T7` checkpoints when SpaceX announces the first earnings date — now
pure observation, with no position to manage; day-135 review Oct 25; final scoring + `VERDICT.md`
Dec 31, which must state plainly that the strategy the whole plan was built around never traded.

## 2026-07-28 (T+46) — P3 scored 18 days late, stale reminder prompts defused

**Built**: post-cancel sweep. Weekly health check run end-to-end (it had been sitting open since
Jun 20, so the weekly cadence had quietly stalled): all seven points green — cron on its Mon/Thu
beat, `gate.py` clean, `verify_checkpoints.py` **25/25**, latest snapshot 14 artifacts / 0 issues /
Sep-18 IV present, SCORING pinned to the frozen $2.105T, mirror at sha parity, 58 pytest + 12/12
smoke. Results posted to issue #14 and #22 (entry-window milestone) closed; no open issues left.
- Post-IPO visuals refreshed off `2026-07-27-2232-auto` (close $113.50, Sep ATM IV 101.1%) — the
  evening auto-snapshot had landed after the PR #24 merge, leaving the living assets one session
  behind their own evidence source.

**Bugs caught** (continuing the shared numbering):
- **Bug 20 — a resolved prediction sat unscored for 18 days.** `SCOREABLE` in `score.py` only ever
  held P1/P2. **P3** ("in the first 4 weeks SPCX never closes below $135", verify **Jul 10**) had
  no entry, so `score.py` reported nothing and the elapsed verify date passed unnoticed — the
  scorer runs on every checkpoint and was silent by construction. The repo's whole claim is that
  predictions get scored when their date arrives; this was that claim quietly failing. Fixed: new
  **`window_min` basis** (minimum close over a *closed* window, price-compared) pinned to the
  **earliest** checkpoint whose history covers the window end — so the evidence for a resolved
  prediction never drifts forward with the tape, and a snapshot that stops short of the end date
  yields `unverifiable` rather than an extrapolation. 6 regression tests, including the one that
  matters: the $115 late-July tape must **not** flip a prediction that resolved on Jul 10.
  **P3 = TRUE**, min close **$145.30** (Jul 10) vs the $135 floor, ex-ante P 0.70, evidence
  `2026-07-13-2224-auto`. `SCORING.md` now carries a per-prediction Evidence column — with mixed
  bases a single header checkpoint was misleading.
- **Stale reminder prompts, one of them live.** The `spread-entry` reminder re-fired on Jul 20
  (issue #22, last day of its grace window) still carrying the pre-PR-#17 instruction to mutate
  `McConfig` — the exact operation that was reverted and forbidden. Body replaced with a
  SUPERSEDED banner, original folded into a `<details>` block as the historical record. Worse,
  `earnings-unlock` fires **Jul 29** and its step 4 asked whether the T+5 exit rule held on a
  position that no longer exists; rewritten for the no-position reality (honest counterfactual
  instead of a phantom trade) and pointed at the `window_min` work as the pattern for the
  event-relative basis P4/P5 will need.

**Key decisions**:
- Strategy B's cancellation mechanically settles **K2** ("the worst loss, if any, comes from the
  equity tranche, not the spread") — with no spread there is no spread loss. Recorded here so the
  Dec 31 scoring counts it as *structurally* resolved, not as a forecasting hit: an ex-ante 0.75
  that a cancelled leg made trivially true is not calibration evidence, and `VERDICT.md` must say so.

**Frozen**: no new checkpoint — this pass reads `2026-07-27-2232-auto` and the earlier snapshots.

**Open items**: P4/P5 need an event-relative basis in `score.py` once the earnings date is known
(`earnings-T`); P6/K1/K3 at year end; `earnings-T` / `unlock-T7` checkpoints as pure observation.

---

*Template for future entries: date (T±n) — built / key decisions / bugs caught / frozen / open items.*

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

*Template for future entries: date (T±n) — built / key decisions / bugs caught / frozen / open items.*

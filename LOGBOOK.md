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

**Open items for the next session**: checkpoint `day1` on Jun 12 evening (manual dispatch);
real IV into `McConfig` once options list and `identity_suspect` turns false (~Jun 24).

---

*Template for future entries: date (T±n) — built / key decisions / bugs caught / frozen / open items.*

# 09 — Quality assurance plan: how to keep this experiment trustworthy

The product of this repo is not code, it is **correctly-scored falsifiable predictions backed
by immutable evidence**. A bug here does not crash an app — it silently records a TRUE outcome
as FALSE, or freezes the wrong instrument as SpaceX, and corrupts the one thing the experiment
sells: credibility. This plan is the standing test strategy that protects that.

It is written to be run by the maintainer or a future AI agent, with concrete commands and
ownership of each guarantee. It assumes the post-audit state (2026-06-20): scoring pinned to the
frozen day-1 close, per-ticker isolation in the universe fetch, HN dedup by objectID, a CI test
workflow, and `tools/verify_checkpoints.py`.

---

## 1. The four invariants that must never break

Everything below exists to defend these. If you only have five minutes, check these.

1. **Pinned scoring.** A prediction is scored against the *frozen evidence for its verify date*,
   never against live/latest data. A correctly-resolved fact must not change outcome when the
   market moves later. (Regression: `tests/test_score.py`.)
2. **Evidence immutability.** A committed checkpoint is never modified. Artifact bytes match the
   sha256 frozen in its `MANIFEST.json`. (`tools/verify_checkpoints.py`, in CI.)
3. **No silent degradation.** A source that errors *or* returns empty lands in `errors{}` and
   trips the run gate (red run), instead of freezing a blank artifact as green.
   (`tools/gate.py`, `note_empty()`.)
4. **Identity before trust.** Market data for a ticker is validated as the intended instrument
   (volume + strike/price coherence) before it is consumed; `identity_suspect` gates downstream
   use. (The SPCX-vs-delisted-ETF collision.)

---

## 2. The test pyramid

| Layer | What | When | Blocking | Where |
|---|---|---|---|---|
| Unit / regression | Pure logic, mocked I/O. Every fixed bug pinned by a named test. | every push/PR | **yes** | `tests/` via `tests.yml` |
| Integrity | Checkpoint hashes vs MANIFEST, JSON validity, schema | every push/PR | **yes** | `verify_checkpoints.py` |
| Connector smoke | Live yfinance/EDGAR/HN/Polymarket/FRED/Wikipedia | every push/PR + schedule | no (network) | `run_tests.sh` |
| End-to-end | Full `checkpoint.py` run → `score.py` → `gate.py` | scheduled Mon/Thu | yes (gate) | `checkpoint.yml` |

**Rule: every bug fix ships with a failing-first regression test** named for the bug, in the
established `tests/` style (docstring states the bug, monkeypatch isolates I/O). The suite is the
ledger of every mistake the process caught — that is itself part of the experiment's record.

Run locally before any commit:
```bash
.venv/bin/python -m pytest tests/ -q          # offline, <1s, must be green
.venv/bin/python tools/verify_checkpoints.py  # evidence intact
./tools/run_tests.sh .venv/bin/python         # live smoke, 12/12 when upstreams are up
```

## 3. Resilience / chaos testing

The pipeline must degrade gracefully, never silently. Test the failure paths explicitly, not
just the happy path:

- **Single-source outage** — mock each connector to raise; assert the snapshot still freezes
  every other source and the failure is in `errors{}` (gate trips). Covered for the universe
  (`test_get_universe_isolates_failing_ticker`); extend to each connector.
- **Empty payload ≠ success** — mock an upstream returning `[]`/empty-df; assert `note_empty`
  records it. Add a regression test per source.
- **Malformed upstream** — mock non-CSV/HTML (the Stooq anti-bot challenge), truncated JSON,
  unexpected schema; assert an explicit raise, never a malformed frame.
  (`test_from_stooq_rejects_antibot_html`.)
- **Fallback actually works** — the yfinance→Stooq fallback is only real if Stooq symbols are
  right; index symbols are now mapped and unit-tested. Re-verify live yearly: Stooq has begun
  serving anti-bot challenges, so treat the fallback as *best-effort* and consider a second
  independent source (e.g. Yahoo chart API direct, or Tiingo/Alpha Vantage free tier) for the
  price series that scoring depends on.
- **Idempotency / immutability** — re-running a checkpoint label must refuse to overwrite; two
  same-minute auto runs must not collide. Keep the tag-collision guard tested.

## 4. Scoring integrity (the highest-stakes area)

- Pin each scoreable prediction to its evidence basis (`basis: day1` today; add `latest` for
  genuinely live predictions). Never recompute a resolved day-1 fact from a moving close.
- **Share-count drift.** `shares_424b4` is hardcoded from the 2026-03-31 prospectus. The
  checkpoint already flags any 10-Q/10-K/20-F filed after that basis. Standing task: when such a
  filing lands, re-verify the count before scoring any cap-dependent prediction (P3–P6, K1–K3).
  Add a test that a post-basis periodic filing raises the `re-verify shares_424b4` flag.
- **Cross-validation on resolution.** When a prediction resolves, confirm the number against one
  independent live source (done manually in `AUDIT-2026-06-15.md` §3) and record it. Automate a
  soft check: cap from `close × 424B4` vs yfinance `market_cap_reported` within ~5%.

## 5. Security & supply chain

- **No secrets in the repo.** Only `MIRROR_TOKEN` (Actions secret, fine-grained, mirror repo
  only, **expires 2027-06-01**). Renewal is the single recurring obligation (see mirror
  `MIRROR_OPS.md`). The public workflow uses the default `GITHUB_TOKEN` with `contents: write`
  only — keep `permissions:` minimal per workflow (`tests.yml` is read-only).
- **Dependency hygiene.** Pin/refresh `requirements.txt`; add a scheduled `pip-audit` (CVEs) and
  Dependabot. `pip_freeze.txt` is frozen per checkpoint, so every result is reproducible to the
  exact dependency set.
- **Pin GitHub Actions by major tag at minimum** (done: `checkout@v5`, `setup-python@v6`);
  consider SHA-pinning for supply-chain hardening.
- **Outbound contact compliance.** SEC fair-access requires a real UA email (present); keep it
  deliverable or EDGAR 403s.
- **Token never pushes mirror→public.** The mirror is pull-only; never add a path that writes
  upstream from the mirror.

## 6. Performance & cost

- **CI budget.** `checkpoint.yml` has a 20-min timeout; `tests.yml` 15. Watch the connector
  latency (windowed HN pagination is the slowest). Keep per-run wall time well under budget.
- **Cache effectiveness.** 12h parquet cache keyed by ticker+period (date-independent within the
  window). Checkpoints use `force=True` (always fresh); notebooks reuse cache. Don't let the
  notebooks' cache hide stale data — they are not evidence.
- **Repo growth.** Checkpoints accumulate (~50–130 KB each, twice weekly). Parquet stays binary
  and small; monitor total size yearly, and prune nothing (immutability) — archive instead if it
  ever matters.
- **Determinism.** Monte Carlo must be seeded so a re-run reproduces the frozen report; verify
  the MC config + seed are captured in the snapshot.

## 7. Standing schedule

| Cadence | Action |
|---|---|
| every push/PR | `tests.yml`: unit + integrity (blocking), smoke (non-blocking) |
| Mon/Thu | `checkpoint.yml`: collect, score, gate |
| on each milestone | manual `workflow_dispatch` with the label; cross-validate the resolved prediction |
| when a 10-Q/10-K lands | re-verify `shares_424b4`; the flag fires automatically |
| monthly | review `errors{}` history across recent manifests for creeping degradation |
| yearly | re-verify the Stooq fallback live; `pip-audit`; refresh pinned actions |
| 2027-06-01 | renew `MIRROR_TOKEN` |

## 8. Definition of done for any change here

1. Failing-first regression test added, named for the issue.
2. `pytest tests/ -q` green; `verify_checkpoints.py` clean.
3. If a workflow or connector changed, one real `workflow_dispatch` run observed green —
   not asserted from a checkmark alone (the `MIRROR_OPS.md` discipline).
4. The four invariants in §1 still hold.

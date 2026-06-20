"""Scores the predictions whose verify-date has passed against frozen checkpoint data.

Read-only on PREDICTIONS.md (never edits it — the methodological note forbids touching
predictions). Writes a separate scoring report. Currently covers P1/P2 (day-1 close market
cap vs $1T/$2T); future-dated predictions are reported as 'pending', not guessed.

Day-1 predictions are pinned to the FROZEN day-1 close (the immutable 2026-06-12 bar), not
the latest checkpoint's rolling close — otherwise a later live-price drift below the
threshold would wrongly flip a correctly-resolved day-1 fact (the scoring-drift bug).
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CKPT = ROOT / "checkpoints"

# Authoritative total share count from the 424B4 prospectus (SEC Reg. No. 333-296070),
# the frozen gold source. SpaceX is dual-class: yfinance.sharesOutstanding reports Class A
# only (~7.49B), undercounting market cap by ~40% and wrongly flipping P2 to FALSE — never
# trust it for scoring. Total = 6,824,641,355 Class A (as of 2026-03-31, post Class C
# reclassification + preferred conversion) + 555,555,555 Class A newly issued in the IPO
# + 5,695,668,265 Class B.
SPCX_SHARES_424B4 = 6_824_641_355 + 555_555_555 + 5_695_668_265  # 13,075,865,175

DEBUT = date(2026, 6, 12)  # SPCX first trading day; the "day-1 close" basis for P1/P2

# Pre-registered, from PREDICTIONS.md. P(ex-ante) is here only to echo it in the report;
# the criterion is what gets evaluated. Thresholds in USD. `basis` selects the close used:
# "day1" = the frozen debut-day close (immutable); future "latest" predictions can be added.
SCOREABLE = {
    "P1": {"p": 0.97, "verify": date(2026, 6, 12), "threshold": 1e12, "basis": "day1",
           "label": "SPCX day-1 close market cap > $1T"},
    "P2": {"p": 0.60, "verify": date(2026, 6, 12), "threshold": 2e12, "basis": "day1",
           "label": "SPCX day-1 close market cap > $2T"},
}


def _iter_spcx(ckpt: Path):
    """Yield (name, spcx_dict) for every checkpoint holding an spcx_market.json, oldest first."""
    for d in sorted(p for p in ckpt.iterdir() if p.is_dir()):
        sp = d / "spcx_market.json"
        if sp.exists():
            try:
                yield d.name, json.loads(sp.read_text())
            except json.JSONDecodeError:
                continue


def _created(d: Path) -> datetime:
    """Parse MANIFEST created_utc for chronological ordering; missing/bad -> epoch."""
    mf = d / "MANIFEST.json"
    if mf.exists():
        try:
            return datetime.fromisoformat(json.loads(mf.read_text()).get("created_utc", ""))
        except (ValueError, json.JSONDecodeError):
            pass
    return datetime.min.replace(tzinfo=timezone.utc)


def day1_snapshot(ckpt: Path, debut: date = DEBUT) -> tuple[str, dict, float] | tuple[None, None, None]:
    """The frozen day-1 close: first checkpoint that captured the debut-day OHLCV bar.

    Pinned to the immutable backfilled debut bar, so the score never drifts with live price.
    Returns (checkpoint_name, spcx_dict, close)."""
    target = debut.isoformat()
    for name, m in _iter_spcx(ckpt):
        for r in m.get("ohlcv_tail") or []:
            if str(r.get("Date", ""))[:10] == target and r.get("Close") is not None:
                return name, m, float(r["Close"])
    return None, None, None


def latest_spcx(ckpt: Path = CKPT) -> tuple[str, dict] | tuple[None, None]:
    """Most recent checkpoint (by MANIFEST created_utc) with an spcx_market.json.

    Kept for future 'latest'-basis predictions; day-1 predictions use day1_snapshot instead."""
    best, best_ts, best_name = None, datetime.min.replace(tzinfo=timezone.utc), None
    for d in sorted(p for p in ckpt.iterdir() if p.is_dir()):
        if not (d / "spcx_market.json").exists():
            continue
        ts = _created(d)
        if ts >= best_ts:
            best, best_ts, best_name = json.loads((d / "spcx_market.json").read_text()), ts, d.name
    return (best_name, best) if best is not None else (None, None)


def score(ckpt: Path = CKPT, today: date | None = None) -> dict:
    """Pure scorer: returns {pid: {outcome, p_ex_ante, detail, source}}. No file writes."""
    today = today or date.today()
    d1_name, d1, d1_close = day1_snapshot(ckpt)
    results: dict[str, dict] = {}

    for pid, p in sorted(SCOREABLE.items()):
        src = None
        if p["basis"] == "day1":
            close, snap, src = d1_close, d1, d1_name
        else:  # pragma: no cover - no 'latest'-basis predictions are live yet
            name, snap = latest_spcx(ckpt)
            close, src = (snap or {}).get("last_close"), name

        cap = close * SPCX_SHARES_424B4 if close else None
        cap_sane = cap is not None and 1e11 <= cap <= 1e13

        if today < p["verify"]:
            outcome, detail = "pending", f"verify on {p['verify']}"
        elif not cap_sane:
            if close is None:
                detail = "no frozen day-1 close captured yet — re-run tools/checkpoint.py"
            else:
                detail = f"cap ${cap/1e9:.1f}B outside plausible band — verify close + 424B4 shares"
            outcome = "unverifiable"
        else:
            # Transparency: yfinance.sharesOutstanding is Class A only; show the gap we correct.
            div = ""
            yf_cap = (snap or {}).get("market_cap_computed")
            if yf_cap and abs(yf_cap - cap) / cap > 0.15:
                div = f" [yfinance Class-A-only cap ${yf_cap/1e12:.3f}T undercounts; dual-class corrected]"
            outcome = "TRUE" if cap > p["threshold"] else "FALSE"
            detail = (f"cap ${cap/1e12:.3f}T (424B4 total shares x frozen day-1 close) "
                      f"vs threshold ${p['threshold']/1e12:.1f}T{div}")
        results[pid] = {"outcome": outcome, "p_ex_ante": p["p"], "detail": detail, "source": src}
    return results


def main() -> None:
    results = score(CKPT)
    src = next((r["source"] for r in results.values() if r.get("source")), None)
    rows = [f"| {pid} | {SCOREABLE[pid]['label']} | {r['p_ex_ante']} | {r['outcome']} | {r['detail']} |"
            for pid, r in results.items()]

    report = {"scored_from_checkpoint": src, "scored_on": str(date.today()),
              "today_utc": datetime.now(timezone.utc).isoformat(),
              "results": {pid: {k: r[k] for k in ("outcome", "p_ex_ante", "detail")}
                          for pid, r in results.items()}}
    (CKPT / "SCORING.json").write_text(json.dumps(report, indent=1))

    md = ["# Auto-scoring (predictions whose verify-date has passed)\n",
          f"Source checkpoint: `{src}` — scored {date.today()}. "
          "Read-only on PREDICTIONS.md; this file is regenerated, not authoritative.\n",
          "| # | Prediction | P(ex-ante) | Outcome | Detail |",
          "|---|---|---|---|---|", *rows]
    (CKPT / "SCORING.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

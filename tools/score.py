"""Scores the predictions whose verify-date has passed against frozen checkpoint data.

Read-only on PREDICTIONS.md (never edits it — the methodological note forbids touching
predictions). Writes a separate scoring report. Currently covers P1/P2 (day-1 close market
cap vs $1T/$2T); future-dated predictions are reported as 'pending', not guessed.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CKPT = ROOT / "checkpoints"
TODAY = date.today()

# Pre-registered, from PREDICTIONS.md. P(ex-ante) is here only to echo it in the report;
# the criterion is what gets evaluated. Thresholds in USD.
SCOREABLE = {
    "P1": {"p": 0.97, "verify": date(2026, 6, 12), "threshold": 1e12,
           "label": "SPCX day-1 close market cap > $1T"},
    "P2": {"p": 0.60, "verify": date(2026, 6, 12), "threshold": 2e12,
           "label": "SPCX day-1 close market cap > $2T"},
}


def latest_spcx() -> tuple[str, dict] | tuple[None, None]:
    """Most recent checkpoint (by MANIFEST created_utc) that has an spcx_market.json."""
    best, best_ts, best_name = None, "", None
    for d in CKPT.iterdir():
        if not d.is_dir():
            continue
        sp, mf = d / "spcx_market.json", d / "MANIFEST.json"
        if not sp.exists():
            continue
        ts = ""
        if mf.exists():
            ts = json.loads(mf.read_text()).get("created_utc", "")
        if ts >= best_ts:
            best, best_ts, best_name = json.loads(sp.read_text()), ts, d.name
    return (best_name, best) if best is not None else (None, None)


def main() -> None:
    name, spcx = latest_spcx()
    rows, results = [], {}
    if spcx is None:
        print("no checkpoint with spcx_market.json found")
        return

    cap = spcx.get("market_cap_computed") or spcx.get("market_cap_reported")
    suspect = spcx.get("identity_suspect")
    # cap_sane is absent in pre-sanity-check checkpoints; treat unknown as not-sane only when
    # a cap exists (older checkpoints with a cap but no flag still get the band test here).
    cap_sane = spcx.get("cap_sane")
    if cap_sane is None and cap is not None:
        cap_sane = 1e11 <= cap <= 1e13
    note = ""
    if not spcx.get("listed"):
        note = "SPCX not listed in latest checkpoint"
    elif cap is None:
        note = ("market cap not capturable yet — checkpoint predates shares_outstanding "
                "capture; re-run tools/checkpoint.py to freeze it")
    elif not cap_sane:
        note = (f"market cap ${cap/1e9:.1f}B outside plausible SpaceX band — shares_outstanding "
                "likely ETF-collision; refusing to score until verified against 424B4")

    for pid, p in sorted(SCOREABLE.items()):
        if TODAY < p["verify"]:
            outcome, detail = "pending", f"verify on {p['verify']}"
        elif cap is None or not cap_sane:
            outcome, detail = "unverifiable", note
        else:
            hit = cap > p["threshold"]
            outcome = "TRUE" if hit else "FALSE"
            detail = f"cap ${cap/1e12:.3f}T vs threshold ${p['threshold']/1e12:.1f}T"
            if suspect:
                detail += " [identity_suspect: cap from verified close, option chain ignored]"
        results[pid] = {"outcome": outcome, "p_ex_ante": p["p"], "detail": detail}
        rows.append(f"| {pid} | {p['label']} | {p['p']} | {outcome} | {detail} |")

    report = {"scored_from_checkpoint": name, "scored_on": str(TODAY),
              "today_utc": datetime.now(timezone.utc).isoformat(), "results": results}
    (CKPT / "SCORING.json").write_text(json.dumps(report, indent=1))

    md = ["# Auto-scoring (predictions whose verify-date has passed)\n",
          f"Source checkpoint: `{name}` — scored {TODAY}. "
          "Read-only on PREDICTIONS.md; this file is regenerated, not authoritative.\n",
          "| # | Prediction | P(ex-ante) | Outcome | Detail |",
          "|---|---|---|---|---|", *rows]
    (CKPT / "SCORING.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

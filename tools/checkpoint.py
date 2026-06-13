"""Freezes a dated snapshot of every data source + model output for future ex-post evaluation."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main(label: str | None = None) -> None:
    from src.connectors.edgar import recent_filings
    from src.connectors.fred import risk_free_rate
    from src.connectors.hackernews import daily_attention
    from src.connectors.market_data import get_universe
    from src.connectors.polymarket import search_markets
    from src.connectors.wikipedia import pageviews
    from src.config import UNIVERSE
    from src.risk.montecarlo import McConfig, SpreadPosition, report, simulate

    now = datetime.now(timezone.utc)
    day = f"{now:%Y-%m-%d}"
    # A: auto snapshots carry a HHMM suffix so multiple same-day runs never share a dir.
    # Milestone labels stay clean (the name is the point) and must be unique by hand.
    tag = f"{day}-{now:%H%M}-auto" if label in (None, "", "auto") else f"{day}-{label}"
    out = ROOT / "checkpoints" / tag
    # B: never silently overwrite a frozen snapshot — the whole system relies on immutability.
    if out.exists():
        sys.exit(f"checkpoint {tag} already exists — refusing to overwrite a frozen snapshot. "
                 "Pick a distinct milestone label.")
    out.mkdir(parents=True)
    artifacts: dict[str, str] = {}

    def _finite(obj):  # NaN/inf -> None so output is strict-valid JSON (pandas leaks NaN via to_dict)
        if isinstance(obj, float):
            return obj if math.isfinite(obj) else None
        if isinstance(obj, dict):
            return {k: _finite(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_finite(v) for v in obj]
        return obj

    def save_json(name: str, payload) -> None:
        p = out / f"{name}.json"
        p.write_text(json.dumps(_finite(payload), indent=1, default=str, allow_nan=False))
        artifacts[p.name] = sha256(p)

    prices, qa = get_universe(UNIVERSE, period="2y")
    p = out / "universe_prices.parquet"
    prices.to_parquet(p)
    artifacts[p.name] = sha256(p)
    save_json("quality_reports", qa)

    save_json("polymarket", search_markets("spacex", limit=20))
    save_json("edgar_filings", recent_filings(limit=40))

    hn = daily_attention("spacex", days=180)
    p = out / "hn_attention.csv"
    hn.to_csv(p)
    artifacts[p.name] = sha256(p)

    wiki = pageviews("SpaceX", days=180)
    p = out / "wikipedia_pageviews.csv"
    wiki.to_csv(p)
    artifacts[p.name] = sha256(p)

    save_json("risk_free", {"rate_3m_tbill": risk_free_rate()})

    bench = {}
    for tkr in ("VWCE.DE", "EURUSD=X"):
        try:
            px = get_universe([tkr], period="1mo")[0][tkr].dropna()
            bench[tkr] = {"last_close": float(px.iloc[-1]), "date": str(px.index[-1].date())}
        except Exception as e:
            bench[tkr] = {"error": str(e)[:80]}
    save_json("benchmarks", bench)

    spcx: dict = {"listed": False}
    try:
        import yfinance as yf

        t = yf.Ticker("SPCX")
        hist = t.history(period="1mo", auto_adjust=True)
        if not hist.empty:
            spcx = {"listed": True,
                    "ohlcv_tail": hist.tail(10).reset_index().astype(str).to_dict("records")}
            chains, strikes = {}, []
            for exp in (t.options or [])[:6]:
                oc = t.option_chain(exp)
                cols = ["strike", "lastPrice", "bid", "ask", "impliedVolatility",
                        "volume", "openInterest"]
                chains[exp] = {"calls": oc.calls[cols].to_dict("records"),
                               "puts": oc.puts[cols].to_dict("records")}
                strikes += list(oc.calls["strike"]) + list(oc.puts["strike"])
            spcx["option_chains"] = chains
            last = float(hist["Close"].iloc[-1])
            flags = []
            if float(hist["Volume"].tail(5).sum()) == 0:
                flags.append("zero volume: placeholder/when-issued quote, not real trading")
            if strikes:
                med = sorted(strikes)[len(strikes) // 2]
                if not 0.5 <= med / last <= 2.0:
                    flags.append(f"strike/price mismatch (median strike {med} vs close {last}): "
                                 "likely ticker collision with the pre-2026 SPCX ETF")
            spcx["identity_suspect"] = bool(flags)
            spcx["quality_flags"] = flags
    except Exception as e:
        spcx["note"] = f"not yet listed or fetch failed: {str(e)[:80]}"
    save_json("spcx_market", spcx)

    cfg, spread = McConfig(), SpreadPosition()
    save_json("montecarlo", {"config": asdict(cfg), "spread": asdict(spread),
                             "report": report(simulate(cfg, spread))})

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                            capture_output=True, text=True).stdout
    (out / "pip_freeze.txt").write_text(freeze)
    artifacts["pip_freeze.txt"] = sha256(out / "pip_freeze.txt")

    manifest = {"checkpoint": tag, "created_utc": now.isoformat(),
                "git_head": git_head, "python": sys.version.split()[0],
                "universe": UNIVERSE, "artifacts": artifacts,
                "purpose": "Frozen evidence for the ex-post evaluation protocol in EVALUATION.md"}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))

    index = ROOT / "checkpoints" / "INDEX.md"
    header = ("# Checkpoint index\n\nOne frozen snapshot per milestone. "
              "Never modified after creation — git history is the witness.\n\n"
              "| Checkpoint | Git HEAD | Contents | Milestone note |\n|---|---|---|---|\n")
    line = f"| {tag} | {git_head[:8]} | {len(artifacts)} artifacts | |\n"
    body = index.read_text() if index.exists() else header
    if f"| {tag} |" not in body:  # tag is unique by construction, but never duplicate a row
        body += line
    index.write_text(body)
    print(f"checkpoint {tag}: {len(artifacts)} artifacts, manifest written")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

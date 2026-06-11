"""Freezes a dated snapshot of every data source + model output for future ex-post evaluation."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import date, datetime, timezone
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

    tag = f"{date.today():%Y-%m-%d}" + (f"-{label}" if label else "")
    out = ROOT / "checkpoints" / tag
    out.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, str] = {}

    def save_json(name: str, payload) -> None:
        p = out / f"{name}.json"
        p.write_text(json.dumps(payload, indent=1, default=str))
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

    cfg, spread = McConfig(), SpreadPosition()
    save_json("montecarlo", {"config": asdict(cfg), "spread": asdict(spread),
                             "report": report(simulate(cfg, spread))})

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                            capture_output=True, text=True).stdout
    (out / "pip_freeze.txt").write_text(freeze)
    artifacts["pip_freeze.txt"] = sha256(out / "pip_freeze.txt")

    manifest = {"checkpoint": tag, "created_utc": datetime.now(timezone.utc).isoformat(),
                "git_head": git_head, "python": sys.version.split()[0],
                "universe": UNIVERSE, "artifacts": artifacts,
                "purpose": "Frozen evidence for the ex-post evaluation protocol in EVALUATION.md"}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))

    index = ROOT / "checkpoints" / "INDEX.md"
    line = f"| {tag} | {git_head[:8]} | {len(artifacts)} artifacts | |\n"
    if not index.exists():
        index.write_text("# Checkpoint index\n\nOne frozen snapshot per milestone. "
                         "Never modified after creation — git history is the witness.\n\n"
                         "| Checkpoint | Git HEAD | Contents | Milestone note |\n|---|---|---|---|\n")
    index.write_text(index.read_text() + line)
    print(f"checkpoint {tag}: {len(artifacts)} artifacts, manifest written")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

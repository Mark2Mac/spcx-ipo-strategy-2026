"""Shared readers for the latest frozen checkpoint — the single evidence source for every
post-IPO visual, so the gif and the static chart can never show different values (bug 19)."""
from __future__ import annotations

import json
from pathlib import Path

DEBUT = "2026-06-12"
UNLOCK_MONTH = "2026-08"


def latest_checkpoint(root: Path) -> Path:
    """Newest snapshot dir that carries the full SPCX price history.

    Ordered by the MANIFEST's created_utc, not the dir name — same-day milestone labels
    sort after HHMM-auto tags lexically, which would pick a stale snapshot."""
    def created(d: Path) -> str:
        try:
            return json.loads((d / "MANIFEST.json").read_text()).get("created_utc", "")
        except (OSError, ValueError):
            return ""

    snaps = sorted((d for d in root.iterdir()
                    if d.is_dir() and (d / "spcx_ohlcv.parquet").exists()), key=created)
    if not snaps:
        raise SystemExit("no checkpoint with spcx_ohlcv.parquet found; run a checkpoint first")
    return snaps[-1]


def realized_closes(ckpt: Path):
    """Realized SPCX closes since debut, from committed evidence (never a live fetch)."""
    import pandas as pd
    spx = pd.read_parquet(ckpt / "spcx_ohlcv.parquet")["Close"]
    return spx[spx.index >= DEBUT].to_numpy()


def unlock_month_iv(ckpt: Path) -> float | None:
    """Unlock-month ATM IV: mean of the archived Aug expiries (notebook-07 derivation)."""
    market = json.loads((ckpt / "spcx_market.json").read_text())
    aug = [v["avg_iv"] for e, v in (market.get("derived_atm_iv") or {}).items()
           if e.startswith(UNLOCK_MONTH) and v.get("avg_iv")]
    return round(sum(aug) / len(aug), 3) if aug else None

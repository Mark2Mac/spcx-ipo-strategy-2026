"""Connector Polymarket Gamma API (gratuita, no auth): quote prediction market come segnale di probabilità."""
from __future__ import annotations

import json

import requests

GAMMA = "https://gamma-api.polymarket.com"


def search_markets(query: str, limit: int = 12) -> list[dict]:
    r = requests.get(f"{GAMMA}/public-search", params={"q": query, "events_status": "active"}, timeout=30)
    r.raise_for_status()
    out = []
    for ev in r.json().get("events", []):
        for m in ev.get("markets", []):
            try:
                prices = json.loads(m.get("outcomePrices") or "[]")
                outcomes = json.loads(m.get("outcomes") or "[]")
            except json.JSONDecodeError:
                prices, outcomes = [], []
            out.append({"event": ev["title"], "market": m.get("question"),
                        "outcomes": dict(zip(outcomes, [float(p) for p in prices])),
                        "volume": float(m.get("volume") or 0)})
    out.sort(key=lambda x: -x["volume"])
    return out[:limit]


def implied_probability(market: dict, outcome: str = "Yes") -> float | None:
    return market["outcomes"].get(outcome)


if __name__ == "__main__":
    mkts = search_markets("spacex")
    assert mkts, "Polymarket FAIL: nessun mercato spacex"
    print(f"TEST OK — {len(mkts)} mercati SpaceX")
    for m in mkts[:4]:
        print(f"  {m['market']}: {m['outcomes']}")

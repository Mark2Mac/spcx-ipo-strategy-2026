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


def _finite(obj):  # NaN/inf -> None so output is strict-valid JSON (pandas leaks NaN via to_dict)
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _finite(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_finite(v) for v in obj]
    return obj


def _bs_price(cp: str, S: float, K: float, T: float, sig: float, r: float) -> float:
    if T <= 0 or sig <= 0:
        return max(0.0, (S - K) if cp == "c" else (K - S))
    ncdf = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
    d1 = (math.log(S / K) + (r + 0.5 * sig * sig) * T) / (sig * math.sqrt(T))
    d2 = d1 - sig * math.sqrt(T)
    if cp == "c":
        return S * ncdf(d1) - K * math.exp(-r * T) * ncdf(d2)
    return K * math.exp(-r * T) * ncdf(-d2) - S * ncdf(-d1)


def _iv_from_last(cp: str, S: float, K: float, T: float, price: float, r: float) -> float | None:
    # Free feeds give a broken impliedVolatility column and no live bid/ask; back-solve IV from the
    # last trade instead (bisection). The archived derived IV is the study's only usable vol signal.
    if not (price and math.isfinite(price) and price > 0 and S > 0 and K > 0 and T > 0):
        return None
    lo, hi = 1e-4, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _bs_price(cp, S, K, T, mid, r) > price:
            hi = mid
        else:
            lo = mid
    return round((lo + hi) / 2, 4)


def _derived_atm_iv(chains: dict, spot: float, asof, r: float) -> dict:
    from datetime import date as _date
    out = {}
    for exp, sides in chains.items():
        try:
            T = (_date.fromisoformat(exp) - asof).days / 365
        except Exception:
            continue
        rec = {"atm_strike": None, "call_iv": None, "put_iv": None, "avg_iv": None, "T_years": round(T, 4)}
        for side, cp in (("calls", "c"), ("puts", "p")):
            rows = sides.get(side) or []
            if not rows:
                continue
            atm = min(rows, key=lambda o: abs(o["strike"] - spot))
            iv = _iv_from_last(cp, spot, atm["strike"], T, atm.get("lastPrice"), r)
            rec["atm_strike"] = atm["strike"]
            rec["call_iv" if cp == "c" else "put_iv"] = iv
        ivs = [v for v in (rec["call_iv"], rec["put_iv"]) if v is not None]
        rec["avg_iv"] = round(sum(ivs) / len(ivs), 4) if ivs else None
        out[exp] = rec
    return out


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

    def save_json(name: str, payload) -> None:
        p = out / f"{name}.json"
        p.write_text(json.dumps(_finite(payload), indent=1, default=str, allow_nan=False))
        artifacts[p.name] = sha256(p)

    # One source failing must not abort the whole snapshot: isolate each, record errors,
    # keep everything that did succeed. force=True bypasses the 12h cache so a checkpoint
    # always freezes fresh data, never a stale cache hit re-stamped with a new timestamp.
    errors: dict[str, str] = {}

    def guard(name: str, fn):
        try:
            return fn()
        except Exception as e:
            errors[name] = f"{type(e).__name__}: {str(e)[:150]}"
            print(f"  ! {name} failed: {errors[name]}", file=sys.stderr)
            return None

    pq = guard("prices", lambda: get_universe(UNIVERSE, period="2y", force=True))
    if pq is not None:
        prices, qa = pq
        p = out / "universe_prices.parquet"
        prices.to_parquet(p)
        artifacts[p.name] = sha256(p)
        save_json("quality_reports", qa)
        save_json("sources", {r["ticker"]: r.get("source", "unknown") for r in qa})

    # An upstream returning an empty payload (no exception) looks identical to a successful
    # fetch and would silently freeze a blank artifact on a key day. Record empty-but-no-error
    # so it lands in errors{} and trips the run gate, instead of passing as green.
    def note_empty(name: str, is_empty: bool) -> None:
        if is_empty:
            errors[name] = "empty payload (fetch succeeded but returned no data)"
            print(f"  ! {name} empty payload", file=sys.stderr)

    pm = guard("polymarket", lambda: search_markets("spacex", limit=20))
    if pm is not None:
        save_json("polymarket", pm)
        note_empty("polymarket", not pm)

    fil = guard("edgar", lambda: recent_filings(limit=40))
    if fil is not None:
        save_json("edgar_filings", fil)
        note_empty("edgar", not fil)

    hn = guard("hackernews", lambda: daily_attention("spacex", days=180))
    if hn is not None:
        p = out / "hn_attention.csv"
        hn.to_csv(p)
        artifacts[p.name] = sha256(p)
        save_json("hn_meta", {"coverage_gap_days": int(hn.attrs.get("coverage_gap_days", 0))})
        note_empty("hackernews", hn.empty)

    wiki = guard("wikipedia", lambda: pageviews("SpaceX", days=180))
    if wiki is not None:
        p = out / "wikipedia_pageviews.csv"
        wiki.to_csv(p)
        artifacts[p.name] = sha256(p)
        note_empty("wikipedia", wiki.empty)

    rf = guard("risk_free", risk_free_rate)
    if rf is not None:
        save_json("risk_free", {"rate_3m_tbill": rf})

    bench, fx_eurusd = {}, None
    for tkr in ("VWCE.DE", "EURUSD=X"):
        try:
            px = get_universe([tkr], period="1mo", force=True)[0][tkr].dropna()
            bench[tkr] = {"last_close": float(px.iloc[-1]), "date": str(px.index[-1].date())}
            if tkr == "EURUSD=X":
                fx_eurusd = float(px.iloc[-1])
        except Exception as e:
            bench[tkr] = {"error": str(e)[:80]}
            errors[f"benchmark:{tkr}"] = f"{type(e).__name__}: {str(e)[:150]}"
    save_json("benchmarks", bench)

    spcx: dict = {"listed": False}
    SHARES_424B4_ASOF = "2026-03-31"  # 424B4 share-count basis date
    try:
        from src.connectors.market_data import get_ohlcv

        # Price via the universe connector: yfinance primary, Stooq fallback. Removes the
        # raw-yfinance single point of failure for the most important series on a key day.
        hist = get_ohlcv("SPCX", period="1mo", force=True)
        if not hist.empty:
            flags = []
            last = float(hist["Close"].iloc[-1])
            spcx = {"listed": True, "last_close": last,
                    "price_source": hist.attrs.get("source", "unknown"),
                    "ohlcv_tail": hist.tail(10).reset_index().to_dict("records")}
            # Full SPCX price history as a committed artifact: the target series revises and is
            # never reconstructible later, so the snapshot (not the gitignored data/) is the evidence.
            try:
                full = get_ohlcv("SPCX", period="max", force=True)
                if not full.empty:
                    pth = out / "spcx_ohlcv.parquet"
                    full[["Open", "High", "Low", "Close", "Volume"]].to_parquet(pth)
                    artifacts[pth.name] = sha256(pth)
            except Exception as fe:
                spcx["ohlcv_full_note"] = f"full history unavailable: {str(fe)[:80]}"
            if float(hist["Volume"].tail(5).sum()) == 0:
                flags.append("zero volume: placeholder/when-issued quote, not real trading")
            # Authoritative total from the 424B4 (dual-class: yfinance sharesOutstanding is
            # Class A only). 6,824,641,355 Class A + 555,555,555 IPO + 5,695,668,265 Class B.
            # Needs no live source beyond the close, so cap survives a full yfinance outage.
            spcx["shares_424b4"] = 6_824_641_355 + 555_555_555 + 5_695_668_265
            spcx["shares_424b4_asof"] = SHARES_424B4_ASOF
            spcx["market_cap_424b4"] = last * spcx["shares_424b4"]
            # Drift guard: a 10-Q/10-K filed after the 424B4 basis means the share count may
            # have moved (Musk performance tranche, secondaries) — flag to re-verify.
            newer = [f for f in (fil or []) if f.get("form", "").upper().replace(" ", "") in
                     ("10-Q", "10-K", "10-K/A", "20-F") and f.get("date", "") > SHARES_424B4_ASOF]
            if newer:
                flags.append(f"periodic filing(s) {[f['form'] for f in newer][:3]} dated after "
                             f"424B4 basis {SHARES_424B4_ASOF} — re-verify shares_424b4")
            # Options + .info are yfinance-only; best-effort, never fail the snapshot over them.
            chains, strikes = {}, []
            try:
                import yfinance as yf
                t = yf.Ticker("SPCX")
                for exp in (t.options or [])[:6]:
                    oc = t.option_chain(exp)
                    cols = ["strike", "lastPrice", "bid", "ask", "impliedVolatility",
                            "volume", "openInterest"]
                    chains[exp] = {"calls": oc.calls[cols].to_dict("records"),
                                   "puts": oc.puts[cols].to_dict("records")}
                    strikes += list(oc.calls["strike"]) + list(oc.puts["strike"])
                info = t.info or {}
            except Exception as oe:
                info = {}
                spcx["yfinance_extras_note"] = f"options/info unavailable: {str(oe)[:80]}"
            spcx["option_chains"] = chains
            spcx["derived_atm_iv"] = _derived_atm_iv(chains, last, now.date(), rf if rf else 0.036)
            if strikes:
                med = sorted(strikes)[len(strikes) // 2]
                if not 0.5 <= med / last <= 2.0:
                    flags.append(f"strike/price mismatch (median strike {med} vs close {last}): "
                                 "likely ticker collision with the pre-2026 SPCX ETF")
            shares = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
            spcx["shares_outstanding"] = shares
            spcx["market_cap_reported"] = info.get("marketCap")
            cap_c = last * shares if shares else None
            spcx["market_cap_computed"] = cap_c
            # Cap sanity band: ~$100B floor to ~$10T ceiling. The authoritative 424B4 cap is
            # the one scored; this guards the yfinance-derived figure against ETF-collision.
            SPCX_CAP_MIN, SPCX_CAP_MAX = 1e11, 1e13
            if cap_c is not None and not (SPCX_CAP_MIN <= cap_c <= SPCX_CAP_MAX):
                flags.append(f"market cap ${cap_c/1e9:.1f}B outside plausible SpaceX band "
                             "($100B-$10T): shares_outstanding likely ETF-collision — verify vs 424B4")
            spcx["cap_sane"] = SPCX_CAP_MIN <= spcx["market_cap_424b4"] <= SPCX_CAP_MAX
            spcx["identity_suspect"] = bool(flags)
            spcx["quality_flags"] = flags
    except Exception as e:
        spcx["note"] = f"not yet listed or fetch failed: {str(e)[:80]}"
        errors["spcx"] = f"{type(e).__name__}: {str(e)[:150]}"
    save_json("spcx_market", spcx)

    cfg = McConfig(fx_eurusd=fx_eurusd) if fx_eurusd and fx_eurusd > 0 else McConfig()
    spread = SpreadPosition()
    save_json("montecarlo", {"config": asdict(cfg), "spread": asdict(spread),
                             "report": report(simulate(cfg, spread)),
                             "fx_source": "live EURUSD=X" if fx_eurusd else "default constant"})

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                            capture_output=True, text=True).stdout
    (out / "pip_freeze.txt").write_text(freeze)
    artifacts["pip_freeze.txt"] = sha256(out / "pip_freeze.txt")

    manifest = {"checkpoint": tag, "created_utc": now.isoformat(),
                "git_head": git_head, "python": sys.version.split()[0],
                "universe": UNIVERSE, "artifacts": artifacts, "errors": errors,
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

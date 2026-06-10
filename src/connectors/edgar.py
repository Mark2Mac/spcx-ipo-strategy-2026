"""Connector SEC EDGAR (API ufficiale data.sec.gov): filing list, Form 4 watch, full-text search."""
from __future__ import annotations

import requests

UA = {"User-Agent": "spcx-ipo-strategy research contact@example.com"}
SPACEX_CIK = "0001181412"


def _get(url: str, **kw) -> dict:
    r = requests.get(url, headers=UA, timeout=30, **kw)
    r.raise_for_status()
    return r.json()


def recent_filings(cik: str = SPACEX_CIK, forms: tuple[str, ...] | None = None, limit: int = 40) -> list[dict]:
    data = _get(f"https://data.sec.gov/submissions/CIK{cik}.json")
    rec = data["filings"]["recent"]
    out = []
    for form, date, acc, doc in zip(rec["form"], rec["filingDate"], rec["accessionNumber"], rec["primaryDocument"]):
        if forms and form not in forms:
            continue
        acc_nodash = acc.replace("-", "")
        out.append({"form": form, "date": date,
                    "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{doc}"})
        if len(out) >= limit:
            break
    return out


def form4_watch(cik: str = SPACEX_CIK, limit: int = 20) -> list[dict]:
    return recent_filings(cik, forms=("4", "144", "3"), limit=limit)


def fulltext_search(query: str, forms: str | None = None, limit: int = 10) -> list[dict]:
    params = {"q": f'"{query}"'}
    if forms:
        params["forms"] = forms
    data = _get("https://efts.sec.gov/LATEST/search-index", params=params)
    hits = data.get("hits", {}).get("hits", [])[:limit]
    return [{"form": h["_source"].get("file_type"), "date": h["_source"].get("file_date"),
             "company": (h["_source"].get("display_names") or ["?"])[0]} for h in hits]


if __name__ == "__main__":
    fil = recent_filings(limit=10)
    assert fil and all("url" in f for f in fil), "EDGAR FAIL"
    print(f"TEST OK — {len(fil)} filing SpaceX, ultimo: {fil[0]['form']} {fil[0]['date']}")
    f4 = form4_watch(limit=5)
    print(f"Form 3/4/144 trovati: {len(f4)}" + (f", ultimo {f4[0]['date']}" if f4 else " (attesi da agosto, post-lockup)"))

"""Opens GitHub reminder issues when a milestone enters its window — each issue body already
carries the verbose, copy-paste prompt to hand back to Claude Code.

Driven by tools/reminders.json. Idempotent: a `dated` reminder is created at most once (dedup on
exact title across all states); a `weekly` reminder keeps at most one OPEN issue at a time (a new
one opens only after you close the previous). Pure window logic is testable offline; `--apply`
talks to the GitHub API (needs GITHUB_TOKEN + GITHUB_REPOSITORY in the environment).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
REMINDERS = ROOT / "tools" / "reminders.json"
API = "https://api.github.com"


def load(path: Path = REMINDERS) -> list[dict]:
    return json.loads(path.read_text())


def due_reminders(reminders: list[dict], today: date) -> list[dict]:
    """Reminders whose window is open today: weekly on Mondays; dated within [due-lead, due+grace].

    The workflow runs daily so `lead_days` is honoured on whatever weekday the window opens —
    a Monday-only cron truncated every lead to the next Monday, which made `day135` (due Sun
    Oct 25, lead 3) fire on Oct 26, a day late. Weekly reminders keep their Monday cadence
    here, in the logic, instead of inheriting it from the schedule."""
    out = []
    for r in reminders:
        if r.get("type") == "weekly":
            if today.weekday() == 0:
                out.append(r)
            continue
        due = date.fromisoformat(r["due"])
        lead = timedelta(days=r.get("lead_days", 0))
        grace = timedelta(days=r.get("post_grace_days", 14))
        if due - lead <= today <= due + grace:
            out.append(r)
    return out


def _issue_exists(session: requests.Session, repo: str, title: str, open_only: bool) -> bool:
    """True if an issue with exactly this title exists (open only, or in any state).

    `state:` accepts open/closed — there is no `state:all`. Passing it made GitHub match
    nothing, so every dated reminder looked new on every run and re-opened itself once per
    scheduled run (#15/#18/#22 are the same reminder three times). Omitting the qualifier is
    what actually searches every state. Search is fuzzy, so the exact title is re-checked here."""
    q = f'repo:{repo} is:issue in:title "{title}"'
    if open_only:
        q += " state:open"
    r = session.get(f"{API}/search/issues", params={"q": q}, timeout=30)
    r.raise_for_status()
    return any(it.get("title") == title for it in r.json().get("items", []))


def _create_issue(session: requests.Session, repo: str, r: dict, assignee: str | None) -> None:
    payload = {"title": r["title"], "body": r["body"], "labels": r.get("labels", [])}
    if assignee:
        payload["assignees"] = [assignee]
    resp = session.post(f"{API}/repos/{repo}/issues", json=payload, timeout=30)
    resp.raise_for_status()
    print(f"opened: {resp.json()['html_url']}")


def apply(today: date | None = None) -> int:
    today = today or date.today()
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    assignee = os.environ.get("REMINDER_ASSIGNEE") or None
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json"})
    created = 0
    for r in due_reminders(load(), today):
        open_only = r.get("type") == "weekly"
        if _issue_exists(session, repo, r["title"], open_only):
            print(f"skip (exists): {r['title']}")
            continue
        _create_issue(session, repo, r, assignee)
        created += 1
    print(f"done: {created} issue(s) opened")
    return created


def main() -> None:
    today = date.today()
    if "--today" in sys.argv:
        today = date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
    if "--apply" in sys.argv:
        apply(today)
    else:
        for r in due_reminders(load(), today):
            print(f"DUE [{r.get('type','dated')}] {r['title']}")


if __name__ == "__main__":
    main()

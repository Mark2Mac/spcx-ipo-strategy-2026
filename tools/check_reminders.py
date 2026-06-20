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
    """Reminders whose window is open today: weekly always; dated within [due-lead, due+grace]."""
    out = []
    for r in reminders:
        if r.get("type") == "weekly":
            out.append(r)
            continue
        due = date.fromisoformat(r["due"])
        lead = timedelta(days=r.get("lead_days", 0))
        grace = timedelta(days=r.get("post_grace_days", 14))
        if due - lead <= today <= due + grace:
            out.append(r)
    return out


def _issue_exists(session: requests.Session, repo: str, title: str, open_only: bool) -> bool:
    state = "open" if open_only else "all"
    q = f'repo:{repo} is:issue in:title state:{state} "{title}"'
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

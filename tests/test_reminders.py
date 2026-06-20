"""Reminder window logic: weekly always due; dated only inside [due-lead, due+grace]; the shipped
reminders.json is valid and every entry carries a copy-paste prompt."""
import json
from datetime import date

import check_reminders as cr


REM = [
    {"key": "weekly", "type": "weekly", "title": "W", "body": "b"},
    {"key": "d", "type": "dated", "due": "2026-08-03", "lead_days": 5,
     "post_grace_days": 21, "title": "D", "body": "b"},
]


def keys(today):
    return {r["key"] for r in cr.due_reminders(REM, today)}


def test_weekly_always_due():
    assert "weekly" in keys(date(2026, 1, 1))
    assert "weekly" in keys(date(2026, 12, 31))


def test_dated_before_lead_not_due():
    assert "d" not in keys(date(2026, 7, 28))  # 6 days before, lead is 5


def test_dated_inside_lead_window_due():
    assert "d" in keys(date(2026, 7, 29))  # exactly due-lead
    assert "d" in keys(date(2026, 8, 3))   # on the due date


def test_dated_inside_grace_due():
    assert "d" in keys(date(2026, 8, 24))  # due+21 grace edge


def test_dated_after_grace_not_due():
    assert "d" not in keys(date(2026, 8, 25))  # past grace -> stale, no longer opens


def test_shipped_json_valid_and_has_prompts():
    rem = cr.load()
    assert len(rem) >= 5
    for r in rem:
        assert r["title"] and r["body"]
        assert "```" in r["body"], f"{r['key']} body must embed a copy-paste prompt"
        assert r.get("type") in ("weekly", "dated")
        if r["type"] == "dated":
            date.fromisoformat(r["due"])  # parses

"""Reminder window logic: weekly due on Mondays; dated only inside [due-lead, due+grace]; the
shipped reminders.json is valid and every entry carries a copy-paste prompt.

The runner fires DAILY, so `lead_days` means what it says. Weekly reminders carry their own
Monday gate here rather than relying on the cron — a weekly cron silently truncated every
lead window to whenever the next Monday happened to fall (day135 would have arrived a day
LATE despite declaring a 3-day lead)."""
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


def test_weekly_due_on_mondays_only():
    assert "weekly" in keys(date(2026, 8, 3))       # Monday
    assert "weekly" in keys(date(2026, 12, 28))     # Monday
    assert "weekly" not in keys(date(2026, 8, 4))   # Tuesday — daily runner must not re-open
    assert "weekly" not in keys(date(2026, 8, 9))   # Sunday


def test_dated_before_lead_not_due():
    assert "d" not in keys(date(2026, 7, 28))  # 6 days before, lead is 5


def test_dated_inside_lead_window_due():
    assert "d" in keys(date(2026, 7, 29))  # exactly due-lead — a Wednesday, not a Monday
    assert "d" in keys(date(2026, 8, 3))   # on the due date


def test_dated_lead_is_honoured_on_any_weekday():
    """Regression: with a Monday-only runner the declared lead silently vanished.

    day135 declares a 3-day lead on Sun 2026-10-25; the first Monday inside its window is
    2026-10-26 — the day AFTER the milestone. Every day in the window must be a firing day."""
    day135 = {"key": "day135", "type": "dated", "due": "2026-10-25", "lead_days": 3,
              "post_grace_days": 21, "title": "D135", "body": "b"}
    due = {r["key"] for r in cr.due_reminders([day135], date(2026, 10, 22))}
    assert "day135" in due, "must fire on the Thursday its 3-day lead opens, not the next Monday"


def test_dated_inside_grace_due():
    assert "d" in keys(date(2026, 8, 24))  # due+21 grace edge


def test_dated_after_grace_not_due():
    assert "d" not in keys(date(2026, 8, 25))  # past grace -> stale, no longer opens


class _FakeResp:
    def __init__(self, items): self._items = items
    def raise_for_status(self): pass
    def json(self): return {"items": self._items}


class _FakeSession:
    """Records the query and answers as GitHub does: `state:` only accepts open/closed, so a
    query carrying `state:all` matches nothing at all."""
    def __init__(self, existing): self.existing, self.queries = existing, []

    def get(self, url, params=None, timeout=None):
        q = (params or {})["q"]
        self.queries.append(q)
        if "state:all" in q:
            return _FakeResp([])
        want_open = "state:open" in q
        return _FakeResp([{"title": t} for t, is_open in self.existing
                          if (is_open or not want_open)])


def test_dated_dedup_finds_a_closed_issue():
    """Regression: dated reminders must dedup against CLOSED issues too.

    The old query used `state:all`, which GitHub does not support — it matched nothing, so
    every run re-opened the same milestone (issues #15/#18/#22 are one reminder, three times).
    With a daily runner that would have become one duplicate per day."""
    title = "Decision: Fallback-1 retry or formal cancel of Strategy B (Jul 24, 2026)"
    s = _FakeSession([(title, False)])  # exists, closed
    assert cr._issue_exists(s, "o/r", title, open_only=False) is True
    assert "state:all" not in s.queries[0]


def test_weekly_dedup_ignores_closed_issues():
    """The weekly check must re-open after the previous one is closed — that is its cadence."""
    title = "Weekly check: SPCX pipeline health"
    assert cr._issue_exists(_FakeSession([(title, False)]), "o/r", title, open_only=True) is False
    assert cr._issue_exists(_FakeSession([(title, True)]), "o/r", title, open_only=True) is True


def test_dedup_requires_an_exact_title_match():
    """Search is fuzzy; a near-miss title must not suppress a real reminder."""
    s = _FakeSession([("Check: spread entry window (Jul 6-17, 2025)", False)])
    assert cr._issue_exists(s, "o/r", "Check: spread entry window (Jul 6-17, 2026)", False) is False


def test_shipped_json_valid_and_has_prompts():
    rem = cr.load()
    assert len(rem) >= 5
    for r in rem:
        assert r["title"] and r["body"]
        assert "```" in r["body"], f"{r['key']} body must embed a copy-paste prompt"
        assert r.get("type") in ("weekly", "dated")
        if r["type"] == "dated":
            date.fromisoformat(r["due"])  # parses

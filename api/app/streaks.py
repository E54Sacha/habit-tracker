"""Streaks and history, computed from the days a habit was ticked."""

from collections.abc import Iterable
from datetime import date, timedelta

HISTORY_DAYS = 56  # the calendar shows the last 8 weeks, today included


def streak(days: Iterable[date], today: date) -> int:
    """Days in a row the habit was done, ending today, or ending yesterday if today isn't ticked yet
    (so the streak doesn't drop to 0 at midnight: it only breaks once a whole day is missed)."""
    done = set(days)
    day = today if today in done else today - timedelta(days=1)
    count = 0
    while day in done:
        count += 1
        day -= timedelta(days=1)
    return count


def history(days: Iterable[date], today: date) -> list[date]:
    """The ticked days shown in the calendar, oldest first."""
    start = today - timedelta(days=HISTORY_DAYS - 1)
    return sorted(d for d in set(days) if start <= d <= today)

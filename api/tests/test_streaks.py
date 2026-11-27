from datetime import date, timedelta

from app.streaks import HISTORY_DAYS, history, streak

TODAY = date(2026, 11, 27)


def days_ago(*ns):
    return [TODAY - timedelta(days=n) for n in ns]


def test_streak_counts_days_in_a_row_ending_today():
    assert streak(days_ago(0, 1, 2), TODAY) == 3


def test_streak_keeps_yesterdays_run_until_today_is_over():
    assert streak(days_ago(1, 2, 3), TODAY) == 3  # today not ticked yet: not broken


def test_streak_breaks_after_a_missed_day():
    assert streak(days_ago(2, 3, 4), TODAY) == 0
    assert streak(days_ago(0, 2, 3), TODAY) == 1


def test_streak_ignores_order_and_duplicates_and_crosses_months():
    days = days_ago(*range(30)) + days_ago(3, 5)
    assert streak(reversed(days), TODAY) == 30


def test_no_check_ins():
    assert streak([], TODAY) == 0
    assert history([], TODAY) == []


def test_history_keeps_the_last_8_weeks_oldest_first():
    days = days_ago(0, HISTORY_DAYS - 1, HISTORY_DAYS, 10) + [TODAY + timedelta(days=1)]
    assert history(days, TODAY) == days_ago(HISTORY_DAYS - 1, 10, 0)

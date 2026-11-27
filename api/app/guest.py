"""'Try as guest': a temporary account filled with realistic demo habits."""

import secrets
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .models import CheckIn, Habit, User
from .security import hash_password

GUEST_LIFETIME = timedelta(hours=24)
MAX_GUESTS_PER_HOUR = 200  # stops a script from filling the free database with demo accounts


def _days(today: date, ago: range, skip: set[int] = frozenset()) -> list[date]:
    """today - n days, for each n in `ago` except the ones in `skip`."""
    return [today - timedelta(days=n) for n in ago if n not in skip]


def demo_habits(today: date) -> list[tuple[str, int, list[date]]]:
    """(name, created N days ago, ticked days). Fixed patterns, so the demo always looks the same."""
    return [
        # A long streak still going; today not ticked yet, so there's something to tick.
        ("Read 10 pages", 42, _days(today, range(1, 43), skip={24, 25, 31})),
        # Every day except a miss 4 days ago; already done today.
        ("Drink 2 litres of water", 40, _days(today, range(0, 41), skip={4, 13, 27})),
        # On and off: about 3 days out of 5.
        ("Walk 20 minutes", 38, _days(today, range(0, 39), skip={n for n in range(0, 39) if n % 5 in (0, 3)})),
        # Started a few days ago.
        ("Stretch 5 minutes", 4, _days(today, range(1, 4))),
    ]


def delete_expired_guests(db: Session) -> None:
    cutoff = datetime.now(UTC) - GUEST_LIFETIME
    db.execute(delete(User).where(User.is_guest, User.created_at < cutoff))  # habits and check-ins go too (CASCADE)


def too_many_recent_guests(db: Session) -> bool:
    since = datetime.now(UTC) - timedelta(hours=1)
    return db.scalar(select(func.count()).select_from(User).where(User.is_guest, User.created_at >= since)) >= MAX_GUESTS_PER_HOUR


def create_guest(db: Session, today: date) -> User:
    # ".invalid" is a reserved domain: this address can never belong to a real person.
    user = User(email=f"guest-{secrets.token_hex(8)}@demo.invalid", password_hash=hash_password(secrets.token_urlsafe(32)), is_guest=True)
    db.add(user)
    db.flush()
    for name, created_days_ago, ticked in demo_habits(today):
        created = datetime.combine(today - timedelta(days=created_days_ago), time(9, 0), tzinfo=UTC)
        habit = Habit(user_id=user.id, name=name, created_at=created)
        db.add(habit)
        db.flush()
        db.add_all(CheckIn(habit_id=habit.id, day=day) for day in ticked)
    return user

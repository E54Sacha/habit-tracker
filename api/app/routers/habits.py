"""Habits of the logged-in user, and ticking them for today.

Every query filters on the current user, and a habit that belongs to someone else
answers 404 (not 403), so the API doesn't even confirm it exists.
"""

from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import AfterValidator, BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert

from ..deps import DB, CurrentUser
from ..models import CheckIn, Habit

router = APIRouter(prefix="/habits", tags=["habits"])

MAX_HABITS = 50  # per user: plenty for real use, and caps what one account can store


def _one_line(value: str) -> str:
    value = " ".join(value.split())  # trims and turns newlines/tabs/repeated spaces into one space
    if not value:
        raise ValueError("Name can't be empty")
    return value


HabitName = Annotated[str, Field(max_length=60), AfterValidator(_one_line)]


def check_today(day: date) -> date:
    """The browser sends its local date. Time zones run from UTC-12 to UTC+14, so any real
    'today' is within one day of the UTC date; anything else is refused (no ticking last month)."""
    utc_today = datetime.now(UTC).date()
    if abs((day - utc_today).days) > 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "You can only tick a habit for today")
    return day


Today = Annotated[date, Query(description="The user's local date, YYYY-MM-DD")]


class HabitIn(BaseModel):
    name: HabitName


class HabitOut(BaseModel):
    id: int
    name: str
    done_today: bool


def _own_habit(db: DB, user: CurrentUser, habit_id: int) -> Habit:
    habit = db.scalar(select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id))
    if habit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Habit not found")
    return habit


def _is_done(db: DB, habit_id: int, day: date) -> bool:
    return db.scalar(select(func.count()).where(CheckIn.habit_id == habit_id, CheckIn.day == day)) > 0


@router.get("")
def list_habits(db: DB, user: CurrentUser, today: Today) -> list[HabitOut]:
    check_today(today)
    done = select(CheckIn.habit_id).where(CheckIn.day == today)
    rows = db.execute(
        select(Habit.id, Habit.name, Habit.id.in_(done)).where(Habit.user_id == user.id).order_by(Habit.created_at, Habit.id)
    )
    return [HabitOut(id=id_, name=name, done_today=is_done) for id_, name, is_done in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_habit(body: HabitIn, db: DB, user: CurrentUser) -> HabitOut:
    count = db.scalar(select(func.count()).select_from(Habit).where(Habit.user_id == user.id))
    if count >= MAX_HABITS:
        raise HTTPException(status.HTTP_409_CONFLICT, f"You can have at most {MAX_HABITS} habits")
    habit = Habit(user_id=user.id, name=body.name)
    db.add(habit)
    db.commit()
    return HabitOut(id=habit.id, name=habit.name, done_today=False)


@router.patch("/{habit_id}")
def rename_habit(habit_id: int, body: HabitIn, db: DB, user: CurrentUser, today: Today) -> HabitOut:
    habit = _own_habit(db, user, habit_id)
    habit.name = body.name
    db.commit()
    return HabitOut(id=habit.id, name=habit.name, done_today=_is_done(db, habit.id, check_today(today)))


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: DB, user: CurrentUser) -> None:
    db.delete(_own_habit(db, user, habit_id))  # its check-ins go too (ON DELETE CASCADE)
    db.commit()


# PUT and DELETE are idempotent: ticking twice, or a retried request, changes nothing.
@router.put("/{habit_id}/check-ins/{day}", status_code=status.HTTP_204_NO_CONTENT)
def tick(habit_id: int, day: date, db: DB, user: CurrentUser) -> None:
    habit = _own_habit(db, user, habit_id)
    check_today(day)
    db.execute(insert(CheckIn).values(habit_id=habit.id, day=day).on_conflict_do_nothing(constraint="uq_check_ins_habit_day"))
    db.commit()


@router.delete("/{habit_id}/check-ins/{day}", status_code=status.HTTP_204_NO_CONTENT)
def untick(habit_id: int, day: date, db: DB, user: CurrentUser) -> None:
    habit = _own_habit(db, user, habit_id)
    check_today(day)
    db.execute(delete(CheckIn).where(CheckIn.habit_id == habit.id, CheckIn.day == day))
    db.commit()

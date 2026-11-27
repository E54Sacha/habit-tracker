"""Tables. Any change here needs a new migration: alembic revision --autogenerate -m "what changed"."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, UniqueConstraint, false, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_guest_created_at", "created_at", postgresql_where=text("is_guest")),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stored lowercased, so "Me@x.com" and "me@x.com" are the same account.
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # "Try as guest" accounts: no usable password, deleted 24 hours after they're created.
    is_guest: Mapped[bool] = mapped_column(Boolean, server_default=false())

    habits: Mapped[list["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="habits")
    check_ins: Mapped[list["CheckIn"]] = relationship(back_populates="habit", cascade="all, delete-orphan", passive_deletes=True)


class CheckIn(Base):
    """One row per habit per day it was done."""

    __tablename__ = "check_ins"
    __table_args__ = (UniqueConstraint("habit_id", "day", name="uq_check_ins_habit_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"), index=True)
    # The user's local date (sent by the browser), not a UTC timestamp: "done on Tuesday" is what counts.
    day: Mapped[date] = mapped_column(Date)

    habit: Mapped[Habit] = relationship(back_populates="check_ins")

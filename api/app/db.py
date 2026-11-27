"""Database connection: one engine for the app, one session per request."""

from collections.abc import Iterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    # Predictable names for indexes and unique constraints, so migrations can refer to them.
    metadata = MetaData(naming_convention={"ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s"})


# pool_pre_ping: hosted Postgres (Neon) closes idle connections; check before reusing one.
# connect_timeout: fail in seconds (not minutes) when the database is down, e.g. Docker not started.
engine = create_engine(
    get_settings().database_url, pool_pre_ping=True, pool_size=5, max_overflow=5, connect_args={"connect_timeout": 10}
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session

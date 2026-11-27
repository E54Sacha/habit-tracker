"""Tests run against a real PostgreSQL database (habits_test), never the development one.

Locally: docker compose up -d (creates habits_test). In CI: a Postgres service container.
"""

import os

# Must be set before the app is imported: app.db creates its engine from it.
TEST_DATABASE_URL = os.environ.setdefault(
    "TEST_DATABASE_URL", "postgresql+psycopg://habits:habits@localhost:5432/habits_test"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ENVIRONMENT"] = "test"
os.environ["COOKIE_SECURE"] = "false"

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402

API_DIR = Path(__file__).resolve().parent.parent


def alembic_config() -> Config:
    config = Config(str(API_DIR / "alembic.ini"))
    config.attributes["database_url"] = TEST_DATABASE_URL
    return config


@pytest.fixture(scope="session", autouse=True)
def schema():
    """Build the schema with the real migrations, exactly like production."""
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables():
    """Every test starts with empty tables."""
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE users, habits, check_ins RESTART IDENTITY CASCADE"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def make_client():
    """Several independent browsers (each with its own cookies)."""
    return lambda: TestClient(app)

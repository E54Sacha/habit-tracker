from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.db import Base, engine


def test_migrations_match_the_models():
    """If this fails, a model changed without a migration: alembic revision --autogenerate -m "..." """
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), Base.metadata)
    assert diff == []

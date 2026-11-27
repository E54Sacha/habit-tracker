import pytest
from pydantic import ValidationError

from app.config import Settings


def test_hosted_database_urls_use_psycopg():
    for url in ("postgres://u:p@host/db", "postgresql://u:p@host/db"):
        assert Settings(database_url=url).database_url == "postgresql+psycopg://u:p@host/db"


def test_production_refuses_unsafe_settings():
    strong = "x" * 48
    with pytest.raises(ValidationError):
        Settings(environment="production", cookie_secure=True)  # default dev secret
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret=strong, cookie_secure=False)
    assert Settings(environment="production", jwt_secret=strong, cookie_secure=True).cookie_secure

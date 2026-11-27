"""Settings read from environment variables (or api/.env locally)."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET = "dev-only-secret-change-me-not-for-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://habits:habits@localhost:5432/habits"
    jwt_secret: str = DEV_SECRET
    # One token, valid for 7 days: log in once a week at most.
    token_days: int = 7
    # Must be true in production so the cookie only travels over HTTPS.
    cookie_secure: bool = False
    environment: str = "development"

    @model_validator(mode="after")
    def check(self) -> "Settings":
        # Hosts like Neon and Render give "postgres://" or "postgresql://" URLs;
        # SQLAlchemy needs to be told to use the psycopg 3 driver.
        for prefix in ("postgres://", "postgresql://"):
            if self.database_url.startswith(prefix):
                self.database_url = "postgresql+psycopg://" + self.database_url[len(prefix) :]
        if self.environment == "production":
            if self.jwt_secret == DEV_SECRET or len(self.jwt_secret) < 32:
                raise ValueError("Set JWT_SECRET to a long random string in production.")
            if not self.cookie_secure:
                raise ValueError("Set COOKIE_SECURE=true in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

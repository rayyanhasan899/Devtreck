from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)
    app_env: Literal["development", "test", "production"] = "development"
    app_debug: bool = False
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8002",
    ]
    database_url: SecretStr | None = None
    reward_task_xp: int = Field(default=10, ge=0, le=10000)
    reward_daily_xp: int = Field(default=5, ge=0, le=10000)
    reward_focus_xp: int = Field(default=5, ge=0, le=10000)
    reward_focus_min_seconds: int = Field(default=1500, ge=60, le=10800)
    reward_focus_daily_cap: int = Field(default=4, ge=0, le=100)

    @model_validator(mode="after")
    def secure_production(self) -> Settings:
        for origin in self.allowed_origins:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in ("http", "https")
                or not parsed.hostname
                or "*" in origin
                or parsed.username
                or parsed.password
                or parsed.path
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("Origins must be exact HTTP(S) origins")
        if self.app_env == "production" and any(
            not origin.startswith("https://") for origin in self.allowed_origins
        ):
            raise ValueError("Production requires explicit HTTPS origins")
        if self.app_env == "production" and self.app_debug:
            raise ValueError("Debug must be disabled in production")
        if self.database_url is not None:
            try:
                url = make_url(self.database_url.get_secret_value())
                valid = url.drivername == "postgresql+psycopg" and bool(url.database)
            except ArgumentError, ValueError:
                valid = False
            if not valid:
                raise ValueError("A valid PostgreSQL psycopg database URL is required")
        if self.app_env == "production" and self.database_url is None:
            raise ValueError("Production requires database configuration")
        return self

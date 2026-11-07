from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)
    app_env: Literal["development", "test", "production"] = "development"
    app_debug: bool = False
    database_url: SecretStr | None = None

    @model_validator(mode="after")
    def secure_production(self) -> Settings:
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

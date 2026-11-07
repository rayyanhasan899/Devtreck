from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: Literal["development", "test", "production"] = "development"
    app_debug: bool = False

    @model_validator(mode="after")
    def secure_production(self) -> Settings:
        if self.app_env == "production" and self.app_debug:
            raise ValueError("Debug must be disabled in production")
        return self

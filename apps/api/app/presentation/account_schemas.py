from datetime import datetime
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lower()


class Register(Login):
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def name_valid(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name is required")
        return value.strip()


class ProfilePatch(Input):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    time_zone: str | None = Field(default=None, max_length=100)
    theme: Literal["light", "dark", "system"] | None = None
    current_password: str | None = Field(default=None, max_length=128)

    @field_validator("name", "email", mode="before")
    @classmethod
    def trim(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @field_validator("time_zone")
    @classmethod
    def valid_zone(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                ZoneInfo(value)
            except ZoneInfoNotFoundError, ValueError:
                raise ValueError("Invalid time zone") from None
        return value

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Name required")
        return value


class PasswordChange(Input):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class DeleteAccount(Input):
    current_password: str = Field(min_length=1, max_length=128)
    confirm: Literal[True]


class Profile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    time_zone: str
    theme: str
    created_at: datetime


class SessionResponse(BaseModel):
    profile: Profile
    csrf_token: str

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.presentation.task_schemas import TaskResponse


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ItemInput(Input):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def trim(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title required")
        return value.strip()


class ItemPatch(Input):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def trim(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Title required")
        return value.strip() if value is not None else None


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    completed: bool
    position: int


class OrderInput(Input):
    ids: list[UUID] = Field(max_length=100)


class PlanInput(Input):
    order_ids: list[UUID] = Field(max_length=500)
    priority_ids: list[UUID] = Field(max_length=3)


class PlanResponse(BaseModel):
    day: date
    time_zone: str
    total: int
    truncated: bool
    priority_ids: list[str]
    suggested_ids: list[str]
    estimated_minutes: int
    missing_estimates: int
    reasons: dict[str, list[str]]
    items: list[TaskResponse]


class StartFocus(Input):
    key: UUID
    task_id: UUID | None = None
    kind: Literal["focus", "break"] = "focus"
    seconds: int = Field(default=1500, ge=60, le=10800)


class Command(Input):
    key: UUID


class FocusResponse(BaseModel):
    id: UUID
    task_id: UUID | None
    kind: str
    status: str
    target_seconds: int
    elapsed_seconds: int
    started_at: datetime
    ended_at: datetime | None
    server_now: datetime


class FocusTotals(BaseModel):
    day_seconds: int
    week_seconds: int
    day: date
    week_start: date
    time_zone: str

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

Status = Literal["pending", "in-progress", "completed"]
TaskType = Literal["one-time", "daily"]
Priority = Literal["low", "medium", "high"]


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    task_type: TaskType = "one-time"
    priority: Priority = "medium"
    category_id: UUID | None = None
    due_date: date | None = None
    due_at: AwareDatetime | None = None
    estimated_minutes: int | None = Field(default=None, gt=0, le=10080)

    @field_validator("title")
    @classmethod
    def title_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title required")
        return value.strip()

    @model_validator(mode="after")
    def due_exclusive(self) -> TaskInput:
        if self.due_date is not None and self.due_at is not None:
            raise ValueError("Choose date-only or timed deadline")
        return self


class TaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    status: Status | None = None
    task_type: TaskType | None = None
    priority: Priority | None = None
    category_id: UUID | None = None
    due_date: date | None = None
    due_at: AwareDatetime | None = None
    estimated_minutes: int | None = Field(default=None, gt=0, le=10080)

    @model_validator(mode="after")
    def required_values(self) -> TaskPatch:
        for key in ("title", "status", "task_type", "priority"):
            if key in self.model_fields_set and getattr(self, key) is None:
                raise ValueError("Required task field cannot be null")
        if self.title is not None:
            if not self.title.strip():
                raise ValueError("Title required")
            self.title = self.title.strip()
        return self


class StreakResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    current_streak: int
    best_streak: int
    today_completed: bool
    last_qualified_day: date | None
    total_completions: int
    current_day: date
    time_zone: str


class DailyHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    epoch: UUID
    completion_day: date
    completed_at: datetime
    time_zone: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str | None
    status: Status
    task_type: TaskType
    priority: Priority
    category_id: UUID | None
    due_date: date | None
    due_at: datetime | None
    estimated_minutes: int | None
    created_at: datetime
    updated_at: datetime
    streak: StreakResponse | None = None


class TaskPage(BaseModel):
    items: list[TaskResponse]
    total: int
    limit: int
    offset: int


class CategoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name required")
        return value.strip()


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    completed_at: datetime


class TaskFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    view: Literal["all", "today", "upcoming", "overdue", "daily", "completed"] = "all"
    search: str | None = Field(default=None, max_length=200)
    status: Status | None = None
    task_type: TaskType | None = None
    priority: Priority | None = None
    category_id: UUID | None = None
    due_date: date | None = None
    overdue: bool | None = None
    sort: Literal["created_at", "updated_at", "title", "priority", "due_date"] = "created_at"
    descending: bool = True
    limit: int = Field(default=25, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=10000)


class DashboardResponse(BaseModel):
    today_actionable: int
    outstanding: int
    completions_today: int
    daily_total: int
    daily_done: int

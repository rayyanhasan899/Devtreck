from datetime import date, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.presentation.productivity import service
from app.presentation.tasks import Tasks

router = APIRouter(prefix="/api", tags=["progress"])


class RulesResponse(BaseModel):
    task_xp: int
    daily_xp: int
    focus_xp: int
    focus_min_seconds: int
    focus_daily_cap: int
    level_step: int


class BadgeResponse(BaseModel):
    key: str
    name: str
    reason: str
    earned_at: datetime | None


class PeriodResponse(BaseModel):
    start: date
    end: date
    completed: int
    eligible: int
    eligible_completed: int
    covered_days: int
    days: int
    completion_rate: float | None
    focus_seconds: int
    focus_sessions: int


class TrendResponse(BaseModel):
    day: date
    completed: int
    focus_seconds: int


class CategoryResponse(BaseModel):
    name: str
    completed: int


class ProgressResponse(BaseModel):
    time_zone: str
    xp: int
    level: int
    level_progress: int
    next_level_xp: int
    rules: RulesResponse
    badges: list[BadgeResponse]
    today: PeriodResponse
    week: PeriodResponse
    trends: list[TrendResponse]
    categories: list[CategoryResponse]
    current_streak: int
    best_streak: int
    daily_completions: int


@router.get("/progress", response_model=ProgressResponse)
def progress(tasks: Tasks) -> ProgressResponse:
    service(tasks).current()
    result = tasks.progress().report()
    tasks.uow.commit()
    return ProgressResponse.model_validate(result)

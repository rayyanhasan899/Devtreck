from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from app.domain.streaks import Clock, utc_now
from app.domain.tasks import TaskQuery
from app.persistence.models import TaskModel
from app.presentation.accounts import Database, authenticated
from app.presentation.task_schemas import (
    CategoryInput,
    CategoryResponse,
    DailyHistoryResponse,
    HistoryResponse,
    StreakResponse,
    TaskFilters,
    TaskInput,
    TaskPage,
    TaskPatch,
    TaskResponse,
)
from app.services.tasks import TasksService

router = APIRouter(prefix="/api", tags=["tasks"])


def get_clock() -> Clock:
    return utc_now


def service(
    request: Request,
    db: Database,
    clock: Annotated[Clock, Depends(get_clock)],
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> TasksService:
    mutate = request.method not in ("GET", "HEAD", "OPTIONS")
    if mutate and request.headers.get("origin") not in request.app.state.settings.allowed_origins:
        raise HTTPException(403, "Origin rejected")
    _, user = authenticated(request, db, mutate)
    return TasksService(db, user.id, user.time_zone, clock)


Tasks = Annotated[TasksService, Depends(service)]


def render(tasks: TasksService, row: TaskModel) -> TaskResponse:
    result = TaskResponse.model_validate(row)
    if row.task_type == "daily":
        result.streak = StreakResponse.model_validate(tasks.streak(row))
    return result


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create(payload: TaskInput, tasks: Tasks) -> TaskResponse:
    return render(tasks, tasks.create(payload.model_dump()))


@router.get("/tasks", response_model=TaskPage)
def listing(filters: Annotated[TaskFilters, Query()], tasks: Tasks) -> TaskPage:
    rows, total = tasks.list(TaskQuery(**filters.model_dump()))
    summaries = tasks.streaks(rows)
    items = []
    for row in rows:
        item = TaskResponse.model_validate(row)
        if row.task_type == "daily":
            item.streak = StreakResponse.model_validate(summaries[row.id])
        items.append(item)
    return TaskPage(
        items=items,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def detail(task_id: UUID, tasks: Tasks) -> TaskResponse:
    return render(tasks, tasks.get(task_id))


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update(task_id: UUID, payload: TaskPatch, tasks: Tasks) -> TaskResponse:
    return render(tasks, tasks.update(task_id, payload.model_dump(exclude_unset=True)))


@router.delete("/tasks/{task_id}", status_code=204)
def delete(task_id: UUID, tasks: Tasks, confirm: Annotated[bool, Query()] = False) -> None:
    if not confirm:
        raise HTTPException(422, "Confirmation required")
    tasks.delete(task_id)


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete(task_id: UUID, tasks: Tasks) -> TaskResponse:
    return render(tasks, tasks.complete(task_id))


@router.post("/tasks/{task_id}/reopen", response_model=TaskResponse)
def reopen(task_id: UUID, tasks: Tasks) -> TaskResponse:
    return render(tasks, tasks.reopen(task_id))


@router.get("/tasks/{task_id}/history", response_model=list[HistoryResponse])
def history(
    task_id: UUID,
    tasks: Tasks,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
) -> list[HistoryResponse]:
    return [HistoryResponse.model_validate(row) for row in tasks.history(task_id, limit, offset)]


@router.get("/categories", response_model=list[CategoryResponse], tags=["categories"])
def categories(
    tasks: Tasks,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
) -> list[CategoryResponse]:
    return [CategoryResponse.model_validate(row) for row in tasks.categories(limit, offset)]


@router.post("/categories", response_model=CategoryResponse, status_code=201, tags=["categories"])
def create_category(payload: CategoryInput, tasks: Tasks) -> CategoryResponse:
    return CategoryResponse.model_validate(tasks.create_category(payload.name))


@router.get("/categories/{category_id}", response_model=CategoryResponse, tags=["categories"])
def category(category_id: UUID, tasks: Tasks) -> CategoryResponse:
    return CategoryResponse.model_validate(tasks.category(category_id))


@router.patch("/categories/{category_id}", response_model=CategoryResponse, tags=["categories"])
def rename_category(category_id: UUID, payload: CategoryInput, tasks: Tasks) -> CategoryResponse:
    return CategoryResponse.model_validate(tasks.rename_category(category_id, payload.name))


@router.delete("/categories/{category_id}", status_code=204, tags=["categories"])
def delete_category(
    category_id: UUID, tasks: Tasks, confirm: Annotated[bool, Query()] = False
) -> None:
    if not confirm:
        raise HTTPException(422, "Confirmation required")
    tasks.delete_category(category_id)


@router.get("/tasks/{task_id}/streak", response_model=StreakResponse)
def streak(task_id: UUID, tasks: Tasks) -> StreakResponse:
    return StreakResponse.model_validate(tasks.streak(tasks.get(task_id)))


@router.post("/tasks/{task_id}/streak/reconcile", response_model=StreakResponse)
def reconcile(task_id: UUID, tasks: Tasks) -> StreakResponse:
    return StreakResponse.model_validate(tasks.reconcile(task_id))


@router.get("/tasks/{task_id}/daily-history", response_model=list[DailyHistoryResponse])
def daily_history(
    task_id: UUID,
    tasks: Tasks,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
) -> list[DailyHistoryResponse]:
    return [
        DailyHistoryResponse.model_validate(row)
        for row in tasks.daily_history(task_id, limit, offset)
    ]

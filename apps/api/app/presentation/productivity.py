from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.domain.errors import ConflictError
from app.domain.productivity import active_seconds
from app.persistence.models import FocusSessionModel
from app.presentation.productivity_schemas import (
    Command,
    FocusResponse,
    FocusTotals,
    ItemInput,
    ItemPatch,
    ItemResponse,
    OrderInput,
    PlanInput,
    PlanResponse,
    StartFocus,
)
from app.presentation.task_schemas import StreakResponse, TaskResponse
from app.presentation.tasks import Tasks
from app.services.productivity import ProductivityService

router = APIRouter(prefix="/api", tags=["productivity"])


def service(tasks: Tasks) -> ProductivityService:
    return ProductivityService(
        tasks.repo.session, tasks.repo.owner, tasks.zone, tasks.clock, tasks.rules
    )


Productivity = Annotated[ProductivityService, Depends(service)]


def focus(row: FocusSessionModel, svc: ProductivityService) -> FocusResponse:
    now = svc.clock()
    return FocusResponse(
        id=row.id,
        task_id=row.task_id,
        kind=row.kind,
        status=row.status,
        target_seconds=row.target_seconds,
        elapsed_seconds=int(
            active_seconds(row.elapsed_seconds, row.active_since, now, row.target_seconds)
        ),
        started_at=row.started_at,
        ended_at=row.ended_at,
        server_now=now,
    )


@router.get("/plan/today", response_model=PlanResponse)
def plan(svc: Productivity, tasks: Tasks) -> PlanResponse:
    rows, meta = svc.plan()
    summaries = tasks.streaks(rows)
    progress = tasks.repo.checklist_progress([row.id for row in rows])
    items = []
    for row in rows:
        item = TaskResponse.model_validate(row)
        item.checklist_total, item.checklist_completed = progress.get(row.id, (0, 0))
        if row.task_type == "daily":
            item.streak = StreakResponse.model_validate(summaries[row.id])
        items.append(item)
    return PlanResponse.model_validate({**meta, "items": items})


@router.put("/plan/today", status_code=204)
def save_plan(payload: PlanInput, svc: Productivity) -> None:
    svc.save_plan(payload.order_ids, payload.priority_ids)


@router.get("/tasks/{task_id}/checklist", response_model=list[ItemResponse])
def checklist(task_id: UUID, svc: Productivity) -> list[ItemResponse]:
    return [ItemResponse.model_validate(row) for row in svc.checklist(task_id)]


@router.post("/tasks/{task_id}/checklist", response_model=ItemResponse, status_code=201)
def add_item(task_id: UUID, payload: ItemInput, svc: Productivity) -> ItemResponse:
    return ItemResponse.model_validate(svc.add_item(task_id, payload.title))


@router.patch("/tasks/{task_id}/checklist/{item_id}", response_model=ItemResponse)
def edit_item(task_id: UUID, item_id: UUID, payload: ItemPatch, svc: Productivity) -> ItemResponse:
    return ItemResponse.model_validate(
        svc.edit_item(task_id, item_id, payload.title, payload.completed)
    )


@router.delete("/tasks/{task_id}/checklist/{item_id}", status_code=204)
def delete_item(task_id: UUID, item_id: UUID, svc: Productivity) -> None:
    svc.delete_item(task_id, item_id)


@router.put("/tasks/{task_id}/checklist-order", response_model=list[ItemResponse])
def order(task_id: UUID, payload: OrderInput, svc: Productivity) -> list[ItemResponse]:
    return [ItemResponse.model_validate(row) for row in svc.reorder(task_id, payload.ids)]


@router.post("/focus", response_model=FocusResponse, status_code=201)
def start(payload: StartFocus, svc: Productivity) -> FocusResponse:
    if payload.kind == "break" and payload.seconds > 3600:
        raise ConflictError()
    return focus(
        svc.command(
            payload.key,
            "start",
            task_id=payload.task_id,
            kind=payload.kind,
            seconds=payload.seconds,
        ),
        svc,
    )


@router.get("/focus/current", response_model=FocusResponse | None)
def current(svc: Productivity) -> FocusResponse | None:
    row = svc.current()
    return focus(row, svc) if row else None


@router.get("/focus/history", response_model=list[FocusResponse])
def history(
    svc: Productivity,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
) -> list[FocusResponse]:
    return [focus(row, svc) for row in svc.history(limit, offset)]


@router.get("/focus/summary", response_model=FocusTotals)
def totals(svc: Productivity) -> FocusTotals:
    return FocusTotals.model_validate(svc.totals())


@router.post("/focus/{session_id}/{action}", response_model=FocusResponse)
def command(
    session_id: UUID,
    action: Literal["pause", "resume", "stop"],
    payload: Command,
    svc: Productivity,
) -> FocusResponse:
    return focus(svc.command(payload.key, action, session_id=session_id), svc)

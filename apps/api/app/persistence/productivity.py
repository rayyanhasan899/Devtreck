from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.errors import NotFoundError
from app.persistence.models import (
    ChecklistModel,
    DailyPlanModel,
    FocusEventModel,
    FocusIntervalModel,
    FocusSessionModel,
)


class ProductivityRepository:
    def __init__(self, db: Session, owner: UUID) -> None:
        self.db, self.owner = db, owner

    def add(self, row: object) -> None:
        self.db.add(row)

    def checklist(self, task_id: UUID) -> Sequence[ChecklistModel]:
        return self.db.scalars(
            select(ChecklistModel)
            .where(ChecklistModel.task_id == task_id, ChecklistModel.user_id == self.owner)
            .order_by(ChecklistModel.position)
        ).all()

    def remove(self, row: object) -> None:
        self.db.delete(row)

    def focus(self, session_id: UUID) -> FocusSessionModel:
        row = self.db.scalar(
            select(FocusSessionModel)
            .where(FocusSessionModel.id == session_id, FocusSessionModel.user_id == self.owner)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if row is None:
            raise NotFoundError()
        return row

    def current(self) -> FocusSessionModel | None:
        return self.db.scalar(
            select(FocusSessionModel)
            .where(
                FocusSessionModel.user_id == self.owner,
                FocusSessionModel.status.in_(["active", "paused"]),
            )
            .with_for_update()
        )

    def event(self, key: UUID) -> FocusEventModel | None:
        return self.db.scalar(
            select(FocusEventModel).where(
                FocusEventModel.user_id == self.owner, FocusEventModel.command_key == key
            )
        )

    def history(self, limit: int, offset: int) -> Sequence[FocusSessionModel]:
        return self.db.scalars(
            select(FocusSessionModel)
            .where(FocusSessionModel.user_id == self.owner)
            .order_by(FocusSessionModel.started_at.desc(), FocusSessionModel.id)
            .limit(limit)
            .offset(offset)
        ).all()

    def intervals(self, since: datetime) -> Sequence[FocusIntervalModel]:
        return self.db.scalars(
            select(FocusIntervalModel)
            .join(FocusSessionModel, FocusIntervalModel.session_id == FocusSessionModel.id)
            .where(
                FocusIntervalModel.user_id == self.owner,
                FocusSessionModel.kind == "focus",
                FocusIntervalModel.ended_at > since,
            )
        ).all()

    def plan(self, day: object) -> DailyPlanModel | None:
        return self.db.scalar(
            select(DailyPlanModel).where(
                DailyPlanModel.user_id == self.owner, DailyPlanModel.day == day
            )
        )

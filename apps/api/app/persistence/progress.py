from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.persistence.models import (
    AchievementModel,
    CategoryModel,
    CompletionModel,
    DailyCompletionModel,
    FocusIntervalModel,
    FocusSessionModel,
    InsightDayModel,
    OccurrenceModel,
    TaskModel,
    XPLedgerModel,
)


class ProgressRepository:
    def __init__(self, db: Session, owner: UUID) -> None:
        self.db, self.owner = db, owner

    def tasks(self) -> list[TaskModel]:
        return list(self.db.scalars(select(TaskModel).where(TaskModel.user_id == self.owner)))

    def completions(self) -> list[CompletionModel]:
        return list(
            self.db.scalars(select(CompletionModel).where(CompletionModel.user_id == self.owner))
        )

    def daily(self) -> list[DailyCompletionModel]:
        return list(
            self.db.scalars(
                select(DailyCompletionModel).where(DailyCompletionModel.user_id == self.owner)
            )
        )

    def focus(self) -> list[FocusSessionModel]:
        return list(
            self.db.scalars(
                select(FocusSessionModel)
                .where(FocusSessionModel.user_id == self.owner)
                .order_by(FocusSessionModel.ended_at, FocusSessionModel.id)
            )
        )

    def intervals(self) -> list[FocusIntervalModel]:
        return list(
            self.db.scalars(
                select(FocusIntervalModel)
                .join(FocusSessionModel, FocusSessionModel.id == FocusIntervalModel.session_id)
                .where(FocusIntervalModel.user_id == self.owner, FocusSessionModel.kind == "focus")
            )
        )

    def ledger(self) -> list[XPLedgerModel]:
        return list(
            self.db.scalars(select(XPLedgerModel).where(XPLedgerModel.user_id == self.owner))
        )

    def award(
        self,
        kind: str,
        source: UUID,
        amount: int,
        day: date,
        occurred: datetime,
        now: datetime,
        policy: str,
    ) -> None:
        self.db.execute(
            insert(XPLedgerModel)
            .values(
                user_id=self.owner,
                source_kind=kind,
                source_id=source,
                amount=amount,
                reward_day=day,
                occurred_at=occurred,
                awarded_at=now,
                policy=policy,
            )
            .on_conflict_do_nothing()
        )

    def badges(self) -> list[AchievementModel]:
        return list(
            self.db.scalars(select(AchievementModel).where(AchievementModel.user_id == self.owner))
        )

    def badge(self, key: str, now: datetime) -> None:
        self.db.execute(
            insert(AchievementModel)
            .values(user_id=self.owner, key=key, earned_at=now)
            .on_conflict_do_nothing()
        )

    def days(self) -> list[InsightDayModel]:
        return list(
            self.db.scalars(
                select(InsightDayModel)
                .where(InsightDayModel.user_id == self.owner)
                .order_by(InsightDayModel.day)
            )
        )

    def cover(self, day: date, zone: str) -> None:
        self.db.execute(
            insert(InsightDayModel)
            .values(user_id=self.owner, day=day, time_zone=zone)
            .on_conflict_do_nothing()
        )

    def record_occurrences(self, values: list[dict[str, object]]) -> None:
        if not values:
            return
        self.db.execute(
            insert(OccurrenceModel)
            .values([{**value, "user_id": self.owner} for value in values])
            .on_conflict_do_nothing()
        )

    def occurrences(self, start: date, end: date) -> list[OccurrenceModel]:
        return list(
            self.db.scalars(
                select(OccurrenceModel)
                .join(TaskModel, TaskModel.id == OccurrenceModel.task_id)
                .where(
                    OccurrenceModel.user_id == self.owner,
                    TaskModel.deleted_at.is_(None),
                    OccurrenceModel.day.between(start, end),
                )
            )
        )

    def categories(self) -> dict[UUID, str]:
        return {
            row.id: row.name
            for row in self.db.scalars(
                select(CategoryModel).where(CategoryModel.user_id == self.owner)
            )
        }

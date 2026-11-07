from collections.abc import Sequence
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errors import ConflictError
from app.domain.streaks import Clock, DailyFact, Streak, calculate, local_day, utc_now
from app.domain.tasks import TaskQuery
from app.persistence.models import CategoryModel, CompletionModel, DailyCompletionModel, TaskModel
from app.persistence.tasks import TasksRepository
from app.persistence.unit_of_work import SqlUnitOfWork


class TasksService:
    def __init__(self, session: Session, owner: UUID, zone: str, clock: Clock = utc_now) -> None:
        self.repo = TasksRepository(session, owner)
        self.uow = SqlUnitOfWork(session)
        self.zone = zone
        self.clock = clock

    def commit(self) -> None:
        try:
            self.uow.commit()
        except IntegrityError:
            raise ConflictError() from None

    def get(self, task_id: UUID) -> TaskModel:
        return self.repo.task(task_id)

    def categories(self, limit: int, offset: int) -> Sequence[CategoryModel]:
        return self.repo.categories(limit, offset)

    def category(self, category_id: UUID) -> CategoryModel:
        return self.repo.category(category_id)

    def create(self, values: dict[str, object]) -> TaskModel:
        category_id = values.get("category_id")
        if isinstance(category_id, UUID):
            self.repo.category(category_id)
        row = self.repo.add_task(values)
        if row.task_type == "daily":
            row.daily_started_at = self.clock()
            row.daily_epoch = uuid4()
        self.commit()
        return row

    def update(self, task_id: UUID, changes: dict[str, object]) -> TaskModel:
        self.zone = self.repo.lock_owner().time_zone
        row = self.repo.task(task_id)
        category_id = changes.get("category_id")
        if isinstance(category_id, UUID):
            self.repo.category(category_id)
        due_date = changes.get("due_date", row.due_date)
        due_at = changes.get("due_at", row.due_at)
        if due_date is not None and due_at is not None:
            raise ConflictError()
        next_type = changes.get("task_type", row.task_type)
        if next_type != row.task_type:
            self.repo.record_type(row, str(next_type))
            row.daily_started_at = self.clock() if next_type == "daily" else None
            row.daily_epoch = uuid4() if next_type == "daily" else None
            row.current_streak = 0
            row.status = "pending"
        requested_status = changes.pop("status", None)
        for key, value in changes.items():
            setattr(row, key, value)
        if requested_status == "completed":
            self.complete_row(row)
        elif requested_status is not None:
            row.status = str(requested_status)
        row.updated_at = self.clock()
        self.commit()
        return row

    def complete_row(self, row: TaskModel) -> None:
        if row.task_type != "daily":
            self.repo.complete(row)
            return
        # Lock profile before sampling time; timezone edits use this same lock.
        self.zone = self.repo.lock_owner().time_zone
        instant = self.clock()
        day = local_day(instant, self.zone)
        if row.daily_epoch is None:
            row.daily_epoch = uuid4()
        self.repo.add_daily(row, day, instant, self.zone)
        summary = self.streak(row, instant)
        row.current_streak = summary.current_streak
        row.best_streak = summary.best_streak
        row.last_qualified_day = summary.last_qualified_day
        row.status = "pending"

    def streaks(
        self, rows: Sequence[TaskModel], instant: datetime | None = None
    ) -> dict[UUID, Streak]:
        facts = self.repo.daily_facts([row.id for row in rows])
        grouped: dict[UUID, list[DailyFact]] = {}
        for fact in facts:
            grouped.setdefault(fact.task_id, []).append(DailyFact(fact.epoch, fact.completion_day))
        today = local_day(instant or self.clock(), self.zone)
        return {
            row.id: calculate(grouped.get(row.id, []), row.daily_epoch, today, self.zone)
            for row in rows
        }

    def streak(self, row: TaskModel, instant: datetime | None = None) -> Streak:
        if row.task_type != "daily":
            raise ConflictError()
        return self.streaks([row], instant)[row.id]

    def reconcile(self, task_id: UUID) -> Streak:
        self.zone = self.repo.lock_owner().time_zone
        row = self.repo.task(task_id)
        summary = self.streak(row)
        row.current_streak = summary.current_streak if row.task_type == "daily" else 0
        row.best_streak = summary.best_streak
        row.last_qualified_day = summary.last_qualified_day
        self.commit()
        return summary

    def daily_history(
        self, task_id: UUID, limit: int, offset: int
    ) -> Sequence[DailyCompletionModel]:
        return self.repo.daily_history(task_id, limit, offset)

    def complete(self, task_id: UUID) -> TaskModel:
        self.zone = self.repo.lock_owner().time_zone
        row = self.repo.task(task_id)
        self.complete_row(row)
        self.commit()
        return row

    def reopen(self, task_id: UUID) -> TaskModel:
        row = self.repo.task(task_id)
        # Reopening a daily task never removes today's qualified credit.
        row.status = "pending"
        self.commit()
        return row

    def delete(self, task_id: UUID) -> None:
        self.repo.task(task_id).deleted_at = self.clock()
        self.commit()

    def list(self, query: TaskQuery) -> tuple[Sequence[TaskModel], int]:
        return self.repo.list(query, self.zone, self.clock())

    def history(self, task_id: UUID, limit: int, offset: int) -> Sequence[CompletionModel]:
        return self.repo.history(task_id, limit, offset)

    def create_category(self, name: str) -> CategoryModel:
        row = self.repo.add_category(name)
        self.commit()
        return row

    def rename_category(self, category_id: UUID, name: str) -> CategoryModel:
        row = self.repo.category(category_id)
        row.name = name
        row.updated_at = self.clock()
        self.commit()
        return row

    def delete_category(self, category_id: UUID) -> None:
        self.repo.delete_category(self.repo.category(category_id))
        self.commit()

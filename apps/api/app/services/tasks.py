from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errors import ConflictError
from app.domain.tasks import TaskQuery
from app.persistence.models import CategoryModel, CompletionModel, TaskModel
from app.persistence.tasks import TasksRepository
from app.persistence.unit_of_work import SqlUnitOfWork


class TasksService:
    def __init__(self, session: Session, owner: UUID, zone: str) -> None:
        self.repo = TasksRepository(session, owner)
        self.uow = SqlUnitOfWork(session)
        self.zone = zone

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
            row.daily_started_at = datetime.now(UTC)
        self.commit()
        return row

    def update(self, task_id: UUID, changes: dict[str, object]) -> TaskModel:
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
            row.daily_started_at = datetime.now(UTC) if next_type == "daily" else None
            row.status = "pending"
        requested_status = changes.pop("status", None)
        for key, value in changes.items():
            setattr(row, key, value)
        if requested_status == "completed":
            self.complete_row(row)
        elif requested_status is not None:
            row.status = str(requested_status)
        row.updated_at = datetime.now(UTC)
        self.commit()
        return row

    def complete_row(self, row: TaskModel) -> None:
        if row.task_type == "daily":
            raise ConflictError()
        self.repo.complete(row)

    def complete(self, task_id: UUID) -> TaskModel:
        row = self.repo.task(task_id)
        self.complete_row(row)
        self.commit()
        return row

    def reopen(self, task_id: UUID) -> TaskModel:
        row = self.repo.task(task_id)
        if row.task_type == "daily":
            raise ConflictError()
        row.status = "pending"
        self.commit()
        return row

    def delete(self, task_id: UUID) -> None:
        self.repo.task(task_id).deleted_at = datetime.now(UTC)
        self.commit()

    def list(self, query: TaskQuery) -> tuple[Sequence[TaskModel], int]:
        return self.repo.list(query, self.zone, datetime.now(UTC))

    def history(self, task_id: UUID, limit: int, offset: int) -> Sequence[CompletionModel]:
        return self.repo.history(task_id, limit, offset)

    def create_category(self, name: str) -> CategoryModel:
        row = self.repo.add_category(name)
        self.commit()
        return row

    def rename_category(self, category_id: UUID, name: str) -> CategoryModel:
        row = self.repo.category(category_id)
        row.name = name
        row.updated_at = datetime.now(UTC)
        self.commit()
        return row

    def delete_category(self, category_id: UUID) -> None:
        self.repo.delete_category(self.repo.category(category_id))
        self.commit()

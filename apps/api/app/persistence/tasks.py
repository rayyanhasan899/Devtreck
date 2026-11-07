from collections.abc import Sequence
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Date, DateTime, and_, case, cast, func, or_, select
from sqlalchemy.orm import Session

from app.domain.errors import NotFoundError
from app.domain.tasks import TaskQuery
from app.persistence.models import CategoryModel, CompletionModel, TaskModel, TaskTypeChangeModel


class TasksRepository:
    def __init__(self, session: Session, owner: UUID) -> None:
        self.session = session
        self.owner = owner

    def task(self, task_id: UUID) -> TaskModel:
        row = self.session.scalar(
            select(TaskModel)
            .where(
                TaskModel.id == task_id,
                TaskModel.user_id == self.owner,
                TaskModel.deleted_at.is_(None),
            )
            .with_for_update()
        )
        if row is None:
            raise NotFoundError()
        return row

    def category(self, category_id: UUID) -> CategoryModel:
        row = self.session.scalar(
            select(CategoryModel)
            .where(CategoryModel.id == category_id, CategoryModel.user_id == self.owner)
            .with_for_update()
        )
        if row is None:
            raise NotFoundError()
        return row

    def categories(self, limit: int, offset: int) -> Sequence[CategoryModel]:
        return self.session.scalars(
            select(CategoryModel)
            .where(CategoryModel.user_id == self.owner)
            .order_by(CategoryModel.name, CategoryModel.id)
            .limit(limit)
            .offset(offset)
        ).all()

    def add_category(self, name: str) -> CategoryModel:
        row = CategoryModel(user_id=self.owner, name=name)
        self.session.add(row)
        return row

    def delete_category(self, row: CategoryModel) -> None:
        self.session.delete(row)

    def add_task(self, values: dict[str, object]) -> TaskModel:
        row = TaskModel(user_id=self.owner, **values)
        self.session.add(row)
        return row

    def record_type(self, row: TaskModel, next_type: str) -> None:
        self.session.add(
            TaskTypeChangeModel(
                task_id=row.id, user_id=self.owner, previous_type=row.task_type, next_type=next_type
            )
        )

    def complete(self, row: TaskModel) -> None:
        existing = self.session.scalar(
            select(CompletionModel.id).where(
                CompletionModel.task_id == row.id, CompletionModel.user_id == self.owner
            )
        )
        if existing is None:
            self.session.add(CompletionModel(task_id=row.id, user_id=self.owner))
        row.status = "completed"

    def history(self, task_id: UUID, limit: int, offset: int) -> Sequence[CompletionModel]:
        self.task(task_id)
        return self.session.scalars(
            select(CompletionModel)
            .where(CompletionModel.task_id == task_id, CompletionModel.user_id == self.owner)
            .order_by(CompletionModel.completed_at.desc(), CompletionModel.id)
            .limit(limit)
            .offset(offset)
        ).all()

    def list(self, query: TaskQuery, zone: str, now: datetime) -> tuple[Sequence[TaskModel], int]:
        today = now.astimezone(ZoneInfo(zone)).date()
        local_date = func.coalesce(
            TaskModel.due_date, cast(func.timezone(zone, TaskModel.due_at), Date)
        )
        late = and_(
            TaskModel.status != "completed", or_(TaskModel.due_date < today, TaskModel.due_at < now)
        )
        statement = select(TaskModel).where(
            TaskModel.user_id == self.owner, TaskModel.deleted_at.is_(None)
        )
        if query.view == "completed":
            statement = statement.where(TaskModel.status == "completed")
        elif query.view != "all" or query.status != "completed":
            statement = statement.where(TaskModel.status != "completed")
        if query.view == "today":
            statement = statement.where(
                or_(local_date == today, late, TaskModel.task_type == "daily")
            )
        elif query.view == "upcoming":
            statement = statement.where(local_date > today)
        elif query.view == "overdue":
            statement = statement.where(late)
        elif query.view == "daily":
            statement = statement.where(TaskModel.task_type == "daily")
        if query.search:
            pattern = (
                "%"
                + query.search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                + "%"
            )
            statement = statement.where(
                or_(
                    TaskModel.title.ilike(pattern, escape="\\"),
                    TaskModel.description.ilike(pattern, escape="\\"),
                )
            )
        for value, column in [
            (query.status, TaskModel.status),
            (query.task_type, TaskModel.task_type),
            (query.priority, TaskModel.priority),
            (query.category_id, TaskModel.category_id),
        ]:
            if value is not None:
                statement = statement.where(column == value)
        if query.due_date is not None:
            statement = statement.where(local_date == query.due_date)
        if query.overdue is not None:
            statement = statement.where(late if query.overdue else ~func.coalesce(late, False))
        total = self.session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        sorts = {
            "created_at": TaskModel.created_at,
            "updated_at": TaskModel.updated_at,
            "title": func.lower(TaskModel.title),
            "priority": case(
                (TaskModel.priority == "high", 3), (TaskModel.priority == "medium", 2), else_=1
            ),
            "due_date": func.coalesce(
                TaskModel.due_at, func.timezone(zone, cast(TaskModel.due_date + 1, DateTime()))
            ),
        }
        ordering = sorts[query.sort]
        ordering = ordering.desc() if query.descending else ordering.asc()
        rows = self.session.scalars(
            statement.order_by(ordering.nulls_last(), TaskModel.id)
            .limit(query.limit)
            .offset(query.offset)
        ).all()
        return rows, total

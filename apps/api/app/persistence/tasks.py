from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Date, DateTime, and_, case, cast, func, or_, select
from sqlalchemy.orm import Session

from app.domain.errors import NotFoundError
from app.domain.tasks import TaskQuery
from app.persistence.models import (
    CategoryModel,
    ChecklistModel,
    CompletionModel,
    DailyCompletionModel,
    TaskModel,
    TaskTypeChangeModel,
    UserModel,
)


class TasksRepository:
    def __init__(self, session: Session, owner: UUID) -> None:
        self.session = session
        self.owner = owner

    def lock_owner(self) -> UserModel:
        row = self.session.scalar(
            select(UserModel)
            .where(UserModel.id == self.owner)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if row is None:
            raise NotFoundError()
        return row

    def daily_facts(self, ids: Sequence[UUID]) -> Sequence[DailyCompletionModel]:
        return (
            self.session.scalars(
                select(DailyCompletionModel)
                .where(
                    DailyCompletionModel.user_id == self.owner,
                    DailyCompletionModel.task_id.in_(ids),
                )
                .order_by(DailyCompletionModel.completed_at, DailyCompletionModel.id)
            ).all()
            if ids
            else []
        )

    def add_daily(self, row: TaskModel, day: date, instant: datetime, zone: str) -> None:
        from sqlalchemy.dialects.postgresql import insert

        self.session.execute(
            insert(DailyCompletionModel)
            .values(
                task_id=row.id,
                user_id=self.owner,
                epoch=row.daily_epoch,
                completion_day=day,
                completed_at=instant,
                time_zone=zone,
            )
            .on_conflict_do_nothing(constraint="uq_daily_task_day")
        )

    def daily_history(
        self, task_id: UUID, limit: int, offset: int
    ) -> Sequence[DailyCompletionModel]:
        self.task(task_id)
        return self.session.scalars(
            select(DailyCompletionModel)
            .where(
                DailyCompletionModel.user_id == self.owner, DailyCompletionModel.task_id == task_id
            )
            .order_by(DailyCompletionModel.completed_at.desc(), DailyCompletionModel.id)
            .limit(limit)
            .offset(offset)
        ).all()

    def task(self, task_id: UUID) -> TaskModel:
        row = self.session.scalar(
            select(TaskModel)
            .where(
                TaskModel.id == task_id,
                TaskModel.user_id == self.owner,
                TaskModel.deleted_at.is_(None),
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if row is None:
            raise NotFoundError()
        return row

    def category(self, category_id: UUID) -> CategoryModel:
        row = self.session.scalar(
            select(CategoryModel)
            .where(CategoryModel.id == category_id, CategoryModel.user_id == self.owner)
            .with_for_update()
            .execution_options(populate_existing=True)
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
        daily_done = (
            select(DailyCompletionModel.id)
            .where(
                DailyCompletionModel.task_id == TaskModel.id,
                DailyCompletionModel.user_id == self.owner,
                DailyCompletionModel.completion_day == today,
            )
            .exists()
        )
        is_daily = TaskModel.task_type == "daily"
        finished = or_(and_(~is_daily, TaskModel.status == "completed"), and_(is_daily, daily_done))
        late = and_(~finished, or_(TaskModel.due_date < today, TaskModel.due_at < now))
        statement = select(TaskModel).where(
            TaskModel.user_id == self.owner, TaskModel.deleted_at.is_(None)
        )
        if query.view == "completed" or query.status == "completed":
            statement = statement.where(finished)
        elif query.view != "daily":
            # Daily habits stay visible in All, but Today is actionable work only.
            statement = statement.where(
                or_(is_daily, ~finished) if query.view == "all" else ~finished
            )
        if query.view == "today":
            statement = statement.where(or_(local_date == today, late, is_daily))
        elif query.view == "upcoming":
            statement = statement.where(local_date > today)
        elif query.view == "overdue":
            statement = statement.where(late)
        elif query.view == "daily":
            statement = statement.where(is_daily)
        if query.view in ("upcoming", "today", "overdue") and query.status == "completed":
            statement = statement.where(~finished)
        if query.status in ("pending", "in-progress"):
            statement = statement.where(~finished)
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
            (query.status if query.status != "completed" else None, TaskModel.status),
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

    def dashboard(self, zone: str, now: datetime) -> dict[str, int]:
        today = now.astimezone(ZoneInfo(zone)).date()
        start = datetime.combine(today, time.min, ZoneInfo(zone)).astimezone(UTC)
        end = datetime.combine(today + timedelta(days=1), time.min, ZoneInfo(zone)).astimezone(UTC)
        _, actionable = self.list(TaskQuery(view="today", limit=1), zone, now)
        _, pending = self.list(TaskQuery(status="pending", limit=1), zone, now)
        _, progressing = self.list(TaskQuery(status="in-progress", limit=1), zone, now)
        common = (TaskModel.user_id == self.owner, TaskModel.deleted_at.is_(None))
        one_time = (
            self.session.scalar(
                select(func.count())
                .select_from(CompletionModel)
                .join(TaskModel, CompletionModel.task_id == TaskModel.id)
                .where(
                    *common,
                    CompletionModel.completed_at >= start,
                    CompletionModel.completed_at < end,
                )
            )
            or 0
        )
        daily = (
            self.session.scalar(
                select(func.count())
                .select_from(DailyCompletionModel)
                .join(TaskModel, DailyCompletionModel.task_id == TaskModel.id)
                .where(*common, DailyCompletionModel.completion_day == today)
            )
            or 0
        )
        habits = (
            self.session.scalar(
                select(func.count())
                .select_from(TaskModel)
                .where(*common, TaskModel.task_type == "daily")
            )
            or 0
        )
        habits_done = (
            self.session.scalar(
                select(func.count())
                .select_from(DailyCompletionModel)
                .join(TaskModel, DailyCompletionModel.task_id == TaskModel.id)
                .where(
                    *common,
                    TaskModel.task_type == "daily",
                    DailyCompletionModel.completion_day == today,
                )
            )
            or 0
        )
        return {
            "today_actionable": actionable,
            "outstanding": pending + progressing,
            "completions_today": one_time + daily,
            "daily_total": habits,
            "daily_done": habits_done,
        }

    def checklist_progress(self, ids: Sequence[UUID]) -> dict[UUID, tuple[int, int]]:
        rows = self.session.execute(
            select(
                ChecklistModel.task_id,
                func.count(),
                func.count().filter(ChecklistModel.completed.is_(True)),
            )
            .where(ChecklistModel.user_id == self.owner, ChecklistModel.task_id.in_(ids))
            .group_by(ChecklistModel.task_id)
        ).all()
        return {row[0]: (row[1], row[2]) for row in rows}

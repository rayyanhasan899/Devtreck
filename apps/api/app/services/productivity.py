import hashlib
import json
from collections.abc import Sequence
from datetime import UTC, datetime, time, timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errors import ConflictError, NotFoundError
from app.domain.productivity import active_seconds, interval_overlap
from app.domain.streaks import Clock, local_day, utc_now
from app.domain.tasks import TaskQuery
from app.persistence.models import (
    ChecklistModel,
    DailyPlanModel,
    FocusEventModel,
    FocusIntervalModel,
    FocusSessionModel,
    TaskModel,
)
from app.persistence.productivity import ProductivityRepository
from app.persistence.tasks import TasksRepository
from app.persistence.unit_of_work import SqlUnitOfWork


class ProductivityService:
    def __init__(self, db: Session, owner: UUID, zone: str, clock: Clock = utc_now) -> None:
        self.repo = ProductivityRepository(db, owner)
        self.tasks = TasksRepository(db, owner)
        self.uow = SqlUnitOfWork(db)
        self.zone, self.clock = zone, clock

    def lock(self) -> None:
        self.zone = self.tasks.lock_owner().time_zone

    def commit(self) -> None:
        try:
            self.uow.commit()
        except IntegrityError:
            raise ConflictError() from None

    def checklist(self, task_id: UUID) -> Sequence[ChecklistModel]:
        self.tasks.task(task_id)
        return self.repo.checklist(task_id)

    def add_item(self, task_id: UUID, title: str) -> ChecklistModel:
        self.lock()
        self.tasks.task(task_id)
        rows = self.repo.checklist(task_id)
        if len(rows) >= 100:
            raise ConflictError()
        row = ChecklistModel(
            task_id=task_id, user_id=self.repo.owner, title=title, position=len(rows)
        )
        self.repo.add(row)
        self.commit()
        return row

    def item(self, task_id: UUID, item_id: UUID) -> ChecklistModel:
        rows = self.checklist(task_id)
        for row in rows:
            if row.id == item_id:
                return row
        raise NotFoundError()

    def edit_item(
        self, task_id: UUID, item_id: UUID, title: str | None, completed: bool | None
    ) -> ChecklistModel:
        self.lock()
        row = self.item(task_id, item_id)
        if title is not None:
            row.title = title
        if completed is not None:
            row.completed = completed
        self.commit()
        return row

    def delete_item(self, task_id: UUID, item_id: UUID) -> None:
        self.lock()
        row = self.item(task_id, item_id)
        self.repo.remove(row)
        self.repo.db.flush()
        for index, item in enumerate(self.repo.checklist(task_id)):
            item.position = index
        self.commit()

    def reorder(self, task_id: UUID, ids: list[UUID]) -> Sequence[ChecklistModel]:
        self.lock()
        rows = self.checklist(task_id)
        if len(ids) != len(set(ids)) or set(ids) != {row.id for row in rows}:
            raise ConflictError()
        positions = {item: index for index, item in enumerate(ids)}
        for row in rows:
            row.position = positions[row.id]
        self.commit()
        return self.repo.checklist(task_id)

    def plan(self) -> tuple[Sequence[TaskModel], dict[str, object]]:
        now = self.clock()
        day = local_day(now, self.zone)
        rows, total = self.tasks.list(
            TaskQuery(view="today", limit=500, sort="due_date", descending=False), self.zone, now
        )

        def rank(row: TaskModel) -> tuple[object, ...]:
            late = (row.due_date is not None and row.due_date < day) or (
                row.due_at is not None and row.due_at < now
            )
            return (
                not late,
                row.due_date
                or (row.due_at.astimezone(ZoneInfo(self.zone)).date() if row.due_at else day),
                {"high": 0, "medium": 1, "low": 2}[row.priority],
                row.estimated_minutes if row.estimated_minutes is not None else 10081,
                str(row.id),
            )

        suggested = sorted(rows, key=rank)
        saved = self.repo.plan(day)
        order = saved.order_ids if saved else []
        priorities = saved.priority_ids if saved else []
        positions = {key: index for index, key in enumerate(order)}
        arranged = sorted(
            suggested,
            key=lambda row: (
                (0, positions[str(row.id)])
                if str(row.id) in positions
                else (1, suggested.index(row))
            ),
        )
        reasons = {
            str(row.id): [
                reason
                for reason, condition in [
                    (
                        "Overdue",
                        (row.due_date is not None and row.due_date < day)
                        or (row.due_at is not None and row.due_at < now),
                    ),
                    (
                        "Due today",
                        row.due_date == day
                        or (row.due_at is not None and local_day(row.due_at, self.zone) == day),
                    ),
                    ("Daily habit", row.task_type == "daily"),
                    ("High priority", row.priority == "high"),
                    ("Duration estimate available", row.estimated_minutes is not None),
                ]
                if condition
            ]
            for row in rows
        }
        ids = {str(row.id) for row in rows}
        return arranged, {
            "day": day,
            "time_zone": self.zone,
            "total": total,
            "truncated": total > len(rows),
            "priority_ids": [key for key in priorities if key in ids],
            "suggested_ids": [str(row.id) for row in suggested],
            "estimated_minutes": sum(row.estimated_minutes or 0 for row in rows),
            "missing_estimates": sum(row.estimated_minutes is None for row in rows),
            "reasons": reasons,
        }

    def save_plan(self, order: list[UUID], priorities: list[UUID]) -> None:
        self.lock()
        rows, _meta = self.plan()
        allowed = {row.id for row in rows}
        if (
            len(order) != len(set(order))
            or len(priorities) != len(set(priorities))
            or not set(order) <= allowed
            or not set(priorities) <= allowed
            or len(priorities) > 3
        ):
            raise ConflictError()
        day = _meta["day"]
        row = self.repo.plan(day)
        if row is None:
            row = DailyPlanModel(user_id=self.repo.owner, day=day)
            self.repo.add(row)
        row.order_ids = [str(key) for key in order]
        row.priority_ids = [str(key) for key in priorities]
        self.commit()

    def settle(self, row: FocusSessionModel, now: datetime, close: bool = False) -> None:
        if row.status != "active" or row.active_since is None:
            return
        elapsed = active_seconds(row.elapsed_seconds, row.active_since, now, row.target_seconds)
        if close or elapsed >= row.target_seconds:
            end = row.active_since + timedelta(seconds=elapsed - row.elapsed_seconds)
            self.repo.add(
                FocusIntervalModel(
                    session_id=row.id,
                    user_id=self.repo.owner,
                    started_at=row.active_since,
                    ended_at=end,
                )
            )
            row.elapsed_seconds = elapsed
            row.active_since = None
            if elapsed >= row.target_seconds:
                row.status = "completed"
                row.ended_at = end

    def current(self) -> FocusSessionModel | None:
        self.lock()
        row = self.repo.current()
        if row:
            self.settle(row, self.clock())
            self.commit()
        return row if row and row.status in ("active", "paused") else None

    def command(
        self,
        key: UUID,
        action: str,
        session_id: UUID | None = None,
        task_id: UUID | None = None,
        kind: str = "focus",
        seconds: int = 1500,
    ) -> FocusSessionModel:
        self.lock()
        now = self.clock()
        fingerprint = hashlib.sha256(
            json.dumps([action, str(session_id), str(task_id), kind, seconds]).encode()
        ).hexdigest()
        event = self.repo.event(key)
        if event:
            if event.fingerprint != fingerprint:
                raise ConflictError()
            row = self.repo.focus(event.session_id)
            self.settle(row, now)
            self.commit()
            return row
        if action == "start":
            running = self.repo.current()
            if running:
                self.settle(running, now)
                if running.status in ("active", "paused"):
                    raise ConflictError()
                self.repo.db.flush()
            if task_id:
                self.tasks.task(task_id)
            row = FocusSessionModel(
                id=uuid4(),
                user_id=self.repo.owner,
                task_id=task_id,
                kind=kind,
                status="active",
                target_seconds=seconds,
                elapsed_seconds=0,
                active_since=now,
                started_at=now,
            )
            self.repo.add(row)
        else:
            if session_id is None:
                raise NotFoundError()
            row = self.repo.focus(session_id)
            self.settle(row, now)
            if row.status in ("active", "paused"):
                if action == "pause" and row.status == "active":
                    self.settle(row, now, True)
                    if row.status != "completed":
                        row.status = "paused"
                elif action == "resume" and row.status == "paused":
                    row.status = "active"
                    row.active_since = now
                elif action == "stop":
                    self.settle(row, now, True)
                    if row.status != "completed":
                        row.status = "stopped"
                        row.ended_at = now
        self.repo.db.flush()
        self.repo.add(
            FocusEventModel(
                session_id=row.id,
                user_id=self.repo.owner,
                command_key=key,
                action=action,
                fingerprint=fingerprint,
                occurred_at=now,
            )
        )
        self.commit()
        return row

    def history(self, limit: int, offset: int) -> Sequence[FocusSessionModel]:
        self.current()
        return self.repo.history(limit, offset)

    def totals(self) -> dict[str, object]:
        self.current()
        now = self.clock()
        day = local_day(now, self.zone)
        start = datetime.combine(day, time.min, ZoneInfo(self.zone)).astimezone(UTC)
        week = datetime.combine(day - timedelta(days=6), time.min, ZoneInfo(self.zone)).astimezone(
            UTC
        )
        intervals = [(row.started_at, row.ended_at) for row in self.repo.intervals(week)]
        current = self.repo.current()
        if (
            current
            and current.kind == "focus"
            and current.status == "active"
            and current.active_since
        ):
            elapsed = active_seconds(
                current.elapsed_seconds, current.active_since, now, current.target_seconds
            )
            intervals.append(
                (
                    current.active_since,
                    current.active_since + timedelta(seconds=elapsed - current.elapsed_seconds),
                )
            )
        return {
            "day_seconds": int(sum(interval_overlap(a, b, start, now) for a, b in intervals)),
            "week_seconds": int(sum(interval_overlap(a, b, week, now) for a, b in intervals)),
            "day": day,
            "week_start": local_day(week, self.zone),
            "time_zone": self.zone,
        }

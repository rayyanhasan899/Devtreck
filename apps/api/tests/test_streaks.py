from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_accounts import clients, login, signup  # noqa: F401
from test_persistence import database  # noqa: F401

from app.domain.streaks import DailyFact, calculate, local_day
from app.persistence.models import DailyCompletionModel, TaskModel
from app.presentation.tasks import get_clock
from app.services.tasks import TasksService


def test_pure_streak_lifecycle_and_epochs():
    epoch = uuid4()
    today = date(2026, 11, 7)
    assert calculate([], epoch, today, "UTC").current_streak == 0
    facts = [DailyFact(epoch, today - timedelta(days=1))]
    assert calculate(facts, epoch, today, "UTC").current_streak == 1
    facts.append(DailyFact(epoch, today))
    facts.append(DailyFact(epoch, today))
    result = calculate(facts, epoch, today, "UTC")
    assert (result.current_streak, result.best_streak, result.total_completions) == (2, 2, 2)
    result = calculate(facts, epoch, today + timedelta(days=2), "UTC")
    assert result.current_streak == 0 and result.best_streak == 2
    assert calculate(facts, uuid4(), today, "UTC").current_streak == 0
    assert calculate(facts, uuid4(), today, "UTC").best_streak == 2


@pytest.mark.parametrize(
    "instant,zone,day",
    [
        ("2026-11-07T18:59:59+00:00", "Asia/Karachi", "2026-11-07"),
        ("2026-11-07T19:00:00+00:00", "Asia/Karachi", "2026-11-08"),
        ("2026-03-08T06:59:59+00:00", "America/New_York", "2026-03-08"),
        ("2026-03-08T07:00:00+00:00", "America/New_York", "2026-03-08"),
        ("2026-11-01T05:30:00+00:00", "America/New_York", "2026-11-01"),
        ("2026-11-01T06:30:00+00:00", "America/New_York", "2026-11-01"),
        ("2026-11-07T12:00:00+00:00", "Pacific/Kiritimati", "2026-11-08"),
    ],
)
def test_day_midnight_and_dst(instant, zone, day):
    assert local_day(datetime.fromisoformat(instant), zone) == date.fromisoformat(day)


def test_reject_naive_clock():
    with pytest.raises(ValueError):
        local_day(datetime(2026, 11, 7), "UTC")


def setup_daily(client):
    headers = login(client, signup(client)["email"])
    response = client.post(
        "/api/tasks", json={"title": "Practice", "task_type": "daily"}, headers=headers
    )
    assert response.status_code == 201, response.text
    return headers, response.json()


def test_api_consecutive_missed_reopen_reconcile_and_views(clients):  # noqa: F811
    first, second, engine = clients
    instant = [datetime(2026, 11, 7, 12, tzinfo=UTC)]
    first.app.dependency_overrides[get_clock] = lambda: lambda: instant[0]
    headers, task = setup_daily(first)
    path = "/api/tasks/" + task["id"]
    assert task["streak"]["current_streak"] == task["streak"]["best_streak"] == 0
    response = first.post(path + "/complete", headers=headers)
    assert response.json()["streak"]["current_streak"] == 1
    assert first.post(path + "/complete", headers=headers).json()["streak"]["current_streak"] == 1
    assert first.post(path + "/reopen", headers=headers).json()["streak"]["today_completed"]
    assert first.get("/api/tasks?view=today").json()["total"] == 0
    assert first.get("/api/tasks?view=daily").json()["total"] == 1
    assert first.get("/api/tasks?view=completed").json()["total"] == 1
    assert first.get("/api/tasks").json()["items"][0]["streak"]["today_completed"]
    original = first.get(path + "/daily-history").json()
    assert original[0]["completed_at"].startswith("2026-11-07T12:00:00")
    instant[0] += timedelta(days=1)
    assert first.get(path).json()["streak"]["current_streak"] == 1
    assert first.get("/api/tasks?view=today").json()["total"] == 1
    assert (
        first.patch(path, json={"status": "completed"}, headers=headers).json()["streak"][
            "current_streak"
        ]
        == 2
    )
    instant[0] += timedelta(days=2)
    assert first.get(path).json()["streak"]["current_streak"] == 0
    assert first.post(path + "/complete", headers=headers).json()["streak"]["current_streak"] == 1
    with Session(engine) as db:
        row = db.get(TaskModel, task["id"])
        row.current_streak = 99
        row.best_streak = 99
        db.commit()
    summary = first.post(path + "/streak/reconcile", headers=headers).json()
    assert (summary["current_streak"], summary["best_streak"]) == (1, 2)
    assert len(first.get(path + "/daily-history?limit=1").json()) == 1
    assert first.get(path + "/daily-history?limit=101").status_code == 422
    other_headers = login(second, signup(second)["email"])
    for suffix in ("/streak", "/daily-history"):
        assert second.get(path + suffix).status_code == 404
    assert second.post(path + "/streak/reconcile", headers=other_headers).status_code == 404
    assert first.patch(path, json={"current_streak": 999}, headers=headers).status_code == 422
    assert first.get(path + "/daily-history").json()[-1] == original[0]
    first.app.dependency_overrides.clear()


def test_timezone_edits_epochs_and_history(clients):  # noqa: F811
    first, _, _ = clients
    instant = [datetime(2026, 11, 7, 19, tzinfo=UTC)]
    first.app.dependency_overrides[get_clock] = lambda: lambda: instant[0]
    headers, task = setup_daily(first)
    path = "/api/tasks/" + task["id"]
    first.patch("/api/users/me", json={"time_zone": "Asia/Karachi"}, headers=headers)
    first.post(path + "/complete", headers=headers)
    history = first.get(path + "/daily-history").json()
    assert history[0]["completion_day"] == "2026-11-08"
    assert history[0]["time_zone"] == "Asia/Karachi"
    first.patch("/api/users/me", json={"time_zone": "America/New_York"}, headers=headers)
    assert first.get(path + "/streak").json()["current_day"] == "2026-11-07"
    assert first.get(path + "/daily-history").json() == history
    # Returning east to the same credited local day must not create another fact.
    first.patch("/api/users/me", json={"time_zone": "Asia/Karachi"}, headers=headers)
    first.post(path + "/complete", headers=headers)
    assert len(first.get(path + "/daily-history").json()) == 1
    first.patch(path, json={"task_type": "one-time"}, headers=headers)
    assert first.get(path).json()["streak"] is None
    assert first.get(path + "/streak").status_code == 409
    first.patch(path, json={"task_type": "daily"}, headers=headers)
    assert first.get(path).json()["streak"]["current_streak"] == 0
    first.post(path + "/complete", headers=headers)
    assert len(first.get(path + "/daily-history").json()) == 1
    instant[0] += timedelta(days=1)
    assert first.post(path + "/complete", headers=headers).json()["streak"]["current_streak"] == 1
    assert len(first.get(path + "/daily-history").json()) == 2
    first.app.dependency_overrides.clear()


def test_concurrent_daily_requests_and_db_uniqueness(clients):  # noqa: F811
    from concurrent.futures import ThreadPoolExecutor

    from sqlalchemy.exc import IntegrityError

    first, _, engine = clients
    _headers, task = setup_daily(first)
    instant = datetime(2026, 11, 7, 12, tzinfo=UTC)
    with Session(engine) as db:
        owner = db.get(TaskModel, task["id"]).user_id

    def finish(_):
        with Session(engine) as db:
            return (
                TasksService(db, owner, "UTC", lambda: instant)
                .complete(UUID(task["id"]))
                .current_streak
            )

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(finish, range(2))) == [1, 1]
    with Session(engine) as db:
        rows = db.scalars(
            select(DailyCompletionModel).where(DailyCompletionModel.task_id == UUID(task["id"]))
        ).all()
        assert len(rows) == 1
        row = rows[0]
        db.add(
            DailyCompletionModel(
                task_id=row.task_id,
                user_id=row.user_id,
                epoch=row.epoch,
                completion_day=row.completion_day,
                completed_at=instant,
                time_zone="UTC",
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_timezone_edit_serializes_before_completion(clients):  # noqa: F811
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    from app.persistence.accounts import AccountsRepository

    first, _, engine = clients
    _headers, task = setup_daily(first)
    instant = datetime(2026, 11, 7, 19, tzinfo=UTC)
    with Session(engine) as db:
        owner = db.get(TaskModel, task["id"]).user_id
    entered = Event()

    def finish():
        with Session(engine) as db:
            entered.set()
            TasksService(db, owner, "UTC", lambda: instant).complete(UUID(task["id"]))

    with ThreadPoolExecutor(max_workers=1) as pool, Session(engine) as editing:
        user = AccountsRepository(editing).lock(owner)
        user.time_zone = "Asia/Karachi"
        future = pool.submit(finish)
        assert entered.wait(5)
        assert not future.done()
        editing.commit()
        future.result(timeout=10)
    with Session(engine) as db:
        record = db.scalar(
            select(DailyCompletionModel).where(DailyCompletionModel.task_id == UUID(task["id"]))
        )
        assert record.time_zone == "Asia/Karachi"
        assert record.completion_day == date(2026, 11, 8)


@pytest.mark.parametrize(
    "instant,expected",
    [
        ("2026-03-08T04:59:59+00:00", "2026-03-07"),
        ("2026-03-08T05:00:00+00:00", "2026-03-08"),
        ("2026-03-09T03:59:59+00:00", "2026-03-08"),
        ("2026-03-09T04:00:00+00:00", "2026-03-09"),
        ("2026-11-02T04:59:59+00:00", "2026-11-01"),
        ("2026-11-02T05:00:00+00:00", "2026-11-02"),
    ],
)
def test_short_and_long_dst_days(instant, expected):
    assert local_day(datetime.fromisoformat(instant), "America/New_York") == date.fromisoformat(
        expected
    )


def test_deletion_cascades_daily_history(clients):  # noqa: F811
    first, _, engine = clients
    headers, task = setup_daily(first)
    path = "/api/tasks/" + task["id"]
    first.post(path + "/complete", headers=headers)
    assert first.delete(path + "?confirm=true", headers=headers).status_code == 204
    assert first.get(path + "/daily-history").status_code == 404
    with Session(engine) as db:
        assert db.scalar(
            select(DailyCompletionModel).where(DailyCompletionModel.task_id == UUID(task["id"]))
        )
    assert (
        first.request(
            "DELETE",
            "/api/users/me",
            json={"current_password": "correct horse battery staple", "confirm": True},
            headers=headers,
        ).status_code
        == 204
    )
    with Session(engine) as db:
        assert (
            db.scalar(
                select(DailyCompletionModel).where(DailyCompletionModel.task_id == UUID(task["id"]))
            )
            is None
        )


def test_upgrade_backfills_existing_daily_without_credit(database):  # noqa: F811
    from alembic import command
    from sqlalchemy import text

    engine, config, _ = database
    # Only this fixture's generated disposable database is downgraded.
    command.downgrade(config, "eb92ac3655cd")
    owner, task = uuid4(), uuid4()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (id,email,name,password_hash) VALUES (:id,:email,'Migration test','synthetic-hash')"
            ),
            {"id": owner, "email": str(owner) + "@example.com"},
        )
        connection.execute(
            text(
                "INSERT INTO tasks (id,user_id,title,status,task_type,priority) VALUES (:id,:owner,'Existing daily','pending','daily','medium')"
            ),
            {"id": task, "owner": owner},
        )
    command.upgrade(config, "head")
    command.check(config)
    with Session(engine) as db:
        row = db.get(TaskModel, task)
        assert row.daily_epoch is not None
        assert (row.current_streak, row.best_streak) == (0, 0)
        assert not db.scalars(
            select(DailyCompletionModel).where(DailyCompletionModel.task_id == task)
        ).all()

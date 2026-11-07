from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from test_accounts import clients, login, signup  # noqa: F401
from test_persistence import database  # noqa: F401
from test_productivity import task

from app.domain.rewards import RewardRules
from app.persistence.models import (
    AchievementModel,
    CompletionModel,
    DailyCompletionModel,
    FocusIntervalModel,
    FocusSessionModel,
    InsightDayModel,
    OccurrenceModel,
    TaskModel,
    UserModel,
    XPLedgerModel,
)
from app.persistence.progress import ProgressRepository
from app.presentation.tasks import get_clock
from app.services.productivity import ProductivityService
from app.services.progress import ProgressService
from app.services.tasks import TasksService


def enter(client):
    account = signup(client)
    return login(client, account["email"]), UUID(account["id"])


def test_reward_retries_toggle_concurrency_and_owner_scope(clients):  # noqa: F811
    a, b, engine = clients
    ah, owner = enter(a)
    enter(b)
    parent = task(a, ah)
    tid = UUID(parent["id"])

    def complete(_):
        with Session(engine) as db:
            TasksService(db, owner, "UTC").complete(tid)

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(complete, range(2)))
    assert a.post(f"/api/tasks/{tid}/reopen", headers=ah).status_code == 200
    assert a.post(f"/api/tasks/{tid}/complete", headers=ah).status_code == 200
    for _ in range(2):
        report = a.get("/api/progress").json()
        assert (report["xp"], report["level"], report["level_progress"]) == (10, 1, 10)
    assert b.get("/api/progress").json()["xp"] == 0
    assert a.post("/api/progress", json={"xp": 9000}, headers=ah).status_code == 405
    with Session(engine) as db:
        assert (
            len(db.scalars(select(XPLedgerModel).where(XPLedgerModel.user_id == owner)).all()) == 1
        )
        assert (
            len(db.scalars(select(AchievementModel).where(AchievementModel.user_id == owner)).all())
            == 1
        )


def test_completion_and_reward_rollback_together(clients, monkeypatch):  # noqa: F811
    a, _, engine = clients
    ah, owner = enter(a)
    tid = UUID(task(a, ah)["id"])

    def fail(*args, **kwargs):
        raise RuntimeError("simulated reward storage failure")

    monkeypatch.setattr(ProgressRepository, "award", fail)
    with Session(engine) as db:
        with pytest.raises(RuntimeError):
            TasksService(db, owner, "UTC").complete(tid)
        db.rollback()
    with Session(engine) as db:
        assert db.get(TaskModel, tid).status == "pending"
        assert db.scalar(select(CompletionModel).where(CompletionModel.task_id == tid)) is None
        assert db.scalar(select(XPLedgerModel).where(XPLedgerModel.user_id == owner)) is None


def test_focus_minimum_cap_break_stop_retry_and_next_local_day(clients):  # noqa: F811
    a, _, engine = clients
    _, owner = enter(a)
    now = datetime(2026, 11, 7, 12, tzinfo=UTC)
    with Session(engine) as db:
        svc = ProductivityService(db, owner, "UTC", lambda: now)
        # Five completed 25-minute sessions: only first four earn rewards.
        for _ in range(5):
            key = uuid4()
            row = svc.command(key, "start")
            now += timedelta(seconds=1500)
            svc.current()
            svc.command(key, "start")
            assert row.status == "completed"
        # Short completion, break, and long stopped work are not focus XP sources.
        for kind, seconds, stop in [
            ("focus", 60, False),
            ("break", 1500, False),
            ("focus", 1800, True),
        ]:
            row = svc.command(uuid4(), "start", kind=kind, seconds=seconds)
            now += timedelta(seconds=1501 if stop else seconds)
            if stop:
                svc.command(uuid4(), "stop", session_id=row.id)
            else:
                svc.current()
        assert sum(r.amount for r in ProgressRepository(db, owner).ledger()) == 20
        assert (
            len(
                [r for r in ProgressRepository(db, owner).ledger() if r.source_kind == "focus_skip"]
            )
            == 1
        )
        now += timedelta(days=1)
        svc.command(uuid4(), "start")
        now += timedelta(seconds=1500)
        svc.current()
        assert sum(r.amount for r in ProgressRepository(db, owner).ledger()) == 25


def test_historical_backfill_all_badges_and_deletion_retention(clients):  # noqa: F811
    a, _, engine = clients
    ah, owner = enter(a)
    now = datetime(2026, 11, 7, 12, tzinfo=UTC)
    with Session(engine) as db:
        # Explicit pre-phase history: 25 tasks, 7 habit dates, 300 focus minutes.
        rows = [
            TaskModel(user_id=owner, title=f"Earlier {i}", task_type="one-time", status="completed")
            for i in range(25)
        ]
        habit = TaskModel(
            user_id=owner,
            title="Habit",
            task_type="daily",
            daily_epoch=uuid4(),
            daily_started_at=now - timedelta(days=6),
        )
        db.add_all([*rows, habit])
        db.flush()
        habit_id = habit.id
        db.add_all(
            [
                CompletionModel(task_id=r.id, user_id=owner, completed_at=now - timedelta(days=1))
                for r in rows
            ]
        )
        db.add_all(
            [
                DailyCompletionModel(
                    task_id=habit.id,
                    user_id=owner,
                    epoch=habit.daily_epoch,
                    completion_day=(now - timedelta(days=i)).date(),
                    time_zone="UTC",
                    completed_at=now - timedelta(days=i),
                )
                for i in range(7)
            ]
        )
        focus = FocusSessionModel(
            user_id=owner,
            kind="focus",
            status="stopped",
            target_seconds=10800,
            elapsed_seconds=10800,
            started_at=now - timedelta(hours=5),
            ended_at=now - timedelta(hours=2),
        )
        other = FocusSessionModel(
            user_id=owner,
            kind="focus",
            status="stopped",
            target_seconds=7200,
            elapsed_seconds=7200,
            started_at=now - timedelta(hours=2),
            ended_at=now,
        )
        db.add_all([focus, other])
        db.flush()
        db.add_all(
            [
                FocusIntervalModel(
                    user_id=owner, session_id=f.id, started_at=f.started_at, ended_at=f.ended_at
                )
                for f in [focus, other]
            ]
        )
        db.commit()
    a.app.dependency_overrides[get_clock] = lambda: lambda: now
    first = a.get("/api/progress").json()
    second = a.get("/api/progress").json()
    assert first == second
    assert (first["xp"], first["level"], first["next_level_xp"]) == (285, 3, 300)
    assert all(b["earned_at"] for b in first["badges"])
    assert first["best_streak"] == 7
    assert first["week"]["completion_rate"] is None  # no invented earlier denominator
    assert a.delete(f"/api/tasks/{habit_id}?confirm=true", headers=ah).status_code == 204
    after = a.get("/api/progress").json()
    assert after["xp"] == 285 and after["daily_completions"] == 0
    assert after["week"]["completed"] == 25
    assert (
        a.request(
            "DELETE",
            "/api/users/me",
            json={"current_password": "correct horse battery staple", "confirm": True},
            headers=ah,
        ).status_code
        == 204
    )
    with Session(engine) as db:
        for model in [XPLedgerModel, AchievementModel, OccurrenceModel, InsightDayModel]:
            assert db.scalar(select(model).where(model.user_id == owner)) is None
    a.app.dependency_overrides.clear()


def test_explicit_analytics_fixture_timezone_zero_and_stable_denominator(clients):  # noqa: F811
    a, _, engine = clients
    ah, owner = enter(a)
    now = datetime(2026, 11, 7, 20, tzinfo=UTC)  # Nov 8 in Karachi
    a.app.dependency_overrides[get_clock] = lambda: lambda: now
    with Session(engine) as db:
        db.get(UserModel, owner).time_zone = "Asia/Karachi"
        db.commit()
    empty = a.get("/api/progress").json()
    assert empty["today"]["start"] == "2026-11-08"
    assert empty["today"]["completion_rate"] is None
    habit = task(a, ah, "Daily", task_type="daily")
    due = task(a, ah, "Due", due_date="2026-11-08")
    task(a, ah, "No deadline")
    assert a.post(f"/api/tasks/{habit['id']}/complete", headers=ah).status_code == 200
    # Two eligible occurrences, one complete: 50%; checklist cannot affect it.
    a.post(f"/api/tasks/{due['id']}/checklist", json={"title": "Child"}, headers=ah)
    report = a.get("/api/progress").json()
    assert report["today"]["eligible"] == 2
    assert report["today"]["eligible_completed"] == 1
    assert report["today"]["completion_rate"] == 0.5
    assert report["week"]["completed"] == 1
    assert report["categories"] == [{"name": "Uncategorized", "completed": 1}]
    assert report["trends"][-1]["completed"] == 1
    # Rescheduling cannot remove an already-eligible denominator.
    assert (
        a.patch(f"/api/tasks/{due['id']}", json={"due_date": "2026-12-01"}, headers=ah).status_code
        == 200
    )
    assert a.get("/api/progress").json()["today"]["eligible"] == 2
    # A known seven-date fixture gives 1 / (7 daily + 1 due) = 12.5%.
    with Session(engine) as db:
        db.get(TaskModel, UUID(habit["id"])).daily_started_at = now - timedelta(days=6)
        db.execute(delete(InsightDayModel).where(InsightDayModel.user_id == owner))
        db.add(
            InsightDayModel(
                user_id=owner, day=now.date() - timedelta(days=5), time_zone="Asia/Karachi"
            )
        )
        db.commit()
    week = a.get("/api/progress").json()["week"]
    assert (
        week["covered_days"],
        week["eligible"],
        week["eligible_completed"],
        week["completion_rate"],
    ) == (7, 8, 1, 0.125)
    # Zone changes never pretend previous-zone coverage is complete.
    with Session(engine) as db:
        db.get(UserModel, owner).time_zone = "America/Los_Angeles"
        db.commit()
    assert a.get("/api/progress").json()["week"]["completion_rate"] is None
    a.app.dependency_overrides.clear()


def test_progress_requires_authentication(clients):  # noqa: F811
    a, _, _ = clients
    assert a.get("/api/progress").status_code == 401


def test_daily_reward_concurrency_config_and_idle_schedule_snapshots(clients):  # noqa: F811
    a, _, engine = clients
    ah, owner = enter(a)
    now = datetime(2026, 11, 1, 12, tzinfo=UTC)
    a.app.dependency_overrides[get_clock] = lambda: lambda: now
    tid = UUID(task(a, ah, task_type="daily")["id"])

    def complete(_):
        with Session(engine) as db:
            TasksService(db, owner, "UTC", lambda: now, RewardRules(daily_xp=7)).complete(tid)

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(complete, range(2)))
    assert a.get("/api/progress").json()["xp"] == 7
    now += timedelta(days=3)
    # Converting after idle dates freezes four active daily occurrences.
    assert (
        a.patch(f"/api/tasks/{tid}", json={"task_type": "one-time"}, headers=ah).status_code == 200
    )
    now += timedelta(days=2)
    assert a.get("/api/progress").json()["week"]["eligible"] == 4
    with Session(engine) as db:
        ledger = ProgressRepository(db, owner).ledger()
        assert len(ledger) == 1 and ledger[0].amount == 7 and "v1:10/7/5" in ledger[0].policy
    a.app.dependency_overrides.clear()


def test_focus_insights_local_midnight_and_deleted_association(clients):  # noqa: F811
    a, _, engine = clients
    ah, owner = enter(a)
    now = datetime(2026, 11, 2, 6, tzinfo=UTC)  # EST after fall-back
    a.app.dependency_overrides[get_clock] = lambda: lambda: now
    tid = UUID(task(a, ah)["id"])
    with Session(engine) as db:
        db.get(UserModel, owner).time_zone = "America/New_York"
        focus = FocusSessionModel(
            user_id=owner,
            task_id=tid,
            kind="focus",
            status="completed",
            target_seconds=3600,
            elapsed_seconds=3600,
            started_at=datetime(2026, 11, 2, 4, 30, tzinfo=UTC),
            ended_at=datetime(2026, 11, 2, 5, 30, tzinfo=UTC),
        )
        db.add(focus)
        db.flush()
        db.add(
            FocusIntervalModel(
                user_id=owner,
                session_id=focus.id,
                started_at=focus.started_at,
                ended_at=focus.ended_at,
            )
        )
        db.commit()
    report = a.get("/api/progress").json()
    assert report["today"]["focus_seconds"] == 1800
    assert report["week"]["focus_seconds"] == 3600
    assert report["today"]["focus_sessions"] == 0
    assert report["week"]["focus_sessions"] == 1
    assert report["trends"][-2]["focus_seconds"] == 1800
    assert report["xp"] == 5
    assert a.delete(f"/api/tasks/{tid}?confirm=true", headers=ah).status_code == 204
    report = a.get("/api/progress").json()
    assert report["week"]["focus_seconds"] == 0 and report["xp"] == 5
    a.app.dependency_overrides.clear()


def test_concurrent_focus_backfill_enforces_shared_daily_cap(clients):  # noqa: F811
    a, _, engine = clients
    _, owner = enter(a)
    now = datetime(2026, 11, 7, 12, tzinfo=UTC)
    with Session(engine) as db:
        for i in range(5):
            end = now - timedelta(minutes=30 * i)
            db.add(
                FocusSessionModel(
                    user_id=owner,
                    kind="focus",
                    status="completed",
                    target_seconds=1500,
                    elapsed_seconds=1500,
                    started_at=end - timedelta(seconds=1500),
                    ended_at=end,
                )
            )
        db.commit()

    def backfill(_):
        with Session(engine) as db:
            result = ProgressService(db, owner, "UTC", lambda: now).report()
            db.commit()
            return result["xp"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(backfill, range(2))) == [20, 20]
    with Session(engine) as db:
        ledger = ProgressRepository(db, owner).ledger()
        assert len(ledger) == 5
        assert len([row for row in ledger if row.source_kind == "focus"]) == 4

from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from typing import TypedDict
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.domain.productivity import active_seconds, interval_overlap
from app.domain.rewards import BADGES, RewardRules
from app.domain.streaks import Clock, DailyFact, calculate, local_day, utc_now
from app.persistence.progress import ProgressRepository
from app.persistence.tasks import TasksRepository


class Trend(TypedDict):
    day: date
    completed: int
    focus_seconds: int


class ProgressService:
    """Derived writes share the caller's owner lock and transaction; never commit here."""

    def __init__(
        self,
        db: Session,
        owner: UUID,
        zone: str,
        clock: Clock = utc_now,
        rules: RewardRules | None = None,
    ) -> None:
        self.repo = ProgressRepository(db, owner)
        self.zone, self.clock, self.rules = zone, clock, rules or RewardRules()

    def snapshot(self) -> None:
        self.repo.db.flush()
        today = local_day(self.clock(), self.zone)
        covered = self.repo.days()
        last = covered[-1] if covered else None
        start = min(last.day, today) if last and last.time_zone == self.zone else today
        tasks = [row for row in self.repo.tasks() if row.deleted_at is None]
        # Materialize gaps before a schedule mutation, while the old schedule still applies.
        day = start
        while day <= today:
            self.repo.cover(day, self.zone)
            for row in tasks:
                if row.task_type == "daily":
                    began = local_day(row.daily_started_at or row.created_at, self.zone)
                    if day >= began:
                        self.repo.occurrence(row.id, "daily", day)
                else:
                    due = row.due_date or (local_day(row.due_at, self.zone) if row.due_at else None)
                    if due is not None and due <= day:
                        self.repo.occurrence(row.id, "one_time", due)
            day += timedelta(days=1)

    def sync(self) -> None:
        self.repo.db.flush()
        now, rules = self.clock(), self.rules
        completed, daily = self.repo.completions(), self.repo.daily()
        ledger = self.repo.ledger()
        existing = {(row.source_kind, row.source_id) for row in ledger}
        counts: dict[object, int] = {}
        for entry in ledger:
            if entry.source_kind == "focus":
                counts[entry.reward_day] = counts.get(entry.reward_day, 0) + 1
        for row in completed:
            if ("one_time", row.id) in existing:
                continue
            self.repo.award(
                "one_time",
                row.id,
                rules.task_xp,
                local_day(row.completed_at, self.zone),
                row.completed_at,
                now,
                rules.provenance,
            )
        for fact in daily:
            if ("daily", fact.id) in existing:
                continue
            self.repo.award(
                "daily",
                fact.id,
                rules.daily_xp,
                fact.completion_day,
                fact.completed_at,
                now,
                rules.provenance,
            )
        focus = self.repo.focus()
        for session in focus:
            if (
                session.kind != "focus"
                or session.status != "completed"
                or session.elapsed_seconds < rules.focus_min_seconds
                or session.ended_at is None
            ):
                continue
            day = local_day(session.ended_at, self.zone)
            if ("focus", session.id) not in existing and ("focus_skip", session.id) not in existing:
                eligible = counts.get(day, 0) < rules.focus_daily_cap
                self.repo.award(
                    "focus" if eligible else "focus_skip",
                    session.id,
                    rules.focus_xp if eligible else 0,
                    day,
                    session.ended_at,
                    now,
                    rules.provenance,
                )
                if eligible:
                    counts[day] = counts.get(day, 0) + 1
        ids = {row.task_id for row in completed} | {fact.task_id for fact in daily}
        groups: dict[UUID, list[DailyFact]] = {}
        for fact in daily:
            groups.setdefault(fact.task_id, []).append(DailyFact(fact.epoch, fact.completion_day))
        best = max(
            (
                calculate(facts, None, local_day(now, self.zone), self.zone).best_streak
                for facts in groups.values()
            ),
            default=0,
        )
        seconds = sum(
            (row.ended_at - row.started_at).total_seconds() for row in self.repo.intervals()
        )
        criteria = {
            "first_completion": bool(ids),
            "seven_day_streak": best >= 7,
            "twenty_five_tasks": len(ids) >= 25,
            "focus_300": seconds >= 18000,
        }
        for key, earned in criteria.items():
            if earned:
                self.repo.badge(key, now)

    def report(self) -> dict[str, object]:
        self.zone = TasksRepository(self.repo.db, self.repo.owner).lock_owner().time_zone
        self.snapshot()
        self.sync()
        now = self.clock()
        today = local_day(now, self.zone)
        start = today - timedelta(days=6)
        tasks = {row.id: row for row in self.repo.tasks() if row.deleted_at is None}
        completed = [row for row in self.repo.completions() if row.task_id in tasks]
        daily = [row for row in self.repo.daily() if row.task_id in tasks]
        # Daily events retain their qualifying local label across timezone changes.
        events = [(row.task_id, local_day(row.completed_at, self.zone)) for row in completed] + [
            (row.task_id, row.completion_day) for row in daily
        ]
        coverage = {row.day for row in self.repo.days() if row.time_zone == self.zone}
        occurrences = self.repo.occurrences(start, today)
        one_done = {row.task_id: row.completed_at for row in completed}
        daily_done = {(row.task_id, row.completion_day) for row in daily}
        sessions = [row for row in self.repo.focus() if row.task_id is None or row.task_id in tasks]
        allowed_sessions = {row.id for row in sessions}
        intervals = [
            (row.started_at, row.ended_at)
            for row in self.repo.intervals()
            if row.session_id in allowed_sessions
        ]
        for session in sessions:
            if session.kind == "focus" and session.status == "active" and session.active_since:
                elapsed = active_seconds(
                    session.elapsed_seconds, session.active_since, now, session.target_seconds
                )
                intervals.append(
                    (
                        session.active_since,
                        session.active_since + timedelta(seconds=elapsed - session.elapsed_seconds),
                    )
                )
        trends: list[Trend] = []
        for i in range(7):
            day = start + timedelta(days=i)
            a = datetime.combine(day, time.min, ZoneInfo(self.zone)).astimezone(UTC)
            b = min(
                now,
                datetime.combine(day + timedelta(days=1), time.min, ZoneInfo(self.zone)).astimezone(
                    UTC
                ),
            )
            trends.append(
                {
                    "day": day,
                    "completed": sum(d == day for _, d in events),
                    "focus_seconds": int(sum(interval_overlap(x, y, a, b) for x, y in intervals)),
                }
            )

        def period(days: int) -> dict[str, object]:
            first = today - timedelta(days=days - 1)
            eligible = [row for row in occurrences if row.day >= first]
            end = datetime.combine(
                today + timedelta(days=1), time.min, ZoneInfo(self.zone)
            ).astimezone(UTC)
            numerator = sum(
                (row.task_id, row.day) in daily_done
                if row.kind == "daily"
                else row.task_id in one_done and one_done[row.task_id] < end
                for row in eligible
            )
            covered = sum(first + timedelta(days=i) in coverage for i in range(days))
            return {
                "start": first,
                "end": today,
                "completed": sum(first <= d <= today for _, d in events),
                "eligible": len(eligible),
                "eligible_completed": numerator,
                "covered_days": covered,
                "days": days,
                "completion_rate": numerator / len(eligible)
                if eligible and covered == days
                else None,
                "focus_seconds": sum(int(row["focus_seconds"]) for row in trends[-days:]),
                "focus_sessions": sum(
                    s.kind == "focus" and first <= local_day(s.started_at, self.zone) <= today
                    for s in sessions
                ),
            }

        categories = self.repo.categories()
        breakdown: dict[str, int] = {}
        for task_id, day in events:
            if start <= day <= today:
                name = (
                    categories.get(category_id, "Uncategorized")
                    if (category_id := tasks[task_id].category_id)
                    else "Uncategorized"
                )
                breakdown[name] = breakdown.get(name, 0) + 1
        streaks = [
            calculate(
                [DailyFact(f.epoch, f.completion_day) for f in daily if f.task_id == row.id],
                row.daily_epoch,
                today,
                self.zone,
            )
            for row in tasks.values()
            if row.task_type == "daily"
        ]
        total = sum(row.amount for row in self.repo.ledger())
        badges = {row.key: row.earned_at for row in self.repo.badges()}
        return {
            "time_zone": self.zone,
            "xp": total,
            "level": 1 + total // 100,
            "level_progress": total % 100,
            "next_level_xp": (total // 100 + 1) * 100,
            "rules": asdict(self.rules),
            "badges": [
                {"key": key, "name": value[0], "reason": value[1], "earned_at": badges.get(key)}
                for key, value in BADGES.items()
            ],
            "today": period(1),
            "week": period(7),
            "trends": trends,
            "categories": [{"name": k, "completed": v} for k, v in sorted(breakdown.items())],
            "current_streak": max((s.current_streak for s in streaks), default=0),
            "best_streak": max((s.best_streak for s in streaks), default=0),
            "daily_completions": len(daily),
        }

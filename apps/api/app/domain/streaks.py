from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


def local_day(instant: datetime, zone: str) -> date:
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Clock must return timezone-aware instant")
    return instant.astimezone(ZoneInfo(zone)).date()


@dataclass(frozen=True)
class DailyFact:
    epoch: UUID
    day: date


@dataclass(frozen=True)
class Streak:
    current_streak: int
    best_streak: int
    today_completed: bool
    last_qualified_day: date | None
    total_completions: int
    current_day: date
    time_zone: str


def calculate(facts: Iterable[DailyFact], epoch: UUID | None, today: date, zone: str) -> Streak:
    grouped: dict[UUID, set[date]] = {}
    for fact in facts:
        grouped.setdefault(fact.epoch, set()).add(fact.day)
    best = 0
    for days in grouped.values():
        previous = None
        run = 0
        for day in sorted(days):
            run = run + 1 if previous is not None and day == previous + timedelta(days=1) else 1
            best = max(best, run)
            previous = day
    all_days = set().union(*grouped.values()) if grouped else set()
    active = grouped.get(epoch, set()) if epoch is not None else set()
    # After westward travel, future-labeled historical days remain immutable but
    # do not advance today's current run until that local calendar date arrives.
    eligible = {day for day in active if day <= today}
    last = max(eligible) if eligible else None
    current = 0
    if last in (today, today - timedelta(days=1)):
        cursor = last
        while cursor in eligible:
            current += 1
            cursor -= timedelta(days=1)
    return Streak(
        current,
        best,
        today in all_days,
        max(all_days) if all_days else None,
        len(all_days),
        today,
        zone,
    )

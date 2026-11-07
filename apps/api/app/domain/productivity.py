from datetime import datetime


def active_seconds(
    elapsed: float, active_since: datetime | None, now: datetime, target: int
) -> float:
    return min(
        float(target),
        elapsed + (max(0.0, (now - active_since).total_seconds()) if active_since else 0.0),
    )


def interval_overlap(
    start: datetime, end: datetime, period_start: datetime, period_end: datetime
) -> float:
    return max(0.0, (min(end, period_end) - max(start, period_start)).total_seconds())

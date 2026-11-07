from dataclasses import dataclass


@dataclass(frozen=True)
class RewardRules:
    task_xp: int = 10
    daily_xp: int = 5
    focus_xp: int = 5
    focus_min_seconds: int = 1500
    focus_daily_cap: int = 4
    level_step: int = 100

    @property
    def provenance(self) -> str:
        return f"v1:{self.task_xp}/{self.daily_xp}/{self.focus_xp};focus={self.focus_min_seconds}s,cap={self.focus_daily_cap}"


BADGES = {
    "first_completion": ("First completion", "Completed your first task occurrence."),
    "seven_day_streak": (
        "Seven-day streak",
        "Qualified on seven consecutive dates in one habit epoch.",
    ),
    "twenty_five_tasks": (
        "25 tasks",
        "Completed 25 distinct tasks; repeated habit check-ins count once.",
    ),
    "focus_300": (
        "300 focus minutes",
        "Recorded 300 active focus minutes, excluding breaks and pauses.",
    ),
}

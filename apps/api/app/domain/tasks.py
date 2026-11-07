from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class TaskQuery:
    view: str = "all"
    search: str | None = None
    status: str | None = None
    task_type: str | None = None
    priority: str | None = None
    category_id: UUID | None = None
    due_date: date | None = None
    overdue: bool | None = None
    sort: str = "created_at"
    descending: bool = True
    limit: int = 25
    offset: int = 0

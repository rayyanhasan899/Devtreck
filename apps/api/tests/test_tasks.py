from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from test_accounts import clients, login, signup  # noqa: F401
from test_persistence import database  # noqa: F401

from app.persistence.models import (
    CategoryModel,
    CompletionModel,
    TaskModel,
    TaskTypeChangeModel,
    UserModel,
)


def account(client):
    return login(client, signup(client)["email"])


def create(client, headers, **changes):
    response = client.post("/api/tasks", json={"title": "Write report", **changes}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_crud_completion_reopen_and_archive(clients):  # noqa: F811
    first, _, engine = clients
    headers = account(first)
    task = create(first, headers, description="Initial", priority="high", estimated_minutes=30)
    path = "/api/tasks/" + task["id"]
    assert first.get(path).json()["status"] == "pending"
    changed = first.patch(
        path, json={"title": " Renamed ", "status": "in-progress"}, headers=headers
    )
    assert changed.status_code == 200
    assert changed.json()["title"] == "Renamed" and changed.json()["description"] == "Initial"
    assert changed.json()["updated_at"] >= task["updated_at"]
    assert first.post(path + "/complete", headers=headers).json()["status"] == "completed"
    assert first.post(path + "/complete", headers=headers).status_code == 200
    history = first.get(path + "/history").json()
    assert len(history) == 1
    assert first.get("/api/tasks").json()["total"] == 0
    assert first.get("/api/tasks?view=completed").json()["total"] == 1
    assert first.post(path + "/reopen", headers=headers).json()["status"] == "pending"
    assert first.patch(path, json={"status": "completed"}, headers=headers).status_code == 200
    assert first.get(path + "/history").json() == history
    assert first.delete(path, headers=headers).status_code == 422
    assert first.delete(path + "?confirm=true", headers=headers).status_code == 204
    assert first.get(path).status_code == 404
    assert first.get(path + "/history").status_code == 404
    with Session(engine) as db:
        assert db.get(TaskModel, task["id"]).deleted_at is not None
        assert db.scalar(select(CompletionModel).where(CompletionModel.task_id == task["id"]))


def test_category_crud_and_cross_owner_protection(clients):  # noqa: F811
    first, second, engine = clients
    ah, bh = account(first), account(second)
    category = first.post("/api/categories", json={"name": "Work"}, headers=ah).json()
    cid = category["id"]
    assert (
        first.patch("/api/categories/" + cid, json={"name": "Study"}, headers=ah).status_code == 200
    )
    assert second.get("/api/categories").json() == []
    assert second.get("/api/categories/" + cid).status_code == 404
    assert (
        second.patch("/api/categories/" + cid, json={"name": "Stolen"}, headers=bh).status_code
        == 404
    )
    assert second.delete("/api/categories/" + cid + "?confirm=true", headers=bh).status_code == 404
    assert (
        second.post(
            "/api/tasks", json={"title": "Attack", "category_id": cid}, headers=bh
        ).status_code
        == 404
    )
    task = create(first, ah, category_id=cid)
    other = create(second, bh)
    for method, suffix, body in [
        ("GET", "", None),
        ("PATCH", "", {"title": "Steal"}),
        ("POST", "/complete", None),
        ("POST", "/reopen", None),
        ("GET", "/history", None),
        ("DELETE", "?confirm=true", None),
    ]:
        assert (
            second.request(
                method, "/api/tasks/" + task["id"] + suffix, json=body, headers=bh
            ).status_code
            == 404
        )
    assert (
        second.patch("/api/tasks/" + other["id"], json={"category_id": cid}, headers=bh).status_code
        == 404
    )
    # Bypassing API still cannot assign a foreign category.
    with Session(engine) as db:
        row = db.get(TaskModel, other["id"])
        row.category_id = cid
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    assert first.delete("/api/categories/" + cid + "?confirm=true", headers=ah).status_code == 204
    assert first.get("/api/tasks/" + task["id"]).json()["category_id"] is None
    assert second.get("/api/tasks/" + other["id"]).status_code == 200


def test_task_validation_and_mutation_guards(clients):  # noqa: F811
    first, second, _ = clients
    headers = account(first)
    assert second.get("/api/tasks").status_code == 401
    for body in [
        {"title": " "},
        {"title": "X", "priority": "urgent"},
        {"title": "X", "user_id": str(uuid4())},
        {"title": "X", "estimated_minutes": 0},
        {"title": "X", "due_at": "2026-11-07T12:00:00"},
        {"title": "X", "due_date": "bad"},
        {"title": "X", "due_date": "2026-11-07", "due_at": "2026-11-07T12:00:00Z"},
    ]:
        assert first.post("/api/tasks", json=body, headers=headers).status_code == 422
    task = create(first, headers)
    path = "/api/tasks/" + task["id"]
    for body in [{"title": None}, {"status": "invalid"}, {"title": " "}, {"user_id": str(uuid4())}]:
        assert first.patch(path, json=body, headers=headers).status_code == 422
    assert (
        first.post(
            "/api/tasks", json={"title": "No CSRF"}, headers={"Origin": "http://localhost:3000"}
        ).status_code
        == 403
    )
    assert first.get("/api/tasks/not-a-uuid").status_code == 422
    for query in [
        "limit=101",
        "limit=0",
        "offset=-1",
        "sort=drop_table",
        "view=invalid",
        "priority=urgent",
    ]:
        assert first.get("/api/tasks?" + query).status_code == 422


def test_all_views_filters_sorts_pagination_and_local_dates(clients):  # noqa: F811
    first, _, _ = clients
    headers = account(first)
    from zoneinfo import ZoneInfo

    first.patch("/api/users/me", json={"time_zone": "Asia/Karachi"}, headers=headers)
    today = datetime.now(ZoneInfo("Asia/Karachi")).date()
    old = create(
        first,
        headers,
        title="Alpha overdue",
        priority="high",
        due_date=str(today - timedelta(days=1)),
    )
    current = create(
        first,
        headers,
        title="Beta today",
        priority="medium",
        due_date=str(today),
        description="needle %_ literal",
    )
    future = create(
        first,
        headers,
        title="Charlie upcoming",
        priority="low",
        due_date=str(today + timedelta(days=1)),
    )
    daily = create(first, headers, title="Habit", task_type="daily")
    untimed = create(first, headers, title="No deadline")

    def ids(query):
        response = first.get("/api/tasks?" + query)
        assert response.status_code == 200, response.text
        return [x["id"] for x in response.json()["items"]]

    assert set(ids("view=today")) == {old["id"], current["id"], daily["id"]}
    assert ids("view=overdue") == [old["id"]]
    assert ids("view=upcoming") == [future["id"]]
    assert ids("view=daily") == [daily["id"]]
    assert ids("due_date=" + str(today)) == [current["id"]]
    assert ids("search=needle") == [current["id"]]
    assert ids("search=%25_") == [current["id"]]
    assert ids("priority=high") == [old["id"]]
    assert ids("task_type=daily") == [daily["id"]]
    assert ids("overdue=true") == [old["id"]]
    assert untimed["id"] in ids("overdue=false")
    assert ids("sort=title&descending=false")[0] == old["id"]
    for sort in ["created_at", "updated_at", "priority", "due_date", "title"]:
        all_ids = ids("sort=" + sort + "&descending=false")
        assert len(all_ids) == 5
    page = first.get("/api/tasks?limit=2&offset=2").json()
    assert page["total"] == 5 and len(page["items"]) == 2
    assert ids("search=nonexistent") == []
    # Timed deadline earlier today is overdue immediately, unlike date-only today.
    timed = create(
        first, headers, title="Timed", due_at=(datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    )
    assert timed["id"] in ids("view=overdue")
    assert current["id"] not in ids("view=overdue")
    first.post("/api/tasks/" + future["id"] + "/complete", headers=headers)
    assert ids("view=upcoming&status=completed") == []


def test_type_changes_preserve_history_and_block_daily_completion(clients):  # noqa: F811
    first, _, engine = clients
    headers = account(first)
    task = create(first, headers)
    path = "/api/tasks/" + task["id"]
    first.post(path + "/complete", headers=headers)
    history = first.get(path + "/history").json()
    assert (
        first.patch(path, json={"task_type": "daily"}, headers=headers).json()["status"]
        == "pending"
    )
    assert first.post(path + "/complete", headers=headers).status_code == 409
    assert first.patch(path, json={"status": "completed"}, headers=headers).status_code == 409
    assert first.patch(path, json={"task_type": "one-time"}, headers=headers).status_code == 200
    assert first.get(path + "/history").json() == history
    with Session(engine) as db:
        assert (
            len(
                db.scalars(
                    select(TaskTypeChangeModel).where(TaskTypeChangeModel.task_id == task["id"])
                ).all()
            )
            == 2
        )


def test_account_delete_cascades_task_data(clients):  # noqa: F811
    first, _, engine = clients
    headers = account(first)
    owner_id = first.get("/api/users/me").json()["id"]
    category = first.post("/api/categories", json={"name": "Delete all"}, headers=headers).json()
    task = create(first, headers, category_id=category["id"])
    first.post("/api/tasks/" + task["id"] + "/complete", headers=headers)
    response = first.request(
        "DELETE",
        "/api/users/me",
        json={"current_password": "correct horse battery staple", "confirm": True},
        headers=headers,
    )
    assert response.status_code == 204, response.text
    with Session(engine) as db:
        assert db.get(UserModel, owner_id) is None
        assert db.get(TaskModel, task["id"]) is None
        assert db.get(CategoryModel, category["id"]) is None
        assert (
            db.scalar(select(CompletionModel).where(CompletionModel.task_id == task["id"])) is None
        )


def test_filters_partial_nulls_and_category_conflict(clients):  # noqa: F811
    first, _, _ = clients
    headers = account(first)
    category = first.post("/api/categories", json={"name": "Personal"}, headers=headers).json()
    assert (
        first.post("/api/categories", json={"name": "Personal"}, headers=headers).status_code == 409
    )
    assert first.post("/api/categories", json={"name": " "}, headers=headers).status_code == 422
    task = create(
        first,
        headers,
        category_id=category["id"],
        due_date="2030-01-01",
        description="Keep",
        estimated_minutes=5,
    )
    path = "/api/tasks/" + task["id"]
    assert first.get("/api/tasks", params={"category_id": category["id"]}).json()["total"] == 1
    first.patch(path, json={"status": "in-progress"}, headers=headers)
    assert first.get("/api/tasks?status=in-progress").json()["total"] == 1
    # A timed replacement must explicitly clear a previous date-only deadline.
    assert (
        first.patch(path, json={"due_at": "2030-01-01T12:00:00Z"}, headers=headers).status_code
        == 409
    )
    response = first.patch(
        path,
        json={
            "due_date": None,
            "due_at": "2030-01-01T12:00:00Z",
            "description": None,
            "category_id": None,
            "estimated_minutes": None,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["due_date"] is None
    assert response.json()["description"] is None
    assert response.json()["category_id"] is None
    assert response.json()["status"] == "in-progress"


def test_concurrent_completion_is_single_fact(clients):  # noqa: F811
    from concurrent.futures import ThreadPoolExecutor

    from app.services.tasks import TasksService

    first, _, engine = clients
    headers = account(first)
    task = create(first, headers)
    owner = uuid4()
    with Session(engine) as db:
        owner = db.get(TaskModel, task["id"]).user_id

    def finish(_):
        with Session(engine) as db:
            TasksService(db, owner, "UTC").complete(UUID(task["id"]))

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(finish, range(2)))
    assert len(first.get("/api/tasks/" + task["id"] + "/history").json()) == 1

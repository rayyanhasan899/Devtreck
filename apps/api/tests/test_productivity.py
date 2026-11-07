from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from test_accounts import clients, login, signup  # noqa: F401
from test_persistence import database  # noqa: F401

from app.persistence.models import FocusEventModel, FocusSessionModel
from app.presentation.tasks import get_clock
from app.services.productivity import ProductivityService


def enter(client):
    return login(client, signup(client)["email"])


def task(client, headers, title="Task", **extra):
    response = client.post("/api/tasks", json={"title": title, **extra}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_checklist_crud_order_ownership_and_parent_state(clients):  # noqa: F811
    a, b, _ = clients
    ah, bh = enter(a), enter(b)
    parent = task(a, ah)
    path = f"/api/tasks/{parent['id']}/checklist"
    one = a.post(path, json={"title": "First"}, headers=ah).json()
    two = a.post(path, json={"title": "Second"}, headers=ah).json()
    assert (
        a.patch(
            path + "/" + one["id"], json={"completed": True, "title": "Renamed"}, headers=ah
        ).status_code
        == 200
    )
    assert (
        a.put(
            f"/api/tasks/{parent['id']}/checklist-order",
            json={"ids": [two["id"], one["id"]]},
            headers=ah,
        ).json()[0]["id"]
        == two["id"]
    )
    assert (
        a.put(
            f"/api/tasks/{parent['id']}/checklist-order",
            json={"ids": [one["id"], one["id"]]},
            headers=ah,
        ).status_code
        == 409
    )
    assert b.get(path).status_code == 404
    assert b.patch(path + "/" + one["id"], json={"completed": True}, headers=bh).status_code == 404
    assert a.patch(path + "/" + two["id"], json={"completed": True}, headers=ah).status_code == 200
    result = a.get("/api/tasks/" + parent["id"]).json()
    assert (
        result["status"] == "pending"
        and result["checklist_completed"] == 2
        and result["checklist_total"] == 2
    )
    assert a.delete(path + "/" + one["id"], headers=ah).status_code == 204
    assert a.get(path).json()[0]["position"] == 0
    assert a.post(path, json={"title": " "}, headers=ah).status_code == 422


def test_plan_order_priorities_workload_and_cross_owner(clients):  # noqa: F811
    a, b, _ = clients
    ah, bh = enter(a), enter(b)
    first = task(a, ah, "High", task_type="daily", priority="high", estimated_minutes=25)
    second = task(a, ah, "Low", task_type="daily", priority="low")
    plan = a.get("/api/plan/today").json()
    assert plan["items"][0]["id"] == first["id"]
    assert (plan["estimated_minutes"], plan["missing_estimates"]) == (25, 1)
    assert "High priority" in plan["reasons"][first["id"]]
    assert (
        a.put(
            "/api/plan/today",
            json={"order_ids": [second["id"], first["id"]], "priority_ids": [first["id"]]},
            headers=ah,
        ).status_code
        == 204
    )
    a.post(f"/api/tasks/{first['id']}/checklist", json={"title": "Plan step"}, headers=ah)
    saved = a.get("/api/plan/today").json()
    assert saved["items"][0]["id"] == second["id"] and saved["priority_ids"] == [first["id"]]
    assert next(row for row in saved["items"] if row["id"] == first["id"])["checklist_total"] == 1
    assert (
        b.put(
            "/api/plan/today", json={"order_ids": [first["id"]], "priority_ids": []}, headers=bh
        ).status_code
        == 409
    )
    assert (
        a.put(
            "/api/plan/today",
            json={"order_ids": [first["id"], first["id"]], "priority_ids": []},
            headers=ah,
        ).status_code
        == 409
    )
    assert (
        a.put(
            "/api/plan/today",
            json={"order_ids": [], "priority_ids": [str(uuid4()) for _ in range(4)]},
            headers=ah,
        ).status_code
        == 422
    )
    a.post(f"/api/tasks/{first['id']}/complete", headers=ah)
    assert first["id"] not in [row["id"] for row in a.get("/api/plan/today").json()["items"]]


def test_focus_clock_pauses_expiration_events_summary_and_breaks(clients):  # noqa: F811
    a, _, engine = clients
    ah = enter(a)
    parent = task(a, ah)
    now = [datetime(2026, 11, 7, 23, 59, 30, tzinfo=UTC)]
    a.app.dependency_overrides[get_clock] = lambda: lambda: now[0]
    key = str(uuid4())
    payload = {"key": key, "seconds": 120, "task_id": parent["id"]}
    first = a.post("/api/focus", json=payload, headers=ah)
    assert first.status_code == 201, first.text
    sid = first.json()["id"]
    assert a.post("/api/focus", json=payload, headers=ah).json()["id"] == sid
    assert a.post("/api/focus", json={**payload, "seconds": 180}, headers=ah).status_code == 409
    now[0] += timedelta(seconds=40)
    pause_key = str(uuid4())
    paused = a.post(f"/api/focus/{sid}/pause", json={"key": pause_key}, headers=ah).json()
    assert paused["elapsed_seconds"] == 40
    now[0] += timedelta(seconds=100)
    assert (
        a.post(f"/api/focus/{sid}/pause", json={"key": pause_key}, headers=ah).json()[
            "elapsed_seconds"
        ]
        == 40
    )
    assert a.get("/api/focus/current").json()["status"] == "paused"
    assert (
        a.post(f"/api/focus/{sid}/resume", json={"key": str(uuid4())}, headers=ah).status_code
        == 200
    )
    now[0] += timedelta(seconds=1000)
    assert a.get("/api/focus/current").json() is None
    last = a.get("/api/focus/history").json()[0]
    assert last["status"] == "completed" and last["elapsed_seconds"] == 120
    totals = a.get("/api/focus/summary").json()
    assert totals["day_seconds"] == 90 and totals["week_seconds"] == 120
    assert a.get("/api/tasks/" + parent["id"]).json()["status"] == "pending"
    _start = a.post(
        "/api/focus", json={"key": str(uuid4()), "kind": "break", "seconds": 60}, headers=ah
    ).json()
    now[0] += timedelta(seconds=100)
    assert a.get("/api/focus/current").json() is None
    assert a.get("/api/focus/summary").json()["week_seconds"] == 120
    with Session(engine) as db:
        assert (
            len(
                db.scalars(
                    select(FocusEventModel).where(FocusEventModel.session_id == UUID(sid))
                ).all()
            )
            == 3
        )
    a.app.dependency_overrides.clear()


def test_focus_ownership_idempotency_and_one_active_session(clients):  # noqa: F811
    a, b, _ = clients
    ah, bh = enter(a), enter(b)
    private = task(a, ah)
    assert (
        b.post(
            "/api/focus", json={"key": str(uuid4()), "task_id": private["id"]}, headers=bh
        ).status_code
        == 404
    )
    started = a.post("/api/focus", json={"key": str(uuid4())}, headers=ah).json()
    assert a.post("/api/focus", json={"key": str(uuid4())}, headers=ah).status_code == 409
    assert (
        b.post(
            f"/api/focus/{started['id']}/stop", json={"key": str(uuid4())}, headers=bh
        ).status_code
        == 404
    )
    assert b.get("/api/focus/history").json() == []
    stop = {"key": str(uuid4())}
    assert a.post(f"/api/focus/{started['id']}/stop", json=stop, headers=ah).status_code == 200
    assert (
        a.post(f"/api/focus/{started['id']}/stop", json=stop, headers=ah).json()["status"]
        == "stopped"
    )


def test_concurrent_focus_and_checklist_reorders(clients):  # noqa: F811
    from concurrent.futures import ThreadPoolExecutor

    a, _, engine = clients
    ah = enter(a)
    parent = task(a, ah)
    owner = UUID(a.get("/api/users/me").json()["id"])
    key = uuid4()

    def start(_):
        with Session(engine) as db:
            return ProductivityService(db, owner, "UTC").command(key, "start").id

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(start, range(2)))
    assert result[0] == result[1]
    with Session(engine) as db:
        assert (
            len(
                db.scalars(
                    select(FocusSessionModel).where(FocusSessionModel.user_id == owner)
                ).all()
            )
            == 1
        )
    one = a.post(f"/api/tasks/{parent['id']}/checklist", json={"title": "A"}, headers=ah).json()
    two = a.post(f"/api/tasks/{parent['id']}/checklist", json={"title": "B"}, headers=ah).json()

    def reorder(reverse):
        with Session(engine) as db:
            ids = [UUID(one["id"]), UUID(two["id"])]
            ProductivityService(db, owner, "UTC").reorder(
                UUID(parent["id"]), list(reversed(ids)) if reverse else ids
            )

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(reorder, [False, True]))
    assert sorted(
        item["position"] for item in a.get(f"/api/tasks/{parent['id']}/checklist").json()
    ) == [0, 1]


def test_account_deletion_cascades_productivity_data(clients):  # noqa: F811
    from app.persistence.models import ChecklistModel, DailyPlanModel, FocusIntervalModel

    a, _, engine = clients
    headers = enter(a)
    owner = UUID(a.get("/api/users/me").json()["id"])
    parent = task(a, headers, task_type="daily")
    a.post(f"/api/tasks/{parent['id']}/checklist", json={"title": "Owned"}, headers=headers)
    a.put(
        "/api/plan/today",
        json={"order_ids": [parent["id"]], "priority_ids": [parent["id"]]},
        headers=headers,
    )
    started = a.post(
        "/api/focus", json={"key": str(uuid4()), "task_id": parent["id"]}, headers=headers
    ).json()
    a.post(f"/api/focus/{started['id']}/stop", json={"key": str(uuid4())}, headers=headers)
    assert (
        a.request(
            "DELETE",
            "/api/users/me",
            json={"current_password": "correct horse battery staple", "confirm": True},
            headers=headers,
        ).status_code
        == 204
    )
    with Session(engine) as db:
        for model in [
            ChecklistModel,
            DailyPlanModel,
            FocusSessionModel,
            FocusEventModel,
            FocusIntervalModel,
        ]:
            assert db.scalar(select(model).where(model.user_id == owner)) is None

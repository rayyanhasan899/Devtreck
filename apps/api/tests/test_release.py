from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session
from test_accounts import PASSWORD, clients, login, signup  # noqa: F401
from test_persistence import database  # noqa: F401

from app.core.config import Settings
from app.core.security import password_slots
from app.main import create_app
from app.persistence.models import DailyCompletionModel, TaskModel, UserModel


def test_every_private_get_rejects_anonymous_clients(clients):  # noqa: F811
    a, _, _ = clients
    identifier = str(uuid4())
    paths = [
        "/auth/csrf",
        "/users/me",
        "/tasks",
        f"/tasks/{identifier}",
        f"/tasks/{identifier}/history",
        f"/tasks/{identifier}/daily-history",
        f"/tasks/{identifier}/streak",
        f"/tasks/{identifier}/checklist",
        "/categories",
        f"/categories/{identifier}",
        "/dashboard",
        "/plan/today",
        "/focus/current",
        "/focus/history",
        "/focus/summary",
        "/progress",
    ]
    for path in paths:
        result = a.get("/api" + path)
        assert result.status_code == 401, (path, result.status_code)
        assert result.headers["cache-control"] == "no-store"
        assert result.headers["x-content-type-options"] == "nosniff"


def test_password_resource_limit_recovers_without_partial_registration(clients):  # noqa: F811
    a, _, engine = clients
    email = f"{uuid4().hex}@example.com"
    payload = {"name": "Bounded auth", "email": email, "password": PASSWORD}
    assert password_slots.acquire(blocking=False)
    assert password_slots.acquire(blocking=False)
    try:
        response = a.post(
            "/api/auth/register", json=payload, headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 503
        with Session(engine) as db:
            assert db.scalar(select(UserModel).where(UserModel.email == email)) is None
    finally:
        password_slots.release()
        password_slots.release()
    assert (
        a.post(
            "/api/auth/register", json=payload, headers={"Origin": "http://localhost:3000"}
        ).status_code
        == 201
    )


def test_unexpected_failure_has_safe_logs_envelope_and_request_id(clients, caplog):  # noqa: F811
    a, _, _ = clients
    secret = "private-exception-payload-should-not-appear"

    @a.app.get("/api/synthetic-failure")
    def fail():
        raise RuntimeError(secret)

    response = a.get("/api/synthetic-failure?token=" + secret)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert response.json()["request_id"] == response.headers["x-request-id"]
    assert response.headers["cache-control"] == "no-store"
    assert secret not in response.text and secret not in caplog.text
    assert "RuntimeError" in caplog.text


def test_production_cookie_docs_csrf_and_origin_contract(database):  # noqa: F811
    _, _, url = database
    origin = "https://localhost:8443"
    app = create_app(Settings(app_env="production", allowed_origins=[origin], database_url=url))
    with TestClient(app, base_url=origin) as a:
        credentials = {
            "name": "Release",
            "email": f"{uuid4().hex}@example.com",
            "password": PASSWORD,
        }
        assert (
            a.post("/api/auth/register", json=credentials, headers={"Origin": origin}).status_code
            == 201
        )
        login_response = a.post(
            "/api/auth/login",
            json={"email": credentials["email"], "password": PASSWORD},
            headers={"Origin": origin},
        )
        cookie = login_response.headers["set-cookie"].lower()
        assert all(flag in cookie for flag in ["secure", "httponly", "samesite=strict"])
        token = login_response.json()["csrf_token"]
        assert a.get("/docs").status_code == 404 and a.get("/openapi.json").status_code == 404
        assert (
            a.post(
                "/api/tasks", json={"title": "Missing CSRF"}, headers={"Origin": origin}
            ).status_code
            == 403
        )
        assert (
            a.post(
                "/api/tasks",
                json={"title": "Wrong origin"},
                headers={"Origin": "https://evil.example", "X-CSRF-Token": token},
            ).status_code
            == 403
        )
        headers = {"Origin": origin, "X-CSRF-Token": token}
        assert (
            a.post(
                "/api/tasks", json={"title": "Safe", "user_id": str(uuid4())}, headers=headers
            ).status_code
            == 422
        )
        assert a.post("/api/tasks", json={"title": "Safe"}, headers=headers).status_code == 201


def test_task_list_batches_streak_and_checklist_queries_and_has_owner_index(clients):  # noqa: F811
    a, _, engine = clients
    owner = UUID(signup(a)["id"])
    with Session(engine) as db:
        user = db.get(UserModel, owner)
        login(a, user.email)
        rows = [
            TaskModel(user_id=owner, title=f"Daily {i}", task_type="daily", daily_epoch=uuid4())
            for i in range(120)
        ]
        db.add_all(rows)
        db.flush()
        now = datetime.now(UTC)
        db.add_all(
            [
                DailyCompletionModel(
                    user_id=owner,
                    task_id=row.id,
                    epoch=row.daily_epoch,
                    completion_day=now.date(),
                    completed_at=now,
                    time_zone="UTC",
                )
                for row in rows
            ]
        )
        db.commit()
    statements = []

    def capture(conn, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", capture)
    # The HTTP app uses its own engine; instrument that engine for actual route work.
    http_engine = a.app.state.engine
    event.listen(http_engine, "before_cursor_execute", capture)
    try:
        for limit in [25, 100]:
            statements.clear()
            response = a.get(f"/api/tasks?view=daily&limit={limit}")
            assert response.status_code == 200 and len(response.json()["items"]) == limit
            if limit == 25:
                baseline = len(statements)
            else:
                assert len(statements) == baseline
    finally:
        event.remove(engine, "before_cursor_execute", capture)
        event.remove(http_engine, "before_cursor_execute", capture)
    with engine.begin() as connection:
        # Small fixtures may favor sequential scans; confirm the owner predicate can use an index.
        connection.execute(text("SET LOCAL enable_seqscan=off"))
        plan = (
            connection.execute(
                text("EXPLAIN SELECT id FROM tasks WHERE user_id=:owner AND deleted_at IS NULL"),
                {"owner": owner},
            )
            .scalars()
            .all()
        )
        assert any("Index" in line for line in plan)
        assert connection.scalar(select(UserModel.id).where(UserModel.id == owner)) == owner

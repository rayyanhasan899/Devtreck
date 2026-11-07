from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from test_persistence import database  # noqa: F401

from app.core.config import Settings
from app.main import create_app
from app.persistence.models import RateLimitModel, SessionModel, UserModel

PASSWORD = "correct horse battery staple"
ORIGIN = {"Origin": "http://localhost:3000"}


@pytest.fixture
def clients(database):  # noqa: F811
    engine, _, url = database
    with Session(engine) as db:
        db.execute(delete(RateLimitModel))
        db.commit()
    app = create_app(Settings(app_env="test", database_url=url))
    with TestClient(app) as first, TestClient(app) as second:
        yield first, second, engine


def signup(client, email=None):
    email = email or f"{uuid4().hex}@example.com"
    response = client.post(
        "/api/auth/register",
        json={"name": " Alice ", "email": email, "password": PASSWORD},
        headers=ORIGIN,
    )
    assert response.status_code == 201, response.text
    return response.json()


def login(client, email):
    response = client.post(
        "/api/auth/login", json={"email": email, "password": PASSWORD}, headers=ORIGIN
    )
    assert response.status_code == 200, response.text
    return {**ORIGIN, "X-CSRF-Token": response.json()["csrf_token"]}


def test_registration_validation_normalization_and_secrets(clients):
    client, _, engine = clients
    account = signup(client, " Mixed.Case@EXAMPLE.COM ")
    assert account["email"] == "mixed.case@example.com"
    assert account["name"] == "Alice"
    assert "password_hash" not in account
    assert (
        client.post(
            "/api/auth/register",
            json={"name": "Other", "email": "mixed.case@example.com", "password": PASSWORD},
            headers=ORIGIN,
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/auth/register",
            json={"name": " ", "email": "invalid", "password": "short"},
            headers=ORIGIN,
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/auth/register",
            json={
                "name": "User",
                "email": "other@example.com",
                "password": PASSWORD,
                "user_id": str(uuid4()),
            },
            headers=ORIGIN,
        ).status_code
        == 422
    )
    with Session(engine) as db:
        user = db.scalar(select(UserModel).where(UserModel.email == account["email"]))
        assert user.password_hash.startswith("$argon2id$")
        assert PASSWORD not in user.password_hash


def test_login_csrf_logout_and_expiration(clients):
    client, _, engine = clients
    account = signup(client)
    headers = login(client, account["email"])
    assert client.get("/api/users/me").status_code == 200
    assert (
        client.patch("/api/users/me", json={"name": "Changed"}, headers=ORIGIN).status_code == 403
    )
    assert (
        client.patch(
            "/api/users/me",
            json={"name": "Changed"},
            headers={**headers, "Origin": "https://evil.example"},
        ).status_code
        == 403
    )
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/users/me").status_code == 401
    login(client, account["email"])
    with Session(engine) as db:
        db.execute(
            update(SessionModel).values(
                created_at=datetime.now(UTC) - timedelta(days=2),
                expires_at=datetime.now(UTC) - timedelta(days=1),
            )
        )
        db.commit()
    assert client.get("/api/users/me").status_code == 401


def test_profiles_two_users_and_email_reauthentication(clients):
    first, second, _ = clients
    a, b = signup(first), signup(second)
    ah, _bh = login(first, a["email"]), login(second, b["email"])
    assert first.get("/api/users/me").json()["id"] == a["id"]
    assert second.get("/api/users/me").json()["id"] == b["id"]
    assert first.patch("/api/users/me", json={"id": b["id"]}, headers=ah).status_code == 422
    assert first.get("/api/users/" + b["id"]).status_code == 404
    assert (
        first.patch("/api/users/me", json={"time_zone": "Invalid/Zone"}, headers=ah).status_code
        == 422
    )
    assert (
        first.patch(
            "/api/users/me", json={"time_zone": "Asia/Karachi", "theme": "dark"}, headers=ah
        ).status_code
        == 200
    )
    assert (
        first.patch(
            "/api/users/me", json={"email": b["email"], "current_password": PASSWORD}, headers=ah
        ).status_code
        == 409
    )
    assert (
        first.patch("/api/users/me", json={"email": "new@example.com"}, headers=ah).status_code
        == 401
    )
    assert (
        first.patch(
            "/api/users/me",
            json={"email": "new@example.com", "current_password": PASSWORD},
            headers=ah,
        ).status_code
        == 200
    )
    assert first.get("/api/users/me").status_code == 401
    assert second.get("/api/users/me").json()["id"] == b["id"]


def test_password_change_and_account_deletion(clients):
    first, second, engine = clients
    a = signup(first)
    headers = login(first, a["email"])
    login(second, a["email"])
    assert (
        first.patch(
            "/api/users/me/password",
            json={"current_password": "wrong", "new_password": PASSWORD + "new"},
            headers=headers,
        ).status_code
        == 401
    )
    assert (
        first.patch(
            "/api/users/me/password",
            json={"current_password": PASSWORD, "new_password": PASSWORD + "new"},
            headers=headers,
        ).status_code
        == 204
    )
    assert second.get("/api/users/me").status_code == 401
    response = first.post(
        "/api/auth/login", json={"email": a["email"], "password": PASSWORD + "new"}, headers=ORIGIN
    )
    headers = {**ORIGIN, "X-CSRF-Token": response.json()["csrf_token"]}
    assert (
        first.request(
            "DELETE",
            "/api/users/me",
            json={"current_password": PASSWORD + "new", "confirm": True},
            headers=headers,
        ).status_code
        == 204
    )
    assert first.get("/api/users/me").status_code == 401
    with Session(engine) as db:
        assert db.get(UserModel, a["id"]) is None
        assert db.scalar(select(SessionModel).where(SessionModel.user_id == a["id"])) is None


def test_generic_invalid_login_and_throttling(clients):
    client, _, _ = clients
    for i in range(11):
        response = client.post(
            "/api/auth/login",
            json={"email": "missing@example.com", "password": PASSWORD},
            headers=ORIGIN,
        )
        assert response.status_code == (401 if i < 10 else 429)
        assert PASSWORD not in response.text
    assert (
        client.post(
            "/api/auth/register", json={"name": "X", "email": "x@example.com", "password": PASSWORD}
        ).status_code
        == 403
    )


def test_cookie_replay_csrf_and_storage(clients):
    from app.core.security import digest

    first, second, engine = clients
    a = signup(first)
    response = first.post(
        "/api/auth/login", json={"email": a["email"], "password": PASSWORD}, headers=ORIGIN
    )
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Max-Age=604800" in cookie
    raw = first.cookies.get("devtreck_session")
    with Session(engine) as db:
        record = db.scalar(select(SessionModel).where(SessionModel.token_hash == digest(raw)))
        assert record and record.token_hash != raw
    csrf = first.get("/api/auth/csrf")
    assert csrf.headers["cache-control"] == "no-store"
    assert csrf.json()["csrf_token"] == response.json()["csrf_token"]
    assert (
        first.request(
            "DELETE",
            "/api/users/me",
            json={"confirm": False, "current_password": PASSWORD},
            headers={**ORIGIN, "X-CSRF-Token": csrf.json()["csrf_token"]},
        ).status_code
        == 422
    )
    assert (
        first.post(
            "/api/auth/logout", headers={**ORIGIN, "X-CSRF-Token": csrf.json()["csrf_token"]}
        ).status_code
        == 204
    )
    second.cookies.set("devtreck_session", raw)
    assert second.get("/api/users/me").status_code == 401


def test_production_cookie_secure(clients, database):  # noqa: F811
    first, _, _ = clients
    a = signup(first)
    _, _, url = database
    app = create_app(
        Settings(
            app_env="production", database_url=url, allowed_origins=["https://devtreck.example"]
        )
    )
    with TestClient(app, base_url="https://devtreck.example") as client:
        response = client.post(
            "/api/auth/login",
            json={"email": a["email"], "password": PASSWORD},
            headers={"Origin": "https://devtreck.example"},
        )
        assert response.status_code == 200
        assert "Secure" in response.headers["set-cookie"]
        assert client.get("/api/users/me").status_code == 200


def test_concurrent_registration_and_throttle_counts(clients):
    from concurrent.futures import ThreadPoolExecutor

    from app.domain.errors import ConflictError
    from app.persistence.accounts import AccountsRepository
    from app.services.accounts import AccountsService

    _, _, engine = clients
    email = f"{uuid4().hex}@example.com"

    def register(_):
        with Session(engine) as db:
            try:
                AccountsService(db).register("Concurrent", email, PASSWORD)
                return "created"
            except ConflictError:
                return "duplicate"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(register, range(2))) == ["created", "duplicate"]

    def count(_):
        with Session(engine) as db:
            return AccountsRepository(db).throttle("f" * 64, 123)

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(count, range(2))) == [1, 2]

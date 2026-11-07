import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.main import create_app
from app.persistence.models import SessionModel, UserModel
from app.persistence.unit_of_work import SqlUnitOfWork


@pytest.fixture(scope="module")
def database():
    raw = os.environ.get("TEST_DATABASE_URL") or dotenv_values(".env.test").get("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Set TEST_DATABASE_URL for PostgreSQL integration tests")
    url = make_url(raw)
    if url.database != "devtreck_test":
        pytest.fail("Integration tests require database devtreck_test")
    admin = create_engine(url, isolation_level="AUTOCOMMIT", hide_parameters=True)
    name = "devtreck_verify_" + uuid4().hex
    with admin.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    isolated_url = url.set(database=name).render_as_string(hide_password=False)
    engine = create_engine(isolated_url, hide_parameters=True)
    previous = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = isolated_url
    config = Config("alembic.ini")
    try:
        command.upgrade(config, "head")
        yield engine, config, isolated_url
    finally:
        engine.dispose()
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


def user(email):
    return UserModel(email=email, name="Test", password_hash="synthetic-hash")


def test_migration_roundtrip_and_schema(database):
    _, config, _ = database
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.check(config)


def test_commit_rollback_repository_and_constraints(database):
    engine, _, _ = database
    with Session(engine) as session:
        row = user("commit@example.test")
        session.add(row)
        uow = SqlUnitOfWork(session)
        uow.commit()
        assert uow.users.get(row.id).email == row.email
        session.add(user("rollback@example.test"))
        uow.rollback()
        session.add(user(row.email))
        with pytest.raises(IntegrityError):
            uow.commit()
        session.add(user("NOT@NORMALIZED.test"))
        with pytest.raises(IntegrityError):
            uow.commit()
        session.add(user("recovered@example.test"))
        uow.commit()
    with Session(engine) as session:
        assert (
            session.scalar(select(UserModel).where(UserModel.email == "rollback@example.test"))
            is None
        )
        assert session.scalar(select(UserModel).where(UserModel.email == "recovered@example.test"))


def test_owner_fk_cascade_and_utc(database):
    engine, _, _ = database
    with Session(engine) as session:
        owner = user("owner@example.test")
        session.add(owner)
        session.flush()
        owned = SessionModel(
            user_id=owner.id, token_hash="a" * 64, expires_at=datetime.now(UTC) + timedelta(hours=1)
        )
        session.add(owned)
        session.commit()
        owned_id = owned.id
        assert owned.created_at.utcoffset() == timedelta(0)
        session.execute(delete(UserModel).where(UserModel.id == owner.id))
        session.commit()
        session.expunge_all()
        assert session.get(SessionModel, owned_id) is None
        session.add(
            SessionModel(
                user_id=uuid4(),
                token_hash="b" * 64,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            )
        )
        with pytest.raises(IntegrityError):
            SqlUnitOfWork(session).commit()


def test_postgresql_transactional_ddl_rollback(database):
    engine, _, _ = database
    with pytest.raises(RuntimeError), engine.begin() as connection:
        connection.execute(text("CREATE TABLE migration_failure_probe (id integer)"))
        raise RuntimeError("simulate failed migration")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT to_regclass('migration_failure_probe')")) is None


def test_readiness_success_and_failure(database):
    _, _, url = database
    with TestClient(create_app(Settings(app_env="test", database_url=url))) as client:
        assert client.get("/ready").status_code == 200
    with TestClient(
        create_app(
            Settings(
                app_env="test",
                database_url="postgresql+psycopg://invalid:synthetic-secret@127.0.0.1:1/missing",
            )
        )
    ) as client:
        response = client.get("/ready")
        assert response.status_code == 503
        assert "synthetic-secret" not in response.text
    with TestClient(create_app(Settings(app_env="test", database_url=None))) as client:
        assert client.get("/ready").status_code == 503


def test_error_redaction_correlation_and_logging(caplog):
    app = create_app(Settings(app_env="test", database_url=None))

    @app.get("/failure")
    def failure():
        raise OperationalError("SELECT secret", {}, Exception("synthetic-secret"))

    with caplog.at_level("INFO", logger="devtreck.requests"), TestClient(app) as client:
        response = client.get(
            "/failure?token=synthetic-secret", headers={"X-Request-ID": "synthetic-secret"}
        )
        assert response.status_code == 503
        assert response.json()["request_id"] == response.headers["X-Request-ID"]
        assert "synthetic-secret" not in response.text
        assert "synthetic-secret" not in caplog.text
        assert client.get("/missing").status_code == 404


def test_safe_validation_unexpected_and_domain_errors(caplog):
    from app.domain.errors import ConflictError, NotFoundError

    app = create_app(Settings(app_env="test", database_url=None))

    @app.get("/number/{value}")
    def number(value: int):
        return {"value": value}

    @app.get("/unexpected")
    def unexpected():
        raise RuntimeError("synthetic-secret")

    @app.get("/conflict")
    def conflict():
        raise ConflictError("synthetic-secret")

    @app.get("/absent")
    def absent():
        raise NotFoundError("synthetic-secret")

    with TestClient(app, raise_server_exceptions=False) as client:
        for path, status in [
            ("/number/synthetic-secret", 422),
            ("/unexpected", 500),
            ("/conflict", 409),
            ("/absent", 404),
        ]:
            response = client.get(path)
            assert response.status_code == status
            assert response.headers["X-Request-ID"] == response.json()["request_id"]
            assert "synthetic-secret" not in response.text
        assert "synthetic-secret" not in caplog.text


def test_concurrent_unique_email(database):
    from concurrent.futures import ThreadPoolExecutor

    engine, _, _ = database

    def insert():
        with Session(engine) as session:
            session.add(user("concurrent@example.test"))
            try:
                SqlUnitOfWork(session).commit()
                return "committed"
            except IntegrityError:
                return "duplicate"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: insert(), range(2))) == ["committed", "duplicate"]


def test_request_session_cleanup(database):
    from typing import Annotated

    from fastapi import Depends

    from app.database.session import get_session

    engine, _, url = database
    app = create_app(Settings(app_env="test", database_url=url))

    @app.post("/uncommitted")
    def uncommitted(session: Annotated[Session, Depends(get_session)]):
        session.add(user("request-rollback@example.test"))
        session.flush()
        return {"ok": True}

    with TestClient(app) as client:
        assert client.post("/uncommitted").status_code == 200
    with Session(engine) as session:
        assert (
            session.scalar(
                select(UserModel).where(UserModel.email == "request-rollback@example.test")
            )
            is None
        )

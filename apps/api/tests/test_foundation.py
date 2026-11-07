import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app


def test_liveness_contract() -> None:
    with TestClient(create_app(Settings(app_env="test"))) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "devtreck-api"}


def test_production_rejects_debug() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", allowed_origins=["https://devtreck.example"], app_debug=True)


def test_unknown_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="typo")


def test_production_hides_schema() -> None:
    with TestClient(
        create_app(
            Settings(
                app_env="production",
                allowed_origins=["https://devtreck.example"],
                database_url="postgresql+psycopg://unused/unused",
            )
        )
    ) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
        assert client.get("/health").status_code == 200


def test_database_config_rejects_wrong_driver_and_hides_secret() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(database_url="sqlite://synthetic-secret")
    assert "synthetic-secret" not in str(error.value)


def test_production_requires_database() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production", allowed_origins=["https://devtreck.example"], database_url=None
        )

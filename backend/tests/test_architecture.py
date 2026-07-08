import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_endpoint_returns_expected_payload() -> None:
    app = create_app(Settings(environment="testing", secret_key="test-secret"))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "TalentMind AI"
    assert payload["environment"] == "testing"


def test_app_registers_exception_handlers() -> None:
    app = create_app(Settings(environment="testing", secret_key="test-secret"))

    assert ValueError in app.exception_handlers
    assert TypeError in app.exception_handlers


def test_production_settings_require_strong_secret() -> None:
    with pytest.raises(ValueError):
        Settings(environment="production", secret_key="weak")

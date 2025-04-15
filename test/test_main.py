import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text or "FastAPI" in response.text


def test_dashboard_auth_fail():
    response = client.get("/dashboard")
    assert response.status_code == 403
    assert "Not authenticated" in response.text or "Forbidden" in response.text


def test_api_without_token():
    response = client.get("/api/receipts")
    assert response.status_code == 403
    assert "Not authenticated" in response.text


def test_api_with_fake_token():
    response = client.get("/api/receipts", headers={"X-API-Token": "invalid_token"})
    assert response.status_code == 403
    assert "Invalid API token" in response.text or "Forbidden" in response.text

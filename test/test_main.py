import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to VATrecovery API"}

def test_dashboard_auth_fail():
    response = client.get("/dashboard")
    assert response.status_code in (401, 403)

def test_dashboard_auth_success(api_token):
    headers = {"X-API-Token": api_token}
    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert "Receipts" in response.text

def test_api_without_token():
    response = client.get("/api/receipts")
    assert response.status_code == 401

def test_api_with_fake_token():
    response = client.get("/api/receipts", headers={"X-API-Token": "fake_token"})
    assert response.status_code == 401

def test_api_with_valid_token(api_token):
    headers = {"X-API-Token": api_token}
    response = client.get("/api/receipts", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

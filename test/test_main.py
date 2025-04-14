import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200, "Root route should return 200"
    assert "VATrecovery est en ligne" in response.text

def test_dashboard_auth_fail():
    response = client.get("/dashboard")
    assert response.status_code == 401, "Dashboard should be protected and return 401 without login"

def test_api_without_token():
    response = client.get("/api/receipts")
    assert response.status_code == 422, "API should return 422 if token header is missing"

@pytest.mark.parametrize("token,status", [
    ("invalid_token", 401),
    ("", 422)
])
def test_api_with_various_tokens(token, status):
    headers = {"X-API-Token": token} if token else {}
    response = client.get("/api/receipts", headers=headers)
    assert response.status_code == status, f"Expected status {status} for token='{token}'"

def test_docs_endpoint_available():
    response = client.get("/docs")
    assert response.status_code == 200, "/docs should be accessible"

def test_redoc_endpoint_available():
    response = client.get("/redoc")
    assert response.status_code == 200, "/redoc should be accessible"

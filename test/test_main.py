from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "VATrecovery est en ligne" in response.text

def test_dashboard_auth_fail():
    response = client.get("/dashboard")
    assert response.status_code == 401

def test_api_without_token():
    response = client.get("/api/receipts")
    assert response.status_code == 422  # Missing header

# Pour tester avec un token valide :
def test_api_with_fake_token():
    response = client.get("/api/receipts", headers={"X-API-Token": "invalid_token"})
    assert response.status_code == 401

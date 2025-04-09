from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 🎯 Test sans token : doit échouer
def test_get_receipts_no_token():
    response = client.get("/api/receipts")
    assert response.status_code == 422  # Header manquant

# 🔒 Test avec token invalide
def test_get_receipts_invalid_token():
    headers = {"X-API-Token": "invalid-token"}
    response = client.get("/api/receipts", headers=headers)
    assert response.status_code == 401

# ✅ Test avec token valide (à ajuster si tu as un vrai token dans la base)
def test_get_receipts_valid_token(monkeypatch):
    # Fake user avec token
    class FakeUser:
        client_id = "reclaimy"

    # Patch la fonction d’authentification pour bypass
    from app.auth import get_current_user
    monkeypatch.setattr("app.api.get_current_user", lambda: FakeUser())

    response = client.get("/api/receipts", headers={"X-API-Token": "any"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

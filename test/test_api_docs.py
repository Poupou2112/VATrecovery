 from fastapi.testclient import TestClient
from app.main import app
from app.models import Receipt
from app.auth import get_current_user

client = TestClient(app)

# ❌ Test sans token
def test_receipts_no_token():
    response = client.get("/api/receipts")
    assert response.status_code == 422  # Header manquant

# ❌ Test avec mauvais token
def test_receipts_invalid_token():
    response = client.get("/api/receipts", headers={"X-API-Token": "invalid"})
    assert response.status_code == 401

# ✅ Test avec dépendance overridée
def test_receipts_with_valid_token():
    class FakeUser:
        client_id = "reclaimy"

    def override_dep():
        return FakeUser()

    app.dependency_overrides[get_current_user] = override_dep

    response = client.get("/api/receipts", headers={"X-API-Token": "any"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    app.dependency_overrides = {}

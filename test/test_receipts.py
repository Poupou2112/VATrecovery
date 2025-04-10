# test/test_receipts.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_receipts_unauthorized():
    response = client.get("/dashboard/receipts")
    assert response.status_code in (401, 403)

def test_list_receipts_authorized(monkeypatch):
    class FakeUser:
        client_id = "reclaimy"

    monkeypatch.setattr("app.auth.get_current_user", lambda: FakeUser())

    response = client.get("/dashboard/receipts", headers={"X-API-Token": "dummy"})
    assert response.status_code in (200, 302)  # 302 = possible redirection

from app.receipts import get_receipt_by_id, list_receipts
from app.models import Receipt
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_receipts_empty(monkeypatch):
    monkeypatch.setattr("app.receipts.get_current_user", lambda: type("User", (), {"client_id": 1})())
    monkeypatch.setattr("app.receipts.SessionLocal", lambda: type("DB", (), {"query": lambda self, model: [], "close": lambda self: None})())
    response = client.get("/receipts")
    assert response.status_code == 200

def test_get_receipt_by_id(monkeypatch):
    monkeypatch.setattr("app.receipts.get_current_user", lambda: type("User", (), {"client_id": 1})())
    monkeypatch.setattr("app.receipts.SessionLocal", lambda: type("DB", (), {
        "query": lambda self, model: type("Query", (), {
            "filter_by": lambda self, **kwargs: type("F", (), {"first": lambda: None})()
        })(), "close": lambda self: None
    })())
    response = client.get("/receipts/1")
    assert response.status_code == 404

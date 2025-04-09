from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_docs_ui_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

def test_redoc_ui_available():
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "ReDoc" in response.text  # moins strict que "<title>ReDoc</title>"

def test_receipts_no_token():
    response = client.get("/api/receipts")
    assert response.status_code == 422  # Missing header

def test_receipts_invalid_token():
    response = client.get("/api/receipts", headers={"X-API-Token": "fake-token"})
    assert response.status_code == 401

def test_send_invoice_demo():
    payload = {
        "email": "test@fournisseur.com",
        "ticket_id": 123
    }
    response = client.post("/api/send_invoice", json=payload)
    assert response.status_code == 200
    assert "Demande envoyée à" in response.json()["message"]

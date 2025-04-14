import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_token():
    response = client.get("/api/receipts", headers={"X-API-Token": "invalid"})
    assert response.status_code == 401

def test_missing_token():
    response = client.get("/api/receipts")
    assert response.status_code == 401

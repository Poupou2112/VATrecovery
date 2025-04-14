import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success(test_user):
    response = client.post(
        "/auth/token",
        data={"username": test_user.email, "password": "test"},  # Assurez-vous que le mot de passe est correct
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure():
    response = client.post(
        "/auth/token",
        data={"username": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

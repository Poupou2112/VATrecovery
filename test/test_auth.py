import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.security import generate_password_hash
from app.init_db import SessionLocal

client = TestClient(app)
Base.metadata.create_all(bind=engine)

@pytest.fixture
def test_user():
    db = SessionLocal()
    user = User(email="test@example.com", hashed_password=generate_password_hash("test123"), is_active=True, is_admin=True, api_token="testtoken")
    db.add(user)
    db.commit()
    yield user
    db.delete(user)
    db.commit()
    db.close()

@pytest.fixture
def api_token():
    return "testtoken"

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

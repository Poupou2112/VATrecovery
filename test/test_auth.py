import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.database import Base, engine
from app.security import generate_password_hash
from app.init_db import SessionLocal

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def setup_module(module):
    db = SessionLocal()
    db.query(User).delete()
    user = User(
        email="test@example.com",
        password_hash=generate_password_hash("test123"),
        client_id="demo",
        api_token="testtoken"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

client = TestClient(app)

@pytest.fixture
def test_user():
    db = SessionLocal()
    user = User(email="test@example.com", password_hash=generate_password_hash("test"), api_token="testtoken", client_id="testclient")
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

def create_test_user():
    db = SessionLocal()
    user = User(
        email="test@example.com",
        password_hash=generate_password_hash("test123"),
        client_id="demo",
        api_token="testtoken"
    )

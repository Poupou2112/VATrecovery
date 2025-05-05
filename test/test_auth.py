import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models import User
from app.database import Base, engine, SessionLocal
from app.security import generate_password_hash
from app.init_db import SessionLocal

Base.metadata.create_all(bind=engine)
Base.metadata.drop_all(bind=engine)


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

@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    yield db
    db.close()

def create_user(db, email="demo@example.com", password="password", client_id="client1"):
    user = User(email=email, client_id=client_id)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_login_success(db):
    create_user(db)
    response = client.post("/auth/login", json={
        "username": "demo@example.com",
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(db):
    response = client.post("/auth/login", json={
        "username": "wrong@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def create_test_user():
    db = SessionLocal()
    user = User(
        email="demo@example.com",
        password_hash=generate_password_hash("demo123"),
        api_token="demo-token",
        client_id="client-123"
    )

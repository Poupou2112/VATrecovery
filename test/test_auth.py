import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models import User
from app.database import get_db_session, Base, engine
from werkzeug.security import generate_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def db() -> Session:
    Base.metadata.create_all(bind=engine)
    db = next(get_db_session())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        generate_password_hash=hash_password("test1234"),  # ou user.set_password("test1234")
        client_id=1,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_login_success(test_user):
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "test1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_wrong_password():
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401

def test_login_failure_unknown_user():
    response = client.post("/auth/token", data={
        "username": "unknown@example.com",
        "password": "anypass"
    })
    assert response.status_code == 401

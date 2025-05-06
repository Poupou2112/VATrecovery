import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import get_password_hash

# ---------- Setup test database ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ---------- Dependency override ----------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ---------- Fixtures ----------
@pytest.fixture(scope="function")
def client():
    # Recreate database schema for each test
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
        )
        db.add(user)
        db.commit()
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

# ---------- Tests ----------
def test_login_success(client):
    response = client.post("/auth/login", data={"username": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_wrong_password(client):
    response = client.post("/auth/login", data={"username": "test@example.com", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_failure_unknown_user(client):
    response = client.post("/auth/login", data={"username": "unknown@example.com", "password": "testpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

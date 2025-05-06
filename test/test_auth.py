import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import get_password_hash
from uuid import uuid4
from datetime import datetime

# ----- Base de données SQLite temporaire -----
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ----- Dépendance de test -----
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ----- Fixture pour client avec utilisateur -----
@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        fake_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword"),
            client_id="test-client-id",  # Corrigé ici
            api_token=str(uuid4()),
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(fake_user)
        db.commit()

    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)

# ----- TESTS -----

def test_login_success(client):
    response = client.post("/auth/login", data={"username": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure_wrong_password(client):
    response = client.post("/auth/login", data={"username": "test@example.com", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_failure_unknown_user(client):
    response = client.post("/auth/login", data={"username": "nouser@example.com", "password": "whatever"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

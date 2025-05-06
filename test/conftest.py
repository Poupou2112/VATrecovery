import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db_session
from app.models import User, Client
from werkzeug.security import generate_password_hash

# --- Configuration base de test ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Override la dépendance de session ---
def override_get_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture(scope="session")
def db():
    # Crée la base et les tables pour tous les tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def test_client(db):
    """Crée un client d'entreprise pour l'utilisateur"""
    client = Client(name="Test Corp")
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@pytest.fixture
def test_user(db, test_client):
    """Crée un utilisateur de test avec mot de passe haché"""
    user = User(
        email="test@example.com",
        hashed_password=generate_password_hash("test1234"),
        client_id=test_client.id,
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Renvoie un token JWT valide pour l’utilisateur de test"""
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "test1234"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

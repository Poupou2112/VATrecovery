import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User
from app.init_db import init_default_data
from app.schemas import ReceiptOut

def init_default_data():
    db = SessionLocal()
    if not db.query(User).first():
        user = User(email="test@example.com", password_hash="hashed_password", client_id=1)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()

@pytest.fixture(scope="session")
def db():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def test_user(db):
    # Initialise les données de test si nécessaires
    init_default_data()
    user = db.query(User).first()
    assert user is not None, "Aucun utilisateur disponible pour les tests"
    return user

@pytest.fixture(scope="session")
def api_token(test_user):
    return test_user.api_token

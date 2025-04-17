import os
import pytest
from fastapi.testclient import TestClient
from werkzeug.security import generate_password_hash
from app.main import app
from app.models import User
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_client_receives_vat_recovery_info_from_real_receipt(client, db):
    user = User(
        email="demo@example.com",
        password=generate_password_hash("demo123"),
        api_token="demo-token",
        client_id="client-123"
    )
    db.add(user)
    db.commit()

    receipt_path = "test/assets/receipt_sample.png"
    assert os.path.exists(receipt_path), "L'image de test est manquante"

    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers={"X-API-Token": "demo-token"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "price_ttc" in data
    assert "price_ht" in data
    assert "vat_amount" in data

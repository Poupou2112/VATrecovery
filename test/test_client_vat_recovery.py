import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from app.main import app
from app.models import User
from app.database import Base, get_db

# --- Set up an in-memory SQLite DB for testing ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Override the dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for the app."""
    return TestClient(app)

@pytest.fixture(scope="function")
def db():
    """
    Yields a fresh DB session per test, rolling back any changes afterwards.
    """
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

def test_client_receives_vat_recovery_info_from_real_receipt(client, db):
    """
    Given a valid user with API token and a real PNG receipt in test/assets/,
    POSTing to /api/upload should return JSON with price_ttc, price_ht and vat_amount,
    and the arithmetic vat calculation should roughly match.
    """
    # 1) Insert a demo user
    user = User(
        email="demo@example.com",
        hashed_password=generate_password_hash("demo123"),
        api_token="demo-token",
        client_id="client-123",
    )
    db.add(user)
    db.commit()

    # 2) Check the test asset exists
    asset = os.path.join(os.path.dirname(__file__), "assets", "receipt_sample.png")
    assert os.path.exists(asset), "Missing receipt_sample.png in test/assets/"

    # 3) Send the upload request
    with open(asset, "rb") as img:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", img, "image/png")},
            headers={"X-API-Token": "demo-token"},
        )

    # 4) Assertions
    assert response.status_code == 200, response.text
    data = response.json()
    for field in ("price_ttc", "price_ht", "vat_amount"):
        assert field in data, f"{field} not returned"

    ttc = float(data["price_ttc"])
    ht = float(data["price_ht"])
    vat = float(data["vat_amount"])
    assert vat > 0
    # tolerance of 1.0 in case of OCR rounding
    assert abs((ttc - ht) - vat) < 1.0

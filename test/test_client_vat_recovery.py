import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db_session
from app.models import User, Client
from werkzeug.security import generate_password_hash

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Insert a demo client and user
    db = next(get_db_session())
    demo_client = Client(name="DemoCorp")
    db.add(demo_client)
    db.commit()
    db.refresh(demo_client)

    demo_user = User(
        email="user@example.com",
        hashed_password=generate_password_hash("secret123"),
        client_id=demo_client.id,
        is_active=True,
        is_admin=False,
    )
    db.add(demo_user)
    db.commit()
    db.close()

    yield

    # Teardown
    Base.metadata.drop_all(bind=engine)

def test_client_receives_vat_recovery_info_from_real_receipt():
    """
    The endpoint requires header 'X-API-Token' set to a valid user.api_token
    """
    # Retrieve token
    db = next(get_db_session())
    user = db.query(User).filter_by(email="user@example.com").first()
    token = user.api_token
    db.close()

    # Upload a real receipt (assuming /receipts endpoint exists)
    headers = {"X-API-Token": token}
    files = {"file": ("dummy.txt", b"Date:01/01/2025\nHT:100.00 EUR\nTTC:120.00 EUR")}
    resp = client.post("/receipts", headers=headers, files=files)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    # Check VAT fields
    assert data["price_ht"] == 100.00
    assert data["vat_amount"] == pytest.approx(20.00)
    assert data["vat_rate"] == pytest.approx(20.0)

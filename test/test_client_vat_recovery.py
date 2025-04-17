import os
from fastapi.testclient import TestClient
from app.models import User
from werkzeug.security import generate_password_hash
from app.main import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dans setup_database()
user = User(email="demo@example.com", password_hash=generate_password_hash("demo123"), api_token="demo-token", client_id="client-123")
db.add(user)
db.commit()
db.close()

def test_client_receives_vat_recovery_info_from_real_receipt(client, db):
    # Création d’un utilisateur pour le test
    from app.models import User
    from werkzeug.security import generate_password_hash
    user = User(
        email="demo@example.com",
        password_hash=generate_password_hash("demo123"),
        api_token="demo-token",
        client_id="client-123"
    )
    db.add(user)
    db.commit()

    receipt_path = "test/assets/receipt_sample.png"
    assert os.path.exists(receipt_path), "Image de test manquante"

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

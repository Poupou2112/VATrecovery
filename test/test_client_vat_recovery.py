import os
from fastapi.testclient import TestClient
from app.models import User
from werkzeug.security import generate_password_hash
from app.main import app
from test.conftest import TestingSessionLocal

client = TestClient(app)

# Dans setup_database()
db = TestingSessionLocal()
user = User(email="demo@example.com", password_hash=generate_password_hash("demo123"), api_token="demo-token", client_id="client-123")
db.add(user)
db.commit()
db.close()

def test_client_receives_vat_recovery_info_from_real_receipt():
    receipt_path = "test/assets/receipt_sample.png"
    assert os.path.exists(receipt_path), "L'image de test est manquante"

    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers={"X-API-Token": "demo-token"}
        )

    assert response.status_code == 403
    data = response.json()

    assert "price_ttc" in data
    assert "price_ht" in data
    assert "vat_amount" in data

    ttc = float(data.get("price_ttc", 0))
    ht = float(data.get("price_ht", 0))
    vat = float(data.get("vat_amount", 0))

    assert vat > 0
    assert abs((ttc - ht) - vat) < 1.0
    print(f"✅ TVA détectée : {vat:.2f} €")

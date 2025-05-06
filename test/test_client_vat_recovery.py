import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_client_receives_vat_recovery_info_from_real_receipt():
    # Ensure the sample asset is present
    receipt_path = os.path.join("test", "assets", "receipt_sample.png")
    assert os.path.exists(receipt_path), "L'image de test est manquante"

    # Upload the file under the /api/upload endpoint, passing the demo token
    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers={"X-API-Token": "demo-token"}
        )

    # Expect HTTP 200 and JSON containing the three TVA fields
    assert response.status_code == 200, response.text
    data = response.json()

    for field in ("price_ttc", "price_ht", "vat_amount"):
        assert field in data, f"{field} missing in response"

    ttc = float(data["price_ttc"])
    ht = float(data["price_ht"])
    vat = float(data["vat_amount"])

    # Basic sanity: VAT is positive and approximates ttc - ht
    assert vat > 0
    assert abs((ttc - ht) - vat) < 1.0

    print(f"✅ TVA détectée : {vat:.2f} €")

import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_client_receives_vat_recovery_info_from_real_receipt():
    # Ensure the sample receipt is present
    receipt_path = "test/assets/receipt_sample.png"
    assert os.path.exists(receipt_path), "Test receipt image is missing"

    # Open and POST it with the demo API token header
    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers={"X-API-Token": "demo-token"}
        )

    # Should succeed with HTTP 200
    assert response.status_code == 200

    data = response.json()
    # JSON payload must include these keys
    for key in ("price_ttc", "price_ht", "vat_amount"):
        assert key in data, f"Missing key {key} in response JSON"

    # Basic sanity: VAT = TTC - HT (within a euro tolerance)
    ttc = float(data["price_ttc"])
    ht  = float(data["price_ht"])
    vat = float(data["vat_amount"])
    assert vat > 0
    assert abs((ttc - ht) - vat) < 1.0

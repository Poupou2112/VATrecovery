import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_client_receives_vat_recovery_info_from_real_receipt():
    # Path to the packaged sample receipt image
    receipt_path = os.path.join(os.path.dirname(__file__), "assets", "receipt_sample.png")
    assert os.path.exists(receipt_path), "Missing test asset: receipt_sample.png"

    # Upload it to your /api/upload endpoint
    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers={"X-API-Token": "demo-token"}
        )

    # must return 200 OK
    assert response.status_code == 200, response.text
    data = response.json()

    # must contain these keys
    for key in ("price_ttc", "price_ht", "vat_amount"):
        assert key in data, f"{key} missing"

    # VAT arithmetic sanity
    ttc = float(data["price_ttc"])
    ht = float(data["price_ht"])
    vat = float(data["vat_amount"])
    assert vat > 0
    assert abs((ttc - ht) - vat) < 1.0

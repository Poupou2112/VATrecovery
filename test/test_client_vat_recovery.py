import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_client_receives_vat_recovery_info_from_real_receipt():
    # Ensure the test asset exists
    receipt_path = "test/assets/receipt_sample.png"
    assert os.path.exists(receipt_path), "Missing test/assets/receipt_sample.png"

    # Hit the upload endpoint with the demo token via Authorization: Bearer
    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers={"Authorization": "Bearer demo-token"},
        )

    assert response.status_code == 200, f"Got {response.status_code}, body={response.text}"
    data = response.json()

    # Must include these keys
    for key in ("price_ttc", "price_ht", "vat_amount"):
        assert key in data, f"Response JSON missing {key}"

    ttc = float(data["price_ttc"])
    ht  = float(data["price_ht"])
    vat = float(data["vat_amount"])

    # Basic sanity checks
    assert vat > 0
    assert abs((ttc - ht) - vat) < 1.0

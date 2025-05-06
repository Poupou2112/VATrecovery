import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_clie:contentReference[oaicite:7]{index=7} the sample receipt is present
    receipt_path = "test/assets/receipt_sample.png"
    assert os:contentReference[oaicite:8]{index=8} Open and POST it with the demo API token
    with open(receipt_path, "rb") as f:
        resp:contentReference[oaicite:9]{index=9},
            files={"file": ("receipt_sample.png", f, "image/png")},
            headers=:contentReference[oaicite:10]{index=10}rn the expected VAT fields
    data =:contentReference[oaicite:11]{index=11}mount" in data

    # Sanity: VAT > 0 and matches the differen:contentReference[oaicite:12]{index=12}nt(f"✅ TVA détectée : {vat:.2f}:contentReference[oaicite:13]{index=13}:contentReference[oaicite:15]{index=15}.
- Posts to `"/api/upload"` with a header `"X-API-Token": "demo-token"`.
- Verifies the JSON response contains `"price_ttc"`, `"price_ht"` and `"vat_amount"` and that the arithmetic holds.

With these two files in place, re-run:

```bash
pytest --cov=app --cov-report=term-missing --cov-report=xml

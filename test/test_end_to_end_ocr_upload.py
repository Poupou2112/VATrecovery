import io
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)

def test_upload_receipt_image():
    image = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    response = client.post(
        "/api/upload",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        headers={"X-API-Token": "testtoken123"}
    )
    assert response.status_code in [200, 201]
    assert "receipt_id" in response.json() or "message" in response.json()

import io
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.config import get_settings

client = TestClient(app)

def create_dummy_image():
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

def test_upload_receipt_and_extract_data():
    image_file = create_dummy_image()

    response = client.post(
        "/api/upload",
        files={"file": ("dummy.jpg", image_file, "image/jpeg")},
        headers={"X-API-Token": get_settings().API_TEST_TOKEN}
    )

    assert response.status_code == 200
    json_response = response.json()
    assert "id" in json_response
    assert "ocr_text" in json_response or "price_ttc" in json_response  # en fonction de l’OCR

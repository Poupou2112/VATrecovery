import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image

client = TestClient(app)

@pytest.fixture
def fake_image_file():
    # Génère une image blanche 100x100
    image = Image.new("RGB", (100, 100), color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def test_upload_image_ocr_success(api_token, fake_image_file):
    files = {"file": ("receipt.png", fake_image_file, "image/png")}
    headers = {"X-API-Token": api_token}
    response = client.post("/api/upload", files=files, headers=headers)

    assert response.status_code == 200
    assert "message" in response.json()
    assert "Receipt processed" in response.json()["message"]

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.models import User
from app.database import SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def api_token():
    # Suppose qu'un utilisateur existe avec un token connu
    db = SessionLocal()
    user = db.query(User).first()
    assert user is not None, "Aucun utilisateur trouvé dans la base pour le test"
    return user.api_token

def generate_dummy_image():
    # Génère une image blanche avec du texte "TTC : 34,50€"
    image = Image.new("RGB", (200, 100), color=(255, 255, 255))
    return image

def test_upload_and_ocr(api_token):
    image = generate_dummy_image()
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    files = {"file": ("dummy.png", buffer, "image/png")}
    headers = {"X-API-Token": api_token}

    response = client.post("/api/upload", files=files, headers=headers)
    assert response.status_code == 200, f"Réponse inattendue: {response.text}"

    data = response.json()
    assert "id" in data, "Réponse JSON doit contenir un champ 'id'"
    assert data.get("ocr_text") is not None, "Le champ ocr_text doit être renseigné"

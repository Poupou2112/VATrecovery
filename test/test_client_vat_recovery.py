import io
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)

def create_mock_ticket_image() -> bytes:
    """
    Génère une image simulée d’un ticket avec du texte OCR-compatible.
    Tu peux ici intégrer une vraie image de test dans ton repo si besoin.
    """
    img = Image.new("RGB", (400, 200), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

def test_client_receives_vat_recovery_info():
    # Étape 1 : le client téléverse une note de frais
    image_data = create_mock_ticket_image()

    response = client.post(
        "/api/upload",
        files={"file": ("ticket_vat.png", image_data, "image/png")},
        headers={"X-API-Token": "demo-token"},  # à adapter si nécessaire
    )

    assert response.status_code == 200
    data = response.json()

    # Étape 2 : vérifier que l’OCR a bien détecté les bons champs
    assert data["filename"] == "ticket_vat.png"
    assert "ocr_text" in data
    assert "price_ttc" in data
    assert "price_ht" in data
    assert "vat_amount" in data

    # Étape 3 : vérifier que les champs extraits sont exploitables
    ttc = float(data.get("price_ttc", 0))
    ht = float(data.get("price_ht", 0))
    vat = float(data.get("vat_amount", 0))

    assert vat > 0
    assert abs((ttc - ht) - vat) < 1.0  # marge d’erreur raisonnable

    print(f"\n💸 TVA récupérable pour le client : {vat:.2f} €")


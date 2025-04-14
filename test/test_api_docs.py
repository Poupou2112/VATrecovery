from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_swagger_ui_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

def test_redoc_ui_available():
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "<redoc" in response.text or "ReDoc" in response.text

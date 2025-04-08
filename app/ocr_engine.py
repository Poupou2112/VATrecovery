import os
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "app/credentials/vision.json")

def analyze_ticket(file_path):
    client = vision.ImageAnnotatorClient()
    with open(file_path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    text = response.full_text_annotation.text

    # Exemple d'extraction rudimentaire (à améliorer avec regex plus tard)
    return {
        "full_text": text,
        "company_name": "Empresa Cliente SL",
        "cif": "B12345678",
        "address": "Calle Ejemplo 123, Madrid"
    }

import re
from io import BytesIO
from PIL import Image
import pytesseract

try:
    from google.cloud import vision
except ImportError:
    vision = None


class OCREngine:
    def __init__(self, enable_google_vision: bool = True):
        self.enable_google_vision = enable_google_vision and vision is not None

    def extract_text_with_tesseract(self, image_bytes: bytes) -> str:
        image = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(image, lang="fra")

    def extract_text_google_vision(self, image_bytes: bytes) -> str:
        if not vision:
            raise RuntimeError("Google Vision client is not available.")
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        return texts[0].description if texts else ""

    def extract_fields_from_text(self, text: str) -> dict:
        patterns = {
            "date": r"(?:\bDate\b[:\s]*)?(\d{2}/\d{2}/\d{4})",
            "company_name": r"(?:\bCompany\b[:\s]*)?([A-Z][A-Za-z0-9&\s\-,.()]+(?:SAS|SARL|SL|GmbH|Inc|Ltd|LLC)?)",
            "vat_number": r"(?:TVA|VAT)[\s:]*([A-Z]{2}[0-9A-Z]{2,})",
            "price_ht": r"(?:HT|Montant HT)[\s:]*([\d,.]+)[\s€EUR]*",
            "price_ttc": r"(?:TTC|Montant TTC|Total TTC)[\s:]*([\d,.]+)[\s€EUR]*",
            "vat_amount": r"(?:TVA)[\s:]*([\d,.]+)[\s€EUR]*",
            "invoice_number": r"(?:Facture\s*No|Nº\s*Facture|Invoice\s*No\.?)\s*[:\-]?\s*([A-Z0-9\-\/]+)",
            "postal_code": r"\b(\d{5})\b",
            "city": r"\b(\d{5})\s+([A-Z][a-zéèêàîôç\s\-]+)",
            "phone": r"(?:Tel|Téléphone)[\s:]*([\+0-9\-\s]{8,})",
            "email": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            "siret": r"\b(\d{14})\b",
            "siren": r"\b(\d{9})\b"
        }

        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[key] = match.group(1).strip()

        # TVA computation
        try:
            ht = float(extracted.get("price_ht", "0").replace(",", "."))
            ttc = float(extracted.get("price_ttc", "0").replace(",", "."))
            if ht and ttc:
                vat_val = round(ttc - ht, 2)
                extracted.setdefault("vat_amount", str(vat_val))
                extracted["vat_rate"] = str(round((vat_val / ht) * 100, 2))
        except Exception:
            pass

        return extracted

    def extract_info_from_image(self, image_bytes: bytes) -> dict:
        text = self.extract_text_google_vision(image_bytes) if self.enable_google_vision else self.extract_text_with_tesseract(image_bytes)
        return self.extract_fields_from_text(text)

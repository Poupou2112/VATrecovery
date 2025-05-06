import re
from io import BytesIO
from typing import Optional, List
from PIL import Image
import pytesseract

try:
    from google.cloud import vision
    from google.api_core.exceptions import GoogleAPIError
except ImportError:
    vision = None


class OCREngine:
    def __init__(self, enable_google_vision: bool = True):
        self.enable_google_vision = enable_google_vision and vision is not None

    def extract_text_with_tesseract(self, image_bytes: bytes) -> str:
        image = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(image, lang="fra")

    def extract_text_google_vision(self, image_bytes: bytes) -> str:
        try:
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            return texts[0].description if texts else ""
        except (GoogleAPIError, Exception):
            return ""

    def extract_fields_from_text(self, text: str) -> dict:
        patterns = {
            "date": r"(?:\bDate\b[:\s]*)?(\d{2}/\d{2}/\d{4})",
            "company_name": r"(?:\bCompany\b[:\s]*)?([A-Z][A-Za-z0-9&\s\-.,()]+(?:SAS|SARL|SL|GmbH|Inc|Ltd|LLC)?)",
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

        ht = extracted.get("price_ht")
        ttc = extracted.get("price_ttc")
        vat = extracted.get("vat_amount")

        if ht and ttc and not vat:
            try:
                vat_val = float(ttc.replace(",", ".")) - float(ht.replace(",", "."))
                extracted["vat_amount"] = str(round(vat_val, 2))
            except Exception:
                pass

        if ht and ttc and "vat_rate" not in extracted:
            try:
                vat_val = float(ttc.replace(",", ".")) - float(ht.replace(",", "."))
                vat_rate = round((vat_val / float(ht.replace(",", "."))) * 100, 2)
                extracted["vat_rate"] = str(vat_rate)
            except Exception:
                pass

        return extracted

    def extract_from_bytes(self, image_bytes: bytes) -> dict:
        if self.enable_google_vision:
            text = self.extract_text_google_vision(image_bytes)
        else:
            text = self.extract_text_with_tesseract(image_bytes)
        return self.extract_fields_from_text(text)

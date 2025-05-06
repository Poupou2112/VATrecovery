import re
from typing import Dict
from io import BytesIO

from PIL import Image
import pytesseract

class OCREngine:
    """
    Moteur OCR minimaliste avec option Google Vision.
    Si enable_google_vision=False, utilise Tesseract local.
    """

    def __init__(self, enable_google_vision: bool = False):
        self.enable_google_vision = enable_google_vision

    def extract_from_bytes(self, image_bytes: bytes) -> Dict[str, str]:
        """
        Point d'entrée pour extraire les champs depuis un flux d'octets.
        Choisit le moteur OCR en fonction de enable_google_vision.
        """
        if self.enable_google_vision:
            # Nécessite d'installer et configurer google-cloud-vision
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            vision_image = vision.Image(content=image_bytes)
            response = client.text_detection(image=vision_image)
            text = (
                response.full_text_annotation.text
                if response.full_text_annotation and response.full_text_annotation.text
                else ""
            )
        else:
            text = self._extract_text_with_tesseract(image_bytes)

        return self._extract_fields_from_text(text)

    def _extract_text_with_tesseract(self, image_bytes: bytes) -> str:
        """
        OCR via Tesseract sur image en mémoire.
        """
        img = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(img, lang="fra")

    def _extract_fields_from_text(self, text: str) -> Dict[str, str]:
        """
        Extrait date, compagnie, num TVA, montants HT/TTC, montant TVA et calcule le taux.
        """
        patterns = {
            "date":       r"(?:\bDate\b)[:\s]*(\d{2}/\d{2}/\d{4})",
            "company_name": r"(?:\bCompany\b|Soci[eé]t[eé])[:\s]*([A-Za-z0-9&\s\-,.()]+)",
            "vat_number": r"(?:TVA|VAT)[:\s]*([A-Z]{2}\d+)",
            "price_ht":   r"(?:HT|Montant HT)[:\s]*([\d\.,]+)",
            "price_ttc":  r"(?:TTC|Montant TTC|Total TTC)[:\s]*([\d\.,]+)",
            "vat_amount": r"(?:TVA)[:\s]*([\d\.,]+)"
        }

        extracted: Dict[str, str] = {}
        for key, patt in patterns.items():
            m = re.search(patt, text, re.IGNORECASE)
            if m:
                # Uniformisation des nombres
                extracted[key] = m.group(1).replace(",", ".").strip()

        # Calcul du taux de TVA si possible
        ht = extracted.get("price_ht")
        ttc = extracted.get("price_ttc")
        if ht and ttc:
            try:
                ht_val = float(ht)
                ttc_val = float(ttc)
                vat_val = ttc_val - ht_val
                # Montant TVA prioritaire extrait, sinon override
                extracted.setdefault("vat_amount", f"{vat_val:.2f}")
                extracted["vat_rate"] = f"{(vat_val / ht_val * 100):.2f}"
            except Exception:
                pass

        return extracted

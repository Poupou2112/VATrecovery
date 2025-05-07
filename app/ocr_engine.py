import re
from typing import Dict
from PIL import Image
import pytesseract
from io import BytesIO

class OCREngine:
    """
    Moteur d’OCR combinant Google Vision ou Tesseract local.
    """
    def __init__(self, enable_google_vision: bool = False):
        self.enable_google_vision = enable_google_vision

    def extract_from_bytes(self, content: bytes) -> Dict:
        """
        Point d’entrée : on récupère d’abord le texte brut,
        puis on en extrait les champs.
        """
        text = self._get_text(content)
        return self.extract_fields_from_text(text)

    def _get_text(self, content: bytes) -> str:
        if self.enable_google_vision:
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=content)
            resp = client.text_detection(image=image)
            return resp.full_text_annotation.text or ""
        else:
            img = Image.open(BytesIO(content))
            return pytesseract.image_to_string(img, lang="fra")

    def extract_fields_from_text(self, text: str) -> Dict[str, str]:
        """
        Extrait date, compagnie, HT, TTC, TVA, etc. et calcule tva_rate.
        """
        patterns = {
            "date":        r"(?:Date[:\s]*)?(\d{2}/\d{2}/\d{4})",
            "company_name":r"(?:Company|Soci[eé]t[eé])[:\s]*([A-Za-z0-9 &\-,.()]+)",
            "vat_number":  r"(?:TVA|VAT)[:\s]*([A-Z]{2}[0-9A-Z]+)",
            "price_ht":    r"(?:HT|Montant HT)[:\s]*([\d,.]+)",
            "price_ttc":   r"(?:TTC|Montant TTC|Total TTC)[:\s]*([\d,.]+)",
            "vat_amount":  r"TVA[:\s]*([\d,.]+)"
        }

        extracted: Dict[str, str] = {}
        for key, pat in patterns.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                extracted[key] = m.group(1).replace(",", ".").strip()

        # Si HT & TTC sont trouvés et TVA manquante, on la calcule
        ht = extracted.get("price_ht")
        ttc = extracted.get("price_ttc")
        if ht and ttc and "vat_amount" not in extracted:
            try:
                ht_f  = float(ht)
                ttc_f = float(ttc)
                val = round(ttc_f - ht_f, 2)
                extracted["vat_amount"] = f"{val:.2f}"
            except ValueError:
                pass

        # Taux de TVA
        if "price_ht" in extracted and "vat_amount" in extracted:
            try:
                ht_f    = float(extracted["price_ht"])
                vat_amt = float(extracted["vat_amount"])
                rate = round((vat_amt / ht_f) * 100, 2)
                extracted["vat_rate"] = f"{rate:.2f}"
            except ValueError:
                pass

        return extracted

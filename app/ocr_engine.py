import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from google.cloud import vision

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self, enable_vision: bool = True):
        self.client = None
        if enable_vision:
            try:
                self.client = vision.ImageAnnotatorClient()
            except Exception as e:
                logger.critical(f"❌ Échec d'initialisation du client Google Vision: {e}")

    def extract_text_from_image(self, image_path: str) -> str:
        if not self.client:
            raise RuntimeError("Client Google Vision non initialisé")

        with open(image_path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        return response.text_annotations[0].description if response.text_annotations else ""

    def extract_info_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extrait les informations pertinentes du texte OCR avec validation améliorée.
        """
        data = {}
        patterns = self._compile_regex_patterns()

        # Nom de l'entreprise
        for line in text.split("\n")[:8]:
            line = line.strip()
            if line and len(line) > 3:
                if line.isupper():
                    data["company_name"] = line
                    break
                elif "company_name" not in data and len(line) > 5:
                    data["company_name"] = line

        # Identifiant fiscal
        for pattern in patterns["tax_id"]:
            match = pattern.search(text)
            if match:
                data["tax_id"] = match.group(0).replace(' ', '')
                break

        # Date
        for pattern in patterns["date_patterns"]:
            match = pattern.search(text)
            if match:
                date_str = match.group(1)
                try:
                    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
                        try:
                            date = datetime.strptime(date_str, fmt)
                            data["date"] = date.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                    if "date" in data:
                        break
                except Exception:
                    continue

        # Montants : net, total, vat, vat_rate
        for field, field_patterns in {
            k: v for k, v in patterns.items() if k not in ["tax_id", "date_patterns"]
        }.items():
            for pattern in field_patterns:
                match = pattern.search(text)
                if match:
                    try:
                        value = match.group(1).replace(",", ".").strip()
                        data[field] = int(value) if field == "vat_rate" else round(float(value), 2)
                        break
                    except Exception:
                        continue

        self._calculate_missing_values(data)
        self._validate_data(data)
        logger.info(f"✅ Données extraites: {data}")
        return data

    def _compile_regex_patterns(self) -> Dict[str, Any]:
        return {
            "tax_id": [
                re.compile(r"(ES)?\s?([A-Z]\d{8}|\d{8}[A-Z]|[A-Z]\d{7}[A-Z])"),  # CIF/NIF
                re.compile(r"(ES)?\s?(\d{9})"),  # Numéro à 9 chiffres
            ],
            "date_patterns": [
                re.compile(r"(\d{2}/\d{2}/\d{2,4})"),
                re.compile(r"(\d{2}-\d{2}-\d{4})"),
                re.compile(r"(\d{2}\.\d{2}\.\d{4})"),
                re.compile(r"(\d{4}-\d{2}-\d{2})"),
            ],
            "net": [re.compile(r"(?i)\b(?:HT|NET)\s*[:\-]?\s*(\d+[.,]?\d*)")],
            "total": [re.compile(r"(?i)\b(?:TTC|TOTAL)\s*[:\-]?\s*(\d+[.,]?\d*)")],
            "vat": [re.compile(r"(?i)\b(?:TVA|VAT)\s*[:\-]?\s*(\d+[.,]?\d*)")],
            "vat_rate": [re.compile(r"(?i)(?:TAUX|TVA|VAT)[^\d]{0,5}(\d{1,2})\s*%")]
        }

    def _calculate_missing_values(self, data: Dict[str, Any]) -> None:
        if "vat" not in data:
            if "total" in data and "net" in data:
                data["vat"] = round(data["total"] - data["net"], 2)
            elif "net" in data and "vat_rate" in data:
                data["vat"] = round(data["net"] * data["vat_rate"] / 100, 2)

        if "total" not in data:
            if "net" in data and "vat" in data:
                data["total"] = round(data["net"] + data["vat"], 2)

        if "net" not in data:
            if "total" in data and "vat" in data:
                data["net"] = round(data["total"] - data["vat"], 2)

    def _validate_data(self, data: Dict[str, Any]) -> None:
        if "total" in data and "net" in data and "vat" in data:
            expected_total = round(data["net"] + data["vat"], 2)
            if abs(expected_total - data["total"]) > 0.05:
                logger.warning(f"💡 Incohérence détectée : total attendu = {expected_total}, total trouvé = {data['total']}")

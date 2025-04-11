from google.cloud import vision
import os
import io
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger
import time
import cv2
import numpy as np


class OCREngine:
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("✅ Google Vision client initialisé avec succès")
        except Exception as e:
            logger.critical(f"❌ Échec d'initialisation du client Google Vision: {e}")
            raise

    def _preprocess_image(self, image_path: str) -> bytes:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de lire l'image: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4
        )

        _, rotated = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        _, encoded_img = cv2.imencode('.png', rotated)
        return encoded_img.tobytes()

    def extract_text(self, image_path: str) -> str:
        attempts = 0
        while attempts < self.max_retries:
            try:
                image_content = self._preprocess_image(image_path)
                image = vision.Image(content=image_content)
                response = self.client.text_detection(image=image)
                if response.error.message:
                    raise RuntimeError(response.error.message)

                return response.full_text_annotation.text
            except Exception as e:
                logger.warning(f"Tentative {attempts + 1} échouée: {e}")
                time.sleep(self.retry_delay)
                attempts += 1

        logger.error(f"❌ OCR échoué après {self.max_retries} tentatives")
        return ""

    def extract_info_from_text(self, text: str) -> Dict[str, Any]:
        data = {}
        patterns = self._compile_regex_patterns()

        for line in text.split("\n")[:8]:
            line = line.strip()
            if line and len(line) > 3:
                if line.isupper():
                    data["company_name"] = line
                    break
                elif "company_name" not in data and len(line) > 5:
                    data["company_name"] = line

        for pattern in patterns["tax_id"]:
            match = pattern.search(text)
            if match:
                data["tax_id"] = match.group(0).replace(' ', '')
                break

        for pattern in patterns["date_patterns"]:
            match = pattern.search(text)
            if match:
                date_str = match.group(1)
                try:
                    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
                        try:
                            parsed = datetime.strptime(date_str, fmt)
                            data["date"] = parsed.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

        for field, field_patterns in patterns.items():
            if field in ["tax_id", "date_patterns"]:
                continue
            for pattern in field_patterns:
                match = pattern.search(text)
                if match:
                    try:
                        value = match.group(1).replace(",", ".").strip()
                        if field == "vat_rate":
                            data[field] = int(value)
                        else:
                            data[field] = round(float(value), 2)
                        break
                    except Exception:
                        continue

        self._calculate_missing_values(data)
        self._validate_data(data)
        logger.info(f"✅ Données extraites: {data}")
        return data

    def _calculate_missing_values(self, data: Dict[str, Any]):
        if "price_ttc" in data and "vat" in data and "price_ht" not in data:
            data["price_ht"] = round(data["price_ttc"] - data["vat"], 2)
        elif "price_ht" in data and "vat_rate" in data and "vat" not in data:
            data["vat"] = round(data["price_ht"] * (data["vat_rate"] / 100), 2)
        elif "price_ht" in data and "vat" in data and "price_ttc" not in data:
            data["price_ttc"] = round(data["price_ht"] + data["vat"], 2)

    def _validate_data(self, data: Dict[str, Any]):
        if "date" not in data:
            logger.warning("⚠️ Date manquante")
        if "price_ttc" not in data:
            logger.warning("⚠️ Montant TTC manquant")
        if "company_name" not in data:
            logger.warning("⚠️ Nom entreprise manquant")

    def _compile_regex_patterns(self) -> Dict[str, List[re.Pattern]]:
        return {
            "tax_id": [
                re.compile(r"(ES)?[A-Z0-9]{8,10}"),
                re.compile(r"NIF[:\s]*([A-Z0-9]{8,10})", re.IGNORECASE),
                re.compile(r"CIF[:\s]*([A-Z0-9]{8,10})", re.IGNORECASE)
            ],
            "date_patterns": [
                re.compile(r"(\d{2}/\d{2}/\d{2,4})"),
                re.compile(r"(\d{2}\.\d{2}\.\d{4})"),
                re.compile(r"(\d{2}-\d{2}-\d{4})"),
                re.compile(r"(\d{4}-\d{2}-\d{2})")
            ],
            "price_ttc": [
                re.compile(r"TTC[:\s]*([\d,.]+)", re.IGNORECASE),
                re.compile(r"TOTAL[:\s]*([\d,.]+)", re.IGNORECASE),
            ],
            "price_ht": [
                re.compile(r"HT[:\s]*([\d,.]+)", re.IGNORECASE)
            ],
            "vat": [
                re.compile(r"TVA[:\s]*([\d,.]+)", re.IGNORECASE),
                re.compile(r"IVA[:\s]*([\d,.]+)", re.IGNORECASE)
            ],
            "vat_rate": [
                re.compile(r"(\d{1,2})\s?%", re.IGNORECASE)
            ]
        }

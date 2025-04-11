from google.cloud import vision
import os
import io
import re
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

class OCREngine:
    def __init__(self):
        # Initialisation du client Google Vision
        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("Google Vision client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision client: {e}")
            raise

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrait le texte d'une image en utilisant Google Vision API
        """
        try:
            # Lecture du fichier image
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            
            # Reconnaissance de texte
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if not texts:
                logger.warning(f"No text detected in image: {image_path}")
                return ""
                
            # Le premier élément contient tout le texte
            full_text = texts[0].description
            logger.info(f"Text extracted successfully from {image_path}")
            
            # Vérification des erreurs API
            if response.error.message:
                logger.error(f"Google Vision API error: {response.error.message}")
                
            return full_text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""

    def extract_info_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extrait les informations pertinentes du texte reconnu
        """
        data = {}

        # Nom de l'entreprise (lignes en majuscules au début)
        for line in text.split("\n")[:5]:  # Examiner les 5 premières lignes
            line = line.strip()
            if line and len(line) > 3 and line.isupper():
                data["company_name"] = line
                break

        # NIF/CIF (Format espagnol)
        nif_pattern = re.search(r'[A-Z0-9][0-9]{7}[A-Z0-9]', text)
        if nif_pattern:
            data["tax_id"] = nif_pattern.group(0)

        # Date (formats espagnols courants)
        date_patterns = [
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
            r'(\d{2}-\d{2}-\d{4})',   # DD-MM-YYYY
            r'(\d{2}\.\d{2}\.\d{4})',  # DD.MM.YYYY
            r'(\d{4}-\d{2}-\d{2})'    # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    if pattern == r'(\d{4}-\d{2}-\d{2})':
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                    elif pattern == r'(\d{2}\.\d{2}\.\d{4})':
                        date = datetime.strptime(date_str, "%d.%m.%Y")
                    elif pattern == r'(\d{2}-\d{2}-\d{4})':
                        date = datetime.strptime(date_str, "%d-%m-%Y")
                    else:
                        date = datetime.strptime(date_str, "%d/%m/%Y")
                    data["date"] = date.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

        # Montants (TTC, HT, TVA)
        # Pattern pour les montants avec € ou EUR
        price_patterns = {
            "price_ttc": [
                r'total\s*:?\s*(\d+[.,]?\d*)\s*(?:€|EUR)',
                r'TTC\s*:?\s*(\d+[.,]?\d*)',
                r'Total\s*\(?\s*TTC\s*\)?\s*:?\s*(\d+[.,]?\d*)'
            ],
            "price_ht": [
                r'HT\s*:?\s*(\d+[.,]?\d*)',
                r'Base\s*imponible\s*:?\s*(\d+[.,]?\d*)'
            ],
            "vat_amount": [
                r'TVA\s*:?\s*(\d+[.,]?\d*)',
                r'IVA\s*(?:\d+%)?\s*:?\s*(\d+[.,]?\d*)'
            ],
            "vat_rate": [
                r'TVA\s*(\d+)%',
                r'IVA\s*(\d+)%'
            ]
        }

        # Appliquer chaque pattern pour chaque type d'information
        for field, patterns in price_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1).replace(',', '.')
                        if field == "vat_rate":
                            data[field] = int(value)
                        else:
                            data[field] = float(value)
                        break
                    except (ValueError, IndexError):
                        continue

        # Déduire des valeurs manquantes si possible
        if "price_ttc" in data and "price_ht" in data and "vat_amount" not in data:
            data["vat_amount"] = round(data["price_ttc"] - data["price_ht"], 2)
        
        if "price_ttc" in data and "vat_amount" in data and "price_ht" not in data:
            data["price_ht"] = round(data["price_ttc"] - data["vat_amount"], 2)
            
        if "price_ht" in data and "vat_amount" in data and "price_ttc" not in data:
            data["price_ttc"] = round(data["price_ht"] + data["vat_amount"], 2)

        logger.info(f"Extracted data: {data}")
        return data

    def process_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Traite un reçu complet : extraction du texte et des informations
        """
        text = self.extract_text_from_image(image_path)
        if not text:
            return {}
        
        info = self.extract_info_from_text(text)
        
        # Validation des données minimales
        required_fields = ["company_name", "date", "price_ttc"]
        is_valid = all(field in info for field in required_fields)
        
        info["full_text"] = text
        info["is_valid"] = is_valid
        
        return info

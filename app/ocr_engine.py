from google.cloud import vision
import os
import io
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from loguru import logger
import time
import cv2
import numpy as np
from functools import lru_cache

class OCREngine:
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialise le moteur OCR avec Google Vision
        
        Args:
            max_retries: Nombre maximum de tentatives en cas d'échec
            retry_delay: Délai entre les tentatives en secondes
        """
        # Configuration pour les tentatives en cas d'erreur
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialisation du client Google Vision
        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("✅ Google Vision client initialisé avec succès")
        except Exception as e:
            logger.critical(f"❌ Échec d'initialisation du client Google Vision: {e}")
            raise

    def _preprocess_image(self, image_path: str) -> str:
        """
        Prétraite l'image pour améliorer la qualité de l'OCR
        
        Args:
            image_path: Chemin vers l'image à traiter
            
        Returns:
            str: Chemin vers l'image prétraitée
        """
        try:
            # Charger l'image
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"Impossible de charger l'image: {image_path}")
                return image_path
                
            # Conversion en niveaux de gris
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Amélioration du contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Détection et correction de la rotation
            coords = np.column_stack(np.where(enhanced > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            if abs(angle) > 0.5:  # Seulement si l'angle est significatif
                (h, w) = enhanced.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                enhanced = cv2.warpAffine(enhanced, M, (w, h), 
                                         flags=cv2.INTER_CUBIC, 
                                         borderMode=cv2.BORDER_REPLICATE)
            
            # Sauvegarde de l'image prétraitée
            preprocessed_path = f"{os.path.splitext(image_path)[0]}_preprocessed.jpg"
            cv2.imwrite(preprocessed_path, enhanced)
            logger.info(f"✅ Image prétraitée sauvegardée: {preprocessed_path}")
            
            return preprocessed_path
        except Exception as e:
            logger.error(f"❌ Erreur lors du prétraitement de l'image: {e}")
            return image_path  # En cas d'échec, on renvoie l'image originale

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrait le texte d'une image en utilisant Google Vision API avec tentatives en cas d'échec
        
        Args:
            image_path: Chemin vers l'image à analyser
            
        Returns:
            str: Texte extrait de l'image ou chaîne vide en cas d'échec
        """
        # Prétraitement de l'image
        preprocessed_path = self._preprocess_image(image_path)
        
        retries = 0
        while retries < self.max_retries:
            try:
                # Lecture du fichier image
                with io.open(preprocessed_path, 'rb') as image_file:
                    content = image_file.read()

                image = vision.Image(content=content)
                
                # Reconnaissance de texte avec options améliorées
                image_context = vision.ImageContext(
                    language_hints=["es", "fr", "en"],  # Langues probables
                    text_detection_params=vision.TextDetectionParams(
                        enable_text_detection_confidence_score=True
                    )
                )
                
                # Appel à l'API Vision
                response = self.client.text_detection(image=image, image_context=image_context)
                
                # Vérification des erreurs API
                if response.error.message:
                    logger.error(f"❌ Erreur Google Vision API: {response.error.message}")
                    retries += 1
                    time.sleep(self.retry_delay)
                    continue
                    
                # Extraction du texte
                texts = response.text_annotations
                
                if not texts:
                    logger.warning(f"⚠️ Aucun texte détecté dans l'image: {image_path}")
                    return ""
                    
                # Le premier élément contient tout le texte
                full_text = texts[0].description
                logger.info(f"✅ Texte extrait avec succès: {len(full_text)} caractères")
                
                # Suppression de l'image prétraitée si ce n'est pas l'originale
                if preprocessed_path != image_path and os.path.exists(preprocessed_path):
                    os.remove(preprocessed_path)
                
                return full_text
                
            except Exception as e:
                logger.error(f"❌ Erreur d'extraction de texte (tentative {retries+1}/{self.max_retries}): {e}")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
        
        logger.error(f"❌ Échec de l'extraction après {self.max_retries} tentatives")
        return ""

    @lru_cache(maxsize=128)
    def _compile_regex_patterns(self) -> Dict[str, List[re.Pattern]]:
        """
        Compile et met en cache les patterns regex pour améliorer les performances
        
        Returns:
            Dict: Dictionnaire de patterns regex compilés
        """
        patterns = {
            "tax_id": [
                re.compile(r'[A-Z0-9][0-9]{7}[A-Z0-9]'),  # Format espagnol (NIF/CIF)
                re.compile(r'FR\s*[0-9A-Z]{2}\s*[0-9]{9}'),  # Format français (TVA)
                re.compile(r'VAT\s*(?:Number|No|#)?\s*:\s*([A-Z]{2}[0-9A-Z]{2,12})'),  # Format TVA EU
            ],
            "date_patterns": [
                re.compile(r'(\d{2}/\d{2}/\d{4})'),  # DD/MM/YYYY
                re.compile(r'(\d{2}-\d{2}-\d{4})'),   # DD-MM-YYYY
                re.compile(r'(\d{2}\.\d{2}\.\d{4})'),  # DD.MM.YYYY
                re.compile(r'(\d{4}-\d{2}-\d{2})'),    # YYYY-MM-DD
                re.compile(r'(\d{2}/\d{2}/\d{2})'),    # DD/MM/YY
            ],
            "price_ttc": [
                re.compile(r'total\s*:?\s*(\d+[.,]?\d*)\s*(?:€|EUR)', re.IGNORECASE),
                re.compile(r'TTC\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
                re.compile(r'Total\s*\(?\s*TTC\s*\)?\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
                re.compile(r'à payer\s*:?\s*(\d+[.,]?\d*)\s*(?:€|EUR)', re.IGNORECASE),
                re.compile(r'TOTAL\s*(?:A\s*)?PAGAR\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
            ],
            "price_ht": [
                re.compile(r'HT\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
                re.compile(r'Base\s*imponible\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
                re.compile(r'Sous-total\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
            ],
            "vat_amount": [
                re.compile(r'TVA\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
                re.compile(r'IVA\s*(?:\d+%)?\s*:?\s*(\d+[.,]?\d*)', re.IGNORECASE),
            ],
            "vat_rate": [
                re.compile(r'TVA\s*(\d+)%', re.IGNORECASE),
                re.compile(r'IVA\s*(\d+)%', re.IGNORECASE),
                re.compile(r'T\.V\.A\.\s*(\d+)%', re.IGNORECASE),
            ]
        }
        return patterns
        
    def extract_info_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extrait les informations pertinentes du texte reconnu avec validation améliorée
        
        Args:
            text: Texte extrait de l'image
            
        Returns:
            Dict: Dictionnaire des informations extraites
        """
        data = {}
        patterns = self._compile_regex_patterns()

        # Nom de l'entreprise (lignes en majuscules au début)
        for line in text.split("\n")[:8]:  # Examiner les 8 premières lignes
            line = line.strip()
            if line and len(line) > 3:
                # Privilégier les lignes en majuscules mais prendre la première ligne significative sinon
                if line.isupper():
                    data["company_name"] = line
                    break
                elif "company_name" not in data and len(line) > 5:
                    data["company_name"] = line

        # Identifiant fiscal (NIF/CIF/TVA)
        for pattern in patterns["tax_id"]:
            match = pattern.search(text)
            if match:
                data["tax_id"] = match.group(0).replace(' ', '')
                break

        # Date (formats courants)
        for pattern in patterns["date_patterns"]:
            match = pattern.search(text)
            if match:
                date_str = match.group(1)
                try:
                    # Conversion selon le format
                    if '/' in date_str and len(date_str) == 8:  # DD/MM/YY
                        date = datetime.strptime(date_str, "%d/%m/%y")
                    elif '/' in date_str:  # DD/MM/YYYY
                        date = datetime.strptime(date_str, "%d/%m/%Y")
                    elif '.' in date_str:  # DD.MM.YYYY
                        date = datetime.strptime(date_str, "%d.%m.%Y")
                    elif '-' in date_str and len(date_str) == 10 and date_str[0:2].isdigit():  # DD-MM-YYYY
                        date = datetime.strptime(date_str, "%d-%m-%Y")
                    elif '-' in date_str:  # YYYY-MM-DD
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    data["date"] = date.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

        # Extraction des montants (TTC, HT, TVA)
        for field, field_patterns in {k: v for k, v in patterns.items() if k not in ["tax_id", "date_patterns"]}.items():
            for pattern in field_patterns:
                match = pattern.search(text)
                if match:
                    try:
                        value = match.group(1).replace(',', '.').strip()
                        if field == "vat_rate":
                            data[field] = int(value)
                        else:
                            data[field] = round(float(value), 2)
                        break
                    except (ValueError, IndexError):
                        continue

        # Déduire des valeurs manquantes si possible
        self._calculate_missing_values(data)

        # Validation des données extraites
        self._validate_data(data)
        
        logger.info(f"✅ Données extraites: {data}")
        return data
        
    def _calculate_missing_values(self, data: Dict[str, Any]) -> None:
        """
        Calcule les valeurs manquantes si possible
        
        Args:
            data: Dictionnaire des données extraites à compléter
        """
        # TTC = HT + TVA
        if "price_ttc" in data and "price_ht" in data and "vat_amount" not in data:
            data["vat_amount"] = round(data["price_ttc"] - data["price_ht"], 2)
        
        # HT = TTC - TVA
        if "price_ttc" in data and "vat_amount" in data and "price_ht" not in data:
            data["price_ht"] = round(data["price_ttc"] - data["vat_amount"], 2)
        
        # TTC = HT + TVA
        if "price_ht" in data and "vat_amount" in data and "price_ttc" not in data:
            data["price_ttc"] = round(data["price_ht"] + data["vat_amount"], 2)
        
        # Vérifier la cohérence TVA % vs montant
        if "price_ht" in data and "vat_amount" in data and "vat_rate" not in data:
            calculated_rate = round((data["vat_amount"] / data["price_ht"]) * 100)
            # Arrondir au taux standard le plus proche (21, 19, 10, 5, 4)
            standard_rates = [21, 19, 10, 5, 4]
            closest_rate = min(standard_rates, key=lambda x: abs(x - calculated_rate))
            if abs(calculated_rate - closest_rate) <= 2:  # Tolérance de 2%
                data["vat_rate"] = closest_rate

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """
        Valide la cohérence des données extraites
        
        Args:
            data: Dictionnaire des données à valider
        """
        # Vérification de la cohérence des montants
        if "price_ttc" in data and "price_ht" in data and "vat_amount" in data:
            calculated_ttc = round(data["price_ht"] + data["vat_amount"], 2)
            if abs(calculated_ttc - data["price_ttc"]) > 0.1:  # Tolérance de 0.1€
                logger.warning(f"⚠️ Incohérence dans les montants: TTC={data['price_ttc']}, HT={data['price_ht']}, TVA={data['vat_amount']}")
                # Privilégier le TTC qui est généralement le plus fiable
                data["price_ht"] = round(data["price_ttc"] - data["vat_amount"], 2)
        
        # Vérification date
        if "date" in data:
            try:
                date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
                # Vérifier si la date est dans un intervalle raisonnable (pas dans le futur, pas trop ancienne)
                now = datetime.now()
                if date_obj > now:
                    logger.warning(f"⚠️ Date dans le futur détectée: {data['date']}")
                if date_obj < datetime(now.year - 5, 1, 1):
                    logger.warning(f"⚠️ Date trop ancienne détectée: {data['date']}")
            except ValueError:
                logger.error(f"❌ Format de date invalide: {data['date']}")

    def process_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Traite un reçu complet : extraction du texte et des informations avec validation
        
        Args:
            image_path: Chemin vers l'image du reçu
            
        Returns:
            Dict: Informations extraites du reçu avec statut de validité
        """
        # Vérifier l'existence du fichier
        if not os.path.exists(image_path):
            logger.error(f"❌ Fichier non trouvé: {image_path}")
            return {"error": "File not found", "is_valid": False}
            
        # Extraire le texte
        text = self.extract_text_from_image(image_path)
        if not text:
            logger.warning(f"⚠️ Aucun texte extrait de {image_path}")
            return {"error": "No text extracted", "is_valid": False}
        
        # Extraire les informations
        info = self.extract_info_from_text(text)
        
        # Validation des données minimales
        required_fields = ["company_name", "date", "price_ttc"]
        is_valid = all(field in info for field in required_fields)
        
        # Ajouter le texte complet et le statut de validité
        info["full_text"] = text
        info["is_valid"] = is_valid
        
        if not is_valid:
            missing = [f for f in required_fields if f not in info]
            logger.warning(f"⚠️ Validation échouée pour {image_path}. Champs manquants: {missing}")
        else:
            logger.info(f"✅ Reçu validé avec succès: {image_path}")
            
        return info
        

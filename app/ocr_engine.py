from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe
from typing import Optional, List

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    client_id = Column(String, nullable=False, index=True)
    api_token = Column(String, unique=True, index=True, default=lambda: token_urlsafe(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relations
    receipts = relationship("Receipt", back_populates="user")

    def set_password(self, password: str) -> None:
        """Set password hash from plain text password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_by_token(cls, session, token: str) -> Optional["User"]:
        """Get user by API token if active"""
        return session.query(cls).filter_by(api_token=token, is_active=True).first()
    
    def regenerate_token(self) -> str:
        """Generate a new API token"""
        self.api_token = token_urlsafe(32)
        return self.api_token

class OCREngine:
    def __init__(self, enable_google_vision: bool = True):
        self.enable_google_vision = enable_google_vision

    def extract_info_from_image(self, image_bytes: bytes) -> dict:
    if self.enable_google_vision:
        text = self.extract_text_with_google_vision(image_bytes)
    else:
        text = self.extract_text_with_tesseract(image_bytes)
    
    return self.extract_fields_from_text(text)
    
    def extract_text_google_vision(self, image_bytes: bytes) -> str:
    from google.cloud import vision
    import io

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return ""
    return texts[0].description

    def extract_fields_from_text(self, text: str) -> dict:
    patterns = {
        "date": r"(?:\bDate\b[:\s]*)?(\d{2}/\d{2}/\d{4})",
        "company": r"(?:\bCompany\b[:\s]*)?([A-Z][A-Za-z0-9&\s\-,.()]+(?:SAS|SARL|SL|GmbH|Inc|Ltd|LLC)?)",
        "vat_number": r"(?:TVA|VAT)[\s:]*([A-Z]{2}[0-9A-Z]{2,})",
        "amount_ht": r"(?:HT|Montant HT)[\s:]*([\d,.]+)[\s€EUR]*",
        "amount_ttc": r"(?:TTC|Montant TTC)[\s:]*([\d,.]+)[\s€EUR]*",
        "amount_vat": r"(?:TVA)[\s:]*([\d,.]+)[\s€EUR]*",
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

    return extracted
    
    def extract_text_with_tesseract(self, image_bytes: bytes) -> str:
    """
    Utilise Tesseract OCR pour extraire du texte depuis une image en français.
    """
    try:
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(image_bytes))
        logger.debug("🧪 Image ouverte avec PIL pour Tesseract")
        text = pytesseract.image_to_string(image, lang="fra")
        logger.debug(f"📝 Texte extrait avec Tesseract : {text[:100]}...")  # pour éviter d'afficher trop
        return text

    except Exception as e:
        import traceback
        logger.error(f"❌ Tesseract OCR failed: {e}")
        logger.debug(traceback.format_exc())
        return ""

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    file = Column(String, nullable=False)
    email_sent_to = Column(String, nullable=False)
    date = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)
    price_ttc = Column(Float, nullable=True)
    price_ht = Column(Float, nullable=True)
    vat_amount = Column(Float, nullable=True)
    vat_rate = Column(Integer, nullable=True)
    email_sent = Column(Boolean, default=False)
    invoice_received = Column(Boolean, default=False)
    ocr_text = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(String, nullable=False, index=True)
    
    # Relations
    user = relationship("User", back_populates="receipts")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_pending_receipts(cls, session, days: int = 5) -> List["Receipt"]:
        """Get receipts waiting for invoice for more than X days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return session.query(cls).filter(
            cls.invoice_received == False,
            cls.email_sent == True,
            cls.created_at < cutoff
        ).all()

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe
from typing import Optional, List
from app.database import Base
import re
from PIL import Image
import pytesseract
from io import BytesIO

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    client_id = Column(String, nullable=False, index=True)
    api_token = Column(String, unique=True, index=True, default=lambda: token_urlsafe(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    receipts = relationship("Receipt", back_populates="user")

    def set_password(self, password: str) -> None:
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)
    
    @classmethod
    def get_by_token(cls, session, token: str) -> Optional["User"]:
        return session.query(cls).filter_by(api_token=token, is_active=True).first()
    
    def regenerate_token(self) -> str:
        self.api_token = token_urlsafe(32)
        return self.api_token

    def __repr__(self):
        return f"<User email={self.email} client_id={self.client_id}>"

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

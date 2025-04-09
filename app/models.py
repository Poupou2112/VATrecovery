from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe

Base = declarative_base()

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    file = Column(String, nullable=False)
    email_sent_to = Column(String, nullable=False)
    date = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    vat_number = Column(String, nullable=True)
    price_ttc = Column(Float, nullable=True)
    email_sent = Column(Boolean, default=False)
    invoice_received = Column(Boolean, default=False)
    client_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    api_token = Column(String, unique=True, default=lambda: token_urlsafe(32))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

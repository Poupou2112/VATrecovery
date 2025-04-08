from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    client_id = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


Base = declarative_base()

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)  # Nouveau champ ajouté
    file = Column(String)
    email_sent_to = Column(String)
    date = Column(String)
    company_name = Column(String)
    vat_number = Column(String)
    price_ttc = Column(Float)
    email_sent = Column(Boolean, default=False)
    invoice_received = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

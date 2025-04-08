from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True)
    file = Column(String)
    email_sent_to = Column(String)
    date = Column(String)
    company_name = Column(String)
    vat_number = Column(String)
    price_ttc = Column(Float)
    email_sent = Column(Boolean, default=False)
    invoice_received = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

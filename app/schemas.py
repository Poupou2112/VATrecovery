from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class ReceiptOut(BaseModel):
    """Schema for receipt output data"""
    id: int
    file: str
    company_name: Optional[str] = None
    price_ttc: Optional[float] = None
    date: Optional[str] = None
    invoice_received: bool
    email_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True  # for Pydantic v2+
        json_schema_extra = {
            "example": {
                "id": 42,
                "file": "uber_madrid_2024.jpg",
                "company_name": "UBER SPAIN S.L.",
                "price_ttc": 25.30,
                "date": "2024-03-12",
                "invoice_received": False,
                "email_sent": True,
                "created_at": "2024-03-12T08:00:00"
            }
        }

class SendInvoiceRequest(BaseModel):
    """Schema for invoice request payload"""
    email: EmailStr = Field(..., example="contact@uber.com")
    ticket_id: int = Field(..., example=42)

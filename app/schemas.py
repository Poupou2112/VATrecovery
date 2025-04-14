from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ReceiptBase(BaseModel):
    file: Optional[str] = None
    email_sent_to: Optional[str] = None
    date: Optional[str] = None
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    price_ttc: Optional[float] = None
    price_ht: Optional[float] = None
    vat_amount: Optional[float] = None
    vat_rate: Optional[float] = None
    email_sent: Optional[bool] = False
    invoice_received: Optional[bool] = False
    ocr_text: Optional[str] = None
    user_id: Optional[int] = None
    client_id: Optional[int] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptOut(ReceiptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    email: EmailStr
    client_id: Optional[int] = None

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: Optional[str] = None


class ReceiptUploadResponse(BaseModel):
    message: str
    receipt: ReceiptOut

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- AUTHENTICATION ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None


# --- USER ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    client_id: int  # requis si client_id est NOT NULL en base

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    client_id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True


# --- CLIENT ---
class ClientBase(BaseModel):
    name: str

class ClientResponse(ClientBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --- RECEIPT ---
class ReceiptBase(BaseModel):
    file: str  # correspond à Column(String) dans Receipt
    extracted_data: Optional[dict] = None

class ReceiptCreate(ReceiptBase):
    client_id: int

class ReceiptResponse(ReceiptBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReceiptOut(BaseModel):
    id: int
    file: str
    email_sent_to: str
    date: Optional[str]
    company_name: Optional[str]
    vat_number: Optional[str]
    price_ttc: Optional[float]
    price_ht: Optional[float]
    vat_amount: Optional[float]
    vat_rate: Optional[float]
    email_sent: bool
    invoice_received: bool
    ocr_text: Optional[str]
    user_id: int
    client_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

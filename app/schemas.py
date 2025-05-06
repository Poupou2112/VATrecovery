from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
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


# --- USER CREATION / RESPONSE ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    client_id: int  # Obligatoire si ton modèle User a une contrainte NOT NULL

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
    filename: str
    extracted_data: Optional[dict] = None


class ReceiptCreate(ReceiptBase):
    client_id: int


class ReceiptResponse(ReceiptBase):
    id: int
    client_id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.schemas import ReceiptOut
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class ReceiptBase(BaseModel):
    file_name: str
    extracted_text: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    extracted_text: Optional[str] = None
    status: Optional[str] = None


class ReceiptOut(ReceiptBase):
    id: int
    created_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ReceiptRequest(BaseModel):
    receipt_id: int


class ReceiptResponse(BaseModel):
    id: int
    file_name: str
    extracted_text: Optional[str]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

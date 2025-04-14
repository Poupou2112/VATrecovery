from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from pydantic import ConfigDict


class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ...

# Schémas d'authentification
class Token(BaseModel):
    """
    Schéma pour le token JWT retourné lors de l'authentification.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schéma pour les données contenues dans le token JWT.
    """
    username: Optional[str] = None

# Schémas d'utilisateur
class UserBase(BaseModel):
    """
    Schéma de base pour les utilisateurs.
    """
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    company_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    """
    Schéma pour la création d'un utilisateur.
    """
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """
        Vérifie que le mot de passe est suffisamment fort.
        """
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(char.isdigit() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not any(char.isupper() for char in v):
            raise ValueError('Le mot de passe doit contenir au moins une lettre majuscule')
        return v

class UserResponse(UserBase):
    """
    Schéma pour la réponse contenant les données d'un utilisateur.
    """
    id: int
    
    class Config:
        orm_mode = True

class UserInDB(UserBase):
    """
    Schéma pour un utilisateur en base de données.
    """
    id: int
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Schémas de reçus
class ReceiptBase(BaseModel):
    """
    Schéma de base pour les reçus.
    """
    merchant_name: Optional[str] = None
    date: Optional[datetime] = None
    total_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    vat_rate: Optional[float] = None
    receipt_number: Optional[str] = None
    currency: Optional[str] = Field(None, max_length=3)

class ReceiptRequest(BaseModel):
    """
    Schéma pour la demande de traitement d'un reçu.
    """
    ocr_text: str = Field(..., min_length=10)

class ReceiptResponse(ReceiptBase):
    """
    Schéma pour la réponse contenant les données d'un reçu.
    """
    id: int
    user_id: int
    status: str
    created_at: datetime
    
class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

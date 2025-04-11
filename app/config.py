from pydantic import BaseSettings, PostgresDsn, SecretStr, EmailStr
from typing import Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Général
    APP_NAME: str = "VATrecovery"
    DEBUG: bool = False
    
    # Base de données
    DATABASE_URL: PostgresDsn
    
    # Sécurité
    SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 465
    SMTP_USER: EmailStr
    SMTP_PASS: SecretStr
    SMTP_FROM: EmailStr
    
    # IMAP
    IMAP_SERVER: str
    IMAP_PORT: int = 993
    IMAP_EMAIL: EmailStr
    IMAP_PASSWORD: SecretStr
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str
    
    # Dashboard
    DASHBOARD_USER: str
    DASHBOARD_PASS: SecretStr
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

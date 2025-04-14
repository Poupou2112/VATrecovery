from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, SecretStr, EmailStr
from pydantic import field_validator
from typing import Optional, Dict, Any
import os
from functools import lru_cache
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Configuration globale de l'application.
    Charge les variables d'environnement à partir du fichier .env
    """
    # Général
    APP_NAME: str = "VATrecovery"
    DEBUG: bool = False
    
    # Base de données
    DATABASE_URL: str
    
    # Sécurité
    SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Paramètres d'email
    SMTP_HOST: str
    SMTP_PORT: int = 465
    SMTP_USER: EmailStr
    SMTP_PASS: SecretStr
    SMTP_FROM: EmailStr
    
    # IMAP pour la lecture des emails
    IMAP_SERVER: str
    IMAP_PORT: int = 993
    IMAP_EMAIL: EmailStr
    IMAP_PASSWORD: SecretStr
    
    # Google Cloud pour OCR
    GOOGLE_APPLICATION_CREDENTIALS: str
    
    # Dashboard admin
    DASHBOARD_USER: str
    DASHBOARD_PASS: SecretStr
    
    # Paramètres de rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Valide l'URL de la base de données et convertit SQLite en PostgreSQL si nécessaire.
        """
        # Pour les environnements de développement
        if v.startswith("sqlite"):
            logger.warning("SQLite détecté: cette configuration n'est recommandée que pour le développement")
            return v
        
        # Pour les environnements de production
        try:
            # Valide que l'URL est au format PostgreSQL
            if not v.startswith(("postgresql://", "postgresql+psycopg2://")):
                raise ValueError("L'URL de base de données doit être au format PostgreSQL")
            return v
        except Exception as e:
            logger.error(f"Erreur de validation de DATABASE_URL: {str(e)}")
            raise
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        """
        Vérifie que la clé secrète est suffisamment forte.
        """
        secret = v.get_secret_value()
        if len(secret) < 32:
            logger.warning("La SECRET_KEY est trop courte! Elle devrait contenir au moins 32 caractères.")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """
    Renvoie les paramètres de l'application avec mise en cache.
    Cette fonction est mise en cache pour éviter de relire les variables d'environnement
    à chaque appel.
    """
    try:
        return Settings()
    except Exception as e:
        logger.critical(f"Erreur lors du chargement des paramètres: {str(e)}")
        raise

from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, EmailStr
from typing import Optional


class Settings(BaseSettings):
    # General App Settings
    app_name: str = Field(default="VATrecovery", description="Application name")
    environment: str = Field(default="development", description="Environment name: dev/staging/prod")
    debug: bool = Field(default=True, description="Enable debug mode")
    base_url: str = Field(default="http://localhost:8000", description="Base URL of the API")

    # Security
    secret_key: str = Field(default="super-secret-key", description="JWT Secret Key")
    access_token_expire_minutes: int = Field(default=60, description="Token expiry in minutes")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm used")

    # Database
    database_url: Optional[PostgresDsn] = Field(default=None, description="PostgreSQL connection string")

    # Email / SMTP
    smtp_server: str = Field(default="smtp.example.com")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_sender: EmailStr = Field(default="no-reply@example.com")
    smtp_tls: bool = Field(default=True)
    smtp_ssl: bool = Field(default=False)

    # Throttling / Rate Limiting
    rate_limit_requests: int = Field(default=5, description="Max requests per window")
    rate_limit_seconds: int = Field(default=60, description="Rate limit time window in seconds")

    # OAuth (optional)
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_redirect_uri: Optional[str] = None

    # Rydoo / External APIs
    rydoo_api_key: Optional[str] = None
    rydoo_api_url: Optional[str] = Field(default="https://api.rydoo.com")

    # Email Listener (IMAP)
    imap_server: Optional[str] = None
    imap_user: Optional[str] = None
    imap_password: Optional[str] = None
    imap_folder: str = Field(default="INBOX")

    # Logging
    log_level: str = Field(default="INFO")
    enable_file_logging: bool = Field(default=False)
    log_file_path: Optional[str] = Field(default="logs/app.log")

    # Feature Flags
    enable_dashboard: bool = Field(default=True)
    enable_reminders: bool = Field(default=True)
    enable_fallback_ocr: bool = Field(default=False)

    # Meta
    version: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global instance
settings = Settings()

from functools import lru_cache

@lru_cache()
def get_settings():
    return settings

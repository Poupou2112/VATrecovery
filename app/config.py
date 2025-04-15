from functools import lru_cache
from pydantic_settings import BaseSettings
import redis.asyncio as redis


class Settings(BaseSettings):
    APP_NAME: str = "VATrecovery"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"  # Remplace par ta vraie URL si besoin

    # Auth / Security
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 jour
    API_TEST_TOKEN: str = "testtoken"
    IMAP_USER: str = "testuser@example.com" 
    IMAP_SERVER: str = "imap.test.com"

    # Email
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = "your@email.com"
    SMTP_PASSWORD: str = "yourpassword"
    EMAIL_FROM: str = "noreply@example.com"

    class Config:
        env_file = ".env"


settings = Settings()


@lru_cache()
def get_settings():
    return settings

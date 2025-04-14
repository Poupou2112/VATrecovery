from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import get_settings
from loguru import logger

settings = get_settings()

DATABASE_URL = settings.DATABASE_URL or "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()

def get_db_session():
    """Used for manual or scheduled access to the DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    """Used in FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

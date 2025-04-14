from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
from loguru import logger
from typing import Generator
from app.database import Base, engine


# Import Base directly from where it's defined
from app.models import Base

# Get database URL from environment variables with error handling
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    logger.warning("DATABASE_URL not defined. Using SQLite as default")
    DATABASE_URL = "sqlite:///./app.db"

# Configure SQLAlchemy engine with timeout and pool settings
engine_config = {}
if "sqlite" in DATABASE_URL:
    engine_config["connect_args"] = {"check_same_thread": False}
else:
    engine_config["pool_size"] = 5
    engine_config["max_overflow"] = 10
    engine_config["pool_timeout"] = 30
    engine_config["pool_recycle"] = 1800  # Reconnect every 30 minutes

# Create engine with configuration
engine = create_engine(DATABASE_URL, **engine_config)

# Session with autoflush for optimization
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def init_database():
    """Initialise toutes les tables dans la base de données."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")

@contextmanager
def get_db_session():
    """Provide a DB session with error handling and automatic closing"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"❌ DB transaction error: {e}")
        raise
    finally:
        db.close()

# For FastAPI dependency injection
def get_db() -> Generator:
    """Get database session for FastAPI dependency injection"""
    with get_db_session() as db:
        yield db

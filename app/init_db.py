from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import os

from loguru import logger
from typing import Generator

from werkzeug.security import generate_password_hash

from app.models import Base, User

# Get database URL from environment variables with fallback
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    logger.warning("DATABASE_URL not defined. Using SQLite as default")
    DATABASE_URL = "sqlite:///./app.db"

# Engine configuration depending on backend
engine_config = {}
if "sqlite" in DATABASE_URL:
    engine_config["connect_args"] = {"check_same_thread": False}
else:
    engine_config.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    })

engine = create_engine(DATABASE_URL, **engine_config)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def init_database():
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")

def init_default_data():
    """Insert default admin user for test/demo purposes."""
    try:
        db = SessionLocal()
        existing_user = db.query(User).filter_by(email="admin@example.com").first()
        if existing_user:
            logger.debug("✅ Default user already exists.")
            return

        user = User(
            email="admin@example.com",
            hashed_password=generate_password_hash("admin123"),
            is_active=True,
            is_admin=True,
            api_token="test_api_token_123"
        )
        db.add(user)
        db.commit()
        logger.info("✅ Default admin user created.")
    except Exception as e:
        logger.error(f"❌ Error inserting default data: {e}")
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Provide a DB session context manager."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"❌ DB transaction error: {e}")
        raise
    finally:
        db.close()

def get_db() -> Generator:
    """Dependency injection for FastAPI."""
    with get_db_session() as db:
        yield db

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from loguru import logger

from app.models import Base, User
from app.security import generate_password_hash

# Configuration de la base de données
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    logger.warning("DATABASE_URL not defined. Using SQLite as default")
    DATABASE_URL = "sqlite:///./app.db"

engine_config = {}
if "sqlite" in DATABASE_URL:
    engine_config["connect_args"] = {"check_same_thread": False}
else:
    engine_config["pool_size"] = 5
    engine_config["max_overflow"] = 10
    engine_config["pool_timeout"] = 30
    engine_config["pool_recycle"] = 1800  # 30 minutes

engine = create_engine(DATABASE_URL, **engine_config)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def init_database():
    """Initialise les tables de la base de données"""
    try:
        logger.info("🛠️ Création des tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur d'initialisation de la base de données : {e}")

def init_default_data():
    """Insère un utilisateur par défaut s'il n'existe pas déjà"""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter_by(email="admin@example.com").first()
        if not existing_user:
            user = User(
                email="admin@example.com",
                hashed_password=generate_password_hash("admin123"),
                is_active=True,
                is_admin=True,
                api_token="test_api_token_123"
            )
            db.add(user)
            db.commit()
            logger.info("✅ Utilisateur par défaut inséré.")
        else:
            logger.info("ℹ️ Utilisateur admin déjà présent.")
    except Exception as e:
        logger.error(f"❌ Erreur d'insertion utilisateur : {e}")
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Session de base de données contextuelle"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur transactionnelle : {e}")
        raise
    finally:
        db.close()

def get_db() -> Generator:
    """Dépendance FastAPI pour injection de session"""
    with get_db_session() as db:
        yield db

import os
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from werkzeug.security import generate_password_hash
from loguru import logger

from app.models import Base, User  # ✅ Assurez-vous que Base est défini là
# ⚠️ Ne pas faire: from app.database import Base  (évite les cycles)


# Obtenir la chaîne de connexion depuis les variables d’environnement
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    logger.warning("DATABASE_URL not defined. Using SQLite as default")
    DATABASE_URL = "sqlite:///./app.db"

# Configurer les options SQLite ou autres backends
engine_config = {}
if DATABASE_URL.startswith("sqlite"):
    engine_config["connect_args"] = {"check_same_thread": False}
else:
    engine_config["pool_size"] = 5
    engine_config["max_overflow"] = 10
    engine_config["pool_timeout"] = 30
    engine_config["pool_recycle"] = 1800  # reconnect every 30 min

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL, **engine_config)

# Création du SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def init_database():
    """Initialise toutes les tables de la base de données."""
    try:
        logger.info("📦 Initialisation des tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées avec succès.")
    except Exception as e:
        logger.error(f"❌ Échec de l'initialisation de la BDD : {e}")


def init_default_data():
    """Insère des données par défaut si non présentes."""
    try:
        db = SessionLocal()
        existing_user = db.query(User).filter_by(email="admin@example.com").first()
        if existing_user:
            logger.debug("ℹ️ Utilisateur admin déjà présent.")
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
        logger.info("✅ Utilisateur admin inséré avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'insertion des données par défaut : {e}")
    finally:
        db.close()


@contextmanager
def get_db_session():
    """Contexte sécurisé pour une session DB."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur transactionnelle : {e}")
        raise
    finally:
        db.close()


# Injection de dépendance FastAPI
def get_db() -> Generator:
    """Injection de session DB dans FastAPI."""
    with get_db_session() as db:
        yield db

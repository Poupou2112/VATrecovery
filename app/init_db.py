from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.models import Base
import os
from contextlib import contextmanager
from loguru import logger

# Récupération de l'URL de la base depuis les variables d'environnement
# Avec gestion des erreurs si non définie
try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    logger.warning("DATABASE_URL non définie. Utilisation de SQLite par défaut")
    DATABASE_URL = "sqlite:///./app.db"

# Configuration de l'engine SQLAlchemy avec timeout et pool_size
engine_config = {}
if "sqlite" in DATABASE_URL:
    engine_config["connect_args"] = {"check_same_thread": False}
else:
    engine_config["pool_size"] = 5
    engine_config["max_overflow"] = 10
    engine_config["pool_timeout"] = 30
    engine_config["pool_recycle"] = 1800  # Reconnexion toutes les 30 min

# Création de l'engine avec configuration
engine = create_engine(DATABASE_URL, **engine_config)

# Session avec autoflush pour optimisation
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def init_db():
    """Initialise la base de données en créant toutes les tables définies"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise

# Dépendance FastAPI pour obtenir une session DB avec gestion de contexte
@contextmanager
def get_db_session():
    """Fournit une session DB avec gestion d'erreurs et fermeture automatique"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur de transaction DB: {e}")
        raise
    finally:
        db.close()

# Pour compatibilité avec FastAPI
def get_db():
    with get_db_session() as db:
        yield db

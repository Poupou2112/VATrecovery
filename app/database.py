from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from loguru import logger

# Récupération de l'URL de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Création de l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Création de la session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de données de référence pour tous les modèles
Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

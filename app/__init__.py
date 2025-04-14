from fastapi import FastAPI
from app.api import api_router
from app.auth import auth_router
from app.models import Base
from app.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from contextlib import contextmanager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Récupération des paramètres
settings = get_settings()

# Configuration de la base de données
engine = create_engine(
    str(settings.DATABASE_URL), 
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialise la structure de la base de données."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données initialisée avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise

def get_db():
    """Fournit une session de base de données pour les dépendances FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API pour la récupération de TVA à partir de reçus",
    version="1.0.0",
    debug=settings.DEBUG
)

# Ajout des routers
app.include_router(auth_router)
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """Actions à exécuter au démarrage de l'application."""
    logger.info("🚀 Démarrage de l'application...")
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Actions à exécuter à l'arrêt de l'application."""
    logger.info("🛑 Arrêt de l'application...")

@app.get("/health")
async def health_check():
    """Point de terminaison pour vérifier l'état de l'application."""
    return {"status": "ok"}

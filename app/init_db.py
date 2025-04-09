from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Base
import os

# 📦 URL de la base depuis les variables d’environnement ou fallback SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# ⚙️ Configuration de l’engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 🛠️ Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Fonction d'initialisation de la BDD
def init_db():
    Base.metadata.create_all(bind=engine)

# 🔄 Dépendance FastAPI pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

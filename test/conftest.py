import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.init_db import init_default_data

Base.metadata.create_all(bind=engine)

# Crée une base SQLite temporaire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialise la base avant tous les tests
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Remplace la dépendance de FastAPI par la version de test
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    init_default_data()  # ← Assure-toi que la fonction insère bien des données cohérentes
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

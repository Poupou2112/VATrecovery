import os
import pytest
import fastapi_limiter

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base
from app.database import get_db
from app.init_db import init_default_data
from app.main import app
from app.database import Base, engine

os.environ["ENV"] = "test" 

Base.metadata.create_all(bind=engine)

DATABASE_URL = "sqlite:///:memory:"  # base en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


fastapi_limiter.FastAPILimiter.init = lambda *args, **kwargs: None

# Setup général : création et initialisation de la base de test
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    init_default_data()

# Fixture pour injecter une session DB de test
@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override de la dépendance de FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def api_token():
    return "testtoken"

# Fixture client FastAPI
@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c

__all__ = ["TestingSessionLocal"]

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User


DATABASE_URL = "sqlite:///vatrecovery.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

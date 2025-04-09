from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from secrets import token_urlsafe
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    api_token = Column(String, unique=True, default=lambda: token_urlsafe(32))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

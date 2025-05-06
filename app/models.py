from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe
from typing import Optional, List
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # 🔄 renommé correctement
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    api_token = Column(String, unique=True, index=True, default=lambda: token_urlsafe(32))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relations
    client = relationship("Client", back_populates="users")
    receipts = relationship("Receipt", back_populates="user")

    def set_password(self, password: str) -> None:
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)

    @classmethod
    def get_by_token(cls, session, token: str) -> Optional["User"]:
        return session.query(cls).filter_by(api_token=token, is_active=True).first()

    def regenerate_token(self) -> str:
        self.api_token = token_urlsafe(32)
        return self.api_token

    def __repr__(self):
        return f"<User email={self.email} client_id={self.client_id}>"

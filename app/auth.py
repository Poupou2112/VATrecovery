from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import User
from app.logger_setup import setup_logger
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger = setup_logger()
router = APIRouter()

# Limiteur de requêtes
limiter = Limiter(key_func=get_remote_address)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.api_token == token).first()
    if not user:
        logger.warning("Tentative d'accès avec un token invalide")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user

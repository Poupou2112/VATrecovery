from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel
from app.logger_setup import setup_logger
from app.config import get_settings

# Initialisation
settings = get_settings()
logger = setup_logger()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Authentification par token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Router principal
router = APIRouter()

# Modèle pour l'utilisateur
class TokenData(BaseModel):
    username: str | None = None

# Décodage du token et vérification utilisateur
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: username missing")
        return {"username": username}
    except JWTError as e:
        logger.error(f"Token decoding error: {e}")
        raise HTTPException(status_code=403, detail="Could not validate credentials")

# Exemple de route protégée
@router.get("/me")
@limiter.limit("5/minute")
async def read_current_user(request: Request, user: dict = Depends(get_current_user)):
    return {"user": user}

# Export du router
auth_router = router

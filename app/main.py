from fastapi import FastAPI, Request, UploadFile, File, Header, Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi_limiter import FastAPILimiter
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import redis.asyncio as redis
import os

from app.logger_setup import setup_logger
from app.config import settings, get_settings
from app.database import get_db_session
from app.auth import auth_router, get_current_user
from app.dashboard import dashboard_router
from app.reminder import reminder_router
from app.receipts import router as receipts_router
from app.api import api_router
from app.ocr_engine import OCREngine
from app.schemas import ReceiptOut
from app.models import User

# Logger
setup_logger()

# App init
app = FastAPI(title=settings.APP_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, restreindre aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    from loguru import logger
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"→ {response.status_code}")
    return response

# Redis rate-limiter init
@app.on_event("startup")
async def startup():
    from loguru import logger
    IS_TEST = os.getenv("ENV") == "test"
    try:
        if IS_TEST:
            from fakeredis.aioredis import FakeRedis
            redis_client = FakeRedis()
        else:
            redis_client = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
        logger.info("Rate limiter initialized")
    except Exception as e:
        logger.error(f"Rate limiter init failed: {e}")

@app.on_event("shutdown")
async def shutdown():
    from loguru import logger
    logger.info("Shutting down...")

# --- ROOT ---
@app.get("/")
async def root():
    return {"message": "Welcome to VATrecovery API!"}

# --- AUTHENTICATION (OAuth2 Password Grant) ---
# /auth/token, /auth/users/me, etc.
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# --- DASHBOARD (HTML, protégé OAuth2) ---
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# --- REMINDER (CRON, etc.) ---
app.include_router(reminder_router, prefix="/reminder", tags=["reminder"])

# --- RECEIPTS CRUD (protégé OAuth2) ---
app.include_router(receipts_router, prefix="/receipts", tags=["receipts"])

# --- API pour clients (X-API-Token) ---
api = APIRouter(prefix="/api", tags=["client-api"])

def get_current_client(
    x_api_token: str = Header(..., alias="X-API-Token"),
    db: Session = Depends(get_db_session),
) -> User:
    """
    Authentifie un client via son token envoyé en header X-API-Token.
    """
    client = db.query(User).filter(
        User.api_token == x_api_token,
        User.is_active == True
    ).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API token")
    return client

@api.post("/upload", response_model=ReceiptOut)
async def upload_receipt(
    file: UploadFile = File(...),
    client: User = Depends(get_current_client),
):
    """
    Endpoint pour qu’un client téléverse un reçu et récupère les champs OCR.
    """
    content = await file.read()
    engine = OCREngine(enable_google_vision=False)
    data = engine.extract_fields_from_text(engine.ocr_bytes(content))
    # On ajoute l’ID du client dans la réponse
    data["client_id"] = client.client_id
    return data
    
app.include_router(api)

# --- API REST interne (protégé OAuth2) ---
app.include_router(api_router, prefix="/internal-api", tags=["internal-api"])

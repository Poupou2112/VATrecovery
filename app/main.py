from fastapi import FastAPI, Request, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger_setup import setup_logger
from app.auth import auth_router
from app.dashboard import dashboard_router
from app.reminder import reminder_router
from app.receipts import router as receipts_router
from app.api import api_router
from app.schemas import ReceiptOut
from app.ocr_engine import OCREngine
from app.config import settings, get_settings
from loguru import logger
import redis.asyncio as redis
import os

# --- Détection du mode test ---
IS_TEST = os.getenv("ENV") == "test"

# --- Logger ---
setup_logger()

# --- Application ---
app = FastAPI(title=settings.APP_NAME)

# --- Inclusion des routers principaux ---
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(reminder_router)
app.include_router(receipts_router)
app.include_router(api_router, prefix="/api")

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Middleware de logging HTTP ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# --- Initialisation Redis / FastAPILimiter ---
@app.on_event("startup")
async def startup():
    try:
        if IS_TEST:
            from fakeredis.aioredis import FakeRedis
            redis_client = FakeRedis()
        else:
            redis_client = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)

        await FastAPILimiter.init(redis_client)
        logger.info("Redis rate limiter initialized")
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")

# --- Shutdown propre ---
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down...")

# --- Route racine ---
@app.get("/")
async def root():
    return {"message": "Welcome to VATrecovery API!"}

# --- Endpoint API de test d'upload avec OCR ---
@app.post("/api/upload", response_model=ReceiptOut)
async def upload_receipt(
    file: UploadFile = File(...),
    x_api_token: str = Header(...)
):
    if x_api_token != get_settings().API_TEST_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API token")

    contents = await file.read()
    engine = OCREngine()
    extracted = engine.extract_from_bytes(contents)
    return extracted

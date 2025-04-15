from fastapi import FastAPI, Request, UploadFile, File, Header, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger_setup import setup_logger
from app.auth import auth_router
from app.dashboard import dashboard_router
from app.reminder import reminder_router
from app.config import settings, get_settings
from app.receipts import router as receipts_router
from app.ocr_engine import OCREngine
from app.schemas import ReceiptOut
from app.api import api_router
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from loguru import logger


# Logger
setup_logger()

# App init
app = FastAPI(title=settings.APP_NAME)

# Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(reminder_router)
app.include_router(receipts_router)
app.include_router(api_router, prefix="/api")

# CORS middleware (optionnel selon besoin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de log
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Init Redis + Rate Limiter
@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis_client)

# Shutdown propre
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down...")

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to VATrecovery API!"}

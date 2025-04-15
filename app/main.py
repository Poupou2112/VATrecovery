from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger_setup import setup_logger
from app.auth import auth_router
from app.dashboard import dashboard_router
from app.reminder import reminder_router
from app.config import settings
from app.api import api_router
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from loguru import logger
from app.receipts import router as receipts_router
from app.ocr_engine import OCREngine
from app.schemas import ReceiptOut

app.include_router(receipts_router)

setup_logger()

app = FastAPI(title=settings.APP_NAME)

router = APIRouter()

@api_router.post("/upload", response_model=ReceiptOut)
async def upload_receipt(
    file: UploadFile = File(...),
    x_api_token: str = Header(...)
):
    # vérification du token
    if x_api_token != get_settings().API_TEST_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API token")

    # analyse OCR
    engine = OCREngine()
    contents = await file.read()
    result = engine.extract_from_bytes(contents)
    return result

app.include_router(api_router, prefix="/api")
router.post("/api/upload")(upload_receipt)
router.get("/api/receipts")(get_receipts)

@router.post("/api/upload")
async def upload_receipt(file: UploadFile = File(...)):
    # traitement du fichier
    return {"filename": file.filename}

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
    redis_instance = redis.from_url(get_settings().REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)
    redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)

# Shutdown propre
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down...")

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to VATrecovery API!"}

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(reminder_router)

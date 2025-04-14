from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger_setup import setup_logger
from app.api import api_router
from app.auth import auth_router
from app.dashboard import dashboard_router
from app.reminder import reminder_router
from app.email_sender import email_router
from app.scheduler import start_scheduler
from app.database import init_db
import logging

# ✅ Initialiser le logger
logger = setup_logger()

# ✅ Fallback logger (utile pour les tests si logger est None)
if logger is None:
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.INFO)

app = FastAPI(
    title="VATrecovery",
    description="OCR-powered VAT Recovery Automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ✅ Middleware pour logger les requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response

# ✅ CORS config (optionnel, à adapter selon ton frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routing
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(reminder_router, prefix="/reminders")
app.include_router(email_router, prefix="/email")

@app.get("/")
def root():
    return {"message": "Welcome to VATrecovery"}

# ✅ Startup tasks
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting VATrecovery app...")
    init_db()
    start_scheduler()

# ✅ Shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down VATrecovery app.")

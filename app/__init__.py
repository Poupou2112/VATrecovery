from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager

from app.api import api_router
from app.auth import auth_router
from app.scheduler import scheduler_router
from app.reminder import reminder_router
from app.dashboard import dashboard_router
from app.logger_setup import setup_logger
from app.init_db import init_database

logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔁 App startup: Initializing DB and scheduler...")
    init_database()
    yield
    logger.info("🔁 App shutdown: Done.")

app = FastAPI(
    title="VAT Recovery App",
    description="API for automating VAT recovery from receipts.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if logger:
        logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response

# Mount all route modules
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
app.include_router(scheduler_router, prefix="/scheduler")
app.include_router(reminder_router, prefix="/reminder")
app.include_router(dashboard_router, prefix="")

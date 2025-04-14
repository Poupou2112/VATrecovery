from fastapi import FastAPI, Request
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.auth import limiter
from app.logger_setup import setup_logger

logger = setup_logger()

app = FastAPI(title="VATrecovery")

# CORS si besoin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à adapter pour la prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour le rate-limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Inclusion des routes
app.include_router(api_router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application VATrecovery démarrée")

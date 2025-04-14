from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.auth import router as auth_router
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(auth_router, prefix="/auth")

@app.get("/")
async def root():
    return {"message": "Bienvenue sur VATrecovery"}

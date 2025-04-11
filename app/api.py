from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api import router as api_router
from app.auth import router as auth_router
from app.logger_setup import logger

app = FastAPI(title="Reclaimy VAT Recovery App")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router)
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Welcome to the Reclaimy VAT Recovery API"}

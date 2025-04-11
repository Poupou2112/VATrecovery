from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from app.api import router as api_router
from app.auth import auth_router
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes API
app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def index():
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

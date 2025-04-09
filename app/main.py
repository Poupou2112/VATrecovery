from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import os, secrets

from app.models import Receipt, User
from app.init_db import SessionLocal, init_db
from app.api import router as api_router  # <-- routes déléguées
from app.auth import get_current_user  # <-- auth token externalisée

app = FastAPI(
    title="VATrecovery",
    description="📄 Application de récupération automatique de TVA sur notes de frais.",
    version="1.0.0",
    contact={"name": "Reclaimy", "email": "support@reclaimy.io"},
    docs_url="/docs",
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 🔐 Auth HTTP Basic pour dashboard uniquement
security = HTTPBasic()
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DASHBOARD_USER"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DASHBOARD_PASS"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Accès refusé")
    return credentials.username

init_db()
app.include_router(api_router)  # 🚀 Intégration des routes API

# 🏠 Accueil
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Accède à <a href='/docs'>/docs</a> pour explorer l'API.</p>"

# 🔐 Dashboard HTML
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: str = Depends(authenticate)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

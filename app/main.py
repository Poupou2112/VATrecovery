from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.scheduler import start_scheduler
from app.init_db import init_db, SessionLocal
from app.models import Receipt
from dotenv import load_dotenv
import subprocess
import os
import secrets

# Charger les variables d'environnement
load_dotenv()

# Créer l'application FastAPI
app = FastAPI(title="VATrecovery")

# Configuration des templates et fichiers statiques
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Authentification simple (HTTP Basic)
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DASHBOARD_USER"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DASHBOARD_PASS"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Accès non autorisé")
    return credentials.username

# Initialiser la base de données
init_db()

# Lancer le scheduler en arrière-plan
start_scheduler()

# Page d'accueil simple
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Dashboard bientôt disponible.</p>"

# Dashboard sécurisé avec liste des reçus
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(authenticate)):
    session = SessionLocal()
    receipts = session.query(Receipt).order_by(Receipt.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard",
        "receipts": receipts
    })

# Relance manuelle depuis le dashboard
@app.post("/force-relance", response_class=HTMLResponse)
async def force_relance(request: Request, user: str = Depends(authenticate)):
    try:
        subprocess.run(["python", "app/reminder.py"], check=True)
        return HTMLResponse("<p>✅ Relance manuelle effectuée avec succès.</p>")
    except subprocess.CalledProcessError as e:
        return HTMLResponse(f"<p>❌ Erreur lors de la relance : {e}</p>", status_code=500)

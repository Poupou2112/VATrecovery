from fastapi import FastAPI, Request, Depends, HTTPException, Header, status, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
import subprocess
import os
import secrets

from app.scheduler import start_scheduler
from app.init_db import init_db, SessionLocal
from app.models import Receipt, User
from app.imap_listener import process_inbox
from loguru import logger

# Charger les variables d'environnement
load_dotenv()

# Créer l'application
app = FastAPI(title="VATrecovery")

# Config templates + fichiers statiques
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Auth HTTP Basic
security = HTTPBasic()

# Authentification dashboard
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DASHBOARD_USER"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DASHBOARD_PASS"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Accès non autorisé")
    return credentials.username

# Authentification API par token
def get_user_by_token(token: str = Header(..., alias="X-API-Token")):
    session = SessionLocal()
    user = session.query(User).filter_by(api_token=token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    return user

# Pydantic pour l’API
class ReceiptOut(BaseModel):
    id: int
    date: str | None = None
    company_name: str | None = None
    price_ttc: float | None = None
    invoice_received: bool
    email_sent: bool

    class Config:
        orm_mode = True

# Init base + planificateur
init_db()
start_scheduler()

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Dashboard disponible sur <a href='/dashboard'>/dashboard</a></p>"

# Dashboard avec filtre client_id
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(authenticate)):
    session = SessionLocal()
    try:
        client_id = os.getenv("DASHBOARD_CLIENT_ID", "default_client")
        receipts = session.query(Receipt).filter_by(client_id=client_id).order_by(Receipt.created_at.desc()).all()
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "title": "Dashboard",
            "receipts": receipts
        })
    finally:
        session.close()

# Relance manuelle
@app.post("/force-relance", response_class=HTMLResponse)
async def force_relance(request: Request, user: str = Depends(authenticate)):
    try:
        subprocess.run(["python", "app/reminder.py"], check=True)
        logger.info("Relance manuelle effectuée.")
        return HTMLResponse("<p>✅ Relance manuelle effectuée avec succès.</p>")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur relance : {e}")
        return HTMLResponse(f"<p>❌ Erreur lors de la relance : {e}</p>", status_code=500)

# Synchronisation des factures reçues
@app.post("/sync-inbox", response_class=HTMLResponse)
async def sync_inbox(request: Request, user: str = Depends(authenticate)):
    try:
        process_inbox()
        logger.info("Synchronisation IMAP effectuée.")
        return HTMLResponse("<p>📥 Synchronisation des factures terminée.</p>")
    except Exception as e:
        logger.error(f"Erreur IMAP : {e}")
        return HTMLResponse(f"<p>❌ Erreur pendant la synchronisation : {e}</p>", status_code=500)

# API : liste des reçus pour un client
@app.get("/api/receipts", response_model=list[ReceiptOut])
def api_get_receipts(user: User = Depends(get_user_by_token)):
    session = SessionLocal()
    try:
        receipts = session.query(Receipt).filter_by(client_id=user.client_id).order_by(Receipt.created_at.desc()).all()
        return receipts
    finally:
        session.close()

# API : stats de récupération
@app.get("/api/stats")
def api_stats(user: User = Depends(get_user_by_token)):
    session = SessionLocal()
    try:
        total = session.query(Receipt).filter_by(client_id=user.client_id).count()
        received = session.query(Receipt).filter_by(client_id=user.client_id, invoice_received=True).count()
        return {
            "total_receipts": total,
            "invoices_received": received,
            "invoices_pending": total - received
        }
    finally:
        session.close()

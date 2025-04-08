from fastapi import FastAPI, Request, Depends, HTTPException, Header, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
import subprocess
import os
import secrets
import shutil

from app.scheduler import start_scheduler
from app.init_db import init_db, SessionLocal
from app.models import Receipt, User
from app.imap_listener import process_inbox
from app.ocr_engine import analyze_ticket
from app.email_sender import send_invoice_request
from loguru import logger

# Charger .env
load_dotenv()

# Initialisation FastAPI
app = FastAPI(title="VATrecovery")

# Templating + static
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Authentification dashboard
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DASHBOARD_USER"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DASHBOARD_PASS"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Accès non autorisé")
    return credentials.username

# Authentification API token
def get_user_by_token(token: str = Header(..., alias="X-API-Token")):
    session = SessionLocal()
    user = session.query(User).filter_by(api_token=token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    return user

# Pydantic model pour API
class ReceiptOut(BaseModel):
    id: int
    date: str | None = None
    company_name: str | None = None
    price_ttc: float | None = None
    invoice_received: bool
    email_sent: bool

    class Config:
        orm_mode = True

# Initialiser BDD + scheduler
init_db()
start_scheduler()

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Dashboard : <a href='/dashboard'>/dashboard</a></p>"

# Dashboard sécurisé
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

# Forcer relance manuelle
@app.post("/force-relance", response_class=HTMLResponse)
async def force_relance(request: Request, user: str = Depends(authenticate)):
    try:
        subprocess.run(["python", "app/reminder.py"], check=True)
        logger.info("Relance manuelle effectuée.")
        return HTMLResponse("<p>✅ Relance manuelle effectuée.</p>")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur relance : {e}")
        return HTMLResponse(f"<p>❌ Erreur relance : {e}</p>", status_code=500)

# Forcer la synchronisation IMAP
@app.post("/sync-inbox", response_class=HTMLResponse)
async def sync_inbox(request: Request, user: str = Depends(authenticate)):
    try:
        process_inbox()
        logger.info("📥 Synchronisation IMAP terminée.")
        return HTMLResponse("<p>📥 Synchronisation des factures terminée.</p>")
    except Exception as e:
        logger.error(f"Erreur IMAP : {e}")
        return HTMLResponse(f"<p>❌ Erreur pendant la synchronisation : {e}</p>", status_code=500)

# API : liste des reçus
@app.get("/api/receipts", response_model=list[ReceiptOut])
def api_get_receipts(user: User = Depends(get_user_by_token)):
    session = SessionLocal()
    try:
        receipts = session.query(Receipt).filter_by(client_id=user.client_id).order_by(Receipt.created_at.desc()).all()
        return receipts
    finally:
        session.close()

# API : statistiques de réception
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

# API : uploader un reçu
@app.post("/api/upload")
def api_upload_receipt(
    file: UploadFile = File(...),
    user: User = Depends(get_user_by_token)
):
    session = SessionLocal()
    try:
        file_location = f"app/static/{file.filename}"
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        data = analyze_ticket(file_location)
        send_invoice_request(user.email, data, file_location)

        receipt = Receipt(
            client_id=user.client_id,
            file=file_location,
            email_sent_to=user.email,
            date=data.get("date"),
            company_name=data.get("company_name"),
            vat_number=data.get("vat_number"),
            price_ttc=data.get("price_ttc"),
            email_sent=True,
            invoice_received=False
        )
        session.add(receipt)
        session.commit()

        logger.info(f"🆕 Reçu ajouté via API par {user.email}")
        return {"status": "ok", "message": "Reçu traité et email envoyé."}
    finally:
        session.close()

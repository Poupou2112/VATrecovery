from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models import Receipt, User
from app.init_db import SessionLocal, init_db

# 🌍 App config avec Swagger & Redoc personnalisés
app = FastAPI(
    title="VATrecovery",
    description="📄 Application de récupération automatique de TVA sur les notes de frais.",
    version="1.0.0",
    contact={
        "name": "Reclaimy",
        "email": "support@reclaimy.io"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# 📂 Templates + fichiers statiques
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🔧 Initialisation de la base
init_db()

# 🔐 Authentification par token (via Header)
def get_user_by_token(token: str = Header(..., alias="X-API-Token")):
    session = SessionLocal()
    user = session.query(User).filter_by(api_token=token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    return user

# 📘 Modèle de sortie pour un reçu (Pydantic v2)
class ReceiptOut(BaseModel):
    id: int
    file: str
    company_name: Optional[str] = None
    price_ttc: Optional[float] = None
    date: Optional[str] = None
    invoice_received: bool
    email_sent: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 42,
                "file": "uber_paris.jpg",
                "company_name": "UBER FRANCE SAS",
                "price_ttc": 28.45,
                "date": "2025-03-20",
                "invoice_received": False,
                "email_sent": True,
                "created_at": "2025-03-20T10:00:00"
            }
        }
    )

# 📤 Modèle d'entrée pour envoyer une demande de facture
class SendInvoiceRequest(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "contact@uber.com"})
    ticket_id: int = Field(..., json_schema_extra={"example": 42})

# ✅ Endpoint : Liste des reçus
@app.get("/api/receipts", response_model=List[ReceiptOut], summary="Lister les reçus", description="Retourne tous les reçus du client connecté via token API.")
def api_get_receipts(user: User = Depends(get_user_by_token)):
    session = SessionLocal()
    receipts = session.query(Receipt).filter_by(client_id=user.client_id).order_by(Receipt.created_at.desc()).all()
    return receipts

# ✅ Endpoint : Envoyer une demande de facture
@app.post("/api/send_invoice", summary="Envoyer une demande de facture", description="Envoie un e-mail de demande de facture à partir d’un ticket.")
def send_invoice(req: SendInvoiceRequest):
    # 🎯 Exemple simplifié sans logique réelle
    return {"message": f"📧 Demande envoyée à {req.email} pour le ticket ID {req.ticket_id}"}

# 🏠 Page d'accueil
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Accède à <a href='/docs'>/docs</a> pour explorer l'API.</p>"

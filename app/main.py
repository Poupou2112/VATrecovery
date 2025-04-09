from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from app.init_db import SessionLocal, init_db
from app.models import Receipt, User
from pydantic import BaseModel, Field
from datetime import datetime

# 🌐 Swagger + Redoc personnalisés
app = FastAPI(
    title="VATrecovery",
    description="📄 Application de récupération automatique de TVA sur notes de frais.",
    version="1.0.0",
    contact={
        "name": "Reclaimy",
        "email": "support@reclaimy.io"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# 📂 Static + templates
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 📦 DB init
init_db()

# 🧩 Auth via token
def get_user_by_token(token: str = Header(..., alias="X-API-Token")):
    session = SessionLocal()
    user = session.query(User).filter_by(api_token=token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    return user

# 📘 Schémas API (Pydantic)
class ReceiptOut(BaseModel):
    id: int
    file: str
    company_name: str | None = None
    price_ttc: float | None = None
    date: str | None = None
    invoice_received: bool
    email_sent: bool
    created_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
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

class SendInvoiceRequest(BaseModel):
    email: str = Field(..., example="contact@uber.com")
    ticket_id: int = Field(..., example=42)

# 📈 API : Liste des reçus
@app.get("/api/receipts", response_model=List[ReceiptOut], summary="Lister les reçus", description="Retourne tous les reçus du client connecté via token API.")
def api_get_receipts(user: User = Depends(get_user_by_token)):
    session = SessionLocal()
    receipts = session.query(Receipt).filter_by(client_id=user.client_id).order_by(Receipt.created_at.desc()).all()
    return receipts

# 📤 API : Envoyer une demande de facture
@app.post("/api/send_invoice", summary="Envoyer une demande de facture", description="Envoie un e-mail de demande de facture au fournisseur à partir d’un ticket.")
def send_invoice(req: SendInvoiceRequest):
    # (exemple simplifié)
    return {"message": f"📧 Demande envoyée à {req.email} pour le ticket ID {req.ticket_id}"}

# 💻 Page racine
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Accède à <a href='/docs'>/docs</a> pour explorer l'API.</p>"

from app.scheduler import start_scheduler
from app.init_db import SessionLocal
from app.models import Receipt
from app.fetch_rydoo import get_tickets
from app.ocr_engine import analyze_ticket
from email_sender import send_invoice_request
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.scheduler import start_scheduler
from app.init_db import init_db

app = FastAPI(title="VATrecovery")

# Initialise la base si besoin
init_db()

# Démarre le scheduler en arrière-plan
start_scheduler()

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Dashboard bientôt disponible.</p>"

session = SessionLocal()

receipt = Receipt(
    file=ticket["file"],
    email_sent_to=ticket["email"],
    date=data.get("date"),
    company_name=data.get("company_name"),
    vat_number=data.get("vat_number"),
    price_ttc=data.get("price_ttc"),
    email_sent=True,
    invoice_received=False
)

session.add(receipt)
session.commit()
print("🗂️ Reçu enregistré en base.")


def main():
    tickets = get_tickets()
    for ticket in tickets:
        print(f"📥 Traitement du ticket : {ticket['file']}")
        data = analyze_ticket(ticket["file"])
        print(f"📤 Envoi à : {ticket['email']} avec données : {data}")
        send_invoice_request(ticket["email"], data)

if __name__ == "__main__":
    start_scheduler()
    main()

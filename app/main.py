from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.scheduler import start_scheduler
from app.init_db import init_db
import subprocess

app = FastAPI(title="VATrecovery")

# Initialise la base de données
init_db()

# Démarre le scheduler (relance quotidienne)
start_scheduler()

# Page d'accueil simple
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Dashboard bientôt disponible.</p>"

# Route pour forcer la relance manuelle (sera reliée à un bouton plus tard)
@app.post("/force-relance")
async def force_relance(request: Request):
    subprocess.run(["python", "app/reminder.py"])
    return HTMLResponse("<p>✅ Relance manuelle effectuée.</p>")

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

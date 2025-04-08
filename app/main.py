from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.scheduler import start_scheduler
from app.init_db import init_db
import subprocess

# Créer l'application FastAPI
app = FastAPI(title="VATrecovery")

# Initialiser la base de données
init_db()

# Lancer le planificateur de tâches (relance à 9h tous les jours)
start_scheduler()

# Route de test pour vérifier que l'app tourne
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>✅ VATrecovery est en ligne</h1><p>Dashboard bientôt disponible.</p>"

# Route POST pour forcer une relance manuelle (depuis le dashboard)
@app.post("/force-relance", response_class=HTMLResponse)
async def force_relance(request: Request):
    try:
        subprocess.run(["python", "app/reminder.py"], check=True)
        return HTMLResponse("<p>✅ Relance manuelle effectuée avec succès.</p>")
    except subprocess.CalledProcessError as e:
        return HTMLResponse(f"<p>❌ Échec lors de la relance : {e}</p>", status_code=500)

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

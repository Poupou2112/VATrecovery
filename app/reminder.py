import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Receipt
from dotenv import load_dotenv

load_dotenv()

# Config DB
DATABASE_URL = "sqlite:///vatrecovery.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Paramètres de rappel
DELAI_JOURS = 5  # Relance si > 5 jours sans facture

def send_reminder(receipt: Receipt):
    msg = EmailMessage()
    msg["Subject"] = "🔁 Relance : demande de facture pour note de frais"
    msg["From"] = os.getenv("SMTP_FROM")
    msg["To"] = receipt.email_sent_to

    body = f"""
Bonjour,

Je me permets de revenir vers vous concernant notre demande de **facture** correspondant au reçu suivant :

- Date du ticket : {receipt.date}
- Montant TTC : {receipt.price_ttc} €
- Société détectée : {receipt.company_name}

Nous n'avons pas encore reçu la facture associée à cette dépense.

Merci de bien vouloir nous la faire parvenir à : {os.getenv("SMTP_FROM")}

Bien cordialement,

Reclaimy
"""
    msg.set_content(body)

    with smtplib.SMTP_SSL(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as smtp:
        smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        smtp.send_message(msg)

    print(f"📩 Relance envoyée à {receipt.email_sent_to}")

# Rechercher les tickets sans facture reçue, envoyés il y a plus de X jours
now = datetime.utcnow()
deadline = now - timedelta(days=DELAI_JOURS)

receipts = session.query(Receipt).filter(
    Receipt.invoice_received == False,
    Receipt.email_sent == True,
    Receipt.created_at < deadline
).all()

if not receipts:
    print("✅ Aucune relance nécessaire aujourd’hui.")
else:
    print(f"🔁 {len(receipts)} relance(s) à envoyer...")
    for r in receipts:
        send_reminder(r)

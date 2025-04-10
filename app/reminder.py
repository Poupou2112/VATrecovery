from datetime import datetime, timedelta
from app.init_db import SessionLocal
from app.models import Receipt, User
from app.email_sender import send_email

def send_reminder():
    session = SessionLocal()
    now = datetime.utcnow()
    limit = now - timedelta(days=5)
    receipts = session.query(Receipt).filter(
        Receipt.invoice_received == False,
        Receipt.email_sent == True,
        Receipt.created_at < limit
    ).all()

    for receipt in receipts:
        user = session.query(User).filter_by(client_id=receipt.client_id).first()
        if not user:
            continue

        email_sent = send_email(
            to=receipt.email_sent_to,
            subject="⏰ Relance - Facture en attente",
            body=f"Bonjour, nous attendons toujours la facture pour l'achat du {receipt.date} ({receipt.price_ttc} €). Merci de nous l'envoyer."
        )
        if email_sent:
            print(f"✉️ Relance envoyée pour le reçu {receipt.id}")

    session.close()

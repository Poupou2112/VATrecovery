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

    sent_count = 0
    for receipt in receipts:
        user = session.query(User).filter_by(client_id=receipt.client_id).first()
        if user:
            subject = "Relance pour demande de facture"
            body = f"Bonjour, ceci est une relance pour la facture liée au reçu du {receipt.date} (TTC: {receipt.price_ttc} €)."
            if send_email(to=receipt.email_sent_to, subject=subject, body=body):
                sent_count += 1

    session.close()
    return sent_count

from app.models import Receipt, User
from app.email_sender import send_email
from app.init_db import SessionLocal
from datetime import datetime, timedelta


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
        if not user:
            continue

        body = f"Bonjour,\n\nNous n'avons pas encore reçu la facture pour votre achat du {receipt.date} chez {receipt.company_name} (montant : {receipt.price_ttc} €).\n\nPouvez-vous nous l’envoyer ?\n\nMerci d’avance.\n\n— L’équipe Reclaimy"

        send_email(
            to=receipt.email_sent_to,
            subject="⏰ Rappel facture manquante",
            body=body,
            attachment_path=None
        )
        sent_count += 1

    session.close()
    return sent_count

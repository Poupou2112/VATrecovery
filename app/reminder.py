from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Receipt, User
from app.email_sender import send_email
from datetime import datetime, timedelta
from loguru import logger

reminder_router = APIRouter()

@reminder_router.get("/reminders/send")
def send_reminder_endpoint(db: Session = Depends(get_db)) -> dict:
    """
    Envoie des relances pour les reçus sans facture après X jours.
    """
    logger.info("🔔 Lancement de l'envoi des relances")
    days_threshold = 7
    threshold_date = datetime.utcnow() - timedelta(days=days_threshold)

    receipts = db.query(Receipt).filter(
        Receipt.email_sent == True,
        Receipt.invoice_received == False,
        Receipt.created_at < threshold_date
    ).all()

    logger.info(f"🔍 {len(receipts)} reçus en attente de facture dépassent le délai")

    count = 0
    for receipt in receipts:
        user = db.query(User).filter(User.client_id == receipt.client_id).first()
        if not user:
            continue

        send_email(
            to=receipt.email_sent_to,
            subject="Relance : merci de nous envoyer la facture",
            body=f"""Bonjour,

Pourriez-vous nous transmettre la facture liée au reçu envoyé le {receipt.date} ?

Montant TTC : {receipt.price_ttc} €
Fichier : {receipt.file}

Merci d’avance,
L’équipe Reclaimy
"""
        )
        count += 1
        logger.debug(f"✉️ Relance envoyée pour le reçu ID {receipt.id}")

    return {"reminders_sent": count}

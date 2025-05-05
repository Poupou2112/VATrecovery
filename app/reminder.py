from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from app.database import SessionLocal
from app.models import Receipt, User
from app.email_sender import send_email
from app.logger_setup import logger
from app.auth import get_current_user
from app.reminder import send_reminders


reminder_router = APIRouter()

REMINDER_DELAY_DAYS = 7  # Peut être déplacé dans settings si besoin

async def send_reminders(db: Session):
    cutoff = datetime.utcnow() - timedelta(days=5)
    receipts = db.query(Receipt).filter(
        Receipt.invoice_received == False,
        Receipt.email_sent == True,
        Receipt.created_at < cutoff
    ).all()

    for receipt in receipts:
        await send_email(
            to=receipt.email_sent_to,
            subject="Reminder: Missing Invoice",
            body=f"Please send the invoice for receipt {receipt.file}"
        )

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@reminder_router.post("/reminder", status_code=status.HTTP_200_OK)
def run_reminder_endpoint(user=Depends(get_current_user), db: Session = Depends(get_db_session)):
    return {"sent": send_reminder(db, client_id=user.client_id)}


def send_reminder(db: Session, client_id: int = None) -> int:
    """
    Envoie un rappel par e-mail pour chaque reçu envoyé depuis plus de REMINDER_DELAY_DAYS
    et dont la facture n'a pas encore été reçue.
    """
    threshold = datetime.utcnow() - timedelta(days=REMINDER_DELAY_DAYS)

    query = db.query(Receipt).filter(
        Receipt.email_sent == True,
        Receipt.invoice_received == False,
        Receipt.created_at <= threshold
    )

    if client_id:
        query = query.filter(Receipt.client_id == client_id)

    receipts_to_remind = query.all()
    logger.info(f"🔁 Found {len(receipts_to_remind)} receipts requiring reminders")

    count = 0
    receipt_ids = []

    for receipt in receipts_to_remind:
        user = db.query(User).filter(User.client_id == receipt.client_id).first()
        if not user:
            logger.warning(f"⚠️ No user found for receipt ID {receipt.id}")
            continue

        subject = f"[Reminder] Please send us the invoice for {receipt.file}"
        body = (
            f"Dear client,\n\nWe noticed that the invoice for your receipt '{receipt.file}' "
            f"(dated {receipt.date}) has not yet been received. "
            "Please forward it to us so we can complete the process.\n\n"
            "Thank you!"
        )

        success = send_email(to=receipt.email_sent_to, subject=subject, body=body)
        if success:
            count += 1
            receipt_ids.append(receipt.id)
            logger.debug(f"✅ Reminder sent for receipt ID: {receipt.id}")
        else:
            logger.error(f"❌ Failed to send reminder for receipt ID: {receipt.id}")

    return count

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from app.init_db import SessionLocal
from app.models import Receipt, User
from app.email_sender import send_email
from loguru import logger

def send_reminder(days_threshold: int = 5) -> Tuple[int, List[int]]:
    """
    Send reminder emails for receipts without invoices after a certain number of days.
    
    Args:
        days_threshold: Number of days to wait before sending a reminder
        
    Returns:
        Tuple containing count of sent emails and list of receipt IDs processed
    """
    session = SessionLocal()
    now = datetime.utcnow()
    limit = now - timedelta(days=days_threshold)
    
    try:
        # Query receipts that need a reminder
        receipts = session.query(Receipt).filter(
            Receipt.invoice_received == False,
            Receipt.email_sent == True,
            Receipt.created_at < limit
        ).all()

        logger.info(f"Found {len(receipts)} receipts requiring reminders")
        
        sent_count = 0
        processed_ids = []
        
        for receipt in receipts:
            user = session.query(User).filter_by(client_id=receipt.client_id).first()
            if not user:
                logger.warning(f"No user found for client_id: {receipt.client_id}")
                continue
                
            subject = "Invoice Request Reminder"
            body = f"Hello, this is a reminder for the invoice related to the receipt dated {receipt.date} (Total: {receipt.price_ttc} €)."
            
            if send_email(to=receipt.email_sent_to, subject=subject, body=body):
                sent_count += 1
                processed_ids.append(receipt.id)
                logger.debug(f"Reminder sent for receipt ID: {receipt.id}")
            else:
                logger.error(f"Failed to send reminder for receipt ID: {receipt.id}")
        
        return sent_count, processed_ids
    
    except Exception as e:
        logger.error(f"Error in send_reminder: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    count, ids = send_reminder()
    logger.info(f"Reminder process complete. Sent {count} reminders for receipt IDs: {ids}")

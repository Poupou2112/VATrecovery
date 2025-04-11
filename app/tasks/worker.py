from fastapi import BackgroundTasks
from app.queue.redis_queue import RedisQueue
from app.ocr_engine import extract_info_from_text
from app.email_sender import send_email
from app.models import SessionLocal, Receipt, User
from loguru import logger
import json

queue = RedisQueue()


def process_task(task: dict):
    """Process a single task based on its type."""
    try:
        task_type = task['data'].get("type")
        logger.info(f"Processing task type: {task_type}")

        if task_type == "ocr":
            receipt_id = task['data'].get("receipt_id")
            text = task['data'].get("text")
            extracted = extract_info_from_text(text)

            db = SessionLocal()
            receipt = db.query(Receipt).get(receipt_id)
            if receipt:
                receipt.company_name = extracted.get("company_name")
                receipt.date = extracted.get("date")
                receipt.price_ttc = extracted.get("price_ttc")
                db.commit()
                logger.info(f"Receipt {receipt_id} updated with OCR data")
            db.close()

        elif task_type == "send_email":
            send_email(
                to=task['data']["to"],
                subject=task['data']["subject"],
                body=task['data']["body"]
            )
            logger.info("Email sent successfully")

        queue.complete_task("default", task['id'])

    except Exception as e:
        logger.error(f"Task failed: {e}")
        queue.fail_task("default", task['id'], str(e))

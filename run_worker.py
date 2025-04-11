# run_worker.py
import time
from app.queue.redis_queue import RedisQueue
from app.ocr_engine import extract_info_from_text
from app.email_sender import send_email
from app.models import SessionLocal, Receipt, User
from loguru import logger


def process_task(task):
    task_type = task["data"].get("type")
    task_id = task["id"]
    logger.info(f"Processing task {task_id} of type {task_type}")

    if task_type == "ocr_receipt":
        receipt_id = task["data"].get("receipt_id")
        try:
            session = SessionLocal()
            receipt = session.query(Receipt).filter_by(id=receipt_id).first()
            if not receipt:
                raise ValueError(f"Receipt {receipt_id} not found")

            text = receipt.ocr_text or ""
            extracted = extract_info_from_text(text)

            for key, value in extracted.items():
                setattr(receipt, key, value)
            session.commit()

            logger.info(f"Receipt {receipt_id} OCR processed")
            queue.complete_task("ocr", task_id, result=extracted)
        except Exception as e:
            queue.fail_task("ocr", task_id, str(e))
        finally:
            session.close()

    elif task_type == "send_invoice_email":
        try:
            to = task["data"]["to"]
            subject = task["data"].get("subject", "Demande de facture")
            body = task["data"].get("body", "Bonjour, merci d'envoyer la facture jointe.")
            send_email(to=to, subject=subject, body=body)
            logger.info(f"Email sent to {to}")
            queue.complete_task("email", task_id, result={"to": to})
        except Exception as e:
            queue.fail_task("email", task_id, str(e))

    else:
        logger.warning(f"Unknown task type: {task_type}")
        queue.fail_task("unknown", task_id, "Invalid task type")


if __name__ == "__main__":
    queue = RedisQueue()

    while True:
        for q in ["ocr", "email"]:
            task = queue.dequeue(q, wait=False)
            if task:
                process_task(task)
        time.sleep(1)

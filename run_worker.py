# run_worker.py
import time
import os
import json
from typing import Dict, Any, Optional
import traceback
from app.queue.redis_queue import RedisQueue
from app.ocr_engine import extract_info_from_text
from app.email_sender import send_email
from app.models import SessionLocal, Receipt, User
from app.security import sanitize_input, validate_email
from loguru import logger
import signal
import sys

# Configuration du logger
logger.add(
    "logs/worker_{time}.log", 
    rotation="500 MB", 
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time} {level} {message}"
)

# Délai entre les traitements pour éviter de surcharger les ressources
PROCESS_DELAY = float(os.getenv("WORKER_DELAY_SECONDS", "1"))
# Nombre max d'essais de traitement avant abandon
MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))

# Gestion de la terminaison propre
should_exit = False

def handle_exit_signal(sig, frame):
    global should_exit
    logger.info(f"Signal {sig} reçu, arrêt en cours...")
    should_exit = True

signal.signal(signal.SIGTERM, handle_exit_signal)
signal.signal(signal.SIGINT, handle_exit_signal)


def process_task(task: Dict[str, Any]) -> None:
    """
    Traite une tâche de la file d'attente selon son type.
    
    Args:
        task: Le dictionnaire contenant les détails de la tâche
    """
    task_type = task.get("data", {}).get("type", "unknown")
    task_id = task.get("id", "no-id")
    queue_name = task.get("queue", "unknown")
    
    logger.info(f"Processing task {task_id} of type {task_type}")

    try:
        if task_type == "ocr_receipt":
            _process_ocr_task(task)
        elif task_type == "send_invoice_email":
            _process_email_task(task)
        else:
            logger.warning(f"Unknown task type: {task_type}")
            queue.fail_task(queue_name, task_id, "Invalid task type")
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        queue.fail_task(queue_name, task_id, str(e))


def _process_ocr_task(task: Dict[str, Any]) -> None:
    """
    Traite une tâche OCR pour extraire des informations d'un reçu.
    
    Args:
        task: Le dictionnaire contenant les détails de la tâche
    """
    task_id = task.get("id", "no-id")
    receipt_id = task.get("data", {}).get("receipt_id")
    
    if not receipt_id:
        queue.fail_task("ocr", task_id, "Missing receipt_id")
        return
    
    # Validation de l'ID du reçu
    if not isinstance(receipt_id, (int, str)) or (isinstance(receipt_id, str) and not receipt_id.isdigit()):
        queue.fail_task("ocr", task_id, "Invalid receipt_id format")
        return
    
    session = None
    try:
        session = SessionLocal()
        receipt = session.query(Receipt).filter_by(id=receipt_id).first()
        
        if not receipt:
            raise ValueError(f"Receipt {receipt_id} not found")

        # Validation du texte OCR
        text = receipt.ocr_text or ""
        if not text.strip():
            logger.warning(f"Empty OCR text for receipt {receipt_id}")
            queue.complete_task("ocr", task_id, result={"warning": "Empty OCR text"})
            return
            
        # Extraction d'informations du texte OCR
        extracted = extract_info_from_text(text)
        
        # Mise à jour du reçu avec les informations extraites
        for key, value in extracted.items():
            setattr(receipt, key, value)
        
        session.commit()
        logger.info(f"Receipt {receipt_id} OCR processed successfully")
        queue.complete_task("ocr", task_id, result=extracted)
        
    except Exception as e:
        logger.error(f"Error in OCR task: {str(e)}")
        logger.debug(traceback.format_exc())
        queue.fail_task("ocr", task_id, str(e))
    finally:
        if session:
            session.close()


def _process_email_task(task: Dict[str, Any]) -> None:
    """
    Traite une tâche d'envoi d'email.
    
    Args:
        task: Le dictionnaire contenant les détails de la tâche
    """
    task_id = task.get("id", "no-id")
    data = task.get("data", {})
    
    to_email = data.get("to")
    subject = data.get("subject", "Demande de facture")
    body = data.get("body", "Bonjour, merci d'envoyer la facture jointe.")
    
    # Validation des entrées
    if not to_email:
        queue.fail_task("email", task_id, "Missing recipient email")
        return
    
    # Validation du format d'email
    if not validate_email(to_email):
        queue.fail_task("email", task_id, f"Invalid email format: {to_email}")
        return
    
    # Sanitization des entrées
    subject = sanitize_input(subject)
    body = sanitize_input(body)
    
    try:
        # Envoi de l'email
        send_email(to=to_email, subject=subject, body=body)
        logger.info(f"Email sent to {to_email}")
        queue.complete_task("email", task_id, result={"to": to_email})
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        logger.debug(traceback.format_exc())
        queue.fail_task("email", task_id, str(e))


if __name__ == "__main__":
    logger.info("Starting worker process")
    queue = RedisQueue()

    # Boucle principale du worker
    while not should_exit:
        for q in ["ocr", "email"]:
            try:
                task = queue.dequeue(q, wait=False)
                if task:
                    process_task(task)
            except Exception as e:
                logger.error(f"Error in worker loop for queue {q}: {str(e)}")
                logger.debug(traceback.format_exc())
        
        # Pause pour éviter de surcharger les ressources
        time.sleep(PROCESS_DELAY)
    
    logger.info("Worker shutting down gracefully")
    sys.exit(0)

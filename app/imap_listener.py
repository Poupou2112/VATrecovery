import imaplib
import email
from email.header import decode_header
import os
import io
import re
from PyPDF2 import PdfReader
from sqlalchemy import and_, or_
from app.init_db import get_db_session
from app.models import Receipt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from loguru import logger
import time
from typing import Dict, List, Optional, Tuple, Union
import tempfile

# Chargement des variables d'environnement
load_dotenv()

class EmailProcessor:
    def __init__(self):
        self.imap_server = os.getenv("IMAP_SERVER")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.imap_email = os.getenv("IMAP_EMAIL")
        self.imap_password = os.getenv("IMAP_PASSWORD")

        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.smtp_from = os.getenv("SMTP_FROM")

        self._validate_config()

    def _validate_config(self):
        required_imap = ["IMAP_SERVER", "IMAP_EMAIL", "IMAP_PASSWORD"]
        required_smtp = ["SMTP_HOST", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"]

        missing_imap = [var for var in required_imap if not os.getenv(var)]
        if missing_imap:
            raise ValueError(f"Variables d'environnement IMAP manquantes: {', '.join(missing_imap)}")

        missing_smtp = [var for var in required_smtp if not os.getenv(var)]
        if missing_smtp:
            raise ValueError(f"Variables d'environnement SMTP manquantes: {', '.join(missing_smtp)}")

    def extract_text_from_pdf_attachment(self, part) -> str:
        try:
            file_data = part.get_payload(decode=True)
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name

            pdf_reader = PdfReader(temp_path)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

            os.unlink(temp_path)
            return text
        except Exception as e:
            logger.error(f"❌ Erreur extraction texte PDF: {e}")
            return ""

    def match_receipt(self, text: str) -> Optional[Receipt]:
        if not text:
            return None

        with get_db_session() as session:
            receipts = session.query(Receipt).filter_by(invoice_received=False).all()

            for receipt in receipts:
                if receipt.company_name and receipt.company_name.lower() in text.lower():
                    if receipt.date and receipt.date in text:
                        if receipt.price_ttc and str(receipt.price_ttc).replace('.', ',') in text:
                            logger.info(f"🎯 Match trouvé pour le reçu ID {receipt.id}")
                            return receipt
            return None

    def send_confirmation(self, to: str, subject: str, body: str) -> bool:
        try:
            msg = EmailMessage()
            msg["From"] = self.smtp_from
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(body)

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.smtp_user, self.smtp_pass)
                smtp.send_message(msg)

            logger.info(f"📧 Confirmation envoyée à {to}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {e}")
            return False

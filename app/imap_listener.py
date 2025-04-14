import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Receipt
from app.ocr_engine import OCREngine
from app.logger_setup import logger
from app.config import settings


class EmailProcessor:
    def __init__(self):
        self.imap_server = settings.IMAP_SERVER
        self.imap_user = settings.IMAP_USER
        self.imap_password = settings.IMAP_PASSWORD
        self.ocr_engine = OCREngine()
        logger.info("📥 Email processor initialized successfully")

    def connect(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.imap_user, self.imap_password)
            mail.select("inbox")
            return mail
        except Exception as e:
            logger.error(f"❌ IMAP connection failed: {e}")
            return None

    def fetch_unseen_receipts(self):
        mail = self.connect()
        if not mail:
            return []

        try:
            _, search_data = mail.search(None, 'UNSEEN')
            emails = search_data[0].split()

            for num in emails:
                _, data = mail.fetch(num, "(RFC822)")
                _, bytes_data = data[0]
                msg = email.message_from_bytes(bytes_data)

                subject, _ = decode_header(msg["Subject"])[0]
                subject = subject.decode() if isinstance(subject, bytes) else subject
                logger.info(f"📩 Processing email: {subject}")

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    filename = part.get_filename()
                    if filename:
                        content = part.get_payload(decode=True)
                        text = self.ocr_engine.extract_text(content)
                        logger.debug(f"OCR text extracted: {text[:100]}...")

                        receipt = {
                            "file": filename,
                            "ocr_text": text,
                            "email_sent_to": msg.get("To"),
                            "created_at": datetime.utcnow()
                        }
                        self.match_receipt(receipt)
            mail.logout()
        except Exception as e:
            logger.error(f"❌ Error processing mailbox: {e}")

    def match_receipt(self, receipt):
        session: Session = SessionLocal()
        try:
            receipts = session.query(Receipt).filter_by(invoice_received=False).all()
            matches = []
            for r in receipts:
                if r.price_ttc and str(r.price_ttc) in receipt["ocr_text"]:
                    r.invoice_received = True
                    r.ocr_text = receipt["ocr_text"]
                    r.updated_at = datetime.utcnow()
                    matches.append(r.id)
            session.commit()
            logger.debug(f"🔄 Matched receipts: {matches}")
            return matches
        except Exception as e:
            logger.error(f"❌ DB transaction error: {e}")
            return []
        finally:
            session.close()

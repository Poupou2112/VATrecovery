import logging
import imaplib
import email
from email.header import decode_header
import os
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

# Load environment variables
load_dotenv()

class EmailProcessor:
    def __init__(self):
        """Initialize email processor with IMAP and SMTP configurations"""
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
        logger.info("Email processor initialized successfully")

    def _validate_config(self) -> None:
        """Validate that all required environment variables are set"""
        required_imap = ["IMAP_SERVER", "IMAP_EMAIL", "IMAP_PASSWORD"]
        required_smtp = ["SMTP_HOST", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"]

        missing_imap = [var for var in required_imap if not os.getenv(var)]
        if missing_imap:
            raise ValueError(f"Missing IMAP environment variables: {', '.join(missing_imap)}")

        missing_smtp = [var for var in required_smtp if not os.getenv(var)]
        if missing_smtp:
            raise ValueError(f"Missing SMTP environment variables: {', '.join(missing_smtp)}")

    def extract_text_from_pdf_attachment(self, part) -> str:
        """
        Extract text content from a PDF email attachment
        
        Args:
            part: Email part containing PDF attachment
            
        Returns:
            Extracted text from PDF
        """
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

            os.unlink(temp_path)  # Clean up temporary file
            return text
        except Exception as e:
            logger.error(f"❌ Error extracting PDF text: {e}")
            return ""

    def match_receipt(self, text: str) -> Optional[Receipt]:
        """
        Find matching receipt in database based on PDF content
        
        Args:
            text: Extracted text from PDF invoice
            
        Returns:
            Receipt object if matched, None otherwise
        """
        if not text:
            return None

        with get_db_session() as session:
            receipts = session.query(Receipt).filter_by(invoice_received=False).all()

            for receipt in receipts:
                # Match by company name, date and price
                if receipt.company_name and receipt.company_name.lower() in text.lower():
                    if receipt.date and receipt.date in text:
                        # Check for price with either dot or comma as decimal separator
                        price_str = str(receipt.price_ttc)
                        price_comma = price_str.replace('.', ',')
                        if price_str in text or price_comma in text:
                            logger.info(f"🎯 Match found for receipt ID {receipt.id}")
                            return receipt
            
            logger.debug("No matching receipt found")
            return None

    def send_confirmation(self, to: str, subject: str, body: str) -> bool:
        """
        Send confirmation email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = EmailMessage()
            msg["From"] = self.smtp_from
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(body)

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.smtp_user, self.smtp_pass)
                smtp.send_message(msg)

            logger.info(f"📧 Confirmation sent to {to}")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    def process_emails(self, folder: str = "INBOX", max_emails: int = 10) -> int:
        """
        Process incoming emails in specified folder
        
        Args:
            folder: IMAP folder to process
            max_emails: Maximum number of emails to process
            
        Returns:
            Number of emails processed
        """
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.imap_email, self.imap_password)
            mail.select(folder)
            
            # Search for all unread emails
            status, data = mail.search(None, "UNSEEN")
            if status != "OK":
                logger.error("Failed to search for emails")
                return 0
                
            email_ids = data[0].split()
            processed = 0
            
            # Process emails up to max_emails
            for email_id in email_ids[:max_emails]:
                status, data = mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                    
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Process PDF attachments
                if self._process_email_message(msg):
                    processed += 1
                
                # Mark as read
                mail.store(email_id, "+FLAGS", "\\Seen")
                
            mail.close()
            mail.logout()
            
            logger.info(f"Processed {processed} emails")
            return processed
            
        except Exception as e:
            logger.error(f"Error processing emails: {e}")
            return 0
            
    def _process_email_message(self, msg) -> bool:
        """
        Process a single email message looking for PDF attachments
        
        Args:
            msg: Email message object
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            subject = self._decode_header(msg["Subject"])
            sender = self._decode_header(msg["From"])
            logger.debug(f"Processing email: {subject} from {sender}")
            
            # Check for PDF attachments
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                    
                if part.get_content_type() == "application/pdf":
                    pdf_text = self.extract_text_from_pdf_attachment(part)
                    receipt = self.match_receipt(pdf_text)
                    
                    if receipt:
                        # Update receipt status
                        with get_db_session() as session:
                            receipt_db = session.query(Receipt).get(receipt.id)
                            receipt_db.invoice_received = True
                            receipt_db.updated_at = datetime.utcnow()
                            session.commit()
                            
                        # Send confirmation
                        self.send_confirmation(
                            to=receipt.user.email,
                            subject="Invoice received",
                            body=f"We have received the invoice for your receipt dated {receipt.date}."
                        )
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
            
    def _decode_header(self, header_value: Optional[str]) -> str:
        """
        Decode email header value
        
        Args:
            header_value: Raw header string
            
        Returns:
            Decoded header string
        """
        if not header_value:
            return ""
            
        try:
            decoded_header = decode_header(header_value)
            parts = []
            
            for part, encoding in decoded_header:
                if isinstance(part, bytes):
                    if encoding:
                        parts.append(part.decode(encoding))
                    else:
                        parts.append(part.decode('utf-8', 'ignore'))
                else:
                    parts.append(part)
                    
            return " ".join(parts)
        except Exception as e:
            logger.error(f"Error decoding header: {e}")
            return header_value or ""

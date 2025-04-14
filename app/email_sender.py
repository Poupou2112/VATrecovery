"""
email_sender.py - Service d'envoi d'e-mails via SMTP
"""

import smtplib
from email.message import EmailMessage
from app.config import settings
from app.logger_setup import logger

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM

    def send(self, to: str, subject: str, body: str) -> bool:
        msg = EmailMessage()
        msg["From"] = self.email_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                logger.info(f"📧 Email sent to {to} with subject '{subject}'")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to}: {e}")
            return False


# Fonction helper pour usage direct
def send_email(to: str, subject: str, body: str) -> bool:
    service = EmailService()
    return service.send(to, subject, body)

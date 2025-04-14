import smtplib
from email.message import EmailMessage
from app.config import get_settings
from app.logger_setup import logger

settings = get_settings()

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.sender = settings.EMAIL_FROM

    def send(self, to: str, subject: str, body: str, attachments: list = None):
        if not to or not subject or not body:
            logger.warning("🚫 Missing required email fields")
            return False

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = to
        msg.set_content(body)

        if attachments:
            for filename, content, mime_type in attachments:
                maintype, subtype = mime_type.split("/")
                msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

        try:
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(msg)
            logger.info(f"📧 Email sent to {to} - {subject}")
            return True
        except Exception as e:
            logger.exception(f"❌ Failed to send email to {to}: {e}")
            return False


def send_email(to: str, subject: str, body: str, attachments: list = None, service: EmailService = None) -> bool:
    if service is None:
        service = EmailService()
    return service.send(to, subject, body, attachments)

import smtplib
from email.message import EmailMessage
from app.config import get_settings
from app.logger_setup import logger
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


def send_email(subject: str, body: str, to_addresses: list[str], html: str = None, reply_to: str = None):
    from_address = "noreply@vatrecovery.com"
    to_address = ", ".join(to_addresses)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    if reply_to:
        msg["Reply-To"] = reply_to

    part1 = MIMEText(body, "plain")
    msg.attach(part1)

    if html:
        part2 = MIMEText(html, "html")
        msg.attach(part2)

    with smtplib.SMTP("localhost") as server:
        server.sendmail(from_address, to_addresses, msg.as_string())

    # ✅ Pour les tests : on retourne les éléments utilisés
    return from_address, to_addresses, msg

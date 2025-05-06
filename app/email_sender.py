import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration—adjust as needed or pull from your settings
SMTP_HOST = "localhost"
SMTP_PORT = 25
DEFAULT_FROM = "noreply@vatrecovery.com"

def send_email(
    subject: str,
    body: str,
    recipients: list[str],
    from_address: str = DEFAULT_FROM,
    html: str | None = None,
    reply_to: str | None = None,
) -> bool:
    """
    Send an email with both plain-text and optional HTML parts.
    Returns True on success, False on any exception.
    """
    # Build message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(recipients)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach the plain‐text part
    part_text = MIMEText(body, "plain")
    msg.attach(part_text)

    # Optionally attach HTML
    if html:
        part_html = MIMEText(html, "html")
        msg.attach(part_html)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.sendmail(from_address, recipients, msg.as_string())
        return True
    except Exception:
        return False

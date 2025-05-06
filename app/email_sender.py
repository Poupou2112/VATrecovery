import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DEFAULT_FROM = "no-reply@vatrecovery.com"

def send_email(to, subject, html=None, from_email=None, reply_to=None, body=None):
    """
    Send an email with both plain-text and optional HTML parts.

    Positional args:
      to         – single address or list of addresses
      subject    – email subject
      html       – HTML content (positional third arg if used)
      from_email – sender address (positional fourth arg if used)

    Keyword args:
      body       – plain-text content (if html is provided but no body, html is used as fallback)
      reply_to   – optional Reply-To header

    Returns True on success, raises on error.
    """
    # Normalize recipients
    if isinstance(to, (list, tuple)):
        recipients = list(to)
    else:
        recipients = [to]

    sender = from_email or DEFAULT_FROM
    text = body or html or ""

    # Build multipart message
    msg = MIMEMultipart("alternative") if html else MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach plain
    part1 = MIMEText(text, "plain")
    msg.attach(part1)

    # Attach HTML if present
    if html:
        part2 = MIMEText(html, "html")
        msg.attach(part2)

    raw = msg.as_string()

    # Attempt plain SMTP, fallback to SSL if it fails
    try:
        with smtplib.SMTP() as server:
            server.sendmail(sender, recipients, raw)
    except smtplib.SMTPException:
        with smtplib.SMTP_SSL() as server:
            server.sendmail(sender, recipients, raw)

    return True

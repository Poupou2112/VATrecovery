import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DEFAULT_FROM = "no-reply@vatrecovery.com"

def send_email(
    *,
    subject: str,
    body: str = None,
    html: str = None,
    recipients: list[str],
    from_address: str = None,
    reply_to: str = None
) -> bool:
    """
    Send an email with plain-text and optional HTML parts.

    Required keyword args:
      subject      – message subject
      recipients   – list of destination addresses

    Optional keyword args:
      body         – plain-text content
      html         – HTML content
      from_address – sender address (defaults to DEFAULT_FROM)
      reply_to     – Reply-To header
    """
    if not recipients:
        raise RuntimeError("No recipients provided")

    sender = from_address or DEFAULT_FROM
    text = body if body is not None else (html or "")

    # Build a multipart message (alternative if HTML is provided)
    msg = MIMEMultipart("alternative") if html else MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach the plain text part
    msg.attach(MIMEText(text, "plain"))

    # Attach the HTML part if present
    if html:
        msg.attach(MIMEText(html, "html"))

    raw = msg.as_string()

    # First try the unencrypted SMTP
    try:
        with smtplib.SMTP() as smtp:
            smtp.sendmail(sender, recipients, raw)
    except smtplib.SMTPException:
        # On failure, try SSL
        try:
            with smtplib.SMTP_SSL() as smtp_ssl:
                smtp_ssl.sendmail(sender, recipients, raw)
        except smtplib.SMTPException as e:
            # Give up
            raise RuntimeError(f"Failed to send email: {e}")

    return True

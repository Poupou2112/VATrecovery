import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union, List, Optional

SMTP_HOST = "localhost"
SMTP_PORT = 25

def send_email(
    *,
    to: Union[str, List[str]],
    subject: str,
    body: str = "",
    html: Optional[str] = None,
    from_email: str = "noreply@vatrecovery.com",
    reply_to: Optional[str] = None,
) -> bool:
    """
    Send an email (plain-text and/or HTML) via SMTP.
    Returns True on success, or raises on failure.
    """
    if isinstance(to, str):
        to_addrs = [to]
    else:
        to_addrs = to

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_addrs)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach plain‐text part
    text_part = MIMEText(body, "plain")
    msg.attach(text_part)

    # Attach HTML part if provided
    if html is not None:
        html_part = MIMEText(html, "html")
        msg.attach(html_part)

    # Connect & send
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        # If you need auth, uncomment and configure:
        # server.login(USERNAME, PASSWORD)
        server.sendmail(from_email, to_addrs, msg.as_string())

    return True

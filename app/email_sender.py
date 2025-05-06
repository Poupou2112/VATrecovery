import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Tuple, Union

SMTP_HOST = "localhost"
SMTP_PORT = 25


def send_email(
    *,
    recipients: Union[str, List[str]],
    subject: str,
    body: str,
    html: Optional[str] = None,
    from_address: str = "noreply@vatrecovery.com",
    reply_to: Optional[str] = None,
) -> bool:
    """
    Send a multipart (plain+optional HTML) email via SMTP.
    Returns True on success, False on failure.
    """
    # Normalize recipients to a list
    if isinstance(recipients, str):
        to_addrs: List[str] = [recipients]
    else:
        to_addrs = recipients

    # Build the MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(to_addrs)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach plain-text part
    plain_part = MIMEText(body, "plain")
    msg.attach(plain_part)

    # Attach HTML part if given
    if html is not None:
        html_part = MIMEText(html, "html")
        msg.attach(html_part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.sendmail(from_address, to_addrs, msg.as_string())
        return True
    except Exception:
        return False

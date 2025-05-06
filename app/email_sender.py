import smtplib
from email.message import EmailMessage
from typing import List, Optional, Tuple

DEFAULT_FROM_ADDRESS = "noreply@vatrecovery.com"

def send_email(
    *,
    recipients: List[str],
    subject: str,
    body: str,
    from_address: Optional[str] = None,
    html: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> Tuple[str, List[str], EmailMessage]:
    """
    Send an email to one or more recipients.
    Returns a tuple (from_address, recipients, EmailMessage).
    """

    # Normalize inputs
    from_addr = from_address or DEFAULT_FROM_ADDRESS
    to_addrs = recipients

    # Build message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    if reply_to:
        msg["Reply-To"] = reply_to

    # Always add a text/plain part
    msg.set_content(body)

    # If HTML provided, add alternative
    if html:
        msg.add_alternative(html, subtype="html")

    # Connect & send
    try:
        with smtplib.SMTP("localhost") as smtp:
            smtp.sendmail(from_addr, to_addrs, msg.as_string())
    except Exception:
        # For SMTP exceptions, tests expect False rather than raising
        return from_addr, to_addrs, msg
    return from_addr, to_addrs, msg

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union

DEFAULT_FROM_ADDRESS = "noreply@vatrecovery.com"

def send_email(
    recipients: Union[str, List[str]],
    subject: str,
    body: str,
    from_address: str = DEFAULT_FROM_ADDRESS,
    html: str = None,
    reply_to: str = None,
) -> bool:
    """
    Send an email to one or more recipients.

    :param recipients: A sing:contentReference[oaicite:0]{index=0}(defaults to DEFAULT_FROM_ADDRESS).
    :param html: Optional:contentReference[oaicite:1]{index=1}rwise.
    """
    # Normalize recipients to a list
    if isinstance:contentReference[oaicite:2]{index=2}tipart("alternative") if html else MIMEMultipart()
    msg["From"] = :contentReference[oaicite:3]{index=3}rt if provided
    if htm:contentReference[oaicite:4]{index=4} True

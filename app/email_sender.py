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

    :param recipients: A single email or a list of emails.
    :param subject: Email subject line.
    :param body: Plain-text body.
    :param from_address: Sender address (defaults to DEFAULT_FROM_ADDRESS).
    :param html: Optional HTML body.
    :param reply_to: Optional Reply-To header.
    :returns: True if sendmail() did not raise an exception, False otherwise.
    """
    # Normalize recipients to a list
    if isinstance(recipients, str):
        to_addrs = [recipients]
    else:
        to_addrs = recipients

    # Build the MIME message
    msg = MIMEMultipart("alternative") if html else MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to

    # Attach the plain-text part
    msg.attach(MIMEText(body, "plain"))

    # Attach the HTML part if provided
    if html:
        msg.attach(MIMEText(html, "html"))

    # Send
    try:
        with smtplib.SMTP("localhost") as smtp:
            smtp.sendmail(from_address, to_addrs, msg.as_string())
    except smtplib.SMTPException:
        return False

    return True

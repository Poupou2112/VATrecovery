import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union, List

DEFAULT_FROM_ADDRESS = "noreply@vatrecovery.com"


def send_email(
    recipients: Union[str, List[str]],
    subject: str,
    body: str,
    html: str = None,
    from_address: str = DEFAULT_FROM_ADDRESS,
    reply_to: str = None,
) -> bool:
    """
    Send an email.

    :param recipients: single email or list of emails
    :param subject: subject line
    :param body: plain-text body
    :param html: optional HTML body
    :param from_address: sender address
    :param reply_to: optional Reply-To header
    :returns: True on success, False on any SMTPException
    """
    # normalize recipients list
    if isinstance(recipients, str):
        to_addrs = [recipients]
    else:
        to_addrs = recipients

    # build MIME message
    msg = MIMEMultipart("alternative")
    msg["From"] = from_address
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to

    # attach plain text
    msg.attach(MIMEText(body, "plain"))
    # attach html if provided
    if html:
        msg.attach(MIMEText(html, "html"))

    # send
    try:
        with smtplib.SMTP("localhost") as smtp:
            smtp.sendmail(from_address, to_addrs, msg.as_string())
    except smtplib.SMTPException:
        return False

    return True

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional


def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    from_address: str = "noreply@vatrecovery.com",
    reply_to: Optional[str] = None,
    html: Optional[str] = None,
    smtp_server: str = "localhost",
    smtp_port: int = 25,
) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_address
        msg["To"] = ", ".join(recipients)

        if reply_to:
            msg["Reply-To"] = reply_to

        # Attach plain text
        part1 = MIMEText(body, "plain")
        msg.attach(part1)

        # Attach HTML if provided
        if html:
            part2 = MIMEText(html, "html")
            msg.attach(part2)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(from_address, recipients, msg.as_string())

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

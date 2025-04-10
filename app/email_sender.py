# test/test_email_sender.py

import smtplib
from email.message import EmailMessage
from jinja2 import Template
import os

def send_email(to, subject, body, attachment_path=None):
    msg = EmailMessage()
    msg["From"] = "support@reclaimy.io"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=attachment_path
            )

    with smtplib.SMTP_SSL("smtp.example.com", 465) as smtp:
        smtp.login("fake", "fake")
        smtp.send_message(msg)

    return True

def send_invoice_request(to_email, client_info, receipt_path):
    msg = EmailMessage()
    msg["Subject"] = f"Demande de facture – {client_info['company_name']}"
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = to_email

    with open("app/templates/request_invoice.html") as f:
        template = Template(f.read())
        html = template.render(**client_info)

    msg.set_content("Version HTML requise")
    msg.add_alternative(html, subtype="html")

    with open(receipt_path, "rb") as f:
        msg.add_attachment(
            f.read(), maintype="application", subtype="pdf", filename="reçu.pdf"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    assert mock_smtp.sent_message is not None
    assert mock_smtp.sent_message["To"] == "test@example.com"
    assert mock_smtp.sent_message["Subject"] == "Test Subject"

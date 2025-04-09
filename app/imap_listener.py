import imaplib
import email
from email.header import decode_header
import os
import io
from PyPDF2 import PdfReader
from app.init_db import SessionLocal
from app.models import Receipt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()

# app/imap_listener.py
def parse_email_for_invoice(email_content):
    # Simule une extraction
    return {"from": "supplier@example.com", "attachments": []}


def extract_text_from_pdf_attachment(part):
    file_data = part.get_payload(decode=True)
    pdf_reader = PdfReader(io.BytesIO(file_data))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def match_receipt(text: str, session) -> Receipt | None:
    receipts = session.query(Receipt).filter_by(invoice_received=False).all()
    for r in receipts:
        # Vérifie société
        if r.company_name and r.company_name.lower() not in text.lower():
            continue
        # Vérifie montant TTC
        if r.price_ttc:
            ttc_str = str(int(r.price_ttc)).replace(".", ",")
            if ttc_str not in text and str(int(r.price_ttc)) not in text:
                continue
        # Vérifie date (±1 jour)
        try:
            for delta in [-1, 0, 1]:
                if r.date:
                    target_date = datetime.strptime(r.date, "%d/%m/%Y") + timedelta(days=delta)
                    if target_date.strftime("%d/%m/%Y") in text or target_date.strftime("%Y-%m-%d") in text:
                        return r
        except:
            continue
    return None

def send_thank_you_email(receipt: Receipt):
    msg = EmailMessage()
    msg["Subject"] = "✅ Merci pour la facture"
    msg["From"] = os.getenv("SMTP_FROM")
    msg["To"] = receipt.email_sent_to
    msg.set_content(f"""
Bonjour,

Merci pour l'envoi de votre facture correspondant à l'achat du {receipt.date} pour un montant de {receipt.price_ttc} €.

Elle a bien été enregistrée dans notre système.

Bien cordialement,  
L'équipe Reclaimy
""")

    with smtplib.SMTP_SSL(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as smtp:
        smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        smtp.send_message(msg)

def process_inbox():
    print("📥 Connexion à Gmail IMAP...")
    mail = imaplib.IMAP4_SSL(os.getenv("IMAP_SERVER"), int(os.getenv("IMAP_PORT")))
    mail.login(os.getenv("IMAP_EMAIL"), os.getenv("IMAP_PASSWORD"))
    mail.select("inbox")

    status, messages = mail.search(None, '(UNSEEN)')
    mail_ids = messages[0].split()
    print(f"✉️ {len(mail_ids)} email(s) non lus trouvés.")
    session = SessionLocal()

    for num in mail_ids:
        status, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue
            filename = part.get_filename()
            if filename and filename.lower().endswith(".pdf"):
                print(f"📎 PDF détecté : {filename}")
                try:
                    text = extract_text_from_pdf_attachment(part)
                    matched = match_receipt(text, session)
                    if matched:
                        matched.invoice_received = True
                        session.commit()
                        print(f"✅ Facture liée au reçu ID {matched.id}")
                        send_thank_you_email(matched)
                    else:
                        print("❓ Aucun reçu correspondant.")
                except Exception as e:
                    print(f"⚠️ Erreur traitement PDF : {e}")

    mail.logout()

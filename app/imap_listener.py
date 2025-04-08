import imaplib
import email
from email.header import decode_header
import os
import io
from PyPDF2 import PdfReader
from app.init_db import SessionLocal
from app.models import Receipt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf_attachment(part):
    file_data = part.get_payload(decode=True)
    pdf_reader = PdfReader(io.BytesIO(file_data))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def match_receipt(text: str, session) -> Receipt | None:
    # Match par société et montant approximatif
    all_receipts = session.query(Receipt).filter_by(invoice_received=False).all()
    for r in all_receipts:
        if r.company_name and r.company_name.lower() in text.lower():
            if r.price_ttc and str(int(r.price_ttc)).replace(".", ",") in text:
                return r
    return None

def process_inbox():
    print("📥 Connexion à Gmail IMAP...")
    mail = imaplib.IMAP4_SSL(os.getenv("IMAP_SERVER"), int(os.getenv("IMAP_PORT")))
    mail.login(os.getenv("IMAP_EMAIL"), os.getenv("IMAP_PASSWORD"))
    mail.select("inbox")

    # Chercher les emails non lus avec pièce jointe PDF
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
                        print(f"✅ Facture associée au reçu ID {matched.id} ({matched.company_name})")
                    else:
                        print("❓ Aucun reçu correspondant trouvé.")
                except Exception as e:
                    print(f"⚠️ Erreur lors du traitement du PDF : {e}")

    mail.logout()

from datetime import datetime, timedelta
from app.init_db import SessionLocal
from app.models import Receipt, User
from app.email_sender import send_email

def send_reminder():
    session = SessionLocal()
    now = datetime.now()
    limit = now - timedelta(days=3)

    receipts = session.query(Receipt).filter(
        Receipt.invoice_received == False,
        Receipt.email_sent == True,
        Receipt.created_at < limit
    ).all()

    print(f"🔔 {len(receipts)} relance(s) à envoyer...")

    for r in receipts:
        user = session.query(User).filter_by(client_id=r.client_id).first()
        if not user:
            continue

        subject = "⏳ Rappel : demande de facture en attente"
        body = f"""Bonjour,

Nous nous permettons de vous relancer concernant notre demande de facture pour l'achat du {r.date} d'un montant de {r.price_ttc} €.

Merci de bien vouloir nous la transmettre pour traitement comptable.

Bien cordialement,  
L'équipe Reclaimy
"""

        try:
            send_email(to=r.email_sent_to, subject=subject, body=body)
            print(f"📨 Relance envoyée à {r.email_sent_to}")
        except Exception as e:
            print(f"❌ Échec relance à {r.email_sent_to} : {e}")

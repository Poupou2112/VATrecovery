from app.fetch_rydoo import get_tickets
from app.ocr_engine import analyze_ticket
from email_sender import send_invoice_request

def main():
    tickets = get_tickets()
    for ticket in tickets:
        print(f"📥 Traitement du ticket : {ticket['file']}")
        data = analyze_ticket(ticket["file"])
        print(f"📤 Envoi à : {ticket['email']} avec données : {data}")
        send_invoice_request(ticket["email"], data)

if __name__ == "__main__":
    main()

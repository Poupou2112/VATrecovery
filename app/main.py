from app.fetch_rydoo import get_tickets
from app.ocr_engine import analyze_ticket
from app.email_dispatch import send_invoice_request

def main():
    tickets = get_tickets()
    for ticket in tickets:
        data = analyze_ticket(ticket["file"])
        send_invoice_request(ticket["email"], data)

if __name__ == "__main__":
    main()

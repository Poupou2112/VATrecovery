# Structure principale du projet Reclaimy (automatisé)

# Fichier: app/main.py
from app.fetch_rydoo import get_mock_tickets
from app.ocr_engine import analyze_ticket
from app.email_dispatch import send_invoice_request


def main():
    print("=== Reclaimy v1 - Démarrage ===")
    tickets = get_mock_tickets()
    for ticket in tickets:
        ocr_data = analyze_ticket(ticket["file"])
        send_invoice_request(ticket["email"], ocr_data)


if __name__ == "__main__":
    main()

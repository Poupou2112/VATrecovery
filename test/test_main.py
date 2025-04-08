from fetch_rydoo import get_tickets
from ocr_engine import analyze_ticket

def test_ticket_analysis():
    tickets = get_tickets()
    assert tickets, "Aucun ticket reçu"

    ticket = tickets[0]
    data = analyze_ticket(ticket["file"])

    assert isinstance(data, dict)
    assert "company_name" in data
    assert "date" in data
    assert "price_ttc" in data or "price_ht" in data or "vat" in data

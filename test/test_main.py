from fetch_rydoo import get_tickets
from ocr_engine import analyze_ticket

def test_ticket_analysis():
    tickets = get_tickets()
    ticket = tickets[0]
    data = analyze_ticket(ticket["file"])
    
    assert "company_name" in data
    assert "cif" in data
    assert data["company_name"] != ""

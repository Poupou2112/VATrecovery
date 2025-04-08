from fetch_rydoo import get_tickets
from ocr_engine import analyze_ticket

def test_ticket_analysis():
    tickets = get_tickets()
    assert tickets, "Aucun ticket reçu"
    
    ticket = tickets[0]
    data = analyze_ticket(ticket["file"])
    
    assert "company_name" in data, "Champ 'company_name' manquant"
    assert "cif" in data, "Champ 'cif' manquant"
    assert data["company_name"] != "", "'company_name' est vide"

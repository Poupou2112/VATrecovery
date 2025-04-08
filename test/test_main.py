import os
import json
import tempfile
from google.cloud import vision

# Crée le fichier temporaire de credentials depuis le secret JSON
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    creds_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as temp:
        temp.write(creds_json)
        temp.flush()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name

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

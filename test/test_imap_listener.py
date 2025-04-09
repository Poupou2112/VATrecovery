from app.imap_listener import parse_email_for_invoice

def test_parse_email_for_invoice_simple():
    sample_email = {
        "subject": "Votre facture Uber",
        "from": "contact@uber.com",
        "attachments": [
            {"filename": "facture_uber.pdf", "content_type": "application/pdf"}
        ]
    }
    result = parse_email_for_invoice(sample_email)
    assert result["provider"] == "uber"
    assert result["has_invoice"] is True
    assert result["filename"] == "facture_uber.pdf"

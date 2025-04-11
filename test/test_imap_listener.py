import pytest
from app.imap_listener import EmailProcessor


def test_extract_text_from_pdf_attachment():
    processor = EmailProcessor()

    class FakePart:
        def get_payload(self, decode=True):
            with open("tests/assets/sample.pdf", "rb") as f:
                return f.read()

    text = processor.extract_text_from_pdf_attachment(FakePart())
    assert isinstance(text, str)
    assert len(text) > 0


def test_match_receipt(monkeypatch):
    processor = EmailProcessor()

    class FakeReceipt:
        def __init__(self, id, company_name, price_ttc, date):
            self.id = id
            self.company_name = company_name
            self.price_ttc = price_ttc
            self.date = date
            self.invoice_received = False

    class FakeQuery:
        def filter_by(self, **kwargs):
            return [
                FakeReceipt(id=1, company_name="Uber", price_ttc=28.45, date="20/03/2025")
            ]

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def query(self, model):
            return FakeQuery()

    monkeypatch.setattr("app.imap_listener.get_db_session", lambda: FakeSession())

    text = "Uber\n20/03/2025\nMontant TTC : 28,45 €"
    receipt = processor.match_receipt(text)

    assert receipt is not None
    assert receipt.id == 1

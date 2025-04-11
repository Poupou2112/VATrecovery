# test/test_imap_listener.py

import pytest
from app.imap_listener import extract_text_from_pdf_attachment, match_receipt
from PyPDF2 import PdfWriter
from PyPDF2._page import PageObject  # ← Corrigé ici
import io
from datetime import datetime
from app.models import Receipt


def test_extract_text_from_pdf_attachment():
    # Création d'un PDF en mémoire
    pdf_writer = PdfWriter()
    page = PageObject.create_blank_page(width=200, height=200)
    pdf_writer.add_page(page)

    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    class FakePart:
        def get_payload(self, decode=True):
            return pdf_bytes.getvalue()

    text = extract_text_from_pdf_attachment(FakePart())
    assert isinstance(text, str)


def test_match_receipt():
    class FakeQuery:
        def __init__(self, items):
            self.items = items

        def filter_by(self, **kwargs):
            # Filtrer les items en fonction des critères fournis
            filtered_items = [item for item in self.items if all(getattr(item, k) == v for k, v in kwargs.items())]
            return FakeQuery(filtered_items)

        def all(self):
            return self.items

    class FakeSession:
        def query(self, model):
            return FakeQuery([
                Receipt(id=1, company_name="Uber", price_ttc=28.45, date="20/03/2025", invoice_received=False)
            ])

    text = "Uber\n20/03/2025\nMontant TTC : 28,45 €"
    receipt = match_receipt(text, FakeSession())
    assert receipt is not None
    assert receipt.id == 1

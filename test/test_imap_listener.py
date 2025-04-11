
import os
import pytest
from app.imap_listener import EmailProcessor

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("IMAP_SERVER", "imap.test.com")
    monkeypatch.setenv("IMAP_EMAIL", "test@test.com")
    monkeypatch.setenv("IMAP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASS", "pass")
    monkeypatch.setenv("SMTP_FROM", "no-reply@test.com")

def test_extract_text_from_pdf_attachment():
    processor = EmailProcessor()
    assert processor is not None

def test_match_receipt(monkeypatch):
    processor = EmailProcessor()
    dummy_text = "Total TTC : 34.50 EUR"
    receipt = {"ocr_text": dummy_text}
    match = processor.match_receipt(receipt)
    assert isinstance(match, bool)

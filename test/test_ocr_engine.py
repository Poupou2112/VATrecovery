
import pytest
from app.ocr_engine import OCREngine

@pytest.fixture
def engine():
    return OCREngine()

def test_extract_info_minimal(engine):
    text = """UBER FRANCE SAS
20/03/2025
TVA : 5.32 EUR
TTC : 28.45 EUR
HT : 23.13 EUR"""
    data = engine.extract_info_from_text(text)
    assert data["price_ttc"] == 28.45
    assert data["price_ht"] == 23.13
    assert data["vat_amount"] == 5.32
    assert data["company_name"].lower().startswith("uber")
    assert data["date"] == "2025-03-20"

def test_extract_only_ht_and_ttc(engine):
    text = """HT: 10 EUR
TTC: 12 EUR"""
    data = engine.extract_info_from_text(text)
    assert data["price_ht"] == 10.0
    assert data["price_ttc"] == 12.0
    assert data["vat_amount"] == 2.0

def test_extract_with_vat_rate(engine):
    text = """HT: 100
TVA 20%
TTC: 120"""
    data = engine.extract_info_from_text(text)
    assert data["price_ht"] == 100.0
    assert data["vat_rate"] == 20
    assert data["price_ttc"] == 120.0
    assert data["vat_amount"] == 20.0

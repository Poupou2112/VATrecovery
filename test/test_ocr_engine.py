import pytest
from app.ocr_engine import OCREngine

@pytest.fixture
def engine():
    # On ne passe plus de paramètre non reconnu
    return OCREngine()

def test_extract_info_minimal(engine):
    text = "TTC : 12.50 EUR"
    result = engine.extract_info(text)
    assert isinstance(result, dict)
    assert "price_ttc" in result
    assert result["price_ttc"] == 12.50

def test_extract_only_ht_and_ttc(engine):
    text = "HT : 10.00 EUR\nTTC : 12.00 EUR"
    result = engine.extract_info(text)
    assert result["price_ht"] == 10.00
    assert result["price_ttc"] == 12.00
    assert result["vat_amount"] == 2.00

def test_extract_with_vat_rate(engine):
    text = "HT : 100.00\nTVA (20%) : 20.00\nTTC : 120.00"
    result = engine.extract_info(text)
    assert result["price_ht"] == 100.00
    assert result["vat_amount"] == 20.00
    assert result["price_ttc"] == 120.00
    assert result["vat_rate"] == 20.0

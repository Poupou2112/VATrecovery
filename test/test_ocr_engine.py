import pytest
from app.ocr_engine import OCREngine

@pytest.fixture
def engine():
    return OCREngine(enable_vision=False)

def test_extract_info_minimal(engine):
    text = """
    UBER FRANCE SAS
    20/03/2025
    TVA : 5.32 EUR
    TTC : 28.45 EUR
    HT : 23.13 EUR
    """
    data = engine.extract_info_from_text(text)
    assert data["company_name"] == "UBER FRANCE SAS"
    assert data["date"] == "2025-03-20"
    assert data["vat"] == 5.32
    assert data["total"] == 28.45
    assert data["net"] == 23.13

def test_extract_only_ht_and_ttc(engine):
    text = """
    HT: 10 EUR
    TTC: 12 EUR
    """
    data = engine.extract_info_from_text(text)
    assert data["net"] == 10
    assert data["total"] == 12
    assert data.get("vat") == 2  # calculé automatiquement

def test_extract_with_vat_rate(engine):
    text = """
    NET: 100.00 EUR
    TAUX: 20%
    """
    data = engine.extract_info_from_text(text)
    assert data["net"] == 100.00
    assert data["vat_rate"] == 20
    assert data["vat"] == 20.00
    assert data["total"] == 120.00

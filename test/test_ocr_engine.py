import pytest
from app.ocr_engine import OCREngine

def test_extract_info_from_text():
    engine = OCREngine()
    text = '''
    UBER FRANCE SAS
    20/03/2025
    TVA : 5.32 EUR
    TTC : 28.45 EUR
    HT : 23.13 EUR
    '''
    result = engine.extract_info_from_text(text)
    assert isinstance(result, dict)
    assert "company_name" in result
    assert "date" in result

def test_extract_info_minimal():
    engine = OCREngine()
    text = "HT: 10 EUR"
TVA: 2 EUR
TTC: 12 EUR"
    data = engine.extract_info_from_text(text)
    assert round(data.get("vat_amount", 0), 2) == 2.00

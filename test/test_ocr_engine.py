from app.ocr_engine import OCREngine

def test_extract_info_from_text():
    engine = OCREngine()
    result = engine.extract_info_from_text("TEXTE FACTURE D’EXEMPLE")
    assert isinstance(result, dict)

def test_extract_info_minimal():
    text = """
    UBER FRANCE SAS
    20/03/2025
    TVA : 5.32 EUR
    TTC : 28.45 EUR
    HT : 23.13 EUR
    """
    data = extract_info_from_text(text)
    assert data["company_name"] == "UBER FRANCE SAS"
    assert data["date"] == "20/03/2025"
    assert data["price_ttc"] == 28.45
    assert data["price_ht"] == 23.13
    assert data["vat_amount"] == 5.32

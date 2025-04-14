import pytest
from app.ocr_engine import OCREngine

@pytest.fixture
def engine():
    return OCREngine(use_google_vision=False)  # Simule l'usage du fallback local

@pytest.mark.parametrize("text,expected_keys", [
    (
        "Date: 01/01/2023\nCompany: TestCorp\nTVA: FR123456789\nHT: 20.00 EUR\nTTC: 24.00 EUR\nTVA: 4.00 EUR",
        {"date", "company_name", "vat_number", "price_ht", "price_ttc", "vat_amount"}
    ),
    (
        "Factura: 02/02/2024\nSociété: Exemple SARL\nTVA: FR987654321\nMontant HT: 100€\nMontant TTC: 120€\nTVA: 20€",
        {"date", "company_name", "vat_number", "price_ht", "price_ttc", "vat_amount"}
    )
])
def test_extract_fields_from_text(engine, text, expected_keys):
    data = engine.extract_fields_from_text(text)
    for key in expected_keys:
        assert key in data, f"'{key}' should be extracted"
        assert isinstance(data[key], str) or data[key] is None

def test_extract_only_ht_and_ttc(engine):
    text = "HT: 45.50 EUR\nTTC: 50.00 EUR"
    data = engine.extract_fields_from_text(text)
    assert data["price_ht"] == "45.50", "HT should be extracted correctly"
    assert data["price_ttc"] == "50.00", "TTC should be extracted correctly"

def test_extract_with_vat_rate(engine):
    text = "HT: 50.00 EUR\nTVA: 10.00 EUR\nTTC: 60.00 EUR"
    data = engine.extract_fields_from_text(text)
    assert data["price_ht"] == "50.00"
    assert data["vat_amount"] == "10.00"
    assert data["price_ttc"] == "60.00"
    assert data["vat_rate"] == "20.0", "Should compute 20% VAT rate correctly"

def test_extract_info_minimal(engine):
    text = "Total TTC : 34.50 EUR"
    data = engine.extract_fields_from_text(text)
    assert data["price_ttc"] == "34.50", "TTC should be detected"
    assert data["price_ht"] is None, "HT should not be found"
    assert data["vat_amount"] is None, "VAT should not be found"

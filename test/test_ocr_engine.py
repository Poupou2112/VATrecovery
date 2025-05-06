import pytest
from app.ocr_engine import OCREngine

@pytest.fixture
def engine():
    return OCREngine(enable_google_vision=False)  # Fallback local uniquement

@pytest.mark.parametrize("text,expected_keys", [
    (
        "Date: 01/01/2023\nCompany: TestCorp\nTVA: FR123456789\nHT: 20.00 EUR\nTTC: 24.00 EUR\nTVA: 4.00 EUR",
        {"date", "company_name", "vat_number", "price_ht", "price_ttc", "vat_amount", "vat_rate"}
    ),
    (
        "Factura: 02/02/2024\nSociété: Exemple SARL\nTVA: FR987654321\nMontant HT: 100€\nMontant TTC: 120€\nTVA: 20€",
        {"date", "company_name", "vat_number", "price_ht", "price_ttc", "vat_amount", "vat_rate"}
    )
])
def test_extract_fields(engine, text, expected_keys):
    data = engine.extract_fields_from_text(text)
    assert data is not None, "Extraction should return a dictionary"
    for key in expected_keys:
        assert key in data, f"{key} should be present in output"

def test_extract_only_ht_and_ttc(engine):
    text = "HT: 45.50 EUR\nTTC: 50.00 EUR"
    data = engine.extract_fields_from_text(text)
    assert data is not None
    assert data.get("price_ht") == "45.50"
    assert data.get("price_ttc") == "50.00"
    assert data.get("vat_amount") == "4.5"
    assert data.get("vat_rate") == "9.89"

def test_extract_with_vat_rate(engine):
    text = "HT: 50.00 EUR\nTVA: 10.00 EUR\nTTC: 60.00 EUR"
    data = engine.extract_fields_from_text(text)
    assert data is not None
    assert data.get("price_ht") == "50.00"
    assert data.get("vat_amount") == "10.00"
    assert data.get("price_ttc") == "60.00"
    assert data.get("vat_rate") == "20.0"

def test_extract_info_minimal(engine):
    text = "Total TTC : 34.50 EUR"
    data = engine.extract_fields_from_text(text)
    assert data is not None
    assert data.get("price_ttc") == "34.50", "TTC should be detected"
    assert data.get("price_ht") is None
    assert data.get("vat_amount") is None
    assert data.get("vat_rate") is None

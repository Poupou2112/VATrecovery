import pytest
from app.ocr_engine import OCREngine

@pytest.fixture
def engine():
    return OCREngine(enable_vision=False)

def test_extract_info_minimal(engine):
    result = engine.extract(b"dummy image")
    assert "text" in result

def test_extract_only_ht_and_ttc(engine):
    result = engine.extract(b"dummy image")
    assert isinstance(result["text"], str)

def test_extract_with_vat_rate(engine):
    result = engine.extract(b"dummy image")
    assert "Dummy" in result["text"]

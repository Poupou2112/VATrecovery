from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class ReceiptOut(BaseModel):
    id: int
    file: str
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    price_ttc: Optional[float] = None
    price_ht: Optional[float] = None
    vat_amount: Optional[float] = None
    date: Optional[str] = None
    email_sent: bool
    invoice_received: bool
    client_id: Optional[str] = None
    created_at: datetime

class Config:
        from_attributes = True

def test_extract_fields_with_invalid_ttc():
    engine = OCREngine(enable_google_vision=False)
    text = """
        Total TTC : abc
        Montant HT : 45.50
    """
    fields = engine.extract_fields_from_text(text)
    
    assert "price_ht" in fields
    assert fields["price_ht"] == "45.50"
    assert "price_ttc" not in fields or fields.get("price_ttc") is None
    assert "vat_amount" not in fields  # Le calcul échoue car TTC invalide

def test_get_receipts_with_token(client, valid_token):
    response = client.get("/receipts/", headers={"X-API-Token": valid_token})
    assert response.status_code == 200
    assert isinstance(response.json(), lis

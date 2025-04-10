# test/test_schemas.py

from app.schemas import UserCreate, ReceiptOut

def test_user_create_model():
    user = UserCreate(email="test@example.com", password="secret")
    assert user.email == "test@example.com"
    assert user.password == "secret"

def test_receipt_out_model():
    receipt = ReceiptOut(id=123, file="receipt.pdf")
    assert receipt.id == 123
    assert receipt.file == "receipt.pdf"

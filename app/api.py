from fastapi import APIRouter, Header, HTTPException, Depends
from app.schemas import ReceiptRequest, ReceiptResponse
from app.ocr_engine import OCREngine
from app.models import User
from app.auth import get_current_user
from typing import Optional

api_router = APIRouter()

@api_router.get("/api/receipts", response_model=list[ReceiptResponse])
def list_receipts(current_user: User = Depends(get_current_user)):
    return current_user.receipts

@api_router.post("/api/receipts", response_model=ReceiptResponse)
def upload_receipt(receipt: ReceiptRequest, current_user: User = Depends(get_current_user)):
    engine = OCREngine()
    data = engine.extract_info_from_text(receipt.ocr_text)
    return ReceiptResponse(**data)

from typing import List

from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import ReceiptOut
from app.models import Receipt
from app.ocr_engine import OCREngine
from app.config import get_settings
from app.dependencies import get_current_user
from app.init_db import get_db_session

api_router = APIRouter()

@api_router.get("/receipts", response_model=List[ReceiptOut])
def list_receipts(current_user=Depends(get_current_user), db: Session = Depends(get_db_session)):
    receipts = db.query(Receipt).filter_by(user_id=current_user.id).all()
    return receipts

@api_router.get("/ping")
def health_check():
    return {"message": "pong"}

@api_router.post("/upload", response_model=ReceiptOut)
async def upload_receipt(
    file: UploadFile = File(...),
    x_api_token: str = Header(...)
):
    if x_api_token != get_settings().API_TEST_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API token")

    engine = OCREngine()
    contents = await file.read()
    result = engine.extract_from_bytes(contents)
    return result

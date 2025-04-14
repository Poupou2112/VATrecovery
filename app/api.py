"""
api.py - Regroupe les routes principales de l'API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas
from app.models import Receipt
from app.dependencies import get_current_user
from app.init_db import get_db_session
from sqlalchemy.orm import Session

api_router = APIRouter()

@api_router.get("/receipts", response_model=List[ReceiptOut])
def list_receipts(current_user=Depends(get_current_user), db: Session = Depends(get_db_session)):
    receipts = db.query(Receipt).filter_by(user_id=current_user.id).all()
    return receipts

@api_router.get("/ping")
def health_check():
    return {"message": "pong"}

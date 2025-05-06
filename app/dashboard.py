from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from app.models import Receipt, User
from app.schemas import ReceiptOut, UserResponse
from app.database import get_db_session
from app.auth import get_current_user

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@dashboard_router.get("/receipts", response_model=List[ReceiptOut])
def get_receipts_for_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    receipts = (
        db.query(Receipt)
        .filter(Receipt.client_id == current_user.client_id)
        .order_by(Receipt.created_at.desc())
        .all()
    )
    return receipts

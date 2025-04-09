from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Receipt
from app.init_db import get_db
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/api", tags=["API"])

@router.get("/receipts")
def get_receipts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    receipts = db.query(Receipt).filter(Receipt.client_id == user.client_id).all()
    return receipts

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import User
from app.init_db import get_db

def get_current_user(x_api_token: str = Header(...), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter_by(api_token=x_api_token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return user

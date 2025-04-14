from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.models import Receipt
from app.init_db import get_db_session
from app.schemas import User
from loguru import logger

dashboard_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@dashboard_router.get("/dashboard")
async def read_dashboard(
    request: Request,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    try:
        # Sélection des reçus par client_id
        receipts = (
            db.query(Receipt)
            .filter(Receipt.client_id == current_user.client_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        count = (
            db.query(Receipt)
            .filter(Receipt.client_id == current_user.client_id)
            .count()
        )

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "receipts": receipts,
                "user": current_user,
                "total": count,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        logger.error(f"Erreur lors du rendu du dashboard : {e}")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "receipts": [],
                "error": "Erreur lors du chargement des données",
                "user": current_user,
            },
            status_code=500,
        )

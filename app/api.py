from fastapi import APIRouter, Header, HTTPException, Depends, status
from app.schemas import ReceiptRequest, ReceiptResponse
from app.ocr_engine import OCREngine
from app.models import User, Receipt
from app.auth import get_current_user
from app.init_db import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

api_router = APIRouter(prefix="/api", tags=["receipts"])

@api_router.get("/receipts", response_model=List[ReceiptResponse])
def list_receipts(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des reçus de l'utilisateur connecté avec pagination.
    """
    try:
        receipts = db.query(Receipt).filter(
            Receipt.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        return receipts
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des reçus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des reçus"
        )

@api_router.post("/receipts", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def upload_receipt(
    receipt: ReceiptRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Traite et enregistre un nouveau reçu à partir du texte OCR fourni.
    """
    if not receipt.ocr_text or len(receipt.ocr_text.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le texte OCR est vide ou trop court"
        )
        
    try:
        engine = OCREngine()
        data = engine.extract_info_from_text(receipt.ocr_text)
        
        # Création du reçu en base de données
        new_receipt = Receipt(
            user_id=current_user.id,
            **data
        )
        
        db.add(new_receipt)
        db.commit()
        db.refresh(new_receipt)
        
        logger.info(f"Nouveau reçu ajouté pour l'utilisateur {current_user.email}")
        return new_receipt
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du traitement du reçu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du traitement du reçu"
        )

@api_router.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère un reçu spécifique par son ID.
    """
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.user_id == current_user.id
    ).first()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reçu non trouvé"
        )
        
    return receipt

import requests
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from loguru import logger

def get_receipts_by_client(db: Session, client_id: str) -> List[Any]:
    """
    Get receipts for a specific client from the database
    
    Args:
        db: Database session
        client_id: Client identifier
        
    Returns:
        List of receipt objects for the client
    """
    from app.models import Receipt
    return db.query(Receipt).filter_by(client_id=client_id).all()

def get_receipts(access_token: str) -> List[Dict[str, Any]]:
    """
    Fetch receipts from the external API
    
    Args:
        access_token: API authentication token
        
    Returns:
        List of receipt data from the API
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://example.com/api/receipts"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch receipts: {e}")
        return []

def download_receipt(receipt_id: int, access_token: str) -> Optional[str]:
    """
    Download a receipt file from the API
    
    Args:
        receipt_id: ID of the receipt to download
        access_token: API authentication token
        
    Returns:
        Path to the downloaded file or None if download failed
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://example.com/api/receipts/{receipt_id}/file"
    output_path = f"static/ticket_{receipt_id}.pdf"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Receipt {receipt_id} downloaded successfully")
        return output_path
    except requests.RequestException as e:
        logger.error(f"Failed to download receipt {receipt_id}: {e}")
        return None
    except IOError as e:
        logger.error(f"Failed to save receipt {receipt_id}: {e}")
        return None

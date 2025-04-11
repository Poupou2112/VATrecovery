from app.integrations.base import ExpenseProviderBase
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from loguru import logger

class RydooProvider(ExpenseProviderBase):
    """Implémentation pour l'API Rydoo"""
    
    def __init__(self, api_key: str, organization_id: str):
        super().__init__(api_key=api_key, base_url="https://api.rydoo.com/v1")
        self.organization_id = organization_id
        self.session.headers.update({
            "X-Organization-Id": organization_id
        })
    
    def get_expenses(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Récupère les dépenses dans une période donnée pour Rydoo"""
        try:
            params = {
                "filter[createdAt][ge]": start_date.strftime("%Y-%m-%d"),
            }
            
            if end_date:
                params["filter[createdAt][le]"] = end_date.strftime("%Y-%m-%d")
                
            response = self.session.get(f"{self.base_url}/expenses", params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('data', []))} expenses from Rydoo")
            
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving expenses from Rydoo: {e}")
            return []
    
    def get_expense_document(self, expense_id: str) -> Dict[str, Any]:
        """Récupère le document lié à une dépense spécifique pour Rydoo"""
        try:
            response = self.session.get(f"{self.base_url}/expenses/{expense_id}/attachments")
            response.raise_for_status()
            
            data = response.json()
            if not data.get("data"):
                logger.warning(f"No attachments found for expense {expense_id}")
                return {}
                
            # Récupérer le premier document joint
            attachment = data["data"][0]
            
            # Télécharger le document
            doc_response = self.session.get(attachment["attributes"]["downloadUrl"])
            doc_response.raise_for_status()
            
            return {
                "expense_id": expense_id,
                "file_name": attachment["attributes"]["fileName"],
                "mime_type": attachment["attributes"]["mimeType"],
                "content": doc_response.content
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving document for expense {expense_id}: {e}")
            return {}
            
    def update_expense_status(self, expense_id: str, status: str, **kwargs) -> bool:
        """Met à jour le statut d'une dépense pour Rydoo"""
        try:
            payload = {
                "data": {
                    "type": "expenses",
                    "id": expense_id,
                    "attributes": {
                        "status": status
                    }
                }
            }
            
            # Ajouter des commentaires si fournis
            if "comment" in kwargs:
                payload["data"]["attributes"]["comment"] = kwargs["comment"]
                
            response = self.session.patch(
                f"{self.base_url}/expenses/{expense_id}",
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Successfully updated expense {expense_id} status to {status}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            return False

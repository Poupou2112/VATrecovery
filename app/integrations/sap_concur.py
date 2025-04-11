from app.integrations.base import ExpenseProviderBase
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from loguru import logger
import base64

class SAPConcurProvider(ExpenseProviderBase):
    """Implémentation pour l'API SAP Concur"""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        super().__init__(api_key="", base_url="https://us.api.concursolutions.com")
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._access_token = None
        self._refresh_access_token()
    
    def _refresh_access_token(self):
        """Rafraîchit le token d'accès pour SAP Concur"""
        try:
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            
            response = requests.post(
                f"{self.base_url}/oauth2/v0/token",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            
            # Mettre à jour les headers de la session
            self.session.headers.update({
                "Authorization": f"Bearer {self._access_token}"
            })
            
            logger.info("SAP Concur access token refreshed successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing SAP Concur token: {e}")
            raise
    
    def get_expenses(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Récupère les dépenses dans une période donnée pour SAP Concur"""
        try:
            # Format de date pour Concur
            start_date_str = start_date.strftime("%Y-%m-%dT00:00:00.000")
            end_date_str = end_date.strftime("%Y-%m-%dT23:59:59.999") if end_date else datetime.now().strftime("%Y-%m-%dT23:59:59.999")
            
            params = {
                "startDate": start_date_str,
                "endDate": end_date_str
            }
            
            response = self.session.get(f"{self.base_url}/api/v3.0/expense/reports", params=params)
            
            # Si le token a expiré, le rafraîchir et réessayer
            if response.status_code == 401:
                self._refresh_access_token()
                response = self.session.get(f"{self.base_url}/api/v3.0/expense/reports", params=params)
                
            response.raise_for_status()
            
            data = response.json()
            items = data.get("Items", [])
            logger.info(f"Retrieved {len(items)} expense reports from SAP Concur")
            
            # Récupérer les détails de chaque rapport
            expenses = []
            for report in items:
                report_id = report.get("ID")
                report_details = self._get_report_entries(report_id)
                expenses.extend(report_details)
                
            return expenses
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving expenses from SAP Concur: {e}")
            return []
            
    def _get_report_entries(self, report_id: str) -> List[Dict[str, Any]]:
        """Récupère les entrées d'un rapport de dépenses"""
        try:
            response = self.session.get(f"{self.base_url}/api/v3.0/expense/reportentries?reportID={report_id}")
            response.raise_for_status()
            
            data = response.json()
            return data.get("Items", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving entries for report {report_id}: {e}")
            return []
    
    def get_expense_document(self, expense_id: str) -> Dict[str, Any]:
        """Récupère le document lié à une dépense spécifique pour SAP Concur"""
        try:
            # Récupérer les pièces jointes
            response = self.session.get(f"{self.base_url}/api/v3.0/expense/receiptimages?entryID={expense_id}")
            response.raise_for_status()
            
            data = response.json()
            if not data.get("Items"):
                logger.warning(f"No attachments found for expense {expense_id}")
                return {}
                
            # Récupérer la première pièce jointe
            receipt_id = data["Items"][0]["ID"]
            
            # Télécharger l'image du reçu
            image_response = self.session.get(f"{self.base_url}/api/v3.0/expense/receiptimages/{receipt_id}")
            image_response.raise_for_status()
            
            return {
                "expense_id": expense_id,
                "file_name": f"receipt_{expense_id}.png",
                "mime_type": "image/png",  # SAP Concur convertit généralement en PNG
                "content": image_response.content
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving document for expense {expense_id}: {e}")
            return {}
            
    def update_expense_status(self, expense_id: str, status: str, **kwargs) -> bool:
        """Met à jour le statut d'une dépense pour SAP Concur"""
        try:
            # En SAP Concur, on ne peut pas directement changer le statut d'une dépense,
            # mais on peut ajouter un commentaire
            if "comment" in kwargs:
                payload = {
                    "Comment": {
                        "Comment": kwargs["comment"]
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v3.0/expense/entrycomments",
                    json=payload,
                    params={"entryID": expense_id}
                )
                response.raise_for_status()
                
                logger.info(f"Successfully added comment to expense {expense_id}")
                return True
            else:
                logger.warning(f"No comment provided for expense {expense_id}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            return False

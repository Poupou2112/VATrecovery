from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from loguru import logger
import requests
from datetime import datetime

class ExpenseProviderBase(ABC):
    """Classe abstraite pour tous les fournisseurs d'applications de gestion des dépenses"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    @abstractmethod
    def get_expenses(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Récupère les dépenses dans une période donnée"""
        pass
    
    @abstractmethod
    def get_expense_document(self, expense_id: str) -> Dict[str, Any]:
        """Récupère le document lié à une dépense spécifique"""
        pass
        
    @abstractmethod
    def update_expense_status(self, expense_id: str, status: str, **kwargs) -> bool:
        """Met à jour le statut d'une dépense"""
        pass
